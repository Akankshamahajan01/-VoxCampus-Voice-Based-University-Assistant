"""
VoxCampus — RAG Engine
======================
Retrieval-Augmented Generation pipeline.

Two retrieval modes (auto-selected):
  1. Azure AI Search  — when AZURE_SEARCH_ENDPOINT + AZURE_SEARCH_KEY are set
     Uses hybrid search: vector (cosine) + keyword (BM25) for best accuracy.
  2. Local TF-IDF     — zero-config fallback using in-memory cosine similarity
     Works immediately without any extra Azure service.

Flow:
  query  →  embed / tokenise
         →  retrieve top-K chunks
         →  return joined context string
         →  LLM prompt in foundry.py
"""

import math
import re
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

# ── Chunk type ─────────────────────────────────────────────
class Chunk:
    def __init__(self, chunk_id: str, category: str, title: str, content: str):
        self.chunk_id  = chunk_id
        self.category  = category
        self.title     = title
        self.content   = content
        # TF-IDF vector computed at index time
        self._tfidf: Dict[str, float] = {}

    def to_dict(self) -> dict:
        return {
            "id":       self.chunk_id,
            "category": self.category,
            "title":    self.title,
            "content":  self.content,
        }


# ══════════════════════════════════════════════════════════
# LOCAL TF-IDF RETRIEVER  (no Azure needed)
# ══════════════════════════════════════════════════════════
class LocalRAGRetriever:
    """
    Lightweight in-process TF-IDF retriever.
    - Tokenises every chunk at startup.
    - Scores queries with cosine similarity over TF-IDF vectors.
    - O(n*vocab) — perfectly fast for ~100 chunks.
    """

    def __init__(self):
        self._chunks: List[Chunk] = []
        self._idf: Dict[str, float] = {}
        self._indexed = False

    # ── Build index ──────────────────────────────────────
    def build_index(self, chunks: List[Chunk]) -> None:
        self._chunks = chunks
        N = len(chunks)
        if N == 0:
            return

        # Document frequency
        df: Dict[str, int] = {}
        for chunk in chunks:
            tokens = set(self._tokenise(chunk.content + " " + chunk.title))
            for t in tokens:
                df[t] = df.get(t, 0) + 1

        # IDF  = log((N+1) / (df+1)) + 1  (smoothed)
        self._idf = {t: math.log((N + 1) / (v + 1)) + 1 for t, v in df.items()}

        # TF-IDF vectors for every chunk
        for chunk in chunks:
            tf = self._term_freq(chunk.content + " " + chunk.title)
            chunk._tfidf = {
                t: tf_val * self._idf.get(t, 1.0)
                for t, tf_val in tf.items()
            }

        self._indexed = True
        logger.info(f"LocalRAG: indexed {N} chunks, vocab size {len(self._idf)}")

    # ── Query ────────────────────────────────────────────
    def retrieve(self, query: str, top_k: int = 5) -> List[Chunk]:
        if not self._indexed or not self._chunks:
            return []

        q_tf  = self._term_freq(query)
        q_vec = {t: tf_val * self._idf.get(t, 1.0) for t, tf_val in q_tf.items()}
        q_norm = self._norm(q_vec)

        scores = []
        for chunk in self._chunks:
            dot   = sum(q_vec.get(t, 0) * chunk._tfidf.get(t, 0) for t in q_vec)
            denom = q_norm * self._norm(chunk._tfidf)
            score = dot / denom if denom > 0 else 0.0

            # Category boost: if query explicitly mentions the category name,
            # bump its chunks slightly so cross-category queries are still
            # answered correctly.
            cat_hint = chunk.category.lower()
            if cat_hint in query.lower():
                score *= 1.25

            scores.append((score, chunk))

        scores.sort(key=lambda x: x[0], reverse=True)
        top = [c for s, c in scores[:top_k] if s > 0]

        # If nothing scored positively, return top-k by title match
        if not top:
            top = self._chunks[:top_k]

        return top

    # ── Helpers ──────────────────────────────────────────
    @staticmethod
    def _tokenise(text: str) -> List[str]:
        text = text.lower()
        # Keep alphanumeric + ₹ signs
        tokens = re.findall(r"[a-z0-9₹]+", text)
        # Remove very common stop-words
        stop = {"the","a","an","is","it","in","of","to","and","or","for",
                "with","at","on","are","be","was","this","that","by","from"}
        return [t for t in tokens if t not in stop and len(t) > 1]

    @staticmethod
    def _term_freq(text: str) -> Dict[str, float]:
        tokens = LocalRAGRetriever._tokenise(text)
        if not tokens:
            return {}
        tf: Dict[str, int] = {}
        for t in tokens:
            tf[t] = tf.get(t, 0) + 1
        n = len(tokens)
        return {t: c / n for t, c in tf.items()}

    @staticmethod
    def _norm(vec: Dict[str, float]) -> float:
        return math.sqrt(sum(v * v for v in vec.values())) or 1.0


# ══════════════════════════════════════════════════════════
# AZURE AI SEARCH RETRIEVER  (hybrid: vector + keyword)
# ══════════════════════════════════════════════════════════
class AzureSearchRetriever:
    """
    Hybrid retriever using Azure AI Search.
    - BM25 keyword search + optional vector search (if embeddings configured).
    - Falls back to keyword-only if no embeddings deployment is set.
    """

    def __init__(self, endpoint: str, key: str, index: str,
                 openai_endpoint: str = "", openai_key: str = "",
                 embed_deployment: str = "text-embedding-ada-002",
                 api_version: str = "2024-02-01"):
        self._endpoint        = endpoint
        self._key             = key
        self._index           = index
        self._openai_endpoint = openai_endpoint
        self._openai_key      = openai_key
        self._embed_deployment = embed_deployment
        self._api_version     = api_version

    def retrieve(self, query: str, top_k: int = 5) -> List[Chunk]:
        try:
            from azure.search.documents import SearchClient
            from azure.core.credentials import AzureKeyCredential

            client = SearchClient(
                endpoint=self._endpoint,
                index_name=self._index,
                credential=AzureKeyCredential(self._key)
            )

            # Try hybrid search (vector + keyword) first
            vector_queries = self._build_vector_query(query, top_k)

            if vector_queries:
                results = client.search(
                    search_text=query,
                    vector_queries=vector_queries,
                    top=top_k,
                    select=["id", "category", "title", "content"]
                )
            else:
                # Keyword-only search
                results = client.search(
                    search_text=query,
                    top=top_k,
                    select=["id", "category", "title", "content"]
                )

            chunks = []
            for r in results:
                chunks.append(Chunk(
                    chunk_id=r.get("id", ""),
                    category=r.get("category", "general"),
                    title=r.get("title", ""),
                    content=r.get("content", "")
                ))
            logger.info(f"AzureSearch: retrieved {len(chunks)} chunks for query")
            return chunks

        except Exception as e:
            logger.error(f"Azure AI Search retrieval error: {e}")
            return []

    def _build_vector_query(self, query: str, top_k: int):
        """Generate embedding for query, return vector query object."""
        if not self._openai_endpoint or not self._openai_key:
            return None
        try:
            from openai import AzureOpenAI
            from azure.search.documents.models import VectorizedQuery

            oai = AzureOpenAI(
                azure_endpoint=self._openai_endpoint,
                api_key=self._openai_key,
                api_version=self._api_version
            )
            resp = oai.embeddings.create(
                model=self._embed_deployment,
                input=query
            )
            embedding = resp.data[0].embedding
            return [VectorizedQuery(
                vector=embedding,
                k_nearest_neighbors=top_k,
                fields="content_vector"
            )]
        except Exception as e:
            logger.warning(f"Embedding generation failed, using keyword-only: {e}")
            return None


# ══════════════════════════════════════════════════════════
# RAG PIPELINE  (public interface used by foundry.py)
# ══════════════════════════════════════════════════════════
class RAGPipeline:
    """
    Top-level RAG pipeline.
    - Automatically selects Azure AI Search if configured, else local TF-IDF.
    - Call `build()` once at startup to index knowledge chunks.
    - Call `retrieve(query)` at query time to get context string.
    """

    def __init__(self):
        self._local   = LocalRAGRetriever()
        self._azure   = None
        self._use_azure = False
        self._built   = False

    def build(self, chunks: List[Chunk]) -> None:
        """Index all knowledge chunks. Called once at app startup."""
        from app.config import settings

        # Always build local index (used as fallback)
        self._local.build_index(chunks)

        # Try to set up Azure AI Search if credentials present
        if settings.AZURE_SEARCH_ENDPOINT and settings.AZURE_SEARCH_KEY:
            self._azure = AzureSearchRetriever(
                endpoint=settings.AZURE_SEARCH_ENDPOINT,
                key=settings.AZURE_SEARCH_KEY,
                index=settings.AZURE_SEARCH_INDEX_NAME,
                openai_endpoint=settings.AZURE_FOUNDRY_ENDPOINT,
                openai_key=settings.AZURE_FOUNDRY_API_KEY,
                embed_deployment=settings.AZURE_EMBEDDINGS_DEPLOYMENT,
                api_version=settings.AZURE_FOUNDRY_API_VERSION
            )
            self._use_azure = True
            logger.info("RAG: Using Azure AI Search (hybrid mode)")
        else:
            logger.info("RAG: Using local TF-IDF retriever (no Azure Search configured)")

        self._built = True

    def retrieve(self, query: str, top_k: int = 5) -> str:
        """
        Retrieve top-K relevant chunks and return as a single context string.
        This string is injected directly into the LLM prompt.
        """
        if not self._built:
            logger.warning("RAG pipeline not built yet — returning empty context")
            return ""

        # Try Azure first, fall back to local
        chunks: List[Chunk] = []
        if self._use_azure and self._azure:
            chunks = self._azure.retrieve(query, top_k)
            if not chunks:
                logger.info("Azure Search returned 0 results, falling back to local")
                chunks = self._local.retrieve(query, top_k)
        else:
            chunks = self._local.retrieve(query, top_k)

        if not chunks:
            return ""

        # Format chunks into a readable context block
        parts = []
        for i, chunk in enumerate(chunks, 1):
            parts.append(
                f"[Source {i} — {chunk.category.upper()} / {chunk.title}]\n{chunk.content}"
            )

        context = "\n\n---\n\n".join(parts)
        logger.info(
            f"RAG retrieved {len(chunks)} chunks "
            f"({'Azure' if self._use_azure and self._azure else 'Local TF-IDF'})"
        )
        return context

    def get_mode(self) -> str:
        if self._use_azure and self._azure:
            return "azure_search"
        return "local_tfidf"


# ── Singleton ──────────────────────────────────────────────
rag_pipeline = RAGPipeline()

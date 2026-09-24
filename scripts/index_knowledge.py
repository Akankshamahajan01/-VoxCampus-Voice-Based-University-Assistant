"""
VoxCampus — Azure AI Search Index Builder
==========================================
Run this script ONCE to:
  1. Create the Azure AI Search index (with vector field)
  2. Generate embeddings for every knowledge chunk via Azure OpenAI
  3. Upload all chunks to the index

Usage:
    cd /Users/akankshamahajan/Desktop/VoxCampus
    source .venv/bin/activate
    python scripts/index_knowledge.py

Requirements:
    .env must have:
        AZURE_SEARCH_ENDPOINT
        AZURE_SEARCH_KEY
        AZURE_SEARCH_INDEX_NAME   (default: voxcampus-knowledge)
        AZURE_FOUNDRY_ENDPOINT    (Azure OpenAI endpoint for embeddings)
        AZURE_FOUNDRY_API_KEY
        AZURE_EMBEDDINGS_DEPLOYMENT  (default: text-embedding-ada-002)
        AZURE_FOUNDRY_API_VERSION
"""

import sys
import os

# Make sure we can import app modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv
load_dotenv()

from app.config import settings
from app.knowledge import get_all_chunks


# ── Constants ──────────────────────────────────────────────
VECTOR_DIMS = 1536          # text-embedding-ada-002 dimensions
                             # Change to 3072 if using text-embedding-3-large


def create_index(search_client_factory):
    """Create Azure AI Search index with vector field."""
    from azure.search.documents.indexes import SearchIndexClient
    from azure.search.documents.indexes.models import (
        SearchIndex, SimpleField, SearchableField, SearchField,
        SearchFieldDataType, VectorSearch, HnswAlgorithmConfiguration,
        VectorSearchProfile
    )
    from azure.core.credentials import AzureKeyCredential

    index_client = SearchIndexClient(
        endpoint=settings.AZURE_SEARCH_ENDPOINT,
        credential=AzureKeyCredential(settings.AZURE_SEARCH_KEY)
    )

    # Delete existing index if present (re-index cleanly)
    existing = [i.name for i in index_client.list_indexes()]
    if settings.AZURE_SEARCH_INDEX_NAME in existing:
        index_client.delete_index(settings.AZURE_SEARCH_INDEX_NAME)
        print(f"🗑️  Deleted existing index '{settings.AZURE_SEARCH_INDEX_NAME}'")

    # Vector search configuration
    vector_search = VectorSearch(
        algorithms=[HnswAlgorithmConfiguration(name="hnsw-config")],
        profiles=[VectorSearchProfile(
            name="vector-profile",
            algorithm_configuration_name="hnsw-config"
        )]
    )

    fields = [
        SimpleField(name="id",       type=SearchFieldDataType.String, key=True),
        SimpleField(name="category", type=SearchFieldDataType.String, filterable=True),
        SearchableField(name="title",   type=SearchFieldDataType.String),
        SearchableField(name="content", type=SearchFieldDataType.String),
        SearchField(
            name="content_vector",
            type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
            searchable=True,
            vector_search_dimensions=VECTOR_DIMS,
            vector_search_profile_name="vector-profile"
        )
    ]

    index = SearchIndex(
        name=settings.AZURE_SEARCH_INDEX_NAME,
        fields=fields,
        vector_search=vector_search
    )
    index_client.create_index(index)
    print(f"✅ Created index '{settings.AZURE_SEARCH_INDEX_NAME}' with vector field ({VECTOR_DIMS} dims)")


def embed_text(oai_client, text: str) -> list:
    """Generate embedding vector for a text string."""
    response = oai_client.embeddings.create(
        model=settings.AZURE_EMBEDDINGS_DEPLOYMENT,
        input=text
    )
    return response.data[0].embedding


def upload_chunks():
    """Embed and upload all knowledge chunks to the Azure AI Search index."""
    from azure.search.documents import SearchClient
    from azure.core.credentials import AzureKeyCredential
    from openai import AzureOpenAI

    # Validate config
    missing = []
    if not settings.AZURE_SEARCH_ENDPOINT:  missing.append("AZURE_SEARCH_ENDPOINT")
    if not settings.AZURE_SEARCH_KEY:       missing.append("AZURE_SEARCH_KEY")
    if not settings.AZURE_FOUNDRY_ENDPOINT: missing.append("AZURE_FOUNDRY_ENDPOINT")
    if not settings.AZURE_FOUNDRY_API_KEY:  missing.append("AZURE_FOUNDRY_API_KEY")
    if missing:
        print(f"❌ Missing environment variables: {', '.join(missing)}")
        print("   Please fill these in your .env file and try again.")
        sys.exit(1)

    print(f"\n🔧 Index: {settings.AZURE_SEARCH_INDEX_NAME}")
    print(f"🔧 Embeddings model: {settings.AZURE_EMBEDDINGS_DEPLOYMENT}")
    print(f"🔧 Endpoint: {settings.AZURE_SEARCH_ENDPOINT}\n")

    # Create index
    create_index(None)

    # Azure OpenAI client
    oai = AzureOpenAI(
        azure_endpoint=settings.AZURE_FOUNDRY_ENDPOINT,
        api_key=settings.AZURE_FOUNDRY_API_KEY,
        api_version=settings.AZURE_FOUNDRY_API_VERSION
    )

    # Azure Search upload client
    search_client = SearchClient(
        endpoint=settings.AZURE_SEARCH_ENDPOINT,
        index_name=settings.AZURE_SEARCH_INDEX_NAME,
        credential=AzureKeyCredential(settings.AZURE_SEARCH_KEY)
    )

    chunks = get_all_chunks()
    docs = []
    print(f"📦 Embedding {len(chunks)} knowledge chunks...")

    for i, chunk in enumerate(chunks, 1):
        text_to_embed = f"{chunk.title}. {chunk.content}"
        vector = embed_text(oai, text_to_embed)

        docs.append({
            "id":             chunk.chunk_id,
            "category":       chunk.category,
            "title":          chunk.title,
            "content":        chunk.content,
            "content_vector": vector
        })
        print(f"  [{i:2d}/{len(chunks)}] ✅ {chunk.chunk_id} — {chunk.title}")

    # Upload in one batch
    result = search_client.upload_documents(documents=docs)
    succeeded = sum(1 for r in result if r.succeeded)
    print(f"\n🚀 Uploaded {succeeded}/{len(docs)} documents to Azure AI Search")
    print("✅ Indexing complete! RAG is now running in Azure hybrid mode.")


if __name__ == "__main__":
    upload_chunks()

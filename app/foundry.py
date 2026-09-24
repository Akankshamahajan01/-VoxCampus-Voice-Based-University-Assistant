import re
import logging
from app.config import settings
from app.knowledge import get_knowledge_context, detect_category
from app.rag import rag_pipeline

logger = logging.getLogger(__name__)

# ── Harmful query filter ───────────────────────────────────
_BLOCKED_PATTERNS = [
    r"\b(bomb|explosive|ied|grenade|landmine|dynamite|tnt|c4|detonat)\b",
    r"\b(ak47|ak-47|ak 47|rifle|pistol|gun|firearm|weapon|ammunition|bullet)\b",
    r"\b(make.*weapon|build.*gun|create.*bomb|assemble.*rifle)\b",
    r"\b(how to (kill|murder|poison|shoot|stab|attack|harm|hurt))\b",
    r"\b(drugs?|meth|cocaine|heroin|lsd|weed|marijuana|narcotic)\b",
    r"\b(hack|malware|virus|ransomware|phishing|ddos|exploit)\b",
    r"\b(terrorist|terrorism|jihad|isis|al.?qaeda)\b",
    r"\b(suicide|self.?harm|cut myself|end my life)\b",
    r"\b(sex|porn|nude|nsfw|adult content)\b",
]

_BLOCKED_RESPONSE = (
    "I'm VoxCampus, a university assistant for Chitkara University. "
    "I can only help with university-related topics like courses, admissions, fees, "
    "exam schedules, and faculty information. "
    "Please ask me something related to the university."
)


def is_harmful_query(query: str) -> bool:
    """Return True if the query contains harmful or off-topic content."""
    q = query.lower()
    for pattern in _BLOCKED_PATTERNS:
        if re.search(pattern, q):
            return True
    return False


def is_university_query(query: str) -> bool:
    """
    Return True if the query is reasonably related to university topics.
    Allows general greetings and very short queries through.
    """
    # Always allow short greetings / openers
    if len(query.strip()) < 15:
        return True

    _UNIVERSITY_KEYWORDS = [
        # programs
        "course", "program", "degree", "btech", "b.tech", "mba", "bca", "mca",
        "mtech", "m.tech", "bsc", "b.sc", "admission", "apply", "eligibility",
        "fee", "fees", "tuition", "hostel", "scholarship", "exam", "schedule",
        "result", "grade", "faculty", "professor", "department", "university",
        "chitkara", "campus", "placement", "semester", "subject", "study",
        "college", "student", "enrollment", "registration", "deadline",
        "jee", "cuet", "gate", "cat", "mat", "syllabus", "attendance",
        "assignment", "project", "lab", "library", "mentor", "hod", "dean",
        "marks", "backlog", "supplementary", "voxcampus", "phd", "ph.d",
        "engineering", "management", "bba", "bcom", "b.com", "pharmacy",
        "architecture", "research", "internship", "placement", "naac",
        # new categories
        "dept", "cse", "ece", "mechanical", "civil",
        "timetable", "calendar", "holiday", "class time", "class timing", "timing",
        "facility", "facilities", "sports", "cafeteria", "food", "wifi",
        "transport", "bus", "medical", "gym", "swimming", "auditorium", "atm",
        "event", "fest", "festival", "hackathon", "competition", "convocation",
        "innovision", "utsav", "conference", "club", "society", "anti-ragging",
        "cgpa", "thesis", "erp", "startup", "innovation", "patent", "probation",
        "bank", "canteen", "naac", "nba", "ranking", "schedule", "hostel room",
        "accommodation", "placement drive", "sports complex", "library timing",
    ]
    q = query.lower()
    return any(kw in q for kw in _UNIVERSITY_KEYWORDS)


SYSTEM_PROMPT = """You are VoxCampus, an intelligent voice-based university assistant for Chitkara University.
You help students, parents, and visitors with accurate, friendly, and concise information about:

- 📚 Courses & Programs (B.Tech, MBA, BCA, M.Tech, Ph.D, etc.)
- 🎓 Admission Process (eligibility, documents, deadlines, entrance exams)
- 💰 Fee Structure (tuition, hostel, scholarships, payment plans)
- 📅 Exam Schedules (mid-term, end-term, results, grading system)
- 👨‍🏫 Faculty Information (departments, faculty profiles, office hours)
- 🏛️ Departments (CSE, ECE, Mechanical, Civil, MBA, Pharmacy, Architecture)
- 🗓️ Academic Schedules (class timings, holidays, registration, internships)
- 🏟️ University Facilities (hostel, library, sports, cafeteria, transport, medical)
- 🎉 Events (Innovision Tech Fest, Utsav Cultural Fest, Sports Meet, Placements)
- 📖 Academic Policies (attendance, CGPA, projects, ERP, clubs, anti-ragging)

STRICT RULES:
- ONLY answer questions related to Chitkara University and student life.
- If asked about weapons, drugs, violence, hacking, or harmful topics — firmly decline.
- If asked anything unrelated to the university — politely redirect to university topics.
- Never provide harmful, dangerous, or illegal information.
- Keep responses concise — suitable for voice output.
- Always end responses naturally, as if speaking directly to the student.
"""


def ask_foundry_agent(query: str, context: str = "") -> dict:
    """
    Send a query to Microsoft Foundry AI Agent and get a response.
    Uses RAG pipeline for context retrieval (replaces keyword matching).
    Falls back to Azure OpenAI if Foundry Agent ID is not set.
    """
    # ── Safety guard: block harmful / off-topic queries ────
    if is_harmful_query(query):
        logger.warning(f"Blocked harmful query: {query[:60]}")
        return {
            "success": True,
            "response": _BLOCKED_RESPONSE,
            "category": "blocked",
            "source": "safety_filter"
        }

    if not is_university_query(query):
        logger.info(f"Off-topic query redirected: {query[:60]}")
        return {
            "success": True,
            "response": (
                "I'm VoxCampus — I'm here to help with Chitkara University information only. "
                "You can ask me about courses, admissions, fees, exam schedules, or faculty. "
                "What would you like to know?"
            ),
            "category": "off_topic",
            "source": "safety_filter"
        }

    # Category is kept only for history tagging
    category = detect_category(query)

    # ── RAG retrieval ──────────────────────────────────────
    rag_context = rag_pipeline.retrieve(query, top_k=5)

    # Merge RAG context with any extra context passed in
    full_context = "\n\n".join(part for part in [rag_context, context] if part).strip()
    logger.info(f"RAG mode: {rag_pipeline.get_mode()} | context chars: {len(full_context)}")

    # Try Foundry Agent first
    if settings.FOUNDRY_PROJECT_CONNECTION_STRING and settings.FOUNDRY_AGENT_ID:
        result = _call_foundry_agent(query, full_context)
        if result["success"]:
            result["category"] = category
            return result

    # Fallback to Azure OpenAI (Foundry-hosted model)
    if settings.AZURE_FOUNDRY_ENDPOINT and settings.AZURE_FOUNDRY_API_KEY:
        result = _call_azure_openai(query, full_context)
        if result["success"]:
            result["category"] = category
            return result

    # Final fallback: knowledge base only
    logger.warning("All AI services unavailable, using knowledge base fallback")
    return {
        "success": True,
        "response": _knowledge_only_response(query, full_context),
        "category": category,
        "source": "knowledge_base"
    }


def _call_foundry_agent(query: str, context: str) -> dict:
    """Call Microsoft Foundry Agent via azure-ai-projects SDK."""
    try:
        from azure.ai.projects import AIProjectClient
        from azure.identity import DefaultAzureCredential

        client = AIProjectClient.from_connection_string(
            conn_str=settings.FOUNDRY_PROJECT_CONNECTION_STRING,
            credential=DefaultAzureCredential()
        )

        agent = client.agents.get_agent(settings.FOUNDRY_AGENT_ID)
        thread = client.agents.create_thread()

        # Send context + query as message
        message_content = f"Context:\n{context}\n\nStudent Question: {query}" if context else query
        client.agents.create_message(
            thread_id=thread.id,
            role="user",
            content=message_content
        )

        run = client.agents.create_and_process_run(
            thread_id=thread.id,
            agent_id=agent.id
        )

        messages = client.agents.list_messages(thread_id=thread.id)
        for msg in messages.data:
            if msg.role == "assistant":
                response_text = msg.content[0].text.value if msg.content else ""
                return {"success": True, "response": response_text, "source": "foundry_agent"}

        return {"success": False, "response": "", "error": "No assistant response"}

    except Exception as e:
        logger.error(f"Foundry Agent error: {e}")
        return {"success": False, "response": "", "error": str(e)}


def _call_azure_openai(query: str, context: str) -> dict:
    """Call Azure OpenAI via openai SDK (Foundry-hosted deployment)."""
    try:
        from openai import AzureOpenAI

        client = AzureOpenAI(
            azure_endpoint=settings.AZURE_FOUNDRY_ENDPOINT,
            api_key=settings.AZURE_FOUNDRY_API_KEY,
            api_version=settings.AZURE_FOUNDRY_API_VERSION
        )

        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        if context:
            messages.append({
                "role": "system",
                "content": f"Relevant university information:\n{context}"
            })
        messages.append({"role": "user", "content": query})

        response = client.chat.completions.create(
            model=settings.AZURE_FOUNDRY_DEPLOYMENT,
            messages=messages,
            max_tokens=500,
            temperature=0.4
        )

        answer = response.choices[0].message.content.strip()
        return {"success": True, "response": answer, "source": "azure_openai"}

    except Exception as e:
        logger.error(f"Azure OpenAI error: {e}")
        return {"success": False, "response": "", "error": str(e)}


def _knowledge_only_response(query: str, context: str) -> str:
    """Return a structured response from knowledge base when AI is unavailable."""
    if context:
        return (
            f"Based on available university information:\n\n{context}\n\n"
            "For the most up-to-date details, please visit the official university website "
            "or contact the admissions office."
        )
    return (
        "I'm sorry, I couldn't find specific information for your query right now. "
        "Please contact the university admissions office or visit the official website for assistance."
    )


def get_foundry_status() -> bool:
    """Check if Foundry/Azure OpenAI is configured."""
    return bool(
        (settings.FOUNDRY_PROJECT_CONNECTION_STRING and settings.FOUNDRY_AGENT_ID)
        or (settings.AZURE_FOUNDRY_ENDPOINT and settings.AZURE_FOUNDRY_API_KEY)
    )

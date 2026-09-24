# 🎙️ VoxCampus — Voice-Based University Assistant

**AI-103 Group Project | Chitkara University | 2026**

> Ask anything about the university — just speak or type. VoxCampus answers instantly using Azure AI Speech and Microsoft Foundry.

---

## 📌 Project Information

| Field | Details |
|---|---|
| Project Name | VoxCampus |
| Project Topic | #18 — Voice-Based University Assistant |
| Course | AI-103, BE-CSE AI&ML Batch 2024 (5th Sem) |
| University | Chitkara University |
| Primary Technologies | Python, FastAPI, HTML, CSS, JavaScript |
| AI Technologies | Azure AI Speech, Microsoft Foundry, Azure OpenAI |

---

## 🚀 What is VoxCampus?

**VoxCampus** is an AI-powered, voice-first university assistant that helps students, parents, and visitors get instant answers about Chitkara University — through natural speech or typed text.

Students often waste time searching across multiple websites, offices, and notice boards to find basic information. VoxCampus solves this by providing a single, intelligent, conversational interface.

---

## 🎯 Problem Statement

Students struggle to quickly find:
- Available courses and program details
- Admission procedures and eligibility
- Fee structures and scholarship options
- Exam schedules and grading systems
- Faculty contact information

**VoxCampus** eliminates this friction with a voice-first AI assistant.

---

## 💡 Solution

A web application where students can **speak or type** their question and receive an AI-generated response — with voice output powered by Azure AI Speech.

```
Student Speaks / Types
        ↓
   Frontend (HTML/JS)
        ↓
  FastAPI Backend
        ↓
Azure AI Speech (STT)      ← converts voice to text
        ↓
Microsoft Foundry Agent    ← understands & answers
        ↓
Azure AI Speech (TTS)      ← converts answer to voice
        ↓
Student hears the answer
```

---

## ✨ Features

| Feature | Description |
|---|---|
| 🎙️ Voice Input | Hold-to-speak microphone using browser MediaRecorder API |
| 🔊 Voice Output | Azure Neural TTS reads the answer back to you |
| 💬 Text Chat | Type questions directly in the chat interface |
| 📚 Courses | B.Tech, MBA, BCA, M.Tech programs and specializations |
| 🎓 Admissions | Eligibility, documents, deadlines, entrance exams |
| 💰 Fees | Tuition, hostel, scholarships, payment plans |
| 📅 Exams | Schedules, grading, results, supplementary exams |
| 👨‍🏫 Faculty | Departments, HODs, contact, office hours |
| 🔐 Auth | JWT-based login/register with guest mode |
| 📜 History | Stores past queries (voice and text) |

---

## 🧠 RAG Architecture

VoxCampus uses a full **Retrieval-Augmented Generation (RAG)** pipeline to give the AI precise, grounded answers.

### How RAG Works in VoxCampus

```
User Query (voice or text)
        ↓
  Tokenise / Embed query
        ↓
  ┌─────────────────────────────────┐
  │   Retrieval (auto-selected)     │
  │                                 │
  │  Mode A: Azure AI Search        │
  │   BM25 keyword + vector cosine  │
  │   (when AZURE_SEARCH_* is set)  │
  │                                 │
  │  Mode B: Local TF-IDF           │
  │   In-memory cosine similarity   │
  │   (zero-config fallback)        │
  └────────────────┬────────────────┘
                   ↓
       Top-5 most relevant chunks
       (fine-grained passages, ~2-3 sentences each)
                   ↓
       Injected as [Source N] context into LLM prompt
                   ↓
       Microsoft Foundry / Azure OpenAI GPT-4o
                   ↓
       Grounded, accurate response
                   ↓
       Azure AI Speech TTS (optional)
```

### Knowledge Chunks

The university knowledge base is split into **35 fine-grained chunks** across 6 categories:

| Category | Chunks | Examples |
|---|---|---|
| courses | 6 | B.Tech programs, CSE specializations, MBA |
| admissions | 7 | Process steps, eligibility, documents, deadlines |
| fees | 7 | Tuition by program, hostel, scholarships |
| exams | 7 | Schedules, grading, supplementary rules |
| faculty | 7 | Departments, office hours, research labs |
| general | 5 | University overview, facilities, contacts |

### RAG Modes

| Mode | When active | How it works |
|---|---|---|
| **Local TF-IDF** | No Azure Search configured | TF-IDF cosine similarity, instant, no extra cost |
| **Azure AI Search** | `AZURE_SEARCH_*` in `.env` | Hybrid BM25 + vector search, most accurate |

### Setting Up Azure AI Search (Optional)

After filling `.env` with your Azure Search credentials, run:

```bash
python scripts/index_knowledge.py
```

This creates the search index, generates embeddings for all 35 chunks, and uploads them. Takes ~1 minute.

---



```
┌──────────────────────────────────────┐
│           STUDENT (Browser)          │
│   Voice Input  │  Text Input         │
└──────────────┬────────────────────────┘
               │ HTTP / FormData
               ▼
┌──────────────────────────────────────┐
│         FastAPI Backend              │
│  /api/voice/query  /api/chat/query   │
│  /api/auth/login   /api/auth/register│
└──────┬─────────────────┬─────────────┘
       │                 │
       ▼                 ▼
┌────────────┐   ┌──────────────────────┐
│ Azure AI   │   │  Microsoft Foundry   │
│  Speech    │   │    AI Agent          │
│ STT + TTS  │   │  (Azure OpenAI GPT)  │
└────────────┘   └──────────────────────┘
                          │
                          ▼
               ┌──────────────────────┐
               │  University Knowledge│
               │     Base (Python)    │
               │  Courses│Fees│Exams  │
               └──────────────────────┘
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Frontend | HTML5, CSS3 (Glassmorphism), Vanilla JavaScript |
| Backend | Python 3.11+, FastAPI |
| Voice STT | Azure Cognitive Services Speech SDK |
| Voice TTS | Azure Neural TTS (en-US-JennyNeural) |
| AI Agent | Microsoft Foundry Agent / Azure OpenAI GPT-4o |
| Auth | JWT (python-jose) + bcrypt (passlib) |
| Database | SQLite via SQLAlchemy |
| Deployment | Render / Azure App Service |

---

## 📁 Project Structure

```
VoxCampus/
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI entry point
│   ├── config.py        # Environment settings
│   ├── database.py      # SQLAlchemy models
│   ├── auth.py          # JWT authentication
│   ├── speech.py        # Azure Speech STT + TTS
│   ├── foundry.py       # Microsoft Foundry AI Agent
│   ├── knowledge.py     # University knowledge base
│   ├── models/
│   │   └── schemas.py   # Pydantic schemas
│   └── routes/
│       ├── auth.py      # /api/auth/*
│       ├── voice.py     # /api/voice/*
│       └── chat.py      # /api/chat/*
├── frontend/
│   ├── index.html       # Main UI
│   ├── auth.html        # Login / Register
│   ├── style.css        # Dark glassmorphism theme
│   └── script.js        # Voice recording + API calls
├── .env.example         # Environment variable template
├── .gitignore
├── requirements.txt
└── README.md
```

---

## ⚙️ Setup & Run

### 1. Clone the repo
```bash
git clone https://github.com/your-username/VoxCampus.git
cd VoxCampus
```

### 2. Create virtual environment
```bash
python -m venv .venv
source .venv/bin/activate        # macOS/Linux
.venv\Scripts\activate           # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment
```bash
cp .env.example .env
# Edit .env with your Azure credentials
```

### 5. Run the server
```bash
uvicorn app.main:app --reload --port 8000
```

### 6. Open in browser
```
http://localhost:8000
```

---

## 🔑 Environment Variables

| Variable | Description |
|---|---|
| `AZURE_SPEECH_KEY` | Azure AI Speech subscription key |
| `AZURE_SPEECH_REGION` | Azure region (e.g. `eastus`) |
| `FOUNDRY_PROJECT_CONNECTION_STRING` | Microsoft Foundry project connection string |
| `FOUNDRY_AGENT_ID` | Your Foundry Agent ID |
| `AZURE_FOUNDRY_ENDPOINT` | Azure OpenAI endpoint (fallback) |
| `AZURE_FOUNDRY_API_KEY` | Azure OpenAI API key (fallback) |
| `SECRET_KEY` | JWT secret key |

---

## 🧪 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/voice/query` | Upload audio → STT → AI → TTS |
| POST | `/api/chat/query` | Text query → AI response |
| GET | `/api/chat/suggestions` | Sample questions |
| GET | `/api/chat/history` | Query history |
| POST | `/api/auth/register` | Create account |
| POST | `/api/auth/login` | Login |
| GET | `/api/health` | Health check |

Interactive docs: `http://localhost:8000/api/docs`

---

## 🎓 AI-103 Concepts Applied

- **Agents** — Microsoft Foundry AI Agent handles query understanding
- **Speech** — Azure AI Speech for real-time STT and neural TTS
- **GenAI** — Azure OpenAI GPT-4o for intelligent response generation
- **RAG** — Knowledge base context injected into AI prompts
- **Responsible AI** — No credentials stored in code; .env excluded from git

---

## ⚠️ Known Limitations

- Voice recording requires HTTPS or localhost (browser security requirement)
- Faculty HOD names are placeholder — replace with real data
- Azure Speech free tier has 5 hours/month limit
- Knowledge base is static — future work: connect to live university ERP

---

## 🚀 Future Scope

- 🌐 Hindi + English bilingual voice support
- 📄 PDF/document upload for personalized Q&A
- 📊 Student query analytics dashboard  
- 🔔 Exam reminder notifications
- 📱 Progressive Web App (PWA) support
- 🔗 Live ERP integration for real-time data

---

## 👥 Team

| Name | Role |
|---|---|
| Team Member 1 | Backend + AI Integration |
| Team Member 2 | Frontend + UI/UX |
| Team Member 3 | Azure Services + Deployment |
| Team Member 4 | Knowledge Base + Testing |

---

## 📄 License

This project is submitted as part of the AI-103 course at Chitkara University. All third-party libraries and APIs are acknowledged.

- Azure AI Speech — [Microsoft Azure](https://azure.microsoft.com/en-us/services/cognitive-services/speech-services/)
- Microsoft Foundry — [Azure AI Foundry](https://ai.azure.com/)
- FastAPI — [fastapi.tiangolo.com](https://fastapi.tiangolo.com/)

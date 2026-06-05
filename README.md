# 📚 StudyFlow Hybrid – AI Agents for Primary Education

> An intelligent learning system powered by multiple AI agents (Teacher, Tracker, Parent) and a RAG knowledge base. Designed for class 1–5 students.

[![Python](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green.svg)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.35-red.svg)](https://streamlit.io/)
[![License](https://img.shields.io/badge/license-MIT-yellow.svg)](LICENSE)

---

## 🎯 Overview

**StudyFlow Hybrid** is a production‑ready AI agent platform that helps young students learn interactively. It combines:

- 👨‍🏫 **Teacher Agent** – explains topics, answers questions, guides learning
- 📊 **Tracker Agent** – monitors student progress and performance
- 👨‍👩‍👧 **Parent Agent** – generates reports and insights for parents
- 📚 **RAG Knowledge Base** – retrieves relevant content from textbooks (PDF → TXT → vector search)

All agents work together via a **Hybrid Manager** that orchestrates responses and personalizes the learning experience.

---

## 🧠 Architecture

User (Student) → Streamlit UI → FastAPI Backend
↓
Hybrid Manager
┌───────────┼───────────┐
↓ ↓ ↓
Teacher Tracker Parent
Agent Agent Agent
↓ ↓ ↓
└───────────┼───────────┘
↓
RAG Searcher
↓
Knowledge Base (TXT files)


- **Backend**: FastAPI (Python) – REST endpoints for chat, progress tracking, parent reports.
- **Agents**: Custom logic + local LLM (Ollama) for reasoning.
- **RAG**: Simple keyword‑based searcher (can be upgraded to vector search with ChromaDB).
- **Frontend**: Two Streamlit apps – one for students, one for parents.
- **Database**: SQLite (or PostgreSQL) with row‑level security concepts.

---

## 🚀 Quick Start

### 1. Clone the repository
```bash
git clone https://github.com/nh30073007/Studyflow-Hybrid.git
cd Studyflow-Hybrid

2. Setup environment

python -m venv venv
source venv/bin/activate      # Linux/Mac
# or
venv\Scripts\activate         # Windows

pip install -r requirements.txt

3. Configure environment
Copy .env.example to .env and adjust settings if needed (LLM endpoint, database URL, etc.).

4. Run the backend

cd backend
python main.py
Backend runs at http://localhost:8000

5. Run the frontend (student UI)

cd frontend
streamlit run app.py

6. Run the parent dashboard (optional)

streamlit run parent_dashboard.py

🧪 Demo & Use Cases
Agent	Input Example	Output
👨‍🏫 Teacher	"What is a noun?"	Explanation + examples from RAG
📊 Tracker	Student answers quiz	Stores progress, identifies weak topics
👪 Parent	"Show my child's report"	Generates PDF or dashboard view
📚 RAG Knowledge Base
Place your textbook .txt files inside backend/rag/knowledge_base/. The searcher performs keyword matching. For better results, upgrade to ChromaDB + sentence‑transformers (see rag/searcher.py for extensibility).

🛠️ Tech Stack
Area	Technologies
Backend	FastAPI, SQLAlchemy, Pydantic
Frontend	Streamlit
AI Agents	Local LLM (Ollama / Groq API)
RAG	Custom keyword search (upgradable)
Database	SQLite / PostgreSQL (with RLS)
Auth	JWT (planned)

🤝 Contributing
Pull requests are welcome. Please ensure your code passes basic tests:

pytest tests/


📄 License
MIT © A.H.M. Nazmul Hasan

🙏 Acknowledgements
FastAPI

Streamlit

Ollama for local LLMs

Built with ❤️ for young learners. 🚀

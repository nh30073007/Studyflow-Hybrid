# backend/main.py
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict
import uvicorn
from datetime import datetime
import os
import sys
from sqlalchemy.orm import Session

sys.path.append(os.path.dirname(os.path.abspath(__file__)))


from agents.hybrid_manager import get_hybrid_manager
from rag.searcher import search_knowledge_base
from rag.init_rag import init_rag_system, get_knowledge_base_stats
from database.db import get_db, init_db, SessionLocal
from database.models import User, ChildProgress, ChatHistory, TopicMastery, Reminder
from database.crud import (
    create_user, get_user, update_user, update_child_progress,
    get_child_progress, save_chat_history, get_chat_history,
    create_reminder, get_pending_reminders, get_child_report
)
from database.security import encrypt_data, decrypt_data, SecurityManager

# FastAPI অ্যাপ তৈরি
app = FastAPI(
    title="StudyFlow AI API",
    description="প্লে গ্রুপ লার্নিং এর জন্য হাইব্রিড এজেন্ট সিস্টেম",
    version="3.0.0"
)

# CORS মিডলওয়্যার
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ========================
# ডাটা মডেল (Pydantic)
# ========================

class QuestionRequest(BaseModel):
    user_id: str
    question: str
    topic: Optional[str] = None

class QuestionResponse(BaseModel):
    answer: str
    user_id: str
    timestamp: str
    topic: Optional[str] = None

class ReminderRequest(BaseModel):
    child_id: str
    message: str
    scheduled_time: Optional[datetime] = None
    reminder_type: Optional[str] = "study"

class EvaluateRequest(BaseModel):
    user_id: str
    question: str
    student_answer: str
    topic: Optional[str] = None

class UserCreateRequest(BaseModel):
    user_id: str
    username: str
    role: str = "child"
    age: Optional[int] = None
    grade: Optional[str] = None
    email: Optional[str] = None
    parent_phone: Optional[str] = None

# ========================
# টেম্পোরারি ডাটাবেস (ব্যাকআপ)
# ========================

user_progress: Dict[str, Dict] = {}
chat_history: List[Dict] = []

# ========================
# হাইব্রিড এজেন্ট ইনিশিয়ালাইজ
# ========================

hybrid_manager = get_hybrid_manager()
init_rag_system()
init_db()

# ========================
# হেল্পার ফাংশন
# ========================

def get_or_create_user(db: Session, user_id: str, username: str = None) -> User:
    user = get_user(db, user_id)
    if not user:
        user = create_user(
            db=db,
            user_id=user_id,
            username=username or user_id,
            role="child"
        )
    return user

def detect_topic(question: str) -> str:
    question_lower = question.lower()
    
    # বাংলা অক্ষর ডিটেক্ট
    bangla_letters = ['অ', 'আ', 'ই', 'ঈ', 'উ', 'ঊ', 'ঋ', 'এ', 'ঐ', 'ও', 'ঔ',
                      'ক', 'খ', 'গ', 'ঘ', 'ঙ', 'চ', 'ছ', 'জ', 'ঝ', 'ঞ',
                      'ট', 'ঠ', 'ড', 'ঢ', 'ণ', 'ত', 'থ', 'দ', 'ধ', 'ন',
                      'প', 'ফ', 'ব', 'ভ', 'ম', 'য', 'র', 'ল', 'শ', 'ষ', 'স', 'হ']
    
    for letter in bangla_letters:
        if letter in question:
            return f"বাংলা অক্ষর - {letter}"
    
    topics = {
        "গণিত": ["গণনা", "সংখ্যা", "১", "২", "৩", "যোগ", "বিয়োগ"],
        "রং চেনানো": ["রং", "লাল", "নীল", "সবুজ", "হলুদ"],
        "প্রাণী চেনানো": ["গরু", "কুকুর", "বিড়াল", "হাতি"],
        "জাতীয় সঙ্গীত": ["গান", "সঙ্গীত", "জাতীয়", "আমার সোনার বাংলা"],
    }
    
    for topic, keywords in topics.items():
        for keyword in keywords:
            if keyword in question_lower:
                return topic
    
    return "অন্যান্য"

# ========================
# ফিক্সড: সিম্পল get_agent_response ফাংশন
# ========================

def get_agent_response(user_id: str, question: str, db: Session = None) -> str:
    
    try:
       
        book_answer = search_knowledge_base(question)
        
        if book_answer:
            return f"🧸 টিচার এজেন্ট: {book_answer}\n\n❓ আরও কিছু জানতে চাও? 🤗"
        
        
        return f"""🤔 আমি '{question}' সম্পর্কে এখনো শিখিনি।

📖 **আমি যা জানি:**
   • অ, আ, ক, খ - বাংলা অক্ষর
   • ১-১০ পর্যন্ত গণনা
   • গরু, কুকুর - প্রাণী
   • লাল, নীল, সবুজ - রং

💡 **তুমি এভাবে প্রশ্ন করতে পারো:**
   • "অ অক্ষরটা শেখাও"
   • "গণনা করো"
   • "গরু সম্পর্কে জানাও"

🎯 চেষ্টা করো! আমি সাহায্য করতে প্রস্তুত!"""
        
    except Exception as e:
        return f"⚠️ টেকনিক্যাল সমস্যা: {str(e)}। দয়া করে কিছুক্ষণ পর চেষ্টা করো。"

# ========================
# API এন্ডপয়েন্টস
# ========================

@app.get("/")
async def root():
    kb_stats = get_knowledge_base_stats()
    
    return {
        "message": "StudyFlow AI API চালু আছে! 🚀",
        "status": "active",
        "version": "3.0.0",
        "agents": {
            "teacher": "active",
            "tracker": "active",
            "parent": "active"
        },
        "knowledge_base": {
            "total_files": kb_stats.get("total_files", 0),
            "initialized": kb_stats.get("initialized", False)
        }
    }

@app.post("/user/create")
async def create_new_user(request: UserCreateRequest, db: Session = Depends(get_db)):
    existing_user = get_user(db, request.user_id)
    if existing_user:
        return {
            "status": "exists",
            "user": existing_user.to_dict(),
            "message": "ইউজার আগেই আছে"
        }
    
    user = create_user(
        db=db,
        user_id=request.user_id,
        username=request.username,
        role=request.role,
        age=request.age,
        grade=request.grade,
        email=request.email,
        parent_phone=request.parent_phone
    )
    
    return {
        "status": "created",
        "user": user.to_dict(),
        "message": "ইউজার সফলভাবে তৈরি হয়েছে!"
    }

@app.get("/user/{user_id}")
async def get_user_info(user_id: str, db: Session = Depends(get_db)):
    user = get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="ইউজার খুঁজে পাওয়া যায়নি")
    return user.to_dict()



@app.post("/ask", response_model=QuestionResponse)
async def ask_question(request: QuestionRequest, db: Session = Depends(get_db)):
   
    if not request.user_id or not request.question:
        raise HTTPException(status_code=400, detail="user_id এবং question প্রয়োজন")
    
    user = get_or_create_user(db, request.user_id, request.user_id)
    
    
    topic = request.topic or detect_topic(request.question)
    
    answer = get_agent_response(request.user_id, request.question, db)
    
    update_child_progress(
        db=db,
        user_id=request.user_id,
        question_correct=None,
        topic=topic
    )
    
    save_chat_history(
        db=db,
        user_id=request.user_id,
        question=request.question,
        answer=answer,
        topic=topic
    )
    
    return QuestionResponse(
        answer=answer,
        user_id=request.user_id,
        timestamp=datetime.now().isoformat(),
        topic=topic
    )


@app.get("/progress/{user_id}")
async def get_progress(user_id: str, db: Session = Depends(get_db)):
    """ইউজারের প্রোগ্রেস ডাটা রিটার্ন করে"""
    db_progress = get_child_progress(db, user_id)
    
    if db_progress and db_progress.get("total_questions", 0) > 0:
        return {
            "user_id": user_id,
            "total_questions": db_progress.get("total_questions", 0),
            "correct_answers": db_progress.get("correct_answers", 0),
            "accuracy": db_progress.get("accuracy", 0),
            "current_streak": db_progress.get("current_streak", 0),
            "longest_streak": db_progress.get("longest_streak", 0),
            "last_active": db_progress.get("last_active")
        }
    
    return {
        "user_id": user_id,
        "total_questions": 0,
        "correct_answers": 0,
        "accuracy": 0,
        "message": "এখনো কোনো প্রশ্ন করা হয়নি। প্রথম প্রশ্ন করে দেখো! 🎉"
    }

@app.get("/parent/report/{user_id}")
async def get_parent_report(user_id: str, days: int = 7, db: Session = Depends(get_db)):
    db_report = get_child_report(db, user_id, days)
    return {
        "user_id": user_id,
        "period_days": days,
        "report": db_report,
        "generated_at": datetime.now().isoformat()
    }

@app.get("/recommendation/{user_id}")
async def get_recommendation(user_id: str, db: Session = Depends(get_db)):
    db_report = get_child_report(db, user_id, 7)
    weak_topics = db_report.get("weak_topics", [])
    
    if weak_topics:
        return {
            "user_id": user_id,
            "recommendation": f"🎯 দুর্বল বিষয়: {', '.join(weak_topics)} - এগুলোতে বেশি মনোযোগ দিন",
            "timestamp": datetime.now().isoformat()
        }
    
    return {
        "user_id": user_id,
        "recommendation": "📚 তুমি非常好 করছো! নতুন বিষয় শেখা শুরু করতে পারো! 🌟",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/parent/all_children")
async def get_all_children(db: Session = Depends(get_db)):
    from database.crud import get_all_children as get_all_child_users
    
    children = []
    db_children = get_all_child_users(db)
    
    for child in db_children:
        progress = get_child_progress(db, child.user_id)
        children.append({
            "user_id": child.user_id,
            "username": child.username,
            "total_questions": progress.get("total_questions", 0),
            "accuracy": progress.get("accuracy", 0),
            "last_active": progress.get("last_active")
        })
    
    if not children:
        children = [
            {"user_id": "আরিয়ান", "username": "আরিয়ান", "total_questions": 0, "accuracy": 0, "last_active": None},
        ]
    
    return {
        "children": children,
        "total_children": len(children),
        "timestamp": datetime.now().isoformat()
    }

@app.post("/parent/remind")
async def send_reminder(request: ReminderRequest, db: Session = Depends(get_db)):
    scheduled_time = request.scheduled_time or datetime.now()
    reminder_message = request.message or "📚 পড়ার সময় হয়েছে! StudyFlow AI খুলে একটু অনুশীলন করো 🧸"
    
    reminder = create_reminder(
        db=db,
        user_id=request.child_id,
        message=reminder_message,
        scheduled_time=scheduled_time,
        reminder_type=request.reminder_type
    )
    
    return {
        "status": "success",
        "message": f"রিমাইন্ডার পাঠানো হয়েছে {request.child_id} কে",
        "reminder_id": reminder.id,
        "timestamp": datetime.now().isoformat()
    }

@app.post("/evaluate")
async def evaluate_answer(request: EvaluateRequest, db: Session = Depends(get_db)):
    topic = request.topic or detect_topic(request.question)
    
    update_child_progress(
        db=db,
        user_id=request.user_id,
        question_correct=False,
        topic=topic
    )
    
    return {
        "user_id": request.user_id,
        "is_correct": False,
        "feedback": "চেষ্টা চালিয়ে যাও! তুমি পারবে! 💪",
        "score": 0,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/chat/history/{user_id}")
async def get_chat_history_endpoint(user_id: str, limit: int = 20, db: Session = Depends(get_db)):
    db_history = get_chat_history(db, user_id, limit)
    return {
        "user_id": user_id,
        "history": [h.to_dict() for h in db_history],
        "total": len(db_history),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/kb/stats")
async def knowledge_base_stats():
    stats = get_knowledge_base_stats()
    return {
        "knowledge_base": stats,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/agents/status")
async def agents_status():
    return hybrid_manager.get_system_status()

@app.get("/db/stats")
async def database_stats(db: Session = Depends(get_db)):
    return {
        "database_type": "SQLite",
        "users": db.query(User).count(),
        "progress_records": db.query(ChildProgress).count(),
        "chat_history": db.query(ChatHistory).count(),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    kb_stats = get_knowledge_base_stats()
    
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "components": {
            "api": "running",
            "database": "healthy",
            "rag_system": "running" if kb_stats.get("initialized") else "warning"
        }
    }

# ========================
# স্টার্টআপ ইভেন্ট
# ========================

@app.on_event("startup")
async def startup_event():
    print("\n" + "="*70)
    print("🚀 StudyFlow AI API স্টার্ট হচ্ছে...")
    print("="*70)
    print(f"📚 RAG সিস্টেম: {'✅' if get_knowledge_base_stats().get('initialized') else '⚠️'}")
    print(f"🗄️ ডাটাবেস: ✅ SQLite")
    print(f"🤖 হাইব্রিড এজেন্ট: ✅")
    print("="*70)
    print("✅ API রেডি! http://localhost:8000")
    print("📖 API ডক্স: http://localhost:8000/docs")
    print("="*70 + "\n")

@app.on_event("shutdown")
async def shutdown_event():
    print("\n" + "="*50)
    print("🛑 StudyFlow AI API বন্ধ হচ্ছে...")
    print("="*50)
    print("👋 বিদায়!")
    print("="*50 + "\n")

# ========================
# লোকাল রান
# ========================

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )

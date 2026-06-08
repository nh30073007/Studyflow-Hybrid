# backend/database/crud.py
from sqlalchemy.orm import Session
from sqlalchemy import desc, func, and_, or_
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import json
import logging

from .models import User, ChildProgress, ChatHistory, TopicMastery, Reminder
from .security import encrypt_data, decrypt_data, set_current_user

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_user(
    db: Session,
    user_id: str,
    username: str,
    role: str = "child",
    age: Optional[int] = None,
    grade: Optional[str] = None,
    email: Optional[str] = None,
    parent_phone: Optional[str] = None,
    parent_email: Optional[str] = None
) -> User:
    
    try:
        
        encrypted_phone = encrypt_data(parent_phone) if parent_phone else None
        encrypted_email = encrypt_data(email) if email else None
        encrypted_parent_email = encrypt_data(parent_email) if parent_email else None
        
        user = User(
            user_id=user_id,
            username=username,
            role=role,
            age=age,
            grade=grade,
            email=encrypted_email,
            parent_phone=encrypted_phone,
            parent_email=encrypted_parent_email,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            is_active=True
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        logger.info(f"✅ ইউজার তৈরি হয়েছে: {user_id} ({role})")
        
        if role == "child":
            progress = ChildProgress(
                user_id=user_id,
                total_questions=0,
                correct_answers=0,
                accuracy=0.0,
                current_streak=0,
                longest_streak=0,
                topic_mastery={},
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.add(progress)
            db.commit()
            logger.info(f"✅ চাইল্ড প্রোগ্রেস তৈরি হয়েছে: {user_id}")
        
        return user
        
    except Exception as e:
        db.rollback()
        logger.error(f"❌ ইউজার তৈরি ব্যর্থ: {e}")
        raise e

def get_user(db: Session, user_id: str) -> Optional[User]:
    try:
        return db.query(User).filter(User.user_id == user_id).first()
    except Exception as e:
        logger.error(f"❌ ইউজার খুঁজতে ব্যর্থ: {e}")
        return None

def get_user_by_id(db: Session, id: int) -> Optional[User]:

    try:
        return db.query(User).filter(User.id == id).first()
    except Exception as e:
        logger.error(f"❌ ইউজার খুঁজতে ব্যর্থ: {e}")
        return None

def get_all_users(db: Session, role: Optional[str] = None, limit: int = 100, offset: int = 0) -> List[User]:

    try:
        query = db.query(User)
        if role:
            query = query.filter(User.role == role)
        return query.offset(offset).limit(limit).all()
    except Exception as e:
        logger.error(f"❌ ইউজার খুঁজতে ব্যর্থ: {e}")
        return []

def get_all_children(db: Session, limit: int = 100, offset: int = 0) -> List[User]:

    return get_all_users(db, role="child", limit=limit, offset=offset)

def get_all_parents(db: Session) -> List[User]:
   
    return get_all_users(db, role="parent")

def update_user(db: Session, user_id: str, **kwargs) -> Optional[User]:
    
    try:
        user = get_user(db, user_id)
        if not user:
            logger.warning(f"⚠️ ইউজার পাওয়া যায়নি: {user_id}")
            return None
        
        sensitive_fields = ["parent_phone", "parent_email", "email"]
        for key, value in kwargs.items():
            if key in sensitive_fields and value:
                value = encrypt_data(str(value))
            if hasattr(user, key):
                setattr(user, key, value)
        
        user.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(user)
        
        logger.info(f"✅ ইউজার আপডেট হয়েছে: {user_id}")
        return user
        
    except Exception as e:
        db.rollback()
        logger.error(f"❌ ইউজার আপডেট ব্যর্থ: {e}")
        return None

def delete_user(db: Session, user_id: str) -> bool:
    try:
        user = get_user(db, user_id)
        if not user:
            return False
        
        user.is_active = False
        user.updated_at = datetime.utcnow()
        db.commit()
        
        logger.info(f"✅ ইউজার ডিলিট হয়েছে: {user_id}")
        return True
        
    except Exception as e:
        db.rollback()
        logger.error(f"❌ ইউজার ডিলিট ব্যর্থ: {e}")
        return False

def get_user_stats(db: Session) -> Dict:
    try:
        total_users = db.query(User).count()
        active_users = db.query(User).filter(User.is_active == True).count()
        children_count = db.query(User).filter(User.role == "child").count()
        parents_count = db.query(User).filter(User.role == "parent").count()
        
        return {
            "total_users": total_users,
            "active_users": active_users,
            "children_count": children_count,
            "parents_count": parents_count,
            "inactive_users": total_users - active_users
        }
    except Exception as e:
        logger.error(f"❌ ইউজার স্ট্যাটাস ব্যর্থ: {e}")
        return {}

# ========================
# প্রোগ্রেস CRUD
# ========================

def get_child_progress_obj(db: Session, user_id: str) -> Optional[ChildProgress]:

    try:
        return db.query(ChildProgress).filter(ChildProgress.user_id == user_id).first()
    except Exception as e:
        logger.error(f"❌ প্রোগ্রেস খুঁজতে ব্যর্থ: {e}")
        return None

def update_child_progress(
    db: Session,
    user_id: str,
    question_correct: Optional[bool] = None,
    topic: Optional[str] = None,
    study_time_minutes: int = 0
) -> Optional[ChildProgress]:
   
    
    try:
        progress = get_child_progress_obj(db, user_id)
        
        if not progress:
            progress = ChildProgress(
                user_id=user_id,
                total_questions=0,
                correct_answers=0,
                accuracy=0.0,
                current_streak=0,
                longest_streak=0,
                topic_mastery={},
                total_study_time=0,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.add(progress)
        
      
        if question_correct is not None:
            progress.total_questions += 1
            if question_correct:
                progress.correct_answers += 1
            
            progress.accuracy = (progress.correct_answers / progress.total_questions) * 100 if progress.total_questions > 0 else 0
        
        today = datetime.utcnow().date()
        if progress.last_active_date:
            last_date = progress.last_active_date.date()
            if last_date == today - timedelta(days=1):
                progress.current_streak += 1
            elif last_date != today:
                progress.current_streak = 1
        else:
            progress.current_streak = 1
        
        progress.longest_streak = max(progress.longest_streak, progress.current_streak)
        progress.last_active_date = datetime.utcnow()
        
       
        if study_time_minutes > 0:
            progress.total_study_time += study_time_minutes
        
        progress.updated_at = datetime.utcnow()
        
        if topic and question_correct is not None:
            update_topic_mastery(db, user_id, topic, question_correct)
        
        db.commit()
        db.refresh(progress)
        
        logger.info(f"✅ প্রোগ্রেস আপডেট হয়েছে: {user_id} (সঠিক: {question_correct})")
        return progress
        
    except Exception as e:
        db.rollback()
        logger.error(f"❌ প্রোগ্রেস আপডেট ব্যর্থ: {e}")
        return None

def get_child_progress(db: Session, user_id: str) -> Dict:
    
    try:
        progress = get_child_progress_obj(db, user_id)
        if not progress:
            return {
                "user_id": user_id,
                "total_questions": 0,
                "correct_answers": 0,
                "accuracy": 0,
                "current_streak": 0,
                "longest_streak": 0,
                "total_study_time": 0,
                "last_active": None,
                "topic_mastery": []
            }
        
    
        topics = db.query(TopicMastery).filter(TopicMastery.user_id == user_id).all()
        
        weak_topics = [t.topic_name for t in topics if t.mastery_score < 50]
        strong_topics = [t.topic_name for t in topics if t.mastery_score >= 80]
        
        return {
            "user_id": user_id,
            "total_questions": progress.total_questions,
            "correct_answers": progress.correct_answers,
            "accuracy": round(progress.accuracy, 1),
            "current_streak": progress.current_streak,
            "longest_streak": progress.longest_streak,
            "total_study_time": progress.total_study_time,
            "last_active": progress.last_active_date.isoformat() if progress.last_active_date else None,
            "topic_mastery": [t.to_dict() for t in topics],
            "weak_topics": weak_topics,
            "strong_topics": strong_topics
        }
        
    except Exception as e:
        logger.error(f"❌ প্রোগ্রেস রিপোর্ট ব্যর্থ: {e}")
        return {}

def get_all_progress(db: Session, limit: int = 100) -> List[Dict]:
    try:
        progresses = db.query(ChildProgress).limit(limit).all()
        return [p.to_dict() for p in progresses]
    except Exception as e:
        logger.error(f"❌ সব প্রোগ্রেস খুঁজতে ব্যর্থ: {e}")
        return []

def get_top_performers(db: Session, limit: int = 10) -> List[Dict]:

    try:
        progresses = db.query(ChildProgress).filter(
            ChildProgress.total_questions > 10
        ).order_by(
            ChildProgress.accuracy.desc(),
            ChildProgress.total_questions.desc()
        ).limit(limit).all()
        
        result = []
        for p in progresses:
            user = get_user(db, p.user_id)
            result.append({
                "user_id": p.user_id,
                "username": user.username if user else p.user_id,
                "total_questions": p.total_questions,
                "accuracy": round(p.accuracy, 1),
                "current_streak": p.current_streak
            })
        return result
    except Exception as e:
        logger.error(f"❌ সেরা শিক্ষার্থী খুঁজতে ব্যর্থ: {e}")
        return []



def get_topic_mastery(db: Session, user_id: str, topic_name: str) -> Optional[TopicMastery]:
    
    try:
        return db.query(TopicMastery).filter(
            TopicMastery.user_id == user_id,
            TopicMastery.topic_name == topic_name
        ).first()
    except Exception as e:
        logger.error(f"❌ টপিক মাস্টারি খুঁজতে ব্যর্থ: {e}")
        return None

def update_topic_mastery(
    db: Session,
    user_id: str,
    topic_name: str,
    is_correct: bool
) -> Optional[TopicMastery]:
    
    
    try:
        mastery = get_topic_mastery(db, user_id, topic_name)
        
        if not mastery:
            mastery = TopicMastery(
                user_id=user_id,
                topic_name=topic_name,
                questions_attempted=0,
                questions_correct=0,
                mastery_score=0.0,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.add(mastery)
        
        mastery.questions_attempted += 1
        if is_correct:
            mastery.questions_correct += 1
        
       
        mastery.mastery_score = (mastery.questions_correct / mastery.questions_attempted) * 100
        mastery.last_practiced = datetime.utcnow()
        mastery.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(mastery)
        
        logger.info(f"✅ টপিক মাস্টারি আপডেট: {user_id} - {topic_name} ({mastery.mastery_score:.1f}%)")
        return mastery
        
    except Exception as e:
        db.rollback()
        logger.error(f"❌ টপিক মাস্টারি আপডেট ব্যর্থ: {e}")
        return None

def get_all_topics_mastery(db: Session, user_id: str) -> List[Dict]:
    try:
        topics = db.query(TopicMastery).filter(TopicMastery.user_id == user_id).all()
        return [t.to_dict() for t in topics]
    except Exception as e:
        logger.error(f"❌ টপিক মাস্টারি খুঁজতে ব্যর্থ: {e}")
        return []

def get_topic_recommendations(db: Session, user_id: str, limit: int = 3) -> List[str]:

    try:
        topics = get_all_topics_mastery(db, user_id)
        
        weak_topics = [t for t in topics if t.get("mastery_score", 0) < 50]
        
        if weak_topics:
            return [t.get("topic_name") for t in weak_topics[:limit]]
        
       
        all_topics = ["বাংলা অক্ষর", "ইংরেজি অক্ষর", "গণিত", "রং চেনানো", "প্রাণী চেনানো", "জাতীয় সঙ্গীত"]
        learned_topics = [t.get("topic_name") for t in topics]
        new_topics = [t for t in all_topics if t not in learned_topics]
        
        return new_topics[:limit] if new_topics else ["রিভিশন - সব টপিক অনুশীলন করুন"]
        
    except Exception as e:
        logger.error(f"❌ টপিক সুপারিশ ব্যর্থ: {e}")
        return ["বাংলা অক্ষর", "গণিত"]

def save_chat_history(
    db: Session,
    user_id: str,
    question: str,
    answer: str,
    topic: Optional[str] = None,
    is_correct: Optional[bool] = None,
    response_time: float = 0.0
) -> Optional[ChatHistory]:
    
    
    try:
        chat = ChatHistory(
            user_id=user_id,
            question=question[:500],  
            answer=answer[:1000],     
            topic=topic,
            is_correct=is_correct,
            response_time=response_time,
            timestamp=datetime.utcnow()
        )
        
        db.add(chat)
        db.commit()
        db.refresh(chat)
        
        logger.info(f"✅ চ্যাট সেভ হয়েছে: {user_id} - {topic}")
        return chat
        
    except Exception as e:
        db.rollback()
        logger.error(f"❌ চ্যাট সেভ ব্যর্থ: {e}")
        return None

def get_chat_history(
    db: Session,
    user_id: str,
    limit: int = 20,
    offset: int = 0,
    topic: Optional[str] = None
) -> List[ChatHistory]:
   
    
    try:
        query = db.query(ChatHistory).filter(ChatHistory.user_id == user_id)
        
        if topic:
            query = query.filter(ChatHistory.topic == topic)
        
        return query.order_by(desc(ChatHistory.timestamp)).offset(offset).limit(limit).all()
        
    except Exception as e:
        logger.error(f"❌ চ্যাট হিস্টোরি খুঁজতে ব্যর্থ: {e}")
        return []

def get_chat_by_topic(
    db: Session,
    user_id: str,
    topic: str,
    limit: int = 10
) -> List[ChatHistory]:
   
    return get_chat_history(db, user_id, limit=limit, topic=topic)

def get_recent_chats(db: Session, user_id: str, hours: int = 24) -> List[ChatHistory]:
   
    try:
        since_time = datetime.utcnow() - timedelta(hours=hours)
        return db.query(ChatHistory).filter(
            ChatHistory.user_id == user_id,
            ChatHistory.timestamp >= since_time
        ).order_by(desc(ChatHistory.timestamp)).all()
    except Exception as e:
        logger.error(f"❌ রিসেন্ট চ্যাট খুঁজতে ব্যর্থ: {e}")
        return []

def get_chat_stats(db: Session, user_id: str) -> Dict:
  
    try:
        total_chats = db.query(ChatHistory).filter(ChatHistory.user_id == user_id).count()
        correct_chats = db.query(ChatHistory).filter(
            ChatHistory.user_id == user_id,
            ChatHistory.is_correct == True
        ).count()
        
      
        topic_counts = db.query(
            ChatHistory.topic,
            func.count(ChatHistory.id).label('count')
        ).filter(ChatHistory.user_id == user_id).group_by(ChatHistory.topic).all()
        
        return {
            "total_chats": total_chats,
            "correct_answers": correct_chats,
            "accuracy": (correct_chats / total_chats * 100) if total_chats > 0 else 0,
            "topics": [{"topic": t[0], "count": t[1]} for t in topic_counts if t[0]]
        }
    except Exception as e:
        logger.error(f"❌ চ্যাট স্ট্যাটাস ব্যর্থ: {e}")
        return {}



def create_reminder(
    db: Session,
    user_id: str,
    message: str,
    scheduled_time: datetime,
    reminder_type: str = "study",
    parent_id: Optional[str] = None,
    is_recurring: bool = False,
    recurring_pattern: Optional[str] = None
) -> Optional[Reminder]:
   
    
    try:
        reminder = Reminder(
            user_id=user_id,
            parent_id=parent_id,
            reminder_type=reminder_type,
            message=message,
            scheduled_time=scheduled_time,
            is_recurring=is_recurring,
            recurring_pattern=recurring_pattern,
            is_sent=False,
            created_at=datetime.utcnow()
        )
        
        db.add(reminder)
        db.commit()
        db.refresh(reminder)
        
        logger.info(f"✅ রিমাইন্ডার তৈরি হয়েছে: {user_id} - {scheduled_time}")
        return reminder
        
    except Exception as e:
        db.rollback()
        logger.error(f"❌ রিমাইন্ডার তৈরি ব্যর্থ: {e}")
        return None

def get_reminders(db: Session, user_id: str, is_sent: Optional[bool] = None) -> List[Reminder]:
   
    try:
        query = db.query(Reminder).filter(Reminder.user_id == user_id)
        if is_sent is not None:
            query = query.filter(Reminder.is_sent == is_sent)
        return query.order_by(Reminder.scheduled_time).all()
    except Exception as e:
        logger.error(f"❌ রিমাইন্ডার খুঁজতে ব্যর্থ: {e}")
        return []

def get_pending_reminders(db: Session) -> List[Reminder]:
  
    try:
        now = datetime.utcnow()
        return db.query(Reminder).filter(
            Reminder.scheduled_time <= now,
            Reminder.is_sent == False
        ).all()
    except Exception as e:
        logger.error(f"❌ পেন্ডিং রিমাইন্ডার খুঁজতে ব্যর্থ: {e}")
        return []

def mark_reminder_sent(db: Session, reminder_id: int) -> bool:
   
    try:
        reminder = db.query(Reminder).filter(Reminder.id == reminder_id).first()
        if reminder:
            reminder.is_sent = True
            reminder.sent_at = datetime.utcnow()
            db.commit()
            logger.info(f"✅ রিমাইন্ডার সেন্ট মার্ক করা হয়েছে: {reminder_id}")
            return True
        return False
    except Exception as e:
        db.rollback()
        logger.error(f"❌ রিমাইন্ডার আপডেট ব্যর্থ: {e}")
        return False

def delete_reminder(db: Session, reminder_id: int) -> bool:
  
    try:
        reminder = db.query(Reminder).filter(Reminder.id == reminder_id).first()
        if reminder:
            db.delete(reminder)
            db.commit()
            logger.info(f"✅ রিমাইন্ডার ডিলিট হয়েছে: {reminder_id}")
            return True
        return False
    except Exception as e:
        db.rollback()
        logger.error(f"❌ রিমাইন্ডার ডিলিট ব্যর্থ: {e}")
        return False



def get_child_report(db: Session, user_id: str, days: int = 7) -> Dict:
    
    try:
        
        progress = get_child_progress(db, user_id)
        
        since_date = datetime.utcnow() - timedelta(days=days)
        recent_chats = db.query(ChatHistory).filter(
            ChatHistory.user_id == user_id,
            ChatHistory.timestamp >= since_date
        ).order_by(desc(ChatHistory.timestamp)).all()
        
        topics = db.query(TopicMastery).filter(TopicMastery.user_id == user_id).all()
        
        daily_activity = {}
        for chat in recent_chats:
            day = chat.timestamp.date().isoformat()
            daily_activity[day] = daily_activity.get(day, 0) + 1
        
       
        weak_topics = [t.topic_name for t in topics if t.mastery_score < 50]
        strong_topics = [t.topic_name for t in topics if t.mastery_score >= 80]
        
        topics_detail = []
        for t in topics:
            topics_detail.append({
                "topic_name": t.topic_name,
                "mastery_score": round(t.mastery_score, 1),
                "questions_attempted": t.questions_attempted,
                "questions_correct": t.questions_correct,
                "accuracy": (t.questions_correct / t.questions_attempted * 100) if t.questions_attempted > 0 else 0,
                "last_practiced": t.last_practiced.isoformat() if t.last_practiced else None
            })
        
        return {
            "user_id": user_id,
            "period_days": days,
            "report_date": datetime.utcnow().isoformat(),
            "summary": progress,
            "daily_activity": daily_activity,
            "total_chats_recent": len(recent_chats),
            "weak_topics": weak_topics,
            "strong_topics": strong_topics,
            "topics_detail": topics_detail,
            "recommendations": generate_recommendations(weak_topics, progress)
        }
        
    except Exception as e:
        logger.error(f"❌ রিপোর্ট জেনারেশন ব্যর্থ: {e}")
        return {"error": str(e), "user_id": user_id}

def generate_recommendations(weak_topics: List[str], progress: Dict) -> List[str]:
    
    
    recommendations = []
    
    if weak_topics:
        recommendations.append(f"🎯 দুর্বল বিষয়গুলোতে মনোযোগ দিন: {', '.join(weak_topics)}")
        recommendations.append(f"📚 {weak_topics[0]} বিষয়ে প্রতিদিন ৫টি করে প্রশ্নের অনুশীলন করুন")
    
    total_q = progress.get("total_questions", 0)
    if total_q < 20:
        recommendations.append("📚 প্রতিদিন কমপক্ষে ১০-১৫টি প্রশ্নের অনুশীলন করুন")
    elif total_q < 50:
        recommendations.append("🌟 আপনি ভালো করছেন! প্রতিদিন ২০টি প্রশ্ন করার লক্ষ্য রাখুন")
    
    accuracy = progress.get("accuracy", 0)
    if accuracy < 50:
        recommendations.append("📖 মৌলিক বিষয়গুলো (অক্ষর, সংখ্যা) আবার রিভিশন করুন")
    elif accuracy < 70:
        recommendations.append("💪 আরও অনুশীলন প্রয়োজন! দুর্বল বিষয়গুলোতে ফোকাস করুন")
    
    streak = progress.get("current_streak", 0)
    if streak >= 7:
        recommendations.append(f"🎉 অসাধারণ! আপনি {streak} দিন ধরে consistent! পুরস্কারের যোগ্য!")
    elif streak >= 3:
        recommendations.append(f"👍 ভালো যাচ্ছে! {streak} দিনের streak ধরে রাখুন!")
    
    if not recommendations:
        recommendations.append("🌟 আপনার সন্তান非常好 করছে! নতুন চ্যালেঞ্জ দিন")
        recommendations.append("🎨 ছবি আঁকা এবং রং করার মাধ্যমে শেখাকে মজাদার করুন")
        recommendations.append("📖 পরবর্তী লেভেলের বিষয় শেখা শুরু করতে পারেন")
    
    return recommendations[:5] 


def get_dashboard_stats(db: Session) -> Dict:

    try:
        
        user_stats = get_user_stats(db)
        
        total_chats = db.query(ChatHistory).count()
        today_chats = db.query(ChatHistory).filter(
            ChatHistory.timestamp >= datetime.utcnow().replace(hour=0, minute=0, second=0)
        ).count()
        
        topics = db.query(TopicMastery.topic_name, func.avg(TopicMastery.mastery_score)).group_by(TopicMastery.topic_name).all()
        
        recent_activities = db.query(ChatHistory).order_by(desc(ChatHistory.timestamp)).limit(10).all()
        
        return {
            "users": user_stats,
            "chats": {
                "total": total_chats,
                "today": today_chats
            },
            "topics": [{"name": t[0], "avg_mastery": round(t[1], 1)} for t in topics if t[0]],
            "recent_activities": [
                {
                    "user_id": a.user_id,
                    "question": a.question[:50],
                    "timestamp": a.timestamp.isoformat()
                } for a in recent_activities
            ],
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ ড্যাশবোর্ড স্ট্যাটাস ব্যর্থ: {e}")
        return {}

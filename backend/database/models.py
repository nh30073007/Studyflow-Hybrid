# backend/database/models.py
"""
SQLAlchemy ডাটাবেস মডেল
ইউজার, প্রোগ্রেস, চ্যাট হিস্টোরি ইত্যাদি
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, Float, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime

Base = declarative_base()

class User(Base):
    """ইউজার মডেল - শিশু বা প্যারেন্ট"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(100), unique=True, index=True, nullable=False)  # Firebase UID or custom
    username = Column(String(100), nullable=False)
    email = Column(String(200), unique=True, nullable=True)
    role = Column(String(50), default="child")  # child, parent, admin
    age = Column(Integer, nullable=True)
    grade = Column(String(50), nullable=True)  # play_group, nursery, kg
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # এনক্রিপ্টেড ফিল্ড
    parent_phone = Column(String(50), nullable=True)  # এনক্রিপ্ট হবে
    parent_email = Column(String(200), nullable=True)  # এনক্রিপ্ট হবে
    
    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "username": self.username,
            "role": self.role,
            "age": self.age,
            "grade": self.grade,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "is_active": self.is_active
        }

class ChildProgress(Base):
    """শিশুর প্রোগ্রেস ট্র্যাক করার মডেল"""
    __tablename__ = "child_progress"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(100), ForeignKey("users.user_id"), index=True, nullable=False)
    
    # প্রোগ্রেস ডাটা
    total_questions = Column(Integer, default=0)
    correct_answers = Column(Integer, default=0)
    accuracy = Column(Float, default=0.0)
    
    # টপিক ভিত্তিক প্রোগ্রেস (JSON)
    topic_mastery = Column(JSON, default=dict)  # {"bangla_letters": 0.8, "math": 0.6}
    
    # স্ট্রিক তথ্য
    current_streak = Column(Integer, default=0)
    longest_streak = Column(Integer, default=0)
    last_active_date = Column(DateTime, default=datetime.utcnow)
    
    # সময়সীমা
    total_study_time = Column(Integer, default=0)  # মিনিটে
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            "user_id": self.user_id,
            "total_questions": self.total_questions,
            "correct_answers": self.correct_answers,
            "accuracy": self.accuracy,
            "topic_mastery": self.topic_mastery,
            "current_streak": self.current_streak,
            "longest_streak": self.longest_streak,
            "last_active_date": self.last_active_date.isoformat() if self.last_active_date else None,
            "total_study_time": self.total_study_time
        }

class ChatHistory(Base):
    """চ্যাট হিস্টোরি সংরক্ষণের মডেল"""
    __tablename__ = "chat_history"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(100), ForeignKey("users.user_id"), index=True, nullable=False)
    
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    topic = Column(String(100), nullable=True)
    is_correct = Column(Boolean, default=None)  # যদি মূল্যায়ন করা হয়
    
    # মেটাডাটা
    response_time = Column(Float, default=0.0)  # সেকেন্ডে
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "question": self.question,
            "answer": self.answer[:200] + "..." if len(self.answer) > 200 else self.answer,
            "topic": self.topic,
            "is_correct": self.is_correct,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None
        }

class TopicMastery(Base):
    """টপিক ভিত্তিক দক্ষতা ট্র্যাকিং"""
    __tablename__ = "topic_mastery"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(100), ForeignKey("users.user_id"), index=True, nullable=False)
    topic_name = Column(String(100), nullable=False)  # bangla_letters, math, colors, animals
    
    # দক্ষতা স্কোর
    mastery_score = Column(Float, default=0.0)  # 0-100
    questions_attempted = Column(Integer, default=0)
    questions_correct = Column(Integer, default=0)
    
    # শেষ কার্যকলাপ
    last_practiced = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        # Composite unique constraint
        # UniqueConstraint('user_id', 'topic_name', name='unique_user_topic'),
    )
    
    def to_dict(self):
        return {
            "topic_name": self.topic_name,
            "mastery_score": self.mastery_score,
            "questions_attempted": self.questions_attempted,
            "questions_correct": self.questions_correct,
            "accuracy": (self.questions_correct / self.questions_attempted * 100) if self.questions_attempted > 0 else 0,
            "last_practiced": self.last_practiced.isoformat() if self.last_practiced else None
        }

class Reminder(Base):
    """রিমাইন্ডার মডেল"""
    __tablename__ = "reminders"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(100), ForeignKey("users.user_id"), index=True, nullable=False)
    parent_id = Column(String(100), ForeignKey("users.user_id"), nullable=True)
    
    reminder_type = Column(String(50), default="study")  # study, break, custom
    message = Column(Text, nullable=False)
    scheduled_time = Column(DateTime, nullable=False)
    is_sent = Column(Boolean, default=False)
    is_recurring = Column(Boolean, default=False)
    recurring_pattern = Column(String(50), nullable=True)  # daily, weekly, custom
    
    created_at = Column(DateTime, default=datetime.utcnow)
    sent_at = Column(DateTime, nullable=True)
    
    def to_dict(self):
        return {
            "id": self.id,
            "reminder_type": self.reminder_type,
            "message": self.message,
            "scheduled_time": self.scheduled_time.isoformat() if self.scheduled_time else None,
            "is_sent": self.is_sent,
            "is_recurring": self.is_recurring
        }
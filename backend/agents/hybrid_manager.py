# backend/agents/hybrid_manager.py
"""
হাইব্রিড এজেন্ট ম্যানেজার
সব এজেন্টকে একসাথে ম্যানেজ করে
"""

from typing import Dict, Any, Optional
from .teacher import TeacherAgent
from .tracker import TrackerAgent
from .parent import ParentAgent

# RAG ইম্পোর্ট
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from rag.searcher import search_knowledge_base

class HybridAgentManager:
    """
    হাইব্রিড এজেন্ট ম্যানেজার
    টিচার, ট্র্যাকার, প্যারেন্ট - তিনটি এজেন্ট একসাথে কাজ করে
    """
    
    def __init__(self):
        self.teacher = TeacherAgent()
        self.tracker = TrackerAgent()
        self.parent = ParentAgent(tracker=self.tracker)
        
        # AG2 কনফিগ (ভবিষ্যতে)
        self.ag2_enabled = False
        self.group_chat = None
        
        print("✅ হাইব্রিড এজেন্ট ম্যানেজার ইনিশিয়ালাইজ হয়েছে!")
        print(f"   👨‍🏫 টিচার এজেন্ট: {self.teacher.name}")
        print(f"   📊 ট্র্যাকার এজেন্ট: {self.tracker.name}")
        print(f"   👨‍👩‍👧 প্যারেন্ট এজেন্ট: {self.parent.name}")
    
    async def process_query(self, user_id: str, question: str) -> str:
        """
        ইউজারের প্রশ্ন প্রসেস করে
        ১. RAG থেকে খোঁজে
        ২. টিচার এজেন্ট উত্তর দেয়
        ৩. ট্র্যাকার এজেন্ট রেকর্ড করে
        """
        
        print(f"\n📝 প্রসেসিং প্রশ্ন from {user_id}: {question}")
        
        # ১. প্রথমে RAG থেকে খোঁজো
        rag_answer = search_knowledge_base(question)
        
        # ২. টিচার এজেন্ট থেকে উত্তর
        if rag_answer:
            # RAG থেকে পাওয়া উত্তর টিচার স্টাইলে দেওয়া
            teacher_answer = f"🧸 {self.teacher.name}: {rag_answer}\n\n❓ আরও কিছু জানতে চাও? 🤗"
        else:
            # IMPORTANT: সঠিকভাবে প্যারামিটার পাঠাও
            # teacher.teach(question=question) - এভাবে কল করো
            teacher_answer = await self.teacher.teach(question=question)
        
        # ৩. ট্র্যাকারে রেকর্ড করো
        self.tracker.track_question(user_id, question, teacher_answer)
        
        return teacher_answer
    
    async def get_progress(self, user_id: str) -> Dict:
        """
        ইউজারের প্রোগ্রেস রিপোর্ট দেয়
        """
        return self.tracker.get_progress(user_id)
    
    async def get_parent_report(self, user_id: str) -> str:
        """
        প্যারেন্টের জন্য বিস্তারিত রিপোর্ট
        """
        return self.parent.get_parent_summary(user_id)
    
    async def get_study_recommendation(self, user_id: str) -> str:
        """
        পড়ার সুপারিশ দেয়
        """
        return self.tracker.get_study_recommendation(user_id)
    
    async def evaluate_answer(self, user_id: str, question: str, student_answer: str) -> Dict:
        """
        বাচ্চার উত্তর মূল্যায়ন করে
        """
        result = await self.teacher.evaluate_answer(question, student_answer)
        
        # ট্র্যাকারে রেকর্ড করো
        self.tracker.track_question(user_id, question, student_answer, result["is_correct"])
        
        return result
    
    def get_system_status(self) -> Dict:
        """
        সিস্টেমের বর্তমান অবস্থা রিটার্ন করে
        """
        return {
            "status": "active",
            "agents": {
                "teacher": "running",
                "tracker": "running", 
                "parent": "running"
            },
            "ag2_enabled": self.ag2_enabled,
            "total_users": len(self.tracker.tracker_data)
        }

# সিংলটন ইনস্ট্যান্স
_hybrid_manager = None

def get_hybrid_manager() -> HybridAgentManager:
    """সিংলটন হাইব্রিড ম্যানেজার রিটার্ন করে"""
    global _hybrid_manager
    if _hybrid_manager is None:
        _hybrid_manager = HybridAgentManager()
    return _hybrid_manager
from typing import Dict, Any, Optional
from .teacher import TeacherAgent
from .tracker import TrackerAgent
from .parent import ParentAgent
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from rag.searcher import search_knowledge_base

class HybridAgentManager:
    
    def __init__(self):
        self.teacher = TeacherAgent()
        self.tracker = TrackerAgent()
        self.parent = ParentAgent(tracker=self.tracker)
        
        self.ag2_enabled = False
        self.group_chat = None
        
        print("✅ হাইব্রিড এজেন্ট ম্যানেজার ইনিশিয়ালাইজ হয়েছে!")
        print(f"   👨‍🏫 টিচার এজেন্ট: {self.teacher.name}")
        print(f"   📊 ট্র্যাকার এজেন্ট: {self.tracker.name}")
        print(f"   👨‍👩‍👧 প্যারেন্ট এজেন্ট: {self.parent.name}")
    
    async def process_query(self, user_id: str, question: str) -> str:
        
        print(f"\n📝 প্রসেসিং প্রশ্ন from {user_id}: {question}")
        
        rag_answer = search_knowledge_base(question)
        
        if rag_answer:
            teacher_answer = f"🧸 {self.teacher.name}: {rag_answer}\n\n❓ আরও কিছু জানতে চাও? 🤗"
        else:
            teacher_answer = await self.teacher.teach(question=question)
        
        self.tracker.track_question(user_id, question, teacher_answer)
        
        return teacher_answer
    
    async def get_progress(self, user_id: str) -> Dict:
        return self.tracker.get_progress(user_id)
    
    async def get_parent_report(self, user_id: str) -> str:
        return self.parent.get_parent_summary(user_id)
    
    async def get_study_recommendation(self, user_id: str) -> str:
        return self.tracker.get_study_recommendation(user_id)
    
    async def evaluate_answer(self, user_id: str, question: str, student_answer: str) -> Dict:
        result = await self.teacher.evaluate_answer(question, student_answer)
        self.tracker.track_question(user_id, question, student_answer, result["is_correct"])
        return result
    
    def get_system_status(self) -> Dict:
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

_hybrid_manager = None

def get_hybrid_manager() -> HybridAgentManager:
    global _hybrid_manager
    if _hybrid_manager is None:
        _hybrid_manager = HybridAgentManager()
    return _hybrid_manager

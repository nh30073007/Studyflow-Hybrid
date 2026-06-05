# backend/agents/__init__.py
"""
StudyFlow AI - হাইব্রিড এজেন্ট সিস্টেম
প্লে গ্রুপ লেভেলের জন্য ৩টি এজেন্ট:
- Teacher Agent: বাচ্চাদের শেখানো
- Tracker Agent: প্রোগ্রেস ট্র্যাক করা
- Parent Agent: প্যারেন্টকে রিপোর্ট করা
"""

from .teacher import TeacherAgent
from .tracker import TrackerAgent
from .parent import ParentAgent
from .hybrid_manager import HybridAgentManager

__all__ = [
    'TeacherAgent',
    'TrackerAgent', 
    'ParentAgent',
    'HybridAgentManager'
]
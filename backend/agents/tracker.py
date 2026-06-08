# backend/agents/tracker.py

from typing import Dict, List, Any
from datetime import datetime, timedelta
import json
import os

class TrackerAgent:
    
    def __init__(self, name: str = "TrackerAgent"):
        self.name = name
        self.tracker_data = {}
        self.data_file = "tracker_data.json"
        self.load_data()
    
    def get_system_message(self) -> str:
        return """তুমি একজন প্রোগ্রেস ট্র্যাকার Agent।

তোমার কাজ:
1. প্রতিটি শিশুর প্রশ্ন ও উত্তর রেকর্ড করা
2. কোন বিষয়ে শিশু ভালো করছে আর কোথায় দুর্বল, তা বিশ্লেষণ করা
3. দৈনিক, সাপ্তাহিক রিপোর্ট তৈরি করা
4. শিশুর অগ্রগতি অনুযায়ী সুপারিশ দেওয়া

তুমি সবসময় নির্ভুল এবং আপডেটেড তথ্য রাখবে।"""
    
    def load_data(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    self.tracker_data = json.load(f)
            except:
                self.tracker_data = {}
    
    def save_data(self):
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.tracker_data, f, ensure_ascii=False, indent=2)
    
    def track_question(self, user_id: str, question: str, answer: str, is_correct: bool = None):
        
        if user_id not in self.tracker_data:
            self.tracker_data[user_id] = {
                "user_id": user_id,
                "first_seen": datetime.now().isoformat(),
                "total_questions": 0,
                "correct_answers": 0,
                "topics": {},
                "daily_activity": {},
                "learning_history": []
            }
        
        now = datetime.now()
        today = now.date().isoformat()
        
        topic = self._detect_topic(question)
        
        data = self.tracker_data[user_id]
        data["total_questions"] += 1
        
        if is_correct:
            data["correct_answers"] += 1
        
        if topic not in data["topics"]:
            data["topics"][topic] = {"total": 0, "correct": 0}
        data["topics"][topic]["total"] += 1
        if is_correct:
            data["topics"][topic]["correct"] += 1
        
        if today not in data["daily_activity"]:
            data["daily_activity"][today] = 0
        data["daily_activity"][today] += 1
        
        data["learning_history"].append({
            "timestamp": now.isoformat(),
            "question": question,
            "topic": topic,
            "is_correct": is_correct,
            "answer": answer[:100]
        })
        
        if len(data["learning_history"]) > 50:
            data["learning_history"] = data["learning_history"][-50:]
        
        data["last_active"] = now.isoformat()
        
        self.save_data()
        return True
    
    def _detect_topic(self, question: str) -> str:
        question_lower = question.lower()
        
        topics = {
            "বাংলা অক্ষর": ["অ", "আ", "ক", "খ", "অক্ষর", "বর্ণ", "লিখতে"],
            "ইংরেজি অক্ষর": ["a", "b", "c", "english", "ইংরেজি", "letter"],
            "গণিত": ["গণনা", "সংখ্যা", "১", "২", "যোগ", "বিয়োগ", "গণিত"],
            "রং": ["লাল", "নীল", "সবুজ", "হলুদ", "রঙ"],
            "প্রাণী": ["গরু", "কুকুর", "বিড়াল", "হাতি", "প্রাণী"],
            "ভালো অভ্যাস": ["হাত ধোয়া", "পড়া", "ঘুম", "অভ্যাস"]
        }
        
        for topic, keywords in topics.items():
            for keyword in keywords:
                if keyword in question_lower:
                    return topic
        
        return "অন্যান্য"
    
    def get_progress(self, user_id: str) -> Dict:
        if user_id not in self.tracker_data:
            return {
                "user_id": user_id,
                "total_questions": 0,
                "correct_answers": 0,
                "accuracy": 0,
                "topics": {},
                "message": "এখনো কোনো প্রশ্ন করা হয়নি"
            }
        
        data = self.tracker_data[user_id]
        total = data["total_questions"]
        correct = data["correct_answers"]
        accuracy = (correct / total * 100) if total > 0 else 0
        
        topic_analysis = {}
        for topic, stats in data["topics"].items():
            topic_total = stats["total"]
            topic_correct = stats["correct"]
            topic_analysis[topic] = {
                "total": topic_total,
                "correct": topic_correct,
                "accuracy": (topic_correct / topic_total * 100) if topic_total > 0 else 0,
                "status": "strong" if topic_correct / topic_total > 0.7 else "needs_practice"
            }
        
        return {
            "user_id": user_id,
            "total_questions": total,
            "correct_answers": correct,
            "accuracy": round(accuracy, 1),
            "topics": topic_analysis,
            "weak_areas": self._get_weak_areas(topic_analysis),
            "strong_areas": self._get_strong_areas(topic_analysis),
            "last_active": data.get("last_active"),
            "daily_activity": data.get("daily_activity", {})
        }
    
    def _get_weak_areas(self, topic_analysis: Dict) -> List[str]:
        weak = []
        for topic, stats in topic_analysis.items():
            if stats["accuracy"] < 60 and stats["total"] >= 3:
                weak.append(topic)
        return weak
    
    def _get_strong_areas(self, topic_analysis: Dict) -> List[str]:
        strong = []
        for topic, stats in topic_analysis.items():
            if stats["accuracy"] >= 80 and stats["total"] >= 5:
                strong.append(topic)
        return strong
    
    def get_study_recommendation(self, user_id: str) -> str:
        progress = self.get_progress(user_id)
        
        if progress["total_questions"] == 0:
            return "📚 শুরু করার জন্য আজকে 'অ' অক্ষরটা শিখে নাও! তারপর গণনা ১-১০ শিখবে।"
        
        weak_areas = progress.get("weak_areas", [])
        
        if weak_areas:
            topics = ", ".join(weak_areas)
            return f"🎯 দুর্বল বিষয়গুলোতে মনোযোগ দাও: {topics}। এই বিষয়গুলো নিয়ে আজকে ৫টি করে প্রশ্নের অনুশীলন করো!"
        
        strong_areas = progress.get("strong_areas", [])
        if strong_areas:
            return f"🌟 তুমি খুব ভালো করছো! {', '.join(strong_areas)} তে তুমি সাবাশ! নতুন বিষয় শেখা শুরু করতে পারো।"
        
        return "📖 প্রতিদিন ১০ মিনিট করে অনুশীলন করো। তুমি ধীরে ধীরে সব শিখতে পারবে!"
    
    def get_daily_report(self, user_id: str) -> str:
        progress = self.get_progress(user_id)
        today = datetime.now().date().isoformat()
        
        today_activity = progress.get("daily_activity", {}).get(today, 0)
        
        report = f"""📊 দৈনিক প্রোগ্রেস রিপোর্ট - {user_id}

📝 আজকের কার্যকলাপ:
• মোট প্রশ্ন: {today_activity} টি
• সঠিক উত্তর: {progress['correct_answers']} টি
• নির্ভুলতা: {progress['accuracy']}%

🎯 সুপারিশ:
{self.get_study_recommendation(user_id)}

💪 চালিয়ে যাও! তুমি পারবে! 🌟"""
        
        return report

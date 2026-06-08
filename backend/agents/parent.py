# backend/agents/parent.py
from typing import Dict, List, Any
from datetime import datetime, timedelta
from .tracker import TrackerAgent

class ParentAgent:
    
    def __init__(self, name: str = "ParentAgent", tracker: TrackerAgent = None):
        self.name = name
        self.tracker = tracker or TrackerAgent()
    
    def get_system_message(self) -> str:
        return 
    
    def get_child_report(self, user_id: str) -> Dict:
        progress = self.tracker.get_progress(user_id)
        weekly_trend = self._calculate_weekly_trend(user_id)
        recommendations = self._generate_recommendations(progress)
        
        return {
            "child_id": user_id,
            "report_date": datetime.now().isoformat(),
            "summary": {
                "total_questions": progress["total_questions"],
                "accuracy": progress["accuracy"],
                "strong_areas": progress.get("strong_areas", []),
                "weak_areas": progress.get("weak_areas", [])
            },
            "weekly_trend": weekly_trend,
            "recommendations": recommendations,
            "next_milestones": self._get_next_milestones(progress)
        }
    
    def _calculate_weekly_trend(self, user_id: str) -> Dict:
        progress = self.tracker.get_progress(user_id)
        daily_activity = progress.get("daily_activity", {})
        
        weekly_data = []
        for i in range(7):
            date = (datetime.now() - timedelta(days=i)).date().isoformat()
            count = daily_activity.get(date, 0)
            weekly_data.append({"date": date, "questions": count})
        
        return {
            "last_7_days": weekly_data,
            "total_this_week": sum(d["questions"] for d in weekly_data),
            "trend": "improving" if weekly_data[0]["questions"] > weekly_data[-1]["questions"] else "steady"
        }
    
    def _generate_recommendations(self, progress: Dict) -> List[str]:
        recommendations = []
        weak_areas = progress.get("weak_areas", [])
        
        if weak_areas:
            recommendations.append(f"🎯 দুর্বল বিষয়গুলোতে বেশি মনোযোগ দিন: {', '.join(weak_areas)}")
        
        if progress["total_questions"] < 20:
            recommendations.append("📚 প্রতিদিন কমপক্ষে ১০-১৫ মিনিট অনুশীলন করান")
        
        if progress["accuracy"] < 60:
            recommendations.append("📖 মৌলিক বিষয়গুলো (অক্ষর, সংখ্যা) আবার রিভিশন করান")
        
        if not recommendations:
            recommendations.append("🌟 আপনার সন্তান খুব ভালো করছে! নতুন চ্যালেঞ্জ দিন")
            recommendations.append("🎨 ছবি আঁকা এবং রং করার মাধ্যমে শেখাকে মজাদার করুন")
        
        return recommendations
    
    def _get_next_milestones(self, progress: Dict) -> List[str]:
        milestones = []
        
        if progress["total_questions"] < 50:
            milestones.append("৫০টি প্রশ্ন করা")
        
        if "বাংলা অক্ষর" in progress.get("weak_areas", []):
            milestones.append("বাংলা বর্ণমালার সব স্বরবর্ণ শেখা")
        
        if progress["accuracy"] < 70:
            milestones.append("নির্ভুলতা ৭০% এ উন্নীত করা")
        
        if not milestones:
            milestones.append("পরবর্তী লেভেলে উন্নীত হওয়ার জন্য প্রস্তুত")
        
        return milestones
    
    def get_parent_summary(self, user_id: str) -> str:
        report = self.get_child_report(user_id)
        summary = report["summary"]
        
        text = f"""
👨‍👩‍👧 **স্টাডিফ্লো এআই - প্যারেন্ট রিপোর্ট**

**শিশু:** {report['child_id']}
**তারিখ:** {datetime.now().strftime('%d %B, %Y')}

---

📊 **এই সপ্তাহের সারাংশ:**
• মোট প্রশ্ন: {summary['total_questions']} টি
• নির্ভুলতা: {summary['accuracy']}%

✅ **শক্তিশালী বিষয়:**
{', '.join(summary['strong_areas']) if summary['strong_areas'] else 'এখনো চিহ্নিত হয়নি'}

⚠️ **উন্নতির ক্ষেত্র:**
{', '.join(summary['weak_areas']) if summary['weak_areas'] else 'সব বিষয়েই ভালো করছে!'}

---

💡 **আমার সুপারিশ:**
{chr(10).join([f'• {r}' for r in report['recommendations']])}

🎯 **পরবর্তী লক্ষ্য:**
{chr(10).join([f'• {m}' for m in report['next_milestones']])}

---

🌟 মনে রাখবেন: প্রতিটি শিশুর শেখার গতি আলাদা। ধৈর্য ধরুন, উৎসাহ দিন!
        """
        return text
    
    def send_weekly_report(self, user_id: str) -> bool:
        report = self.get_parent_summary(user_id)
        print("\n" + "="*60)
        print("📧 সাপ্তাহিক রিপোর্ট পাঠানো হয়েছে")
        print("="*60)
        print(report)
        print("="*60)
        return True

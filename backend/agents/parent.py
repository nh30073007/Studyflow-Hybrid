# backend/agents/parent.py
"""
প্যারেন্ট এজেন্ট - অভিভাবকদের জন্য রিপোর্ট এবং সুপারিশ তৈরি করে
শিশুর অগ্রগতি সম্পর্কে বিস্তারিত জানায়
"""

from typing import Dict, List, Any
from datetime import datetime, timedelta
from .tracker import TrackerAgent

class ParentAgent:
    """
    প্যারেন্ট এজেন্ট - অভিভাবকদের জন্য রিপোর্ট
    শিশুর শেখার অগ্রগতি, দুর্বল বিষয়, সুপারিশ ইত্যাদি দেয়
    """
    
    def __init__(self, name: str = "ParentAgent", tracker: TrackerAgent = None):
        self.name = name
        self.tracker = tracker or TrackerAgent()
    
    def get_system_message(self) -> str:
        """এজেন্টের সিস্টেম মেসেজ"""
        return """তুমি একজন প্যারেন্ট রিপোর্টার Agent।

তোমার কাজ:
1. অভিভাবকদের শিশুর অগ্রগতি সম্পর্কে বিস্তারিত রিপোর্ট দেওয়া
2. শিশুর দুর্বল ও শক্তিশালী বিষয় চিহ্নিত করা
3. উন্নতির জন্য সুপারিশ দেওয়া
4. সাপ্তাহিক এবং মাসিক রিপোর্ট তৈরি করা

তুমি পেশাদার এবং সহানুভূতিশীল ভাষায় রিপোর্ট দেবে।"""
    
    def get_child_report(self, user_id: str) -> Dict:
        """
        একটি শিশুর সম্পূর্ণ রিপোর্ট তৈরি করে
        """
        progress = self.tracker.get_progress(user_id)
        
        # সাপ্তাহিক প্রবণতা
        weekly_trend = self._calculate_weekly_trend(user_id)
        
        # সুপারিশ
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
        """সাপ্তাহিক প্রবণতা গণনা করে"""
        progress = self.tracker.get_progress(user_id)
        daily_activity = progress.get("daily_activity", {})
        
        # গত ৭ দিনের ডাটা
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
        """উন্নতির জন্য সুপারিশ তৈরি করে"""
        recommendations = []
        
        weak_areas = progress.get("weak_areas", [])
        if weak_areas:
            recommendations.append(f"🎯 দুর্বল বিষয়গুলোতে বেশি মনোযোগ দিন: {', '.join(weak_areas)}")
        
        if progress["total_questions"] < 20:
            recommendations.append("📚 প্রতিদিন কমপক্ষে ১০-১৫ মিনিট অনুশীলন করান")
        
        if progress["accuracy"] < 60:
            recommendations.append("📖 মৌলিক বিষয়গুলো (অক্ষর, সংখ্যা) আবার রিভিশন করান")
        
        if not recommendations:
            recommendations.append("🌟 আপনার সন্তান非常好 করছে! নতুন চ্যালেঞ্জ দিন")
            recommendations.append("🎨 ছবি আঁকা এবং রং করার মাধ্যমে শেখাকে মজাদার করুন")
        
        return recommendations
    
    def _get_next_milestones(self, progress: Dict) -> List[str]:
        """পরবর্তী মাইলস্টোন নির্ধারণ করে"""
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
        """
        প্যারেন্টদের জন্য সহজ ভাষায় সারসংক্ষেপ
        """
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
        """
        সাপ্তাহিক রিপোর্ট পাঠায় (ইমেইল/নোটিফিকেশন)
        এখন শুধু প্রিন্ট করবে, পরে ইমেইল যোগ করা যাবে
        """
        report = self.get_parent_summary(user_id)
        print("\n" + "="*60)
        print("📧 সাপ্তাহিক রিপোর্ট পাঠানো হয়েছে")
        print("="*60)
        print(report)
        print("="*60)
        return True
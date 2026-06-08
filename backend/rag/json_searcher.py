# backend/rag/json_searcher.py
import json
import os
from typing import Optional, Dict, List

JSON_DB_PATH = os.path.join(os.path.dirname(__file__), "json_knowledge_base.json")

_json_cache = None

def load_knowledge_base() -> List[Dict]:
    
    global _json_cache
    if _json_cache is None:
        try:
            with open(JSON_DB_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)
                _json_cache = data.get('questions', [])
                print(f"✅ JSON নলেজ বেস লোড হয়েছে: {len(_json_cache)} টি প্রশ্ন")
        except FileNotFoundError:
            print(f"⚠️ JSON ফাইল খুঁজে পাওয়া যায়নি: {JSON_DB_PATH}")
            _json_cache = []
        except Exception as e:
            print(f"⚠️ JSON লোড ব্যর্থ: {e}")
            _json_cache = []
    return _json_cache

def search_json_knowledge_base(query: str) -> Optional[str]:
    match ভিত্তিক
    query_lower = query.lower().strip()
    knowledge = load_knowledge_base()
    
    if not knowledge:
        return None
    
    best_match = None
    best_score = 0
    
    for item in knowledge:
        score = 0
        keywords = item.get('keywords', [])
        priority = item.get('priority', 10)
        
       
        for keyword in keywords:
            if keyword == query_lower:
                score += 100
            elif keyword in query_lower:
                score += 15
        
        
        question_text = item.get('question', '').lower()
        if query_lower == question_text:
            score += 200
        elif question_text in query_lower or query_lower in question_text:
            score += 30
        
        category = item.get('category', '').lower()
        if category in query_lower:
            score += 5
        score += (100 - priority)
        
        if len(query_lower) < 10:
            score += 5
        
        if score > best_score:
            best_score = score
            best_match = item
    
    if best_match and best_score > 0:
    
        if 'easy_answer' in best_match and len(query) < 20:
            return best_match['easy_answer']
        return best_match['answer']
    
    return None

def get_answer_with_context(query: str) -> str:
    
    answer = search_json_knowledge_base(query)
    if answer:
        return f"📚 {answer}\n\n❓ আরও কিছু জানতে চাও? 🤗"
    
    return f"""🤔 আমি '{query}' সম্পর্কে এখনো শিখিনি।

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

def get_knowledge_stats() -> Dict:
   
    knowledge = load_knowledge_base()
    categories = {}
    for item in knowledge:
        cat = item.get('category', 'unknown')
        categories[cat] = categories.get(cat, 0) + 1
    
    return {
        "total_questions": len(knowledge),
        "categories": categories,
        "status": "loaded" if knowledge else "empty"
    }

# backend/rag/searcher.py
import json
import os
from pathlib import Path
from typing import List, Dict, Optional
import glob

class KnowledgeSearcher:
 
    
    def __init__(self, json_db_path: str = None, knowledge_base_dir: str = None):
        if json_db_path is None:
            json_db_path = Path(__file__).parent / "json_knowledge_base.json"
        
        if knowledge_base_dir is None:
            knowledge_base_dir = Path(__file__).parent / "knowledge_base"
        
        self.json_db_path = json_db_path
        self.knowledge_base_dir = knowledge_base_dir
        self.json_knowledge_base = self._load_json_knowledge_base()
        self.txt_contents = self._load_txt_files()
        
        
        self.exact_matches = {
            # বাংলা অক্ষর - Exact match
            "অ": "অ হলো বাংলা বর্ণমালার প্রথম অক্ষর। এটি স্বরবর্ণ। অ দিয়ে অজগর 🐍",
            "অ অক্ষর": "অ হলো বাংলা বর্ণমালার প্রথম অক্ষর। অ দিয়ে অজগর 🐍",
            "অ অক্ষরটা": "অ হলো বাংলা বর্ণমালার প্রথম অক্ষর। অ দিয়ে অজগর 🐍",
            "অ অক্ষরটা শেখাও": "অ হলো বাংলা বর্ণমালার প্রথম অক্ষর। এটি স্বরবর্ণ। অ দিয়ে অজগর শব্দটি লেখা হয়। আসো একসাথে বলি: অ (আ-ও) 🤗",
            "অ শেখাও": "অ হলো বাংলা বর্ণমালার প্রথম অক্ষর। আসো বলি: অ (আ-ও) 🐍",
            
            "আ": "আ হলো বাংলা বর্ণমালার দ্বিতীয় স্বরবর্ণ। আ দিয়ে আম 🥭",
            "আ অক্ষর": "আ হলো বাংলা বর্ণমালার দ্বিতীয় স্বরবর্ণ। আ দিয়ে আম 🥭",
            "আ অক্ষরটা": "আ হলো বাংলা বর্ণমালার দ্বিতীয় স্বরবর্ণ। আ দিয়ে আম 🥭",
            "আ অক্ষরটা শেখাও": "আ হলো বাংলা বর্ণমালার দ্বিতীয় স্বরবর্ণ। আ দিয়ে আম, আলু, আকাশ শব্দগুলো লেখা হয়। আসো বলি: আ (আ-মা) 🥭",
            "আ শেখাও": "আ হলো বাংলা বর্ণমালার দ্বিতীয় স্বরবর্ণ। আসো বলি: আ (আ-মা) 🥭",
            
            "ক": "ক হলো বাংলা বর্ণমালার প্রথম ব্যঞ্জনবর্ণ। ক দিয়ে কাক 🐦",
            "ক অক্ষর": "ক হলো বাংলা বর্ণমালার প্রথম ব্যঞ্জনবর্ণ। ক দিয়ে কাক 🐦",
            "ক অক্ষরটা শেখাও": "ক হলো বাংলা বর্ণমালার প্রথম ব্যঞ্জনবর্ণ। ক দিয়ে কাক, কলম, কাপড় শব্দগুলো লেখা হয়। আসো বলি: ক (ক-ও) 🐦",
            
            # গণনা
            "গণনা": "আসো গণনা করি: ১, ২, ৩, ৪, ৫, ৬, ৭, ৮, ৯, ১০! এক, দুই, তিন, চার, পাঁচ, ছয়, সাত, আট, নয়, দশ। 🎵",
            "গণনা করো": "১, ২, ৩, ৪, ৫, ৬, ৭, ৮, ৯, ১০! এক, দুই, তিন, চার, পাঁচ, ছয়, সাত, আট, নয়, দশ। 🎵",
            
            # অন্যান্য
            "হ্যালো": "হ্যালো! আমি তোমার স্মার্ট টিচার। পড়তে বসো? 🧸",
            "কেমন আছ": "আমি ভালো আছি! তুমি কেমন আছো? 🤗",
            "ধন্যবাদ": "ধন্যবাদ! তোমাকে সাহায্য করতে পেরে ভালো লাগলো! 🤗",
        }
        
        print(f"📚 RAG সার্চার ইনিশিয়ালাইজ: {len(self.txt_contents)} টি TXT ফাইল, {len(self.exact_matches)} টি Exact Match")
    
    def _load_json_knowledge_base(self) -> Dict:
        
        if os.path.exists(self.json_db_path):
            try:
                with open(self.json_db_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    print(f"✅ JSON নলেজ বেস লোড হয়েছে: {len(data.get('questions', []))} টি প্রশ্ন")
                    return data
            except Exception as e:
                print(f"⚠️ JSON লোড ব্যর্থ: {e}")
                return {"questions": []}
        print(f"⚠️ JSON ফাইল নেই: {self.json_db_path}")
        return {"questions": []}
    
    def _load_txt_files(self) -> List[Dict]:
        
        contents = []
        
        if not os.path.exists(self.knowledge_base_dir):
            print(f"⚠️ knowledge_base ফোল্ডার নেই: {self.knowledge_base_dir}")
            return contents
        
        txt_files = glob.glob(str(self.knowledge_base_dir / "*.txt"))
        
        for txt_file in txt_files:
            try:
                with open(txt_file, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if content and len(content) > 10:
                        contents.append({
                            'content': content,
                            'source': os.path.basename(txt_file),
                            'type': 'txt'
                        })
                        print(f"   ✅ লোড হয়েছে: {os.path.basename(txt_file)} ({len(content)} অক্ষর)")
                    elif content:
                        print(f"   ⚠️ ফাইল খুব ছোট: {os.path.basename(txt_file)} ({len(content)} অক্ষর)")
            except Exception as e:
                print(f"   ❌ এরর পড়তে: {txt_file} - {e}")
        
        return contents
    
    def _exact_match_search(self, query: str) -> Optional[str]:
        
        query_lower = query.lower().strip()
        
       
        for key, answer in self.exact_matches.items():
            if key == query_lower or key in query_lower:
                return answer
        
       
        if len(query_lower) == 1:
            for key, answer in self.exact_matches.items():
                if key == query_lower:
                    return answer
        
        return None
    
    def _json_search(self, query: str) -> Optional[Dict]:
        """JSON ডাটাবেসে সার্চ করে - বিস্তারিত উত্তর প্রায়োরিটি দিয়ে"""
        query_lower = query.lower()
        questions = self.json_knowledge_base.get('questions', [])
        
        best_match = None
        best_score = 0
        
        for item in questions:
            score = 0
            keywords = item.get('keywords', [])
            priority = item.get('priority', 10)
            
          
            for keyword in keywords:
                if keyword == query_lower:
                    score += 100
                elif keyword in query_lower:
                    score += 20
            
            
            question_text = item.get('question', '').lower()
            if query_lower == question_text:
                score += 150
            elif question_text in query_lower or query_lower in question_text:
                score += 30
            
           
            if "শেখাও" in query_lower:
                score += 50
            
           
            score += (100 - priority)
            
            if score > best_score:
                best_score = score
                best_match = item
        
        if best_match and best_score > 10:
            return best_match
        
        return None
    
    def search(self, query: str, top_k: int = 3) -> Dict:
       
        results = []
        query_lower = query.lower()
        
        # 1. Exact Match চেক
        exact_answer = self._exact_match_search(query)
        if exact_answer:
            return {
                'results': [{
                    'content': exact_answer,
                    'score': 1.0,
                    'source': 'exact_match',
                    'type': 'exact'
                }]
            }
        
      
        json_match = self._json_search(query)
        if json_match:
           
            if "শেখাও" in query_lower:
                answer = json_match.get('answer', '')
            else:
                answer = json_match.get('easy_answer') or json_match.get('answer', '')
            
            results.append({
                'content': answer,
                'score': 0.95,
                'source': 'json_db',
                'type': 'json'
            })
        
     
        for doc in self.txt_contents:
            content = doc.get('content', '')
            source = doc.get('source', '')
            
            score = self._calculate_score(query_lower, content)
            if score > 0.3:
                results.append({
                    'content': content[:500],
                    'score': score,
                    'source': source,
                    'type': 'txt'
                })
        
        results.sort(key=lambda x: x['score'], reverse=True)
        
        if results:
            print(f"🔍 সার্চ: '{query}' → {len(results)} টি ফলাফল (সেরা স্কোর: {results[0]['score']})")
        
        return {'results': results[:top_k]}
    
    def _calculate_score(self, query: str, content: str) -> float:
        
        content_lower = content.lower()
        score = 0.0
        
        if query in content_lower:
            score += 0.5
        
        query_words = query.split()
        for word in query_words:
            if len(word) > 1 and word in content_lower:
                score += 0.3
        
        for char in query:
            if char in content_lower and char.strip():
                score += 0.05
        
        return min(score, 1.0)
    
    def search_txt_only(self, query: str) -> Optional[str]:
        
        query_lower = query.lower()
        
        for doc in self.txt_contents:
            content = doc.get('content', '')
            if query in content or query_lower in content.lower():
                lines = content.split('\n')
                relevant_lines = []
                for line in lines:
                    if query in line or query_lower in line.lower():
                        relevant_lines.append(line)
                    elif len(relevant_lines) > 0 and len(relevant_lines) < 8:
                        relevant_lines.append(line)
                
                if relevant_lines:
                    return '\n'.join(relevant_lines)
                else:
                    return content[:500]
        
        return None
    
    def get_answer(self, query: str) -> Optional[str]:
       
        result = self.search(query, top_k=1)
        
        if result and result.get('results'):
            best = result['results'][0]
            content = best.get('content', '')
            
            if content:
                return f"🧸 টিচার এজেন্ট: {content}\n\n❓ আরও কিছু জানতে চাও? 🤗"
        
        return None




_searcher = None

def get_searcher():
    global _searcher
    if _searcher is None:
        _searcher = KnowledgeSearcher()
    return _searcher

def search_knowledge_base(query: str) -> Optional[str]:
   
    try:
        searcher = get_searcher()
        
        
        if "শেখাও" in query.lower():
            json_match = searcher._json_search(query)
            if json_match:
                detailed_answer = json_match.get('answer', '')
                if detailed_answer:
                    return detailed_answer
        
      
        exact_answer = searcher._exact_match_search(query)
        if exact_answer:
            return exact_answer
        
        
        json_match = searcher._json_search(query)
        if json_match:
            answer = json_match.get('easy_answer') or json_match.get('answer', '')
            if answer:
                return answer
        
        
        txt_result = searcher.search_txt_only(query)
        if txt_result:
            return txt_result
        
        
        result = searcher.search(query, top_k=1)
        if result and result.get('results'):
            best = result['results'][0]
            if best.get('score', 0) > 0.2:
                content = best.get('content', '')
                if len(content) > 800:
                    content = content[:800] + "..."
                return content
                
    except Exception as e:
        print(f"❌ Search error: {e}")
    
    return None

def search_json_knowledge_base(query: str) -> Optional[str]:
    
    return search_knowledge_base(query)

def get_answer_with_context(query: str) -> str:
    
    answer = search_knowledge_base(query)
    
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

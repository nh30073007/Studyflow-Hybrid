from typing import Dict, Any, Optional, List
import re
import sys
import os
from pathlib import Path

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from rag.searcher import KnowledgeSearcher

class TeacherAgent:
    
    def __init__(self, name: str = "TeacherAgent"):
        self.name = name
        self.llm_config = None
        self.teaching_style = "friendly_and_patient"
        
        try:
            self.searcher = KnowledgeSearcher()
            self.rag_enabled = True
        except Exception as e:
            print(f"RAG initialization warning: {e}")
            self.rag_enabled = False
            self.searcher = None
        
        self.quick_answers = {
            "অ": {
                "answer": "অ হলো বাংলা বর্ণমালার প্রথম অক্ষর। আসো একসাথে বলি: অ (আ-ও) 🤗 অ দিয়ে অজগর 🐍",
                "write": "অ লেখার নিয়ম:\n1. উপর থেকে বাঁকা দাগ\n2. নিচে গোল হয়ে ডান দিকে\n3. ডান পাশে ছোট বাঁকা দাগ",
                "words": ["অজগর", "অন্ন", "অতীত", "অরণ্য"]
            },
            "আ": {
                "answer": "আ হলো বাংলার দ্বিতীয় স্বরবর্ণ। আ দিয়ে আম 🥭, আর আ দিয়ে আকাশ ☁️",
                "write": "আ লেখার নিয়ম:\n1. সোজা দাগ উপর থেকে নিচে\n2. তার সাথে বাঁকা দাগ যোগ করো",
                "words": ["আম", "আকাশ", "আলু", "আপেল"]
            },
            "ই": {
                "answer": "ই হলো তৃতীয় স্বরবর্ণ। ই দিয়ে ইলিশ মাছ 🐟, ই দিয়ে ইট 🧱",
                "write": "ই লেখার নিয়ম:\n1. ছোট বাঁকা দাগ\n2. উপরে একটি ছোট দাগ",
                "words": ["ইলিশ", "ইট", "ইদানিং", "ইউনিয়ন"]
            },
            "ঈ": {
                "answer": "ঈ হলো চতুর্থ স্বরবর্ণ। ঈ দিয়ে ঈগল পাখি 🦅",
                "write": "ঈ লেখার নিয়ম:\n1. ই এর মতো কিন্তু লম্বা করে\n2. নিচে দাগ টানতে হবে",
                "words": ["ঈগল", "ঈশ্বর", "ঈদ", "ঈমান"]
            },
            "ক": {
                "answer": "ক হলো প্রথম ব্যঞ্জনবর্ণ। ক দিয়ে কাক 🐦, কলম ✒️, কাপড় 👕",
                "write": "ক লেখার নিয়ম:\n1. উপরে বাঁকা দাগ\n2. নিচে গোল দাগ\n3. ডান পাশে সোজা দাগ",
                "words": ["কাক", "কলম", "কাপড়", "কমলা"]
            },
            "খ": {
                "answer": "খ হলো দ্বিতীয় ব্যঞ্জনবর্ণ। খ দিয়ে খেলা ⚽, খাতা 📓, খাবার 🍚",
                "write": "খ লেখার নিয়ম:\n1. ক এর মতো কিন্তু ডান দিকে লম্বা দাগ",
                "words": ["খেলা", "খাতা", "খাবার", "খড়"]
            },
            "গ": {
                "answer": "গ হলো তৃতীয় ব্যঞ্জনবর্ণ। গ দিয়ে গরু 🐄, গাছ 🌳, গান 🎵",
                "write": "গ লেখার নিয়ম:\n1. উপরে বাঁকা দাগ\n2. নিচে দাগ টেনে ডান দিকে নিয়ে যাও",
                "words": ["গরু", "গাছ", "গান", "গল্প"]
            },
            "ঘ": {
                "answer": "ঘ হলো চতুর্থ ব্যঞ্জনবর্ণ। ঘ দিয়ে ঘর 🏠, ঘড়ি ⏰",
                "write": "ঘ লেখার নিয়ম:\n1. গ এর মতো কিন্তু ডান দিকে অতিরিক্ত দাগ",
                "words": ["ঘর", "ঘড়ি", "ঘুম", "ঘাস"]
            },
            "চ": {
                "answer": "চ দিয়ে চাঁদ 🌙, চা ☕, চাকা 🚲",
                "write": "চ লেখার নিয়ম:\n1. দুটি বাঁকা দাগ একসাথে",
                "words": ["চাঁদ", "চা", "চাকা", "চলো"]
            },
            "১": "এক 🎈 - আসো একসাথে আঙ্গুল দেখাই: ☝️ একটি আঙ্গুল!",
            "২": "দুই 🎈🎈 - দুইটি আঙ্গুল দেখাও: ✌️",
            "৩": "তিন 🎈🎈🎈 - তিনটি আঙ্গুল দেখাও: 🤟",
            "৪": "চার - চারটি আঙ্গুল দেখাও",
            "৫": "পাঁচ - পাঁচটি আঙ্গুল দেখাও: ✋",
            "গণনা": "আসো গুনি: ১, ২, ৩, ৪, ৫, ৬, ৭, ৮, ৯, ১০! তুমি কি আমার সাথে গুনতে পারবে? 🤗",
            "লাল": "লাল রঙ ❤️ - লাল ফুল, লাল টমেটো, লাল আপেল 🍎",
            "নীল": "নীল রঙ 💙 - নীল আকাশ, নীল সমুদ্র, নীল চাঁদ 🌙",
            "সবুজ": "সবুজ রঙ 💚 - সবুজ ঘাস, সবুজ গাছ, সবুজ তরমুজ 🍉",
            "গরু": "গরু 🐄 - গরু আমাদের দেশের পোষা প্রাণী। গরু দুধ দেয়। হাম্বা হাম্বা ডাকে।",
            "কুকুর": "কুকুর 🐕 - কুকুর আমাদের খুব ভালো বন্ধু। ঘেউ ঘেউ ডাকে।",
            "বিড়াল": "বিড়াল 🐱 - বিড়াল খুব চুপিচুপি হাঁটে। মিউ মিউ ডাকে।",
        }
        
        self.taught_topics = set()
    
    def get_system_message(self) -> str:
        return """তুমি একজন প্লে গ্রুপের শিক্ষক Agent।
        
তোমার কাজ:
1. বাচ্চাদের খুব মজা করে, ধৈর্য সহকারে শেখানো
2. ছবি, রঙ, গল্পের মাধ্যমে শিক্ষা দেওয়া
3. বাচ্চা ভুল করলে কখনো রাগ করবে না, বরং উৎসাহ দেবে
4. প্রতিটি উত্তরের শেষে একটি প্রশ্ন করবে "তুমি কি বুঝেছ?"
5. ইমোজি ব্যবহার করে শিক্ষাকে মজাদার করা

তোমার শিক্ষার বিষয়:
- বাংলা অক্ষর (অ, আ, ক, খ...)
- ইংরেজি অক্ষর (A, B, C...)
- গণিত (১-১০ পর্যন্ত গণনা, যোগ-বিয়োগ)
- রং চেনানো (লাল, নীল, সবুজ)
- প্রাণী চেনানো (গরু, কুকুর, বিড়াল)
- ভালো অভ্যাস (হাত ধোয়া, সময়মতো পড়া)

উত্তর সংক্ষিপ্ত ও স্পষ্ট হবে। বাচ্চাদের মতো ভাষায় বলবে।"""
    
    async def teach(self, topic: str = "", question: str = "") -> str:
        if not question and topic:
            question = topic
        
        question_lower = question.lower()
        
        for keyword, answer_data in self.quick_answers.items():
            if keyword in question or (topic and keyword in topic):
                if isinstance(answer_data, dict):
                    response = f"🧸 {self.name}: {answer_data['answer']}\n\n"
                    if 'write' in answer_data:
                        response += f"✍️ **লেখার নিয়ম:**\n{answer_data['write']}\n\n"
                    if 'words' in answer_data:
                        response += f"📝 **উদাহরণ শব্দ:** {', '.join(answer_data['words'][:3])}\n\n"
                    response += "❓ তুমি কি এই অক্ষরটা লেখার চেষ্টা করতে চাও? 🤗"
                    self.taught_topics.add(keyword)
                    return response
                else:
                    self.taught_topics.add(keyword)
                    return f"🧸 {self.name}: {answer_data}\n\n❓ তুমি কি বুঝেছ? আরও কিছু জানতে চাও? 🤗"
        
        if "গণনা" in question or "১ থেকে" in question or "গুনতি" in question:
            return self.teach_counting()
        
        if self.rag_enabled and self.searcher:
            try:
                rag_result = self.searcher.search(question, top_k=1)
                if rag_result and rag_result.get('results'):
                    best_result = rag_result['results'][0]
                    if best_result.get('score', 0) > 0.3:
                        return self.format_rag_response(best_result)
            except Exception as e:
                print(f"RAG search error: {e}")
        
        if "অক্ষর" in question or "বর্ণ" in question or "শেখাও" in question:
            return self.teach_letter(question)
        
        return self.get_generic_answer(question)
    
    def format_rag_response(self, rag_result: Dict) -> str:
        content = rag_result.get('content', '')
        score = rag_result.get('score', 0)
        source = rag_result.get('source', '')
        
        lines = content.split('\n')[:10]
        short_content = '\n'.join(lines)
        
        response = f"🧸 {self.name}: দেখো, আমি শিখেছি!\n\n📖 {short_content}\n\n"
        
        if "লেখার নিয়ম" in content or "লেখা" in content:
            response += "✍️ তুমি কি এখন লেখার চেষ্টা করতে চাও?\n\n"
        
        response += "❓ আর কিছু জানতে চাও? আমি এখানেই আছি! 🤗"
        return response
    
    def teach_counting(self) -> str:
        return """🧸 টিচার এজেন্ট: আসো একসাথে গণনা করি! 🎵

এক, দুই, তিন, চার, পাঁচ, ছয়, সাত, আট, নয়, দশ!

তুমি কি আমার সাথে বলতে পারবে? 
এবার তুমি চেষ্টা করো: ১ থেকে ১০ পর্যন্ত বলো! 🤗

💡 টিপ: আঙ্গুল দিয়ে দেখাতে পারো! ✋"""
    
    def teach_letter(self, question: str) -> str:
        letters = re.findall(r'[অ-হক-খ]', question)
        
        if letters:
            letter = letters[0]
            
            if letter in self.quick_answers:
                answer_data = self.quick_answers[letter]
                if isinstance(answer_data, dict):
                    response = f"""🧸 টিচার এজেন্ট: '{letter}' অক্ষরটা শেখানো যাক!

🔊 **উচ্চারণ:** {letter} - {answer_data['answer'].split('🤗')[0]}

✍️ **লেখার নিয়ম:**
{answer_data.get('write', 'বাতাসে আঙুল দিয়ে আঁকো')}

📝 **শব্দ গঠন:**
{', '.join(answer_data.get('words', [f'{letter} অক্ষর দিয়ে শব্দ'])[:3])}

🎨 **মজার ব্যাপার:** 
{letter} অক্ষরটা দেখতে অনেকটা {self.get_letter_shape(letter)} এর মতো!

এখন তুমি আঙুল দিয়ে বাতাসে '{letter}' টা লেখার চেষ্টা করো! ✍️

❓ তুমি কি '{letter}' অক্ষরটা চিনতে পারছো?"""
                    self.taught_topics.add(letter)
                    return response
        
        return """🧸 টিচার এজেন্ট: আমি তোমাকে বাংলা অক্ষর শেখাতে পারি!

আসো 'অ' দিয়ে শুরু করি: অ - অজগর 🐍
অ আ ক খ গ ঘ - এভাবে শিখতে থাকি!

তুমি কোন অক্ষরটা শিখতে চাও? আমাকে বলো:
- "অ শেখাও"
- "আ শেখাও" 
- "ক শেখাও"

অথবা পুরো বর্ণমালা একসাথে শিখতে চাও? 🤗"""
    
    def get_letter_shape(self, letter: str) -> str:
        shapes = {
            'অ': 'একটা সাপ 🐍', 'আ': 'একটা আম 🥭', 'ই': 'একটা ছোট মাছ 🐟',
            'ক': 'একটা বসা কাক 🐦', 'খ': 'একটা খোলা কলম ✒️',
            'গ': 'একটা গরুর মুখ 🐄', 'ঘ': 'একটা ঘড়ির কাঁটা ⏰'
        }
        return shapes.get(letter, 'একটা মজার ছবি')
    
    def get_generic_answer(self, question: str) -> str:
        if self.rag_enabled and self.searcher:
            try:
                rag_result = self.searcher.search(question, top_k=1)
                if rag_result and rag_result.get('results'):
                    best_result = rag_result['results'][0]
                    if best_result.get('score', 0) > 0.2:
                        return self.format_rag_response(best_result)
            except:
                pass
        
        return f"""🧸 টিচার এজেন্ট: দারুণ প্রশ্ন করেছো! 🎉

আমি তোমাকে সাহায্য করতে পারি:
• বাংলা অক্ষর শিখতে (অ, আ, ক, খ, গ, ঘ...)
• স্বরবর্ণ ও ব্যঞ্জনবর্ণ চিনতে
• গণনা করতে (১,২,৩,৪,৫...)
• রং চিনতে (লাল, নীল, সবুজ, হলুদ...)
• প্রাণী চিনতে (গরু, কুকুর, বিড়াল, হাতি...)
• ফলের নাম শিখতে (আম, কাঁঠাল, কলা, লিচু...)

**তুমি কী শিখতে চাও? আমাকে প্রশ্ন করো:**
"অ শেখাও" - অ অক্ষর শিখবে
"গণনা শেখাও" - সংখ্যা গণনা শিখবে
"লাল রং শেখাও" - রং শিখবে

আমি তোমার জন্য অপেক্ষা করছি! 🤗"""
    
    async def evaluate_answer(self, question: str, student_answer: str) -> Dict:
        is_correct = False
        feedback = ""
        score = 0
        
        question_lower = question.lower()
        answer_lower = student_answer.lower().strip()
        
        if "অক্ষর" in question or any(letter in question for letter in "অআইঈকখগঘ"):
            target_letter = None
            for letter in "অআইঈকখগঘচছজঝ":
                if letter in question:
                    target_letter = letter
                    break
            
            if target_letter and target_letter in student_answer:
                is_correct = True
                score = 10
                feedback = f"🎉 ওয়াও! তুমি '{target_letter}' অক্ষরটা চিনতে পারছো! খুব ভালো! 🌟 তুমি আজকে একটা নতুন অক্ষর শিখলে!"
            elif target_letter:
                feedback = f"🤗 প্রায় হয়ে গেছে! '{target_letter}' অক্ষরটা একটু দেখো। তুমি কি বাতাসে আঙুল দিয়ে লেখার চেষ্টা করতে চাও? আমি জানি তুমি পারবে! 💪"
                score = 5
        
        elif "গণনা" in question or "সংখ্যা" in question:
            if any(num in answer_lower for num in ["১", "এক", "1", "২", "দুই", "2"]):
                is_correct = True
                score = 10
                feedback = "🎉 সাবাশ! তুমি সংখ্যা চিনতে শিখে যাচ্ছ! তুমি খুব মেধাবী! 🎊"
            else:
                feedback = "😊 চিন্তা করো না, আসো আবার চেষ্টা করি! ১ মানে একটা আঙ্গুল, ২ মানে দুইটা আঙ্গুল। তুমি পারবে! 💪"
                score = 3
        
        elif "রং" in question or "রঙ" in question:
            if any(color in answer_lower for color in ["লাল", "নীল", "সবুজ", "হলুদ"]):
                is_correct = True
                score = 10
                feedback = "🎨 চমৎকার! তুমি রং চিনতে পারো! তুমি তো বড় শিল্পী হবে! 🖌️"
            else:
                feedback = "🌈 রংগুলো দেখতে খুব সুন্দর! লাল মানে আপেলের রং, নীল মানে আকাশের রং। মনে রাখার চেষ্টা করো!"
                score = 3
        
        elif "প্রাণী" in question or "জানোয়ার" in question:
            animals = {"গরু", "কুকুর", "বিড়াল", "হাতি", "বাঘ", "সিংহ"}
            if any(animal in answer_lower for animal in animals):
                is_correct = True
                score = 10
                feedback = "🐘 বাহ! তুমি প্রাণী চিনতে পারো! তুমি তো বড় প্রকৃতিবিদ হবে! 🌿"
            else:
                feedback = "🦁 প্রাণীদের নাম মনে রাখার চেষ্টা করো! গরু হাম্বা করে, কুকুর ঘেউ ঘেউ করে। মজার না?"
                score = 3
        
        else:
            feedback = "🤗 তুমি খুব ভালো চেষ্টা করছো! আসো আরও কিছু শিখি! তুমি কি আমার সাথে নতুন কিছু শিখতে চাও?"
            score = 5
        
        if is_correct:
            self.taught_topics.add(question)
        
        return {
            "is_correct": is_correct,
            "feedback": feedback,
            "score": score,
            "taught_topics": list(self.taught_topics)
        }
    
    def get_taught_topics(self) -> List[str]:
        return list(self.taught_topics)
    
    def reset_progress(self):
        self.taught_topics = set()
        return "📚 সব প্রোগ্রেস রিসেট করা হয়েছে! নতুন করে শুরু করো! 🌟"

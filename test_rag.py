# test_rag.py (studyflow_hybrid ফোল্ডারে)
import sys
sys.path.append('backend')

from rag.init_rag import init_rag_system, get_knowledge_base_stats, get_knowledge_base_summary
from rag.searcher import search_knowledge_base, get_answer_with_context

def test_rag():
    """RAG সিস্টেম টেস্ট করো"""
    
    print("="*60)
    print("🧪 StudyFlow AI - RAG সিস্টেম টেস্ট")
    print("="*60)
    
    # ১. RAG ইনিশিয়ালাইজ
    print("\n1️⃣ RAG সিস্টেম ইনিশিয়ালাইজ করা হচ্ছে...")
    init_rag_system()
    
    # ২. নলেজ বেস স্ট্যাটাস দেখাও
    print("\n2️⃣ নলেজ বেস স্ট্যাটাস:")
    stats = get_knowledge_base_stats()
    print(get_knowledge_base_summary())
    
    # ৩. কিছু প্রশ্ন টেস্ট করো
    print("\n3️⃣ প্রশ্ন টেস্ট করা হচ্ছে:")
    print("-"*40)
    
    test_questions = [
        "অ অক্ষরটা শেখাও",
        "১ থেকে ১০ পর্যন্ত গণনা করো",
        "জাতীয় সঙ্গীত কি?",
        "বাংলা বর্ণমালায় কয়টি অক্ষর?",
        "আমার নাম আরিয়ান"
    ]
    
    for q in test_questions:
        print(f"\n❓ প্রশ্ন: {q}")
        answer = get_answer_with_context(q)
        print(f"🤖 উত্তর: {answer}")
        print("-"*40)
    
    print("\n✅ RAG টেস্ট সম্পূর্ণ!")

if __name__ == "__main__":
    test_rag()
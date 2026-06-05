# backend/rag/init_rag.py
import os
import glob
from typing import Dict, List

KNOWLEDGE_BASE_PATH = os.path.join(os.path.dirname(__file__), "knowledge_base")

_rag_initialized = False
_knowledge_base_stats = {
    "total_files": 0,
    "total_size_bytes": 0,
    "files": [],
    "initialized": False
}

def init_rag_system(force_reload: bool = False) -> bool:
    global _rag_initialized, _knowledge_base_stats
    
    if _rag_initialized and not force_reload:
        print("✅ RAG সিস্টেম আগেই ইনিশিয়ালাইজ করা আছে")
        return True
    
    print("🔄 RAG সিস্টেম ইনিশিয়ালাইজ করা হচ্ছে...")
    
    # নলেজ বেস ফোল্ডার চেক
    if not os.path.exists(KNOWLEDGE_BASE_PATH):
        print(f"⚠️ knowledge_base ফোল্ডার খুঁজে পাওয়া যায়নি: {KNOWLEDGE_BASE_PATH}")
        print(f"📁 ফোল্ডার তৈরি করা হচ্ছে...")
        os.makedirs(KNOWLEDGE_BASE_PATH, exist_ok=True)
        _rag_initialized = True
        return True
    
    # TXT ফাইল গুলো স্ক্যান
    txt_files = glob.glob(os.path.join(KNOWLEDGE_BASE_PATH, "*.txt"))
    txt_files.extend(glob.glob(os.path.join(KNOWLEDGE_BASE_PATH, "*.TXT")))
    
    if not txt_files:
        print("⚠️ কোনো TXT ফাইল খুঁজে পাওয়া যায়নি!")
        print(f"📚 দয়া করে knowledge_base ফোল্ডারে TXT ফাইল রাখুন")
        print(f"   পাথ: {KNOWLEDGE_BASE_PATH}")
        _rag_initialized = True
        return True
    
    # ফাইলের স্ট্যাটাস কালেক্ট
    total_size = 0
    file_list = []
    
    for file_path in txt_files:
        file_name = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)
        total_size += file_size
        file_list.append({
            "name": file_name,
            "size_bytes": file_size,
            "size_kb": round(file_size / 1024, 2),
            "path": file_path
        })
        
        # ফাইলের প্রথম কয়েক লাইন দেখাও
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                first_lines = f.readlines()[:3]
                preview = ' '.join([line.strip() for line in first_lines if line.strip()])
                file_list[-1]["preview"] = preview[:100] + "..." if len(preview) > 100 else preview
        except:
            file_list[-1]["preview"] = "পড়া যায়নি"
    
    _knowledge_base_stats = {
        "total_files": len(txt_files),
        "total_size_bytes": total_size,
        "total_size_kb": round(total_size / 1024, 2),
        "files": file_list,
        "initialized": True,
        "knowledge_base_path": KNOWLEDGE_BASE_PATH
    }
    
    _rag_initialized = True
    
    # স্ট্যাটাস প্রিন্ট
    print("\n" + "="*50)
    print("📚 RAG সিস্টেম সফলভাবে ইনিশিয়ালাইজ হয়েছে!")
    print("="*50)
    print(f"📁 লোকেশন: {KNOWLEDGE_BASE_PATH}")
    print(f"📄 মোট TXT ফাইল: {_knowledge_base_stats['total_files']}")
    print(f"💾 মোট সাইজ: {_knowledge_base_stats['total_size_kb']} KB")
    print("\n📂 ফাইল তালিকা:")
    for f in file_list:
        print(f"   ✅ {f['name']} ({f['size_kb']} KB)")
        if f.get('preview'):
            print(f"      📖 প্রিভিউ: {f['preview'][:50]}...")
    print("="*50 + "\n")
    
    return True

def get_knowledge_base_stats() -> Dict:
    global _knowledge_base_stats
    return _knowledge_base_stats

def reload_knowledge_base() -> bool:
    return init_rag_system(force_reload=True)

def get_knowledge_base_summary() -> str:
    stats = get_knowledge_base_stats()
    if not stats.get('initialized'):
        return "📚 নলেজ বেস এখনো ইনিশিয়ালাইজ হয়নি।"
    
    summary = f"📚 আমার লাইব্রেরিতে {stats['total_files']} টি বই আছে:\n"
    for f in stats.get('files', []):
        summary += f"   - {f['name']}\n"
    
    return summary
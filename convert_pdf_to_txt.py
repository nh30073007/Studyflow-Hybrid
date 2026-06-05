# convert_pdf_to_txt.py
import os
import PyPDF2

kb_path = r"C:\Users\User\Desktop\studyflow_hybrid\backend\rag\knowledge_base"

print("="*50)
print("📚 PDF to TXT কনভার্টার")
print("="*50)

def convert_pdf_to_txt(pdf_path, txt_path):
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page_num, page in enumerate(reader.pages, 1):
                page_text = page.extract_text()
                if page_text:
                    text += f"\n\n--- পৃষ্ঠা {page_num} ---\n\n"
                    text += page_text
            
            with open(txt_path, 'w', encoding='utf-8') as f:
                f.write(text)
            print(f"✅ কনভার্ট হয়েছে: {os.path.basename(pdf_path)} → {os.path.basename(txt_path)}")
            return True
    except Exception as e:
        print(f"❌ কনভার্ট ব্যর্থ {pdf_path}: {e}")
        return False

# সব PDF ফাইল খোঁজো
pdf_files = []
for file in os.listdir(kb_path):
    if file.endswith('.pdf'):
        pdf_files.append(file)

if not pdf_files:
    print("⚠️ কোনো PDF ফাইল খুঁজে পাওয়া যায়নি!")
    print(f"📁 পাথ: {kb_path}")
else:
    print(f"\n📄 পাওয়া PDF ফাইল: {len(pdf_files)} টি")
    for f in pdf_files:
        print(f"   - {f}")
    
    print("\n🔄 কনভার্ট করা হচ্ছে...\n")
    
    for file in pdf_files:
        pdf_path = os.path.join(kb_path, file)
        # ফাইলের নাম থেকে .pdf বাদ দিয়ে .txt যোগ করো
        txt_name = file.replace('.pdf', '').replace('.txt', '') + '.txt'
        txt_path = os.path.join(kb_path, txt_name)
        convert_pdf_to_txt(pdf_path, txt_path)
    
    print("\n" + "="*50)
    print("✅ সব কনভার্ট সম্পন্ন!")
    print("="*50)
    
    # ফলাফল দেখাও
    print("\n📂 এখন knowledge_base ফোল্ডারে:")
    for f in os.listdir(kb_path):
        if f.endswith('.txt'):
            size = os.path.getsize(os.path.join(kb_path, f))
            print(f"   📄 {f} ({size} bytes)")

print("\n🚀 এখন ব্যাকএন্ড রিস্টার্ট করো:")
print("   cd backend")
print("   uvicorn main:app --reload --port 8000")
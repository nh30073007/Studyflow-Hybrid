# convert_pdf.py - এই ফাইলটা studyflow_hybrid ফোল্ডারে সেভ করো
import PyPDF2
import os

# knowledge_base ফোল্ডার তৈরি করো
os.makedirs("backend/rag/knowledge_base", exist_ok=True)

def pdf_to_txt(pdf_path, txt_name):
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text()
        
        txt_path = f"backend/rag/knowledge_base/{txt_name}.txt"
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(text)
        print(f"✅ {txt_name}.txt তৈরি হয়েছে!")
        return True
    except Exception as e:
        print(f"❌ এরর: {e}")
        return False

# তোমার PDF ফাইলের পাথ দাও
print("PDF কনভার্ট করার সময়!")
print("আমার বই.pdf এর পাথ দাও (যেখানে ডাউনলোড করেছো):")
book1 = input()  # যেমন: C:\Users\User\Downloads\my_book.pdf

print("লিখতে শিখি.pdf এর পাথ দাও:")
book2 = input()

if book1:
    pdf_to_txt(book1, "my_book")
if book2:
    pdf_to_txt(book2, "lets_learn_to_write")

print("✅ সব কাজ শেষ!")
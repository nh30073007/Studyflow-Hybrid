# studyflow start here

# frontend/app.py
import streamlit as st
import requests
import json
from datetime import datetime

# পেজ কনফিগারেশন
st.set_page_config(
    page_title="StudyFlow AI - প্লে গ্রুপ লার্নিং",
    page_icon="🧸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# কাস্টম CSS
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .answer-box {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #4CAF50;
        margin: 1rem 0;
    }
    .question-box {
        background-color: #e3f2fd;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .stButton > button {
        background-color: #4CAF50;
        color: white;
        font-size: 1.2rem;
        padding: 0.5rem 2rem;
    }
    .achievement-badge {
        background: linear-gradient(135deg, #ffd89b 0%, #19547b 100%);
        padding: 0.5rem;
        border-radius: 50%;
        text-align: center;
        margin: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# সেশন স্টেট ইনিশিয়ালাইজ
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'user_name' not in st.session_state:
    st.session_state.user_name = ""
if 'total_questions' not in st.session_state:
    st.session_state.total_questions = 0
if 'correct_answers' not in st.session_state:
    st.session_state.correct_answers = 0

# API এন্ডপয়েন্ট (ব্যাকএন্ডের সাথে কানেক্ট হবে)
# API এন্ডপয়েন্ট (ব্যাকএন্ডের সাথে কানেক্ট হবে)
API_BASE_URL = "http://127.0.0.1:8000"  # localhost এর পরিবর্তে 127.0.0.1 ব্যবহার করো

def ask_question(user_id, question):
    """ব্যাকএন্ডে প্রশ্ন পাঠিয়ে উত্তর নেয়"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/ask",
            json={"user_id": user_id, "question": question},
            timeout=30
        )
        if response.status_code == 200:
            return response.json().get("answer", "দুঃখিত, উত্তর পাওয়া যায়নি")
        else:
            return f"এরর {response.status_code}: সার্ভার থেকে সঠিক উত্তর আসেনি"
    except requests.exceptions.ConnectionError:
        return "🔌 ব্যাকএন্ড সার্ভার চালু নেই! দয়া করে `./run.sh` রান করুন"
    except Exception as e:
        return f"⚠️ সমস্যা: {str(e)}"

def get_progress(user_id):
    """ব্যাকএন্ড থেকে প্রোগ্রেস ডাটা আনে"""
    try:
        response = requests.get(f"{API_BASE_URL}/progress/{user_id}")
        if response.status_code == 200:
            return response.json()
        return {}
    except:
        return {}

# সাইডবার - প্রোফাইল এবং প্রোগ্রেস
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3063/3063131.png", width=80)
    st.title("🎓 StudyFlow AI")
    
    # ইউজার ইনপুট
    user_name = st.text_input("👶 তোমার নাম লিখো:", value=st.session_state.user_name)
    if user_name and user_name != st.session_state.user_name:
        st.session_state.user_name = user_name
        st.session_state.chat_history = []
        st.rerun()
    
    if st.session_state.user_name:
        st.success(f"স্বাগতম {st.session_state.user_name}! 🎉")
        
        # প্রোগ্রেস দেখাও
        progress = get_progress(st.session_state.user_name)
        if progress:
            st.subheader("📊 আজকের অগ্রগতি")
            col1, col2 = st.columns(2)
            with col1:
                st.metric("প্রশ্ন করা হয়েছে", progress.get('total_questions', 0))
            with col2:
                st.metric("সঠিক উত্তর", progress.get('correct_answers', 0))
            
            # প্রোগ্রেস বার
            if progress.get('total_questions', 0) > 0:
                accuracy = (progress.get('correct_answers', 0) / progress.get('total_questions', 0)) * 100
                st.progress(accuracy / 100)
                st.caption(f"নির্ভুলতা: {accuracy:.1f}%")
    
    st.markdown("---")
    st.subheader("📚 আমার লাইব্রেরি")
    st.success("✅ আমার বই (NCTB)")
    st.success("✅ লিখতে শিখি (NCTB)")
    st.info("🔜 নতুন কন্টেন্ট আসছে...")
    
    st.markdown("---")
    st.caption("💡 টিপ: প্রশ্ন করো যেমন:\n- 'অ' অক্ষরটা শেখাও\n- ১ থেকে ১০ পর্যন্ত গণনা করো\n- জাতীয় সঙ্গীত শোনাও")

# মেইন কন্টেন্ট
st.markdown('<div class="main-header"><h1>🧸 StudyFlow AI</h1><p>তোমার ছোট্ট স্মার্ট টিচার - মজায় মজায় শিখি!</p></div>', unsafe_allow_html=True)

# কুইক প্রশ্ন বাটন
st.subheader("🎯 দ্রুত প্রশ্ন করুন:")
quick_questions = [
    "অ অক্ষরটা শেখাও",
    "১ থেকে ১০ পর্যন্ত গণনা করো",
    "আমার সোনার বাংলা গাও",
    "ক অক্ষরটা কিভাবে লিখতে হয়?",
    "আমার পরিচয় দিতে শেখাও"
]

cols = st.columns(5)
for idx, q in enumerate(quick_questions):
    with cols[idx]:
        if st.button(q, key=f"quick_{idx}"):
            st.session_state.question = q

# প্রশ্ন ইনপুট
st.markdown('<div class="question-box">', unsafe_allow_html=True)
question = st.text_area(
    "🤔 কী জানতে চাও?",
    value=st.session_state.get('question', ''),
    placeholder="এখানে তোমার প্রশ্ন লিখো... যেমন: 'আমাকে বি অক্ষরটা শেখাও'",
    height=100,
    key="question_input"
)
st.markdown('</div>', unsafe_allow_html=True)

# জিজ্ঞেস করো বাটন
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    ask_button = st.button("✨ জিজ্ঞেস করো ✨", use_container_width=True)

if ask_button and question and st.session_state.user_name:
    # প্রশ্ন লগ করুন
    st.session_state.total_questions += 1
    
    with st.spinner("📚 বই খুঁজে বের করছি..."):
        answer = ask_question(st.session_state.user_name, question)
        
        # চ্যাট হিস্টোরিতে যোগ করুন
        st.session_state.chat_history.append({
            "question": question,
            "answer": answer,
            "timestamp": datetime.now().strftime("%H:%M:%S")
        })
        
        # উত্তর দেখান
        st.markdown(f'<div class="answer-box"><h4>🤖 টিচার এজেন্ট:</h4><p>{answer}</p></div>', unsafe_allow_html=True)
        
        # ফিডব্যাক ইমোজি
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            if st.button("😊 ভালো লেগেছে"):
                st.success("ধন্যবাদ! ❤️")
        with col2:
            if st.button("😐 আরও ভালো হতে পারে"):
                st.info("আমি আরও ভালো করার চেষ্টা করবো! 💪")
        
        # ক্লিয়ার ইনপুট
        st.session_state.question = ""
        st.rerun()

# চ্যাট হিস্টোরি দেখান
if st.session_state.chat_history:
    st.subheader("📜 তোমার শেখার ইতিহাস")
    for chat in reversed(st.session_state.chat_history[-5:]):  # শেষ ৫টি দেখাবে
        with st.expander(f"❓ {chat['question']} - {chat['timestamp']}"):
            st.write(f"**🤖 উত্তর:** {chat['answer']}")

# প্যারেন্ট ড্যাশবোর্ডের লিংক
st.markdown("---")
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.page_link("http://localhost:8502", label="👨‍👩‍👧 প্যারেন্ট ড্যাশবোর্ড →", icon="📊")

st.markdown("---")
st.caption("© 2025 StudyFlow AI | বাংলাদেশের শিশুদের জন্য তৈরি | NCTB কারিকুলাম ভিত্তিক")
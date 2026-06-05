# frontend/parent_dashboard.py
import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go

# পেজ কনফিগারেশন (ভিন্ন পোর্টের জন্য)
st.set_page_config(
    page_title="StudyFlow AI - প্যারেন্ট ড্যাশবোর্ড",
    page_icon="👨‍👩‍👧",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# কাস্টম CSS
st.markdown("""
<style>
    .parent-header {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 2rem;
    }
    .stat-card {
        background-color: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
    }
    .warning-box {
        background-color: #fff3cd;
        border-left: 5px solid #ffc107;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# API এন্ডপয়েন্ট
API_BASE_URL = "http://localhost:8000"

def get_all_children():
    """ব্যাকএন্ড থেকে সব শিশুর ডাটা আনে"""
    try:
        response = requests.get(f"{API_BASE_URL}/parent/all_children")
        if response.status_code == 200:
            return response.json()
        return []
    except:
        return []

def get_child_report(child_id):
    """নির্দিষ্ট শিশুর বিস্তারিত রিপোর্ট আনে"""
    try:
        response = requests.get(f"{API_BASE_URL}/parent/report/{child_id}")
        if response.status_code == 200:
            return response.json()
        return {}
    except:
        return {}

def send_reminder(child_id, message):
    """শিশুকে রিমাইন্ডার পাঠায়"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/parent/remind",
            json={"child_id": child_id, "message": message}
        )
        return response.status_code == 200
    except:
        return False

# হেডার
st.markdown('<div class="parent-header"><h1>👨‍👩‍👧 StudyFlow AI - প্যারেন্ট ড্যাশবোর্ড</h1><p>আপনার সন্তানের শেখার অগ্রগতি পর্যবেক্ষণ করুন</p></div>', unsafe_allow_html=True)

# ট্যাব তৈরি
tab1, tab2, tab3 = st.tabs(["📊 অগ্রগতি ওভারভিউ", "📝 বিস্তারিত রিপোর্ট", "⏰ রিমাইন্ডার ও সেটিংস"])

with tab1:
    st.subheader("🎯 আজকের সারসংক্ষেপ")
    
    # সিমুলেটেড ডাটা (ব্যাকএন্ড রেডি না হওয়া পর্যন্ত)
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("👶 সক্রিয় শিক্ষার্থী", "১", delta="+০ আজ")
    with col2:
        st.metric("📚 মোট প্রশ্ন", "০", delta="+০")
    with col3:
        st.metric("✅ সঠিক উত্তর", "০", delta="0%")
    with col4:
        st.metric("⭐ আজকের তারকা", "-", delta="নতুন")
    
    # প্রোগ্রেস চার্ট
    st.subheader("📈 সাপ্তাহিক অগ্রগতি")
    
    # সিমুলেটেড ডাটা
    days = ['সোম', 'মঙ্গল', 'বুধ', 'বৃহস্পতি', 'শুক্র', 'শনি', 'রবি']
    questions_asked = [5, 8, 6, 10, 12, 7, 4]
    correct_answers = [4, 6, 5, 8, 10, 6, 3]
    
    fig = go.Figure()
    fig.add_trace(go.Bar(name='প্রশ্ন করা হয়েছে', x=days, y=questions_asked, marker_color='#4CAF50'))
    fig.add_trace(go.Bar(name='সঠিক উত্তর', x=days, y=correct_answers, marker_color='#2196F3'))
    
    fig.update_layout(
        title="সাপ্তাহিক লার্নিং অ্যানালিটিক্স",
        xaxis_title="দিন",
        yaxis_title="সংখ্যা",
        barmode='group',
        height=400
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # স্কিল অ্যানালাইসিস
    st.subheader("🎯 বিষয়ভিত্তিক দক্ষতা বিশ্লেষণ")
    
    subjects = ['বাংলা অক্ষর', 'ইংরেজি অক্ষর', 'গণিত', 'পরিবেশ', 'নৈতিক শিক্ষা']
    mastery_levels = [75, 45, 60, 80, 70]  # শতাংশ
    
    fig2 = px.bar(
        x=subjects, 
        y=mastery_levels,
        title="দক্ষতার স্তর",
        labels={'x': 'বিষয়', 'y': 'দক্ষতা (%)'},
        color=mastery_levels,
        color_continuous_scale='Viridis'
    )
    st.plotly_chart(fig2, use_container_width=True)

with tab2:
    st.subheader("📝 বিস্তারিত লার্নিং রিপোর্ট")
    
    # শিশু সিলেক্ট
    child_name = st.selectbox("শিশু নির্বাচন করুন:", ["আরিয়ান (প্লে গ্রুপ)"])
    
    if child_name:
        # লার্নিং লগ
        st.subheader("📖 শেখার ইতিহাস")
        
        # সিমুলেটেড লার্নিং লগ
        learning_logs = pd.DataFrame({
            'সময়': ['১০:৩০ AM', '১০:৪৫ AM', '১১:০০ AM', '১১:৩০ AM'],
            'বিষয়': ['বাংলা অক্ষর', 'গণিত', 'ইংরেজি অক্ষর', 'পরিবেশ'],
            'প্রশ্ন': ['অ অক্ষর চেনানো', '১-১০ গণনা', 'A অক্ষর', 'ফল চেনানো'],
            'উত্তর': ['সঠিক', 'সঠিক', 'ভুল', 'সঠিক'],
            'টিচার রেটিং': ['⭐ 5/5', '⭐ 4/5', '⭐ 3/5', '⭐ 5/5']
        })
        
        st.dataframe(learning_logs, use_container_width=True)
        
        # দুর্বল বিষয়
        st.subheader("⚠️ উন্নতির ক্ষেত্র")
        st.markdown('<div class="warning-box">📌 <strong>ইংরেজি অক্ষর</strong> - A, B, C অক্ষরগুলোতে আরও অনুশীলন প্রয়োজন<br>📌 <strong>গণিত</strong> - ৭-১০ সংখ্যা চিনতে একটু সময় লাগছে</div>', unsafe_allow_html=True)
        
        # সুপারিশ
        st.subheader("💡 শিক্ষকের সুপারিশ")
        st.info("""
        - 🔹 ইংরেজি অক্ষরের জন্য প্রতিদিন ১০ মিনিট বেশি সময় দিন
        - 🔹 গণিতের জন্য ফ্ল্যাশকার্ড ব্যবহার করুন
        - 🔹 প্রতিদিন সকালে ১৫ মিনিট করে অনুশীলন করান
        - 🔹 সাফল্যের জন্য ছোট পুরস্কার দিন
        """)

with tab3:
    st.subheader("⏰ রিমাইন্ডার ও সেটিংস")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📅 দৈনিক রিমাইন্ডার")
        reminder_time = st.time_input("রিমাইন্ডারের সময়", value=datetime.strptime("08:00", "%H:%M").time())
        reminder_days = st.multiselect("কোন দিনে?", ["সোম", "মঙ্গল", "বুধ", "বৃহস্পতি", "শুক্র", "শনি", "রবি"], default=["সোম", "মঙ্গল", "বুধ", "বৃহস্পতি", "শুক্র"])
        
        reminder_message = st.text_area("রিমাইন্ডার মেসেজ", "📚 পড়ার সময় হয়েছে! আজকে StudyFlow AI খুলে একটু অনুশীলন করো 🧸")
        
        if st.button("⏰ রিমাইন্ডার সেট করুন", type="primary"):
            st.success(f"✅ রিমাইন্ডার সেট করা হয়েছে! প্রতিদিন {reminder_time.strftime('%I:%M %p')} এ নোটিফিকেশন যাবে")
    
    with col2:
        st.subheader("🎯 লক্ষ্য নির্ধারণ")
        
        daily_goal = st.slider("দৈনিক প্রশ্নের লক্ষ্য", min_value=5, max_value=30, value=10, step=5)
        weekly_goal = st.slider("সাপ্তাহিক প্রশ্নের লক্ষ্য", min_value=20, max_value=100, value=50, step=10)
        
        st.subheader("📧 প্যারেন্ট রিপোর্ট")
        email = st.text_input("ইমেইল ঠিকানা", placeholder="parent@example.com")
        report_frequency = st.selectbox("রিপোর্ট ফ্রিকোয়েন্সি", ["প্রতিদিন", "সাপ্তাহিক", "মাসিক"])
        
        if st.button("💾 সেটিংস সংরক্ষণ করুন"):
            st.success("✅ সেটিংস সংরক্ষণ করা হয়েছে!")
    
    # পুশ নোটিফিকেশন টেস্ট
    st.subheader("📱 টেস্ট নোটিফিকেশন")
    test_message = st.text_input("টেস্ট মেসেজ লিখুন", "আজকে পড়তে বসো!")
    if st.button("📨 টেস্ট নোটিফিকেশন পাঠান"):
        st.info("📱 নোটিফিকেশন পাঠানোর অনুরোধ করা হয়েছে...")

# ফুটার
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: gray;'>© 2025 StudyFlow AI | প্যারেন্ট পোর্টাল | <a href='http://localhost:8501'>বাচ্চাদের অ্যাপে ফিরে যান</a></div>",
    unsafe_allow_html=True
)
import streamlit as st
from PIL import Image
import os
import base64
import time
from dotenv import load_dotenv

# นำเข้าฟังก์ชันจากไฟล์ utils ของคุณ
from vision_utils import analyze_room
from prompt_utils import build_design_prompt
from image_gen_utils import generate_design, recommend_furniture_and_palette

# โหลด API Key จากไฟล์ .env
load_dotenv()

# --- Page Configuration ---
st.set_page_config(
    page_title="AI Interior Studio",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Premium UI/UX CSS Styling ---
st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;800;900&family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    
    <style>
    /* Animations */
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .animate-fade-in {
        animation: fadeInUp 0.8s cubic-bezier(0.16, 1, 0.3, 1) forwards;
    }

    /* Main Container */
    [data-testid="stAppViewContainer"] {
        background: #fdfbf7;
        color: #1a1a1a;
    }

    /* Hero Section */
    .hero-section {
        background: linear-gradient(135deg, #121212 0%, #2a2a2a 100%);
        color: white !important;
        padding: 5em 2em;
        text-align: center;
        border-radius: 0 0 30px 30px;
        margin-bottom: 2em;
    }
    .hero-title {
        font-family: 'Playfair Display', serif;
        font-size: 4em;
        font-weight: 900;
        background: linear-gradient(135deg, #d4af6e 0%, #f3e5ab 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    /* Cards - ล็อกสีตัวหนังสือ */
    .step-card, .input-card {
        background: white !important;
        border-radius: 20px;
        padding: 2.5em;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.05);
        border: 1px solid rgba(212, 175, 110, 0.2);
        color: #1a1a1a !important; 
        margin-bottom: 1em;
    }
    .step-card h1, .step-card h3, .step-card p, 
    .input-card h3, .input-card p, .input-card label {
        color: #1a1a1a !important;
    }

    /* Buttons */
    .stButton>button {
        width: 100%;
        height: 3.5em;
        border-radius: 15px;
        background: linear-gradient(135deg, #1a1a1a 0%, #333 100%);
        color: #d4af6e !important;
        font-weight: 700;
        border: 1px solid #d4af6e;
        text-transform: uppercase;
        letter-spacing: 2px;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #d4af6e 0%, #e8c547 100%);
        color: #1a1a1a !important;
        transform: scale(1.02);
    }

    /* Tabs Styling */
    .stTabs [data-baseweb="tab"] {
        font-family: 'Playfair Display', serif;
        font-size: 1.2em;
        color: #666;
    }
    .stTabs [aria-selected="true"] {
        color: #d4af6e !important;
        font-weight: 800;
    }
    </style>
    """, unsafe_allow_html=True)

# --- Session State Management ---
if 'image_bytes' not in st.session_state:
    st.session_state['image_bytes'] = None
if 'last_file_name' not in st.session_state:
    st.session_state['last_file_name'] = None
if 'analysis' not in st.session_state:
    st.session_state['analysis'] = None
if 'result_image' not in st.session_state:
    st.session_state['result_image'] = None
if 'recommendations' not in st.session_state:
    st.session_state['recommendations'] = None

# --- Hero Section ---
if not st.session_state['result_image']:
    st.markdown("""
        <div class="hero-section animate-fade-in">
            <h1 class="hero-title">AI Interior Studio</h1>
            <p style="font-size: 1.5em; color: #ccc;">Transform Your Space with Intelligent Design</p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<div class="step-card"><h1 style="text-align: center;">📸</h1><h3 style="text-align: center;">1. Upload</h3><p style="text-align: center;">Share your room photo.</p></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="step-card"><h1 style="text-align: center;">✨</h1><h3 style="text-align: center;">2. Style</h3><p style="text-align: center;">Pick your aesthetic.</p></div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="step-card"><h1 style="text-align: center;">🪄</h1><h3 style="text-align: center;">3. Generate</h3><p style="text-align: center;">AI magic happens.</p></div>', unsafe_allow_html=True)

# --- Input Section ---
st.write("---")
col_in1, col_in2 = st.columns(2, gap="large")

with col_in1:
    st.markdown('<div class="input-card"><h3>📸 Upload Your Space</h3>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Choose an image", type=["jpg", "jpeg", "png"], label_visibility="collapsed")
    if uploaded_file and uploaded_file.name != st.session_state['last_file_name']:
        st.session_state['image_bytes'] = uploaded_file.getvalue()
        st.session_state['last_file_name'] = uploaded_file.name
        st.toast("📸 Image uploaded!", icon="✅")
    st.markdown('</div>', unsafe_allow_html=True)

with col_in2:
    st.markdown('<div class="input-card"><h3>✨ Design Preferences</h3>', unsafe_allow_html=True)
    style = st.selectbox("Style", ["Modern", "Minimalist", "Luxury", "Scandinavian", "Industrial", "Bohemian", "Japandi"])
    room_type = st.selectbox("Room Type", ["Bedroom", "Living Room", "Kitchen", "Office", "Dining Room"])
    st.markdown('</div>', unsafe_allow_html=True)

# --- Generate Logic (The Magic) ---
if st.session_state['image_bytes']:
    if st.button("🚀 GENERATE MY DREAM SPACE"):
        with st.status("🤖 AI Interior Designer is working...", expanded=True) as status:
            try:
                # 1. วิเคราะห์ห้อง
                st.write("🔍 Analyzing room structure...")
                analysis = analyze_room(st.session_state['image_bytes'])
                st.session_state['analysis'] = analysis
                
                # 2. เตรียมข้อมูล
                st.write(f"🎨 Applying {style} aesthetic...")
                furniture = analysis.get('furniture_list', [])
                wall = analysis.get('room_metadata', {}).get('wall_color', 'neutral')
                light = analysis.get('room_metadata', {}).get('lighting', 'natural')
                desc = analysis.get('room_description', '')
                
                prompt = build_design_prompt(room_type, style, furniture, wall, light, desc)
                
                # 3. สร้างภาพ
                st.write("🪄 Rendering 8K visualization...")
                img_b64 = base64.b64encode(st.session_state['image_bytes']).decode('utf-8')
                image_data_uri = f"data:image/jpeg;base64,{img_b64}"
                
                result_url = generate_design(prompt, image_data_uri)
                st.session_state['result_image'] = result_url
                
                # 4. แนะนำของตกแต่ง (แก้ Error ส่ง Parameter เกินแล้ว)
                st.write("🛋️ Curating recommendations...")
                recs = recommend_furniture_and_palette(prompt) 
                st.session_state['recommendations'] = recs
                
                status.update(label="✨ Transformation Complete!", state="complete", expanded=False)
                st.balloons()
                st.rerun()
                
            except Exception as e:
                status.update(label=f"❌ Error: {str(e)}", state="error")

# --- Results Section ---
if st.session_state['result_image']:
    st.markdown(f"<h1 style='text-align: center; font-family: Playfair Display;'>Your {style} {room_type}</h1>", unsafe_allow_html=True)
    
    t1, t2, t3 = st.tabs(["🖼️ Comparison", "📊 AI Analysis", "🛋️ Shopping List"])
    
    with t1:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("<h3 style='text-align: center; color: #666;'>BEFORE</h3>", unsafe_allow_html=True)
            st.image(st.session_state['image_bytes'], use_container_width=True)
        with c2:
            st.markdown("<h3 style='text-align: center; color: #d4af6e;'>AFTER</h3>", unsafe_allow_html=True)
            res_img = st.session_state['result_image']
            
            if res_img and "http" in str(res_img):
                try:
                    # ท่าไม้ตาย: สั่งให้ Python ไปโหลดรูปมาเป็นก้อนข้อมูล (Bytes) ก่อน
                    import requests
                    with st.spinner("🖼️ กำลังดึงรูปภาพมาแสดงผล..."):
                        response = requests.get(res_img, timeout=30)
                        
                        if response.status_code == 200:
                            # พอได้รูปมาแล้ว ก็สั่งให้ Streamlit โชว์รูปจากก้อนข้อมูลนั้นเลย
                            st.image(response.content, use_container_width=True)
                        else:
                            st.error("⚠️ โหลดภาพมาแสดงผลไม่สำเร็จ")
                            st.markdown(f"[คลิกเพื่อดูรูปภาพด้วยตัวเอง]({res_img})")
                except Exception as e:
                    st.error(f"⚠️ โหลดภาพไม่ได้ Error: {e}")
                    st.markdown(f"[คลิกเพื่อดูรูปภาพด้วยตัวเอง]({res_img})")
            else:
                st.error("⚠️ ไม่ได้รับลิงก์ภาพที่ถูกต้อง")
        st.write("")
        st.markdown(f'<div style="text-align: center;"><a href="{st.session_state["result_image"]}" target="_blank"><button style="padding: 10px 20px; background: #d4af6e; border: none; border-radius: 8px; color: white; cursor: pointer; font-weight: bold;">📥 DOWNLOAD HIGH-RES</button></a></div>', unsafe_allow_html=True)

    with t2:
        st.markdown("### 🧠 AI Analysis Insights")
        if st.session_state['analysis']:
            st.write(st.session_state['analysis'].get('room_description', 'No description available.'))
            m1, m2 = st.columns(2)
            meta = st.session_state['analysis'].get('room_metadata', {})
            m1.metric("Current Lighting", meta.get('lighting', 'N/A'))
            m2.metric("Wall Color", meta.get('wall_color', 'N/A'))

    with t3:
        st.markdown("### 🎨 Interior Design Recommendations")
        st.markdown(st.session_state['recommendations'] if st.session_state['recommendations'] else "No recommendations found.")

# --- Sidebar ---
with st.sidebar:
    st.title("⚙️ Studio Settings")
    if st.button("🔄 Start New Project", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
    st.write("---")
    st.markdown("### 💎 Premium Features\n- 4K Render\n- 360 View")
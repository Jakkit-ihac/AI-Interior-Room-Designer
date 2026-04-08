import streamlit as st
from PIL import Image
import os
import requests
import base64
import time
from vision_utils import analyze_room
from prompt_utils import build_design_prompt
from image_gen_utils import generate_design, recommend_furniture_and_palette

# --- Page Configuration ---
st.set_page_config(
    page_title="LUXE AI Interior Designer",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Luxury Dark Mode CSS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        background-color: #0f172a;
        color: #f8fafc;
    }
    
    .main {
        background-color: #0f172a;
    }
    
    /* Luxury Card Style */
    .luxury-card {
        background: rgba(30, 41, 59, 0.7);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 25px;
        border-radius: 20px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
        margin-bottom: 25px;
    }
    
    /* Premium Button */
    .stButton>button {
        width: 100%;
        border-radius: 12px;
        height: 3.5em;
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
        color: white;
        font-weight: 600;
        border: none;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        letter-spacing: 0.5px;
    }
    
    .stButton>button:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 20px rgba(37, 99, 235, 0.4);
        background: linear-gradient(135deg, #60a5fa 0%, #3b82f6 100%);
    }
    
    /* Title Styling */
    .main-title {
        font-size: 3rem;
        font-weight: 800;
        background: linear-gradient(to right, #f8fafc, #94a3b8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    
    .sub-title {
        color: #94a3b8;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    
    /* Result Header */
    .result-header {
        color: #f8fafc;
        font-size: 1.8rem;
        font-weight: 700;
        margin-top: 2rem;
        margin-bottom: 1.5rem;
        display: flex;
        align-items: center;
    }
    
    .result-header::before {
        content: "";
        width: 6px;
        height: 30px;
        background: #3b82f6;
        margin-right: 15px;
        border-radius: 3px;
    }
    
    /* Badge Style */
    .luxury-badge {
        display: inline-block;
        padding: 6px 16px;
        border-radius: 50px;
        font-size: 0.8rem;
        font-weight: 600;
        background: rgba(59, 130, 246, 0.1);
        color: #60a5fa;
        border: 1px solid rgba(59, 130, 246, 0.2);
        margin-right: 8px;
        margin-bottom: 8px;
    }
    
    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
        background-color: transparent;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background-color: transparent !important;
        border: none !important;
        color: #94a3b8 !important;
        font-weight: 600 !important;
    }
    
    .stTabs [aria-selected="true"] {
        color: #3b82f6 !important;
        border-bottom: 2px solid #3b82f6 !important;
    }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #020617;
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }
    </style>
    """, unsafe_allow_html=True)

# --- Session State Initialization ---
if 'analysis' not in st.session_state:
    st.session_state['analysis'] = None
if 'result_image' not in st.session_state:
    st.session_state['result_image'] = None
if 'recommendations' not in st.session_state:
    st.session_state['recommendations'] = None
if 'last_style' not in st.session_state:
    st.session_state['last_style'] = None
if 'last_uploaded' not in st.session_state:
    st.session_state['last_uploaded'] = None

# --- Helper Function: Upload Image to ImgBB ---
def upload_to_imgbb(image_path):
    """
    อัปโหลดรูปภาพไปยัง ImgBB เพื่อรับ URL สาธารณะสำหรับส่งให้ Replicate API
    """
    try:
        # ใช้ API Key สาธารณะ (กรุณาเปลี่ยนเป็นของคุณเองเพื่อความเสถียร)
        api_key = "c8798933668868868868868868868868" # Placeholder
        with open(image_path, "rb") as file:
            url = "https://api.imgbb.com/1/upload"
            payload = {
                "key": api_key,
                "image": base64.b64encode(file.read()),
            }
            res = requests.post(url, payload, timeout=10)
            if res.status_code == 200:
                return res.json()["data"]["url"]
    except Exception as e:
        st.error(f"Image upload failed: {e}")
    return None

# --- Sidebar Content ---
with st.sidebar:
    st.markdown("<div style='text-align: center; padding: 20px;'>", unsafe_allow_html=True)
    st.image("https://img.icons8.com/fluency/96/home-automation.png", width=80)
    st.markdown("<h2 style='color: white; margin-top: 10px;'>LUXE DESIGNER</h2>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("---")
    
    st.subheader("💎 Premium Services")
    st.markdown("✓ **ControlNet Precision:** รักษาโครงสร้างห้องเดิม 100%")
    st.markdown("✓ **Gemini 2.5 Analysis:** วิเคราะห์เชิงลึก")
    st.markdown("✓ **High-Res Output:** ภาพคมชัดระดับ 8K")
    
    st.markdown("---")
    if st.button("🗑️ ล้างข้อมูลทั้งหมด"):
        for key in st.session_state.keys():
            st.session_state[key] = None
        st.rerun()

# --- Main Content ---
st.markdown('<h1 class="main-title">LUXE AI Interior Designer</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">เนรมิตห้องเดิมของคุณให้หรูหราด้วยเทคโนโลยี AI ระดับโลก</p>', unsafe_allow_html=True)

col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.markdown('<div class="luxury-card">', unsafe_allow_html=True)
    st.subheader("📸 1. อัปโหลดรูปห้องของคุณ")
    uploaded_file = st.file_uploader("ลากไฟล์มาวางที่นี่ (JPG, PNG)", type=["jpg", "jpeg", "png"])
    
    if uploaded_file:
        # ตรวจสอบว่ามีการเปลี่ยนรูปใหม่หรือไม่
        if st.session_state['last_uploaded'] != uploaded_file.name:
            st.session_state['analysis'] = None
            st.session_state['result_image'] = None
            st.session_state['recommendations'] = None
            st.session_state['last_uploaded'] = uploaded_file.name
            
        img = Image.open(uploaded_file)
        st.image(img, caption="Original Space", use_container_width=True)
        
        temp_path = "temp_room.jpg"
        img.save(temp_path)
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔍 เริ่มวิเคราะห์ห้องด้วย AI"):
            with st.spinner("กำลังวิเคราะห์โครงสร้างห้องเชิงลึก..."):
                analysis = analyze_room(temp_path)
                st.session_state['analysis'] = analysis
                st.success("วิเคราะห์ห้องเสร็จสมบูรณ์!")
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="luxury-card">', unsafe_allow_html=True)
    st.subheader("🎨 2. ปรับแต่งสไตล์การออกแบบ")
    
    if st.session_state['analysis']:
        analysis = st.session_state['analysis']
        
        # Analysis Badges
        st.markdown(f'<span class="luxury-badge">Room: {analysis.get("room_type", "unknown")}</span>', unsafe_allow_html=True)
        st.markdown(f'<span class="luxury-badge">Wall: {analysis.get("wall_color", "unknown")}</span>', unsafe_allow_html=True)
        st.markdown(f'<span class="luxury-badge">Light: {analysis.get("natural_light_direction", "unknown")}</span>', unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        interior_style = st.selectbox(
            "เลือกสไตล์การตกแต่งภายในระดับพรีเมียม",
            ["Luxury Modern", "Minimalist Zen", "Industrial Loft", "Scandinavian Warmth", "Japanese Wabi-Sabi", "Art Deco", "Bohemian Chic"]
        )
        
        custom_prompt = st.text_area("คำแนะนำพิเศษสำหรับดีไซน์เนอร์", placeholder="เช่น 'เน้นวัสดุหินอ่อนและสีทอง', 'เพิ่มแสงไฟวอร์มไวท์'")
        
        # ตรวจสอบว่ามีการเปลี่ยนสไตล์หรือไม่
        if st.session_state['last_style'] != interior_style:
            # ไม่ล้างรูปทันที แต่จะล้างเมื่อกดปุ่มเจนใหม่เพื่อให้เห็นรูปเก่าก่อน
            pass

        if st.button("✨ เริ่มการออกแบบใหม่"):
            # เคลียร์ผลลัพธ์เก่าก่อนสร้างใหม่
            st.session_state['result_image'] = None
            st.session_state['recommendations'] = None
            st.session_state['last_style'] = interior_style
            
            with st.spinner("AI กำลังประมวลผลภาพแบบ Image-to-Image..."):
                # 1. อัปโหลดรูปภาพ
                img_url = upload_to_imgbb("temp_room.jpg")
                
                if not img_url:
                    st.warning("⚠️ ไม่สามารถอัปโหลดรูปภาพได้ ระบบจะใช้การเจนภาพแบบปกติแทน")
                
                # 2. สร้าง Prompt
                design_prompt = build_design_prompt(
                    analysis.get("room_type", "room"),
                    interior_style,
                    analysis.get("current_furniture", []),
                    analysis.get("wall_color", "white"),
                    analysis.get("natural_light_direction", "unknown"),
                    custom_prompt
                )
                
                # 3. สร้างรูปภาพ
                result_image_url = generate_design(design_prompt, img_url)
                
                # 4. สร้างคำแนะนำ
                recommendations = recommend_furniture_and_palette(design_prompt)
                
                st.session_state['result_image'] = result_image_url
                st.session_state['recommendations'] = recommendations
                st.rerun() # รีเฟรชเพื่อให้แสดงผลลัพธ์ใหม่ทันที
    else:
        st.info("กรุณาอัปโหลดรูปภาพและกดปุ่มวิเคราะห์ห้องก่อนเพื่อเริ่มการออกแบบ")
    st.markdown('</div>', unsafe_allow_html=True)

# --- Results Section ---
if st.session_state['result_image']:
    st.markdown('<h2 class="result-header">The Final Design Result</h2>', unsafe_allow_html=True)
    
    res_col1, res_col2 = st.columns([1, 1], gap="medium")
    
    with res_col1:
        st.image(uploaded_file, caption="Original Space", use_container_width=True)
    
    with res_col2:
        if "Error" in st.session_state['result_image']:
            st.error(st.session_state['result_image'])
        else:
            st.image(st.session_state['result_image'], caption=f"Redesigned in {st.session_state['last_style']} Style", use_container_width=True)
    
    st.markdown('<h3 class="result-header">AI Designer Insights</h3>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["💎 Design Concept", "🛋️ Furniture Selection", "🎨 Color Palette"])
    
    recs = st.session_state['recommendations']
    
    with tab1:
        st.markdown(f"<div class='luxury-card'>{recs.split('Suggested Furniture:')[0] if 'Suggested Furniture:' in recs else recs}</div>", unsafe_allow_html=True)
    
    with tab2:
        if "Suggested Furniture:" in recs:
            furniture_part = recs.split("Suggested Furniture:")[1].split("Color Palette:")[0]
            st.markdown(f"<div class='luxury-card'>{furniture_part}</div>", unsafe_allow_html=True)
    
    with tab3:
        if "Color Palette:" in recs:
            palette_part = recs.split("Color Palette:")[1]
            st.markdown(f"<div class='luxury-card'>{palette_part}</div>", unsafe_allow_html=True)

    # Download Button
    if "Error" not in st.session_state['result_image']:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f'<a href="{st.session_state["result_image"]}" target="_blank"><button style="width:100%; border-radius:12px; height:3.5em; background: #22c55e; color:white; font-weight:bold; border:none; cursor:pointer;">📥 Download High-Res Design</button></a>', unsafe_allow_html=True)

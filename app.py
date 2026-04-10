import streamlit as st
from PIL import Image
import os
import requests
import base64
import time
import json
import io
from vision_utils import analyze_room
from prompt_utils import build_design_prompt
from image_gen_utils import generate_design, recommend_furniture_and_palette

# --- Page Configuration ---
st.set_page_config(
    page_title="AI Interior Designer",
    page_icon="🏠",
    layout="wide"
)

# --- Professional Slide-like CSS Styling ---
st.markdown("""
    <style>
    * {
        font-family: 'Segoe UI', 'Helvetica Neue', sans-serif;
    }
    
    .main {
        background: linear-gradient(135deg, #f5f1ed 0%, #ede9e4 100%);
    }
    
    /* Header & Title Styling */
    .slide-header {
        font-size: 2.5em;
        font-weight: 700;
        color: #2c2c2c;
        margin-bottom: 0.5em;
        letter-spacing: -0.02em;
    }
    
    .slide-subtitle {
        font-size: 1.1em;
        color: #666;
        font-weight: 300;
        margin-bottom: 2em;
    }
    
    /* Slide Container */
    .slide-container {
        background: white;
        border-radius: 12px;
        padding: 3em;
        margin: 2em 0;
        box-shadow: 0 8px 24px rgba(0,0,0,0.08);
        border: 1px solid rgba(0,0,0,0.05);
    }
    
    .slide-container-dark {
        background: linear-gradient(135deg, #e8e4df 0%, #ddd9d4 100%);
        border-radius: 12px;
        padding: 3em;
        margin: 2em 0;
        box-shadow: 0 8px 24px rgba(0,0,0,0.08);
        border: 1px solid rgba(0,0,0,0.05);
    }
    
    /* Two-Column Layout */
    .slide-two-col {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 3em;
        align-items: center;
    }
    
    .slide-image-container {
        display: flex;
        gap: 1.5em;
        flex-wrap: wrap;
    }
    
    .slide-image-wrapper {
        flex: 1;
        min-width: 200px;
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 4px 12px rgba(0,0,0,0.12);
        transition: transform 0.3s ease;
    }
    
    .slide-image-wrapper:hover {
        transform: translateY(-4px);
    }
    
    .slide-image-wrapper img {
        width: 100%;
        height: auto;
        display: block;
    }
    
    /* Text Content */
    .slide-content {
        padding: 1.5em 0;
    }
    
    .slide-content h3 {
        font-size: 1.8em;
        color: #2c2c2c;
        margin-bottom: 1em;
        font-weight: 600;
    }
    
    .slide-content p {
        font-size: 1em;
        line-height: 1.8;
        color: #555;
        margin-bottom: 1em;
    }
    
    .slide-content ul {
        list-style: none;
        padding-left: 0;
    }
    
    .slide-content li {
        font-size: 0.95em;
        line-height: 1.8;
        color: #555;
        margin-bottom: 0.8em;
        padding-left: 1.5em;
        position: relative;
    }
    
    .slide-content li:before {
        content: "•";
        position: absolute;
        left: 0;
        color: #b8860b;
        font-weight: bold;
    }
    
    /* Button Styling */
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        height: 3em;
        background: linear-gradient(135deg, #8b7355 0%, #6b5344 100%);
        color: white;
        font-weight: 600;
        border: none;
        font-size: 1em;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        background: linear-gradient(135deg, #6b5344 0%, #4b3334 100%);
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
    }
    
    /* Analysis Box */
    .analysis-box {
        background: linear-gradient(135deg, #f0ebe6 0%, #e8e3de 100%);
        padding: 1.5em;
        border-radius: 8px;
        border-left: 5px solid #8b7355;
        margin-bottom: 1.5em;
        font-size: 0.95em;
    }
    
    .analysis-box b {
        color: #2c2c2c;
    }
    
    /* Result Container */
    .result-container {
        background: white;
        padding: 2.5em;
        border-radius: 12px;
        box-shadow: 0 8px 24px rgba(0,0,0,0.08);
        margin-top: 2em;
        border: 1px solid rgba(0,0,0,0.05);
    }
    
    .result-title {
        font-size: 2em;
        color: #2c2c2c;
        margin-bottom: 1.5em;
        font-weight: 700;
        letter-spacing: -0.02em;
    }
    
    /* Recommendation Box */
    .recommendation-box {
        background: linear-gradient(135deg, #f9f7f4 0%, #f5f1ed 100%);
        padding: 2em;
        border-radius: 8px;
        border-left: 4px solid #b8860b;
        margin-top: 1.5em;
    }
    
    .recommendation-box h4 {
        color: #2c2c2c;
        margin-bottom: 1em;
        font-size: 1.2em;
    }
    
    .recommendation-box p {
        color: #555;
        line-height: 1.8;
        font-size: 0.95em;
    }
    
    /* Sidebar */
    .sidebar-content {
        background: white;
        padding: 1.5em;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background-color: #f0ebe6 !important;
        border-radius: 8px !important;
    }
    
    /* Responsive */
    @media (max-width: 768px) {
        .slide-two-col {
            grid-template-columns: 1fr;
        }
        
        .slide-container {
            padding: 1.5em;
        }
        
        .slide-header {
            font-size: 1.8em;
        }
    }
    </style>
    """, unsafe_allow_html=True)

# --- Session State Management ---
def init_session():
    if 'image_bytes' not in st.session_state:
        st.session_state['image_bytes'] = None
    if 'last_file_name' not in st.session_state:
        st.session_state['last_file_name'] = None
    if 'analysis' not in st.session_state:
        st.session_state['analysis'] = None
    if 'imgbb_url' not in st.session_state:
        st.session_state['imgbb_url'] = None
    if 'result_image' not in st.session_state:
        st.session_state['result_image'] = None
    if 'recommendations' not in st.session_state:
        st.session_state['recommendations'] = None
    if 'image_dims' not in st.session_state:
        st.session_state['image_dims'] = (1024, 768)
    if 'scroll_to_results' not in st.session_state:
        st.session_state['scroll_to_results'] = False

init_session()

# --- Helper Function: Upload Image to ImgBB ---
def upload_to_imgbb(image_bytes):
    """
    อัปโหลดรูปภาพไปยัง ImgBB เพื่อรับ URL สาธารณะ
    """
    if not image_bytes:
        return None
    
    api_keys = [
        "533f07276d994ec8350b6177fb133a0d",
        "6d207e021112d492d03f842280a32101",
        "c8798933668868868868868868868868",
        "e1f2g3h4i5j6k7l8m9n0o1p2q3r4s5t6",
        "u7v8w9x0y1z2a3b4c5d6e7f8g9h0i1j2"
    ]
    
    for api_key in api_keys:
        try:
            url = "https://api.imgbb.com/1/upload"
            payload = {
                "key": api_key,
                "image": base64.b64encode(image_bytes),
            }
            res = requests.post(url, payload, timeout=15)
            if res.status_code == 200:
                return res.json()["data"]["url"]
            elif res.status_code == 400 and "quota exceeded" in res.text.lower():
                continue
            else:
                continue
        except:
            continue
            
    st.error("❌ ไม่สามารถอัปโหลดรูปภาพได้ กรุณาลองใหม่อีกครั้ง")
    return None

# --- Main UI ---
st.markdown('<div style="text-align: center; margin-bottom: 2em;"><h1 class="slide-header">🏠 AI Interior Room Designer</h1><p class="slide-subtitle">ออกแบบห้องใหม่ด้วย AI ในเพียงไม่กี่คลิก</p></div>', unsafe_allow_html=True)

st.markdown("---")

col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.markdown('<h3 style="color: #2c2c2c; font-weight: 600; margin-bottom: 1.5em;">📸 ขั้นตอนที่ 1: อัปโหลดรูปห้อง</h3>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("เลือกรูปภาพห้องของคุณ (JPG, PNG)", type=["jpg", "jpeg", "png"])
    
    if uploaded_file:
        if uploaded_file.name != st.session_state['last_file_name']:
            st.session_state['image_bytes'] = uploaded_file.getvalue()
            st.session_state['last_file_name'] = uploaded_file.name
            st.session_state['analysis'] = None
            st.session_state['imgbb_url'] = None
            st.session_state['result_image'] = None
            st.session_state['recommendations'] = None
            
            img = Image.open(io.BytesIO(st.session_state['image_bytes']))
            st.session_state['image_dims'] = img.size
            st.rerun()

    if st.session_state['image_bytes']:
        st.markdown('<div style="border-radius: 12px; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.12);">', unsafe_allow_html=True)
        st.image(st.session_state['image_bytes'], caption="รูปห้องต้นฉบับ", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        room_type_options = ["Living Room", "Bedroom", "Kitchen", "Bathroom", "Office", "Dining Room", "Studio"]
        selected_room_type = st.selectbox("ระบุประเภทห้อง", room_type_options)
        
        if st.button("🔍 วิเคราะห์ห้อง"):
            with st.spinner("AI กำลังวิเคราะห์โครงสร้างห้อง..."):
                img_obj = Image.open(io.BytesIO(st.session_state['image_bytes']))
                analysis = analyze_room(img_obj)
                
                if "room_metadata" in analysis:
                    analysis["room_metadata"]["room_type"] = selected_room_type
                
                st.session_state['analysis'] = analysis
                st.session_state['imgbb_url'] = upload_to_imgbb(st.session_state['image_bytes'])
                st.success("✅ วิเคราะห์เสร็จสมบูรณ์!")

with col2:
    st.markdown('<h3 style="color: #2c2c2c; font-weight: 600; margin-bottom: 1.5em;">✨ ขั้นตอนที่ 2: เลือกสไตล์และออกแบบ</h3>', unsafe_allow_html=True)
    
    if st.session_state['analysis']:
        analysis = st.session_state['analysis']
        
        st.markdown('<div class="analysis-box"><b>✓ ห้องที่ตรวจพบ:</b> ' + analysis.get("room_metadata", {}).get("room_type", "unknown") + '</div>', unsafe_allow_html=True)
        
        with st.expander("📋 ดูรายละเอียด JSON", expanded=False):
            st.json(analysis)
        
        st.markdown("---")
        interior_style = st.selectbox(
            "เลือกสไตล์การออกแบบ",
            ["Minimalist", "Modern Luxury", "Industrial", "Scandinavian", "Japanese Zen", "Bohemian"]
        )
        
        custom_prompt = st.text_area("คำแนะนำเพิ่มเติม (ถ้ามี)", placeholder="เช่น 'เน้นสีขาวและไม้', 'เพิ่มต้นไม้เยอะๆ'", height=80)
        
        if st.button("✨ เริ่มออกแบบห้องใหม่"):
            if not st.session_state['imgbb_url']:
                with st.spinner("กำลังอัปโหลดรูปภาพ..."):
                    st.session_state['imgbb_url'] = upload_to_imgbb(st.session_state['image_bytes'])
            
            if st.session_state['imgbb_url']:
                with st.spinner(f"AI กำลังสร้างห้องสไตล์ {interior_style}..."):
                    metadata = analysis.get("room_metadata", {})
                    detailed_narrative = analysis.get("detailed_narrative", "")
                    furniture_list = [f"{f.get('item')} at {f.get('position')}" for f in analysis.get("furniture_mapping", [])]
                    
                    design_prompt = build_design_prompt(
                        metadata.get("room_type", "room"),
                        interior_style,
                        furniture_list,
                        analysis.get("structural_elements", {}).get("walls", "white"),
                        analysis.get("lighting_and_atmosphere", {}).get("natural_light", "unknown"),
                        f"{custom_prompt}. {detailed_narrative}"
                    )
                    
                    width, height = st.session_state['image_dims']
                    result_url = generate_design(design_prompt, st.session_state['imgbb_url'], width, height)
                    
                    if result_url:
                        st.session_state['result_image'] = result_url
                        st.session_state['recommendations'] = recommend_furniture_and_palette(design_prompt)
                        st.session_state['scroll_to_results'] = True
                        st.rerun()
                    else:
                        st.error("ไม่สามารถสร้างรูปภาพได้ในขณะนี้ กรุณาลองใหม่อีกครั้ง")
            else:
                st.error("❌ ไม่สามารถอัปโหลดรูปภาพได้")
    else:
        st.info("📌 กรุณาอัปโหลดรูปภาพและกดปุ่มวิเคราะห์ห้องก่อน")

# --- Auto-scroll to Results ---
if st.session_state.get('scroll_to_results'):
    st.session_state['scroll_to_results'] = False
    st.markdown("""
    <script>
        setTimeout(function() {
            window.scrollTo(0, document.body.scrollHeight);
        }, 500);
    </script>
    """, unsafe_allow_html=True)

# --- Results Display (Slide Style) ---
if st.session_state['result_image']:
    st.markdown("---")
    
    # Slide 1: Design Proposal
    st.markdown('<div class="slide-container">', unsafe_allow_html=True)
    st.markdown('<h2 class="result-title">🎨 DESIGN PROPOSAL</h2>', unsafe_allow_html=True)
    
    st.markdown('<div class="slide-two-col">', unsafe_allow_html=True)
    
    col_before, col_after = st.columns(2)
    with col_before:
        st.markdown('<div style="text-align: center;"><h4 style="color: #2c2c2c; margin-bottom: 1em;">BEFORE</h4></div>', unsafe_allow_html=True)
        st.markdown('<div class="slide-image-wrapper">', unsafe_allow_html=True)
        st.image(st.session_state['image_bytes'], use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col_after:
        st.markdown('<div style="text-align: center;"><h4 style="color: #2c2c2c; margin-bottom: 1em;">AFTER</h4></div>', unsafe_allow_html=True)
        st.markdown('<div class="slide-image-wrapper">', unsafe_allow_html=True)
        st.image(st.session_state['result_image'], use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Slide 2: Recommendations
    if st.session_state['recommendations']:
        st.markdown('<div class="slide-container-dark">', unsafe_allow_html=True)
        st.markdown('<h2 class="result-title">💡 AI DESIGNER RECOMMENDATIONS</h2>', unsafe_allow_html=True)
        
        st.markdown('<div class="recommendation-box">', unsafe_allow_html=True)
        st.markdown(st.session_state['recommendations'])
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Download Button
    st.markdown('<div style="text-align: center; margin-top: 2em;">', unsafe_allow_html=True)
    st.markdown(f'<a href="{st.session_state["result_image"]}" target="_blank"><button style="padding: 1em 2em; border-radius: 8px; background: linear-gradient(135deg, #8b7355 0%, #6b5344 100%); color: white; font-weight: 600; border: none; cursor: pointer; font-size: 1em;">📥 ดาวน์โหลดรูปภาพ</button></a>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown('<div class="sidebar-content">', unsafe_allow_html=True)
    st.title("⚙️ Settings")
    
    if st.button("🔄 ล้างข้อมูลทั้งหมด"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
    
    st.markdown("---")
    st.markdown("**ℹ️ เกี่ยวกับแอป**")
    st.markdown("""
    AI Interior Room Designer ช่วยให้คุณสามารถ:
    - 📸 อัปโหลดรูปห้องของคุณ
    - 🤖 ให้ AI วิเคราะห์โครงสร้างห้อง
    - 🎨 เลือกสไตล์ที่ชอบ
    - ✨ ได้รูปห้องใหม่ที่สวยงาม
    """)
    
    st.markdown('</div>', unsafe_allow_html=True)

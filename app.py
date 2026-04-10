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

# --- Professional Editorial CSS Styling (Inspired by SOLUTION CONCEPT slide) ---
st.markdown("""
    <style>
    * {
        font-family: 'Segoe UI', 'Helvetica Neue', 'Arial', sans-serif;
    }
    
    .main {
        background: #f5f1ed;
        padding: 0 !important;
    }
    
    /* Input Section */
    .input-section {
        background: #f5f1ed;
        padding: 3em 2em;
    }
    
    .section-title {
        font-size: 1.3em;
        font-weight: 600;
        color: #2c2c2c;
        margin-bottom: 1.5em;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    /* Split Screen Result Container */
    .result-split-container {
        display: grid;
        grid-template-columns: 1fr 1fr;
        min-height: 100vh;
        background: white;
    }
    
    .result-left {
        background: linear-gradient(135deg, #e8e4df 0%, #ddd9d4 100%);
        padding: 4em 3em;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        position: relative;
    }
    
    .result-left::before {
        content: 'ครูบาช่วยหมูเด้งด้วย';
        position: absolute;
        top: 2em;
        left: 3em;
        font-size: 0.85em;
        color: #2c2c2c;
        font-weight: 500;
    }
    
    .result-right {
        background: white;
        padding: 4em 3em;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    
    .image-pair-container {
        display: flex;
        gap: 1.5em;
        justify-content: center;
        flex-wrap: wrap;
    }
    
    .image-box {
        flex: 1;
        min-width: 200px;
        max-width: 280px;
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 12px 32px rgba(0, 0, 0, 0.15);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        background: white;
    }
    
    .image-box:hover {
        transform: translateY(-8px);
        box-shadow: 0 16px 40px rgba(0, 0, 0, 0.2);
    }
    
    .image-box img {
        width: 100%;
        height: auto;
        display: block;
    }
    
    .image-label {
        text-align: center;
        font-size: 0.85em;
        color: #666;
        margin-top: 0.8em;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    /* Right Side Content */
    .result-title {
        font-size: 2.2em;
        font-weight: 700;
        color: #2c2c2c;
        margin-bottom: 1.5em;
        letter-spacing: -0.02em;
    }
    
    .result-description {
        font-size: 0.95em;
        line-height: 1.8;
        color: #555;
        margin-bottom: 1.5em;
    }
    
    .result-description p {
        margin-bottom: 1em;
    }
    
    .result-description strong {
        color: #2c2c2c;
        font-weight: 600;
    }
    
    /* Shopping List */
    .shopping-list {
        margin-top: 2em;
        padding-top: 1.5em;
        border-top: 2px solid #e0dcd7;
    }
    
    .shopping-list h4 {
        font-size: 1em;
        color: #2c2c2c;
        margin-bottom: 1em;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    .shopping-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.8em 0;
        border-bottom: 1px solid #f0ebe6;
        font-size: 0.9em;
    }
    
    .shopping-item:last-child {
        border-bottom: none;
    }
    
    .item-name {
        color: #2c2c2c;
        font-weight: 500;
    }
    
    .item-price {
        color: #666;
        font-size: 0.85em;
    }
    
    .item-buy-btn {
        background: #4a90e2;
        color: white;
        border: none;
        padding: 0.4em 0.8em;
        border-radius: 4px;
        font-size: 0.8em;
        cursor: pointer;
        font-weight: 600;
        transition: background 0.2s ease;
    }
    
    .item-buy-btn:hover {
        background: #357abd;
    }
    
    /* Input Section Styling */
    .input-container {
        background: white;
        padding: 2em;
        border-radius: 8px;
        margin-bottom: 1.5em;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    
    .stButton>button {
        width: 100%;
        border-radius: 6px;
        height: 2.8em;
        background: linear-gradient(135deg, #8b7355 0%, #6b5344 100%);
        color: white;
        font-weight: 600;
        border: none;
        font-size: 0.95em;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        background: linear-gradient(135deg, #6b5344 0%, #4b3334 100%);
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
    }
    
    .stSelectbox, .stTextArea {
        font-size: 0.95em;
    }
    
    /* Responsive */
    @media (max-width: 1024px) {
        .result-split-container {
            grid-template-columns: 1fr;
        }
        
        .result-left {
            padding: 3em 2em;
            min-height: auto;
        }
        
        .result-right {
            padding: 3em 2em;
        }
        
        .result-left::before {
            top: 1.5em;
            left: 2em;
        }
    }
    
    @media (max-width: 768px) {
        .result-title {
            font-size: 1.6em;
        }
        
        .image-box {
            max-width: 100%;
        }
        
        .image-pair-container {
            flex-direction: column;
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
    if 'selected_style' not in st.session_state:
        st.session_state['selected_style'] = None

init_session()

# --- Helper Function: Upload Image to ImgBB ---
def upload_to_imgbb(image_bytes):
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
st.markdown('<div class="input-section">', unsafe_allow_html=True)

col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.markdown('<h3 class="section-title">📸 ขั้นตอนที่ 1: อัปโหลดรูปห้อง</h3>', unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="input-container">', unsafe_allow_html=True)
        uploaded_file = st.file_uploader("เลือกรูปภาพห้องของคุณ (JPG, PNG)", type=["jpg", "jpeg", "png"])
        st.markdown('</div>', unsafe_allow_html=True)
    
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
        st.markdown('<div class="input-container">', unsafe_allow_html=True)
        st.image(st.session_state['image_bytes'], caption="รูปห้องต้นฉบับ", use_container_width=True)
        
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
        
        st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<h3 class="section-title">✨ ขั้นตอนที่ 2: เลือกสไตล์และออกแบบ</h3>', unsafe_allow_html=True)
    
    if st.session_state['analysis']:
        st.markdown('<div class="input-container">', unsafe_allow_html=True)
        
        analysis = st.session_state['analysis']
        room_type = analysis.get("room_metadata", {}).get("room_type", "unknown")
        
        st.markdown(f"**✓ ห้องที่ตรวจพบ:** {room_type}")
        
        with st.expander("📋 ดูรายละเอียด JSON", expanded=False):
            st.json(analysis)
        
        st.markdown("---")
        
        interior_style = st.selectbox(
            "เลือกสไตล์การออกแบบ",
            ["Minimalist", "Modern Luxury", "Industrial", "Scandinavian", "Japanese Zen", "Bohemian"]
        )
        st.session_state['selected_style'] = interior_style
        
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
        
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="input-container">', unsafe_allow_html=True)
        st.info("📌 กรุณาอัปโหลดรูปภาพและกดปุ่มวิเคราะห์ห้องก่อน")
        st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

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

# --- Results Display (SOLUTION CONCEPT Style) ---
if st.session_state['result_image']:
    st.markdown('<div class="result-split-container">', unsafe_allow_html=True)
    
    # Left Side - Images
    st.markdown('<div class="result-left">', unsafe_allow_html=True)
    st.markdown('<div class="image-pair-container">', unsafe_allow_html=True)
    
    col_before, col_after = st.columns(2)
    with col_before:
        st.markdown('<div class="image-box">', unsafe_allow_html=True)
        st.image(st.session_state['image_bytes'], use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('<div class="image-label">BEFORE</div>', unsafe_allow_html=True)
    
    with col_after:
        st.markdown('<div class="image-box">', unsafe_allow_html=True)
        st.image(st.session_state['result_image'], use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('<div class="image-label">AFTER</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Right Side - Content
    st.markdown('<div class="result-right">', unsafe_allow_html=True)
    
    st.markdown('<h2 class="result-title">SOLUTION CONCEPT</h2>', unsafe_allow_html=True)
    
    if st.session_state['recommendations']:
        st.markdown(f'<div class="result-description">{st.session_state["recommendations"]}</div>', unsafe_allow_html=True)
    
    # Shopping List (Mock)
    st.markdown("""
    <div class="shopping-list">
        <h4>Recommended Items</h4>
        <div class="shopping-item">
            <span class="item-name">Premium Furniture Set</span>
            <span class="item-price">$450</span>
            <button class="item-buy-btn">BUY</button>
        </div>
        <div class="shopping-item">
            <span class="item-name">Decorative Lighting</span>
            <span class="item-price">$120</span>
            <button class="item-buy-btn">BUY</button>
        </div>
        <div class="shopping-item">
            <span class="item-name">Area Rug</span>
            <span class="item-price">$95</span>
            <button class="item-buy-btn">BUY</button>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Download Button (Below the split container)
    st.markdown("---")
    st.markdown(f'<div style="text-align: center; padding: 2em;"><a href="{st.session_state["result_image"]}" target="_blank"><button style="padding: 1em 2em; border-radius: 6px; background: linear-gradient(135deg, #8b7355 0%, #6b5344 100%); color: white; font-weight: 600; border: none; cursor: pointer; font-size: 1em;">📥 ดาวน์โหลดรูปภาพ</button></a></div>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.title("⚙️ Settings")
    
    if st.button("🔄 ล้างข้อมูลทั้งหมด"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
    
    st.markdown("---")
    st.markdown("**ℹ️ เกี่ยวกับแอป**")
    st.markdown("""
    AI Interior Room Designer ช่วยให้คุณ:
    - 📸 อัปโหลดรูปห้องของคุณ
    - 🤖 ให้ AI วิเคราะห์โครงสร้าง
    - 🎨 เลือกสไตล์ที่ชอบ
    - ✨ ได้รูปห้องใหม่ที่สวยงาม
    """)

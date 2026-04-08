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
    page_title="AI Interior Designer",
    page_icon="🏠",
    layout="wide"
)

# --- Simple & Clean CSS ---
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        height: 3em;
        background-color: #007bff;
        color: white;
        font-weight: bold;
        border: none;
    }
    .stButton>button:hover {
        background-color: #0056b3;
    }
    .result-container {
        background-color: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-top: 20px;
    }
    .section-header {
        color: #333;
        border-bottom: 2px solid #007bff;
        padding-bottom: 10px;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- Session State Management ---
# ใช้ Session State เพื่อเก็บข้อมูลให้คงอยู่แม้จะมีการเปลี่ยนสไตล์
if 'analysis' not in st.session_state:
    st.session_state['analysis'] = None
if 'result_image' not in st.session_state:
    st.session_state['result_image'] = None
if 'recommendations' not in st.session_state:
    st.session_state['recommendations'] = None
if 'current_image_url' not in st.session_state:
    st.session_state['current_image_url'] = None

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
            res = requests.post(url, payload, timeout=15)
            if res.status_code == 200:
                return res.json()["data"]["url"]
    except Exception as e:
        st.error(f"Image upload failed: {e}")
    return None

# --- Main UI ---
st.title("🏠 AI Interior Room Designer")
st.write("ออกแบบห้องใหม่โดยรักษาโครงสร้างเดิมของคุณ 100%")

col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.header("1. อัปโหลดรูปห้อง")
    uploaded_file = st.file_uploader("เลือกรูปภาพห้องของคุณ (JPG, PNG)", type=["jpg", "jpeg", "png"])
    
    if uploaded_file:
        img = Image.open(uploaded_file)
        st.image(img, caption="รูปห้องต้นฉบับ", use_container_width=True)
        
        temp_path = "temp_room.jpg"
        img.save(temp_path)
        
        if st.button("🔍 วิเคราะห์โครงสร้างห้อง"):
            with st.spinner("AI กำลังวิเคราะห์ห้อง..."):
                analysis = analyze_room(temp_path)
                st.session_state['analysis'] = analysis
                # อัปโหลดรูปเพื่อเตรียมส่งให้ Replicate
                st.session_state['current_image_url'] = upload_to_imgbb(temp_path)
                st.success("วิเคราะห์เสร็จสมบูรณ์!")

with col2:
    st.header("2. เลือกสไตล์การตกแต่ง")
    
    if st.session_state['analysis']:
        analysis = st.session_state['analysis']
        
        # แสดงข้อมูลที่วิเคราะห์ได้
        with st.expander("ดูข้อมูลที่ AI วิเคราะห์ได้"):
            st.write(f"**ประเภทห้อง:** {analysis.get('room_type', 'unknown')}")
            st.write(f"**เฟอร์นิเจอร์เดิม:** {', '.join(analysis.get('current_furniture', []))}")
            st.write(f"**โครงสร้าง:** {analysis.get('architectural_features', 'unknown')}")
        
        interior_style = st.selectbox(
            "เลือกสไตล์ที่ต้องการ",
            ["Minimalist", "Modern Luxury", "Industrial", "Scandinavian", "Japanese Zen", "Bohemian"]
        )
        
        custom_prompt = st.text_area("คำแนะนำเพิ่มเติม (ถ้ามี)", placeholder="เช่น 'เน้นสีขาวและไม้', 'เพิ่มต้นไม้เยอะๆ'")
        
        if st.button("✨ เริ่มออกแบบห้องใหม่"):
            with st.spinner("AI กำลังวาดรูปใหม่ (อาจใช้เวลา 30-60 วินาที)..."):
                # สร้าง Prompt
                design_prompt = build_design_prompt(
                    analysis.get("room_type", "room"),
                    interior_style,
                    analysis.get("current_furniture", []),
                    analysis.get("wall_color", "white"),
                    analysis.get("natural_light_direction", "unknown"),
                    custom_prompt
                )
                
                # สร้างรูปภาพ (ส่ง URL รูปต้นฉบับไปด้วยเพื่อทำ Image-to-Image)
                result_image_url = generate_design(design_prompt, st.session_state['current_image_url'])
                
                # สร้างคำแนะนำ
                recommendations = recommend_furniture_and_palette(design_prompt)
                
                st.session_state['result_image'] = result_image_url
                st.session_state['recommendations'] = recommendations
                st.rerun()
    else:
        st.info("กรุณาอัปโหลดรูปภาพและกดปุ่มวิเคราะห์ห้องก่อน")

# --- Results Display ---
if st.session_state['result_image']:
    st.markdown("---")
    st.header("🎨 ผลลัพธ์การออกแบบ")
    
    res_col1, res_col2 = st.columns(2)
    with res_col1:
        st.image(uploaded_file, caption="ห้องเดิม", use_container_width=True)
    with res_col2:
        st.image(st.session_state['result_image'], caption=f"ห้องใหม่สไตล์ {interior_style}", use_container_width=True)
    
    if st.session_state['recommendations']:
        st.markdown('<div class="result-container">', unsafe_allow_html=True)
        st.subheader("💡 คำแนะนำจาก AI Designer")
        st.write(st.session_state['recommendations'])
        st.markdown('</div>', unsafe_allow_html=True)
        
    # ปุ่มดาวน์โหลด
    st.markdown(f'<a href="{st.session_state["result_image"]}" target="_blank"><button style="width:100%; border-radius:8px; height:3em; background-color:#28a745; color:white; font-weight:bold; border:none; cursor:pointer;">📥 ดาวน์โหลดรูปภาพความละเอียดสูง</button></a>', unsafe_allow_html=True)

# Sidebar for Reset
with st.sidebar:
    st.title("Settings")
    if st.button("ล้างข้อมูลและเริ่มใหม่"):
        for key in st.session_state.keys():
            st.session_state[key] = None
        st.rerun()

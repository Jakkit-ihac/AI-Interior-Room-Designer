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
    .analysis-box {
        background-color: #e9ecef;
        padding: 15px;
        border-radius: 8px;
        border-left: 5px solid #007bff;
        margin-bottom: 15px;
    }
    .section-header {
        color: #333;
        border-bottom: 2px solid #007bff;
        padding-bottom: 10px;
        margin-bottom: 20px;
    }
    pre {
        background-color: #2d2d2d;
        color: #f8f8f2;
        padding: 15px;
        border-radius: 8px;
        font-size: 0.9em;
        overflow-x: auto;
    }
    </style>
    """, unsafe_allow_html=True)

# --- Session State Management ---
def init_session():
    if 'analysis' not in st.session_state:
        st.session_state['analysis'] = None
    if 'result_image' not in st.session_state:
        st.session_state['result_image'] = None
    if 'recommendations' not in st.session_state:
        st.session_state['recommendations'] = None
    if 'current_image_url' not in st.session_state:
        st.session_state['current_image_url'] = None
    if 'last_uploaded_file_name' not in st.session_state:
        st.session_state['last_uploaded_file_name'] = None
    if 'image_dims' not in st.session_state:
        st.session_state['image_dims'] = (1024, 768)
    if 'image_bytes' not in st.session_state:
        st.session_state['image_bytes'] = None

init_session()

# --- Helper Function: Upload Image to ImgBB ---
def upload_to_imgbb(image_bytes):
    """
    อัปโหลดรูปภาพไปยัง ImgBB เพื่อรับ URL สาธารณะสำหรับส่งให้ Replicate API
    """
    if not image_bytes:
        return None
    try:
        # ใช้ API Key สาธารณะ (กรุณาเปลี่ยนเป็นของคุณเองเพื่อความเสถียร)
        api_key = "c8798933668868868868868868868868" # Placeholder
        url = "https://api.imgbb.com/1/upload"
        payload = {
            "key": api_key,
            "image": base64.b64encode(image_bytes),
        }
        res = requests.post(url, payload, timeout=15)
        if res.status_code == 200:
            return res.json()["data"]["url"]
    except Exception as e:
        st.error(f"Image upload failed: {e}")
    return None

# --- Main UI ---
st.title("🏠 AI Interior Room Designer")
st.write("วิเคราะห์ห้องแบบละเอียดและออกแบบใหม่โดยรักษาโครงสร้างเดิม 100%")

st.markdown("---")

col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.header("1. อัปโหลดรูปห้อง")
    uploaded_file = st.file_uploader("เลือกรูปภาพห้องของคุณ (JPG, PNG)", type=["jpg", "jpeg", "png"])
    
    if uploaded_file:
        if uploaded_file.name != st.session_state['last_uploaded_file_name']:
            # ล้างสถานะเฉพาะเมื่อเปลี่ยนไฟล์ใหม่จริงๆ
            st.session_state['analysis'] = None
            st.session_state['result_image'] = None
            st.session_state['recommendations'] = None
            st.session_state['current_image_url'] = None
            st.session_state['last_uploaded_file_name'] = uploaded_file.name
            
            # เก็บข้อมูลรูปภาพในรูปแบบ Bytes
            img_bytes = uploaded_file.getvalue()
            st.session_state['image_bytes'] = img_bytes
            
            img = Image.open(io.BytesIO(img_bytes))
            st.session_state['image_dims'] = img.size
    
    if st.session_state['image_bytes']:
        st.image(st.session_state['image_bytes'], caption="รูปห้องต้นฉบับ", use_container_width=True)
        
        room_type_options = ["Living Room", "Bedroom", "Kitchen", "Bathroom", "Office", "Dining Room", "Studio"]
        selected_room_type = st.selectbox("ระบุประเภทห้อง (เพื่อความแม่นยำ)", room_type_options)
        
        if st.button("🔍 เริ่มวิเคราะห์ห้องแบบละเอียด (Deep Analysis)"):
            with st.spinner("AI กำลังวิเคราะห์โครงสร้างห้องแบบละเอียดสูงสุด..."):
                # สร้างไฟล์ชั่วคราวจาก Bytes เพื่อส่งให้ analyze_room
                temp_path = "temp_analysis_image.jpg"
                with open(temp_path, "wb") as f:
                    f.write(st.session_state['image_bytes'])
                
                analysis = analyze_room(temp_path)
                if "room_metadata" in analysis:
                    analysis["room_metadata"]["room_type"] = selected_room_type
                
                st.session_state['analysis'] = analysis
                # อัปโหลดรูปและเก็บ URL ไว้ถาวรใน Session
                st.session_state['current_image_url'] = upload_to_imgbb(st.session_state['image_bytes'])
                st.success("วิเคราะห์เสร็จสมบูรณ์!")

with col2:
    st.header("2. ผลการวิเคราะห์และเลือกสไตล์")
    
    if st.session_state['analysis']:
        analysis = st.session_state['analysis']
        
        st.subheader("📝 รายละเอียดห้องที่ตรวจพบ")
        metadata = analysis.get("room_metadata", {})
        st.markdown(f'<div class="analysis-box"><b>ประเภทห้อง:</b> {metadata.get("room_type", "unknown")} | <b>มุมมอง:</b> {metadata.get("camera_perspective", "unknown")}</div>', unsafe_allow_html=True)
        
        with st.expander("🔍 ดูโครงสร้าง JSON แบบละเอียด (Deep Structural Data)", expanded=False):
            st.json(analysis)
        
        st.markdown("---")
        interior_style = st.selectbox(
            "เลือกสไตล์การออกแบบใหม่",
            ["Minimalist", "Modern Luxury", "Industrial", "Scandinavian", "Japanese Zen", "Bohemian"]
        )
        
        custom_prompt = st.text_area("คำแนะนำเพิ่มเติม (ถ้ามี)", placeholder="เช่น 'เน้นสีขาวและไม้', 'เพิ่มต้นไม้เยอะๆ'")
        
        if st.button("✨ เริ่มออกแบบห้องใหม่"):
            # ตรวจสอบความพร้อมของข้อมูลก่อนเจน
            if not st.session_state['current_image_url']:
                with st.spinner("กำลังเตรียมรูปภาพต้นฉบับ..."):
                    st.session_state['current_image_url'] = upload_to_imgbb(st.session_state['image_bytes'])
            
            if st.session_state['current_image_url']:
                with st.spinner(f"AI กำลังวาดรูปใหม่สไตล์ {interior_style}..."):
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
                    result_image_url = generate_design(design_prompt, st.session_state['current_image_url'], width, height)
                    
                    if result_image_url:
                        st.session_state['result_image'] = result_image_url
                        st.session_state['recommendations'] = recommend_furniture_and_palette(design_prompt)
                        st.rerun()
                    else:
                        st.error("ไม่สามารถสร้างรูปภาพได้ในขณะนี้ กรุณาลองใหม่อีกครั้ง")
            else:
                st.error("ไม่พบรูปภาพต้นฉบับ กรุณากดปุ่มวิเคราะห์ห้องใหม่อีกครั้ง")
    else:
        st.info("กรุณาอัปโหลดรูปภาพและกดปุ่มวิเคราะห์ห้องก่อน")

# --- Results Display ---
if st.session_state['result_image']:
    st.markdown("---")
    st.header("🎨 ผลลัพธ์การออกแบบ")
    
    res_col1, res_col2 = st.columns(2)
    with res_col1:
        if st.session_state['image_bytes']:
            st.image(st.session_state['image_bytes'], caption="ห้องเดิม", use_container_width=True)
    with res_col2:
        st.image(st.session_state['result_image'], caption=f"ห้องใหม่สไตล์ {interior_style}", use_container_width=True)
    
    if st.session_state['recommendations']:
        st.markdown('<div class="result-container">', unsafe_allow_html=True)
        st.subheader("💡 คำแนะนำจาก AI Designer")
        st.write(st.session_state['recommendations'])
        st.markdown('</div>', unsafe_allow_html=True)
        
    st.markdown(f'<a href="{st.session_state["result_image"]}" target="_blank"><button style="width:100%; border-radius:8px; height:3em; background-color:#28a745; color:white; font-weight:bold; border:none; cursor:pointer;">📥 ดาวน์โหลดรูปภาพความละเอียดสูง</button></a>', unsafe_allow_html=True)

# Sidebar for Reset
with st.sidebar:
    st.title("Settings")
    if st.button("ล้างข้อมูลทั้งหมด"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

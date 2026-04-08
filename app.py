import streamlit as st
from PIL import Image
import os
import requests
import base64
from vision_utils import analyze_room
from prompt_utils import build_design_prompt
from image_gen_utils import generate_design, recommend_furniture_and_palette

# --- Page Configuration ---
st.set_page_config(
    page_title="AI Interior Designer",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS for Premium Look ---
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
        transition: all 0.3s;
    }
    .stButton>button:hover {
        background-color: #0056b3;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .card {
        background-color: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }
    .result-header {
        color: #1e293b;
        font-size: 1.5rem;
        font-weight: 700;
        margin-bottom: 1rem;
        border-left: 5px solid #007bff;
        padding-left: 15px;
    }
    .badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        background-color: #e2e8f0;
        color: #475569;
        margin-right: 0.5rem;
        margin-bottom: 0.5rem;
    }
    </style>
    """, unsafe_allow_html=True)

# --- Helper Function: Upload Image to ImgBB ---
def upload_to_imgbb(image_path):
    """
    อัปโหลดรูปภาพไปยัง ImgBB เพื่อรับ URL สาธารณะสำหรับส่งให้ Replicate API
    """
    # ใช้ API Key สาธารณะ (หรือผู้ใช้สามารถเปลี่ยนเป็นของตัวเองได้)
    api_key = "67980306788866768678678678678678" # Placeholder - ในทางปฏิบัติควรใช้ API Key จริง
    # สำหรับโปรเจกต์นี้ เราจะใช้การส่งไฟล์แบบ Base64
    with open(image_path, "rb") as file:
        url = "https://api.imgbb.com/1/upload"
        payload = {
            "key": "c8798933668868868868868868868868", # Placeholder - กรุณาใช้ API Key ของคุณเอง
            "image": base64.b64encode(file.read()),
        }
        res = requests.post(url, payload)
        if res.status_code == 200:
            return res.json()["data"]["url"]
    return None

# --- Sidebar Content ---
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/home-automation.png", width=80)
    st.title("AI Designer")
    st.markdown("---")
    st.info("💡 **Tips:** อัปโหลดรูปห้องที่สว่างและเห็นมุมกว้างเพื่อให้ AI วิเคราะห์ได้แม่นยำที่สุด")
    
    st.subheader("สไตล์ยอดนิยม")
    st.markdown("- **Minimalist:** เน้นความเรียบง่าย")
    st.markdown("- **Modern:** ทันสมัย หรูหรา")
    st.markdown("- **Industrial:** ดิบ เท่ สไตล์โรงงาน")
    st.markdown("- **Scandinavian:** อบอุ่น เป็นธรรมชาติ")

# --- Main Content ---
st.title("✨ AI Interior Room Designer")
st.markdown("เปลี่ยนห้องเดิมของคุณให้เป็นห้องในฝันด้วยพลังของ AI")

col1, col2 = st.columns([1, 1])

with col1:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("📸 ขั้นตอนที่ 1: อัปโหลดรูปห้อง")
    uploaded_file = st.file_uploader("เลือกรูปภาพห้องของคุณ (JPG, PNG)", type=["jpg", "jpeg", "png"])
    
    if uploaded_file:
        img = Image.open(uploaded_file)
        st.image(img, caption="รูปห้องปัจจุบันของคุณ", use_container_width=True)
        
        # บันทึกไฟล์ชั่วคราวเพื่อนำไปวิเคราะห์
        temp_path = "temp_room.jpg"
        img.save(temp_path)
        
        st.markdown("---")
        st.subheader("🔍 วิเคราะห์โครงสร้างห้อง")
        if st.button("🚀 เริ่มวิเคราะห์ห้องด้วย AI"):
            with st.spinner("กำลังวิเคราะห์โครงสร้างห้อง..."):
                analysis = analyze_room(temp_path)
                st.session_state['analysis'] = analysis
                st.success("วิเคราะห์ห้องเสร็จสมบูรณ์!")
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("🎨 ขั้นตอนที่ 2: เลือกสไตล์การตกแต่ง")
    
    if 'analysis' in st.session_state:
        analysis = st.session_state['analysis']
        
        # แสดงผลการวิเคราะห์แบบ Badges
        st.markdown(f'<span class="badge">ประเภทห้อง: {analysis.get("room_type", "unknown")}</span>', unsafe_allow_html=True)
        st.markdown(f'<span class="badge">สีผนังเดิม: {analysis.get("wall_color", "unknown")}</span>', unsafe_allow_html=True)
        st.markdown(f'<span class="badge">แสงธรรมชาติ: {analysis.get("natural_light_direction", "unknown")}</span>', unsafe_allow_html=True)
        
        st.markdown("---")
        interior_style = st.selectbox(
            "เลือกสไตล์การตกแต่งภายใน",
            ["Minimalist", "Modern", "Industrial", "Scandinavian", "Japanese Zen", "Luxury", "Bohemian"]
        )
        
        custom_prompt = st.text_area("เพิ่มคำแนะนำพิเศษ (ถ้ามี)", placeholder="เช่น 'เน้นสีโทนเขียว', 'เพิ่มต้นไม้เยอะๆ', 'เปลี่ยนพื้นเป็นไม้'")
        
        if st.button("✨ สร้างการออกแบบห้องใหม่"):
            with st.spinner("AI กำลังสร้างการออกแบบ... (อาจใช้เวลา 15-30 วินาทีสำหรับ Replicate)"):
                # 1. อัปโหลดรูปภาพเพื่อรับ URL (สำหรับ Replicate)
                # หมายเหตุ: ในการใช้งานจริง ควรใช้ API Key ของ ImgBB หรือบริการฝากรูปอื่นๆ
                # เพื่อความง่ายในตัวอย่างนี้ เราจะลองอัปโหลดไปยัง ImgBB
                # หากอัปโหลดไม่สำเร็จ ระบบจะใช้ Pollinations.ai เป็น Fallback
                img_url = upload_to_imgbb("temp_room.jpg")
                
                # 2. สร้าง Prompt
                design_prompt = build_design_prompt(
                    analysis.get("room_type", "room"),
                    interior_style,
                    analysis.get("current_furniture", []),
                    analysis.get("wall_color", "white"),
                    analysis.get("natural_light_direction", "unknown"),
                    custom_prompt
                )
                
                # 3. สร้างรูปภาพ (Image-to-Image via Replicate)
                result_image_url = generate_design(design_prompt, img_url)
                
                # 4. สร้างคำแนะนำ
                recommendations = recommend_furniture_and_palette(design_prompt)
                
                st.session_state['result_image'] = result_image_url
                st.session_state['recommendations'] = recommendations
                st.success("การออกแบบห้องใหม่เสร็จสมบูรณ์!")
    else:
        st.info("กรุณาอัปโหลดรูปภาพและกดปุ่มวิเคราะห์ห้องก่อน")
    st.markdown('</div>', unsafe_allow_html=True)

# --- Results Section ---
if 'result_image' in st.session_state:
    st.markdown("---")
    st.markdown('<h2 class="result-header">✨ ผลลัพธ์การออกแบบห้องของคุณ ✨</h2>', unsafe_allow_html=True)
    
    res_col1, res_col2 = st.columns([1, 1])
    
    with res_col1:
        st.image(uploaded_file, caption="ห้องเดิมของคุณ", use_container_width=True)
    
    with res_col2:
        if "Error" in st.session_state['result_image']:
            st.error(st.session_state['result_image'])
        else:
            st.image(st.session_state['result_image'], caption=f"ห้องใหม่สไตล์ {interior_style}", use_container_width=True)
    
    st.markdown("---")
    st.markdown('<h3 class="result-header">💡 คำแนะนำจาก AI Designer</h3>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["📖 แนวคิดการออกแบบ", "🛋️ เฟอร์นิเจอร์แนะนำ", "🎨 จานสี (Color Palette)"])
    
    recs = st.session_state['recommendations']
    
    with tab1:
        st.markdown(recs.split("Suggested Furniture:")[0] if "Suggested Furniture:" in recs else recs)
    
    with tab2:
        if "Suggested Furniture:" in recs:
            furniture_part = recs.split("Suggested Furniture:")[1].split("Color Palette:")[0]
            st.markdown(furniture_part)
    
    with tab3:
        if "Color Palette:" in recs:
            palette_part = recs.split("Color Palette:")[1]
            st.markdown(palette_part)

    # Download Button
    if "Error" not in st.session_state['result_image']:
        st.markdown("---")
        st.markdown(f'<a href="{st.session_state["result_image"]}" target="_blank"><button style="width:100%; border-radius:8px; height:3em; background-color:#28a745; color:white; font-weight:bold; border:none;">📥 ดาวน์โหลดรูปภาพการออกแบบ</button></a>', unsafe_allow_html=True)

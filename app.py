import streamlit as st
from PIL import Image
import os
import io

from prompt_utils import build_design_prompt, parse_ai_explanation
from vision_utils import analyze_room
from image_gen_utils import generate_design, recommend_furniture_and_palette

# --- UI Configuration ---
st.set_page_config(
    page_title="AI Interior Designer | ออกแบบห้องในฝัน",
    page_icon="🛋️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS for Premium Look ---
st.markdown("""
    <style>
    /* Main Background & Font */
    .main {
        background-color: #f8f9fa;
    }
    h1, h2, h3 {
        color: #1e293b;
        font-family: 'Inter', sans-serif;
        font-weight: 700;
    }
    
    /* Custom Card Style */
    .stCard {
        background-color: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        margin-bottom: 2rem;
    }
    
    /* Button Styling */
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        height: 3em;
        background-color: #2563eb;
        color: white;
        font-weight: 600;
        border: none;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #1d4ed8;
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(37, 99, 235, 0.3);
    }
    
    /* Sidebar Styling */
    .css-1d391kg {
        background-color: #ffffff;
    }
    
    /* Success Message */
    .stSuccess {
        background-color: #ecfdf5;
        color: #065f46;
        border: 1px solid #10b981;
        border-radius: 10px;
    }
    
    /* Image Styling */
    .stImage > img {
        border-radius: 15px;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    }
    
    /* Badge Style for Analysis */
    .analysis-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        background-color: #e2e8f0;
        border-radius: 9999px;
        font-size: 0.875rem;
        font-weight: 500;
        color: #475569;
        margin-right: 0.5rem;
        margin-bottom: 0.5rem;
    }
    </style>
    """, unsafe_allow_stdio=True, unsafe_allow_html=True)

# --- Sidebar Content ---
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/home-automation.png", width=80)
    st.title("AI Designer")
    st.markdown("---")
    st.info("💡 **Tips:** ถ่ายรูปห้องในมุมกว้างและมีแสงสว่างเพียงพอเพื่อให้ AI วิเคราะห์ได้แม่นยำที่สุด")
    
    st.subheader("สไตล์ยอดนิยม")
    st.write("✨ Minimal")
    st.write("✨ Modern Luxury")
    st.write("✨ Japanese Muji")
    
    st.markdown("---")
    st.caption("Powered by Gemini 2.5 Flash & Pollinations AI")

# --- Header Section ---
col_title, col_logo = st.columns([4, 1])
with col_title:
    st.title("🛋️ AI Interior Room Designer")
    st.markdown("<p style='font-size: 1.2rem; color: #64748b;'>เปลี่ยนห้องเดิมของคุณให้เป็นห้องในฝันด้วยพลังของ AI</p>", unsafe_allow_html=True)

# --- Initialize Session State ---
for key in ['room_analysis', 'image_path', 'redesigned_image_url', 'explanation_text', 'design_recommendations']:
    if key not in st.session_state:
        st.session_state[key] = None

# --- Step 1: Upload & Analysis ---
st.markdown("### 📸 ขั้นตอนที่ 1: อัปโหลดรูปห้องของคุณ")
uploaded_file = st.file_uploader("", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    
    # Save the uploaded image temporarily
    temp_image_path = "temp_room_image.jpg"
    with open(temp_image_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    st.session_state.image_path = temp_image_path

    col_img, col_info = st.columns([1, 1])
    
    with col_img:
        st.image(image, caption="รูปห้องปัจจุบันของคุณ", use_container_width=True)
    
    with col_info:
        st.markdown("#### 🔍 วิเคราะห์โครงสร้างห้อง")
        if st.button("🚀 เริ่มวิเคราะห์ห้องด้วย AI"):
            if "GOOGLE_API_KEY" not in os.environ:
                st.error("กรุณาตั้งค่า GOOGLE_API_KEY ใน Streamlit Secrets")
            else:
                with st.spinner("AI กำลังสแกนห้องของคุณ..."):
                    st.session_state.room_analysis = analyze_room(st.session_state.image_path)
                    st.success("วิเคราะห์ห้องเสร็จสมบูรณ์!")
        
        if st.session_state.room_analysis:
            analysis = st.session_state.room_analysis
            st.markdown(f"**ประเภทห้อง:** `{analysis.get('room_type', 'N/A')}`")
            st.markdown("**เฟอร์นิเจอร์ที่ตรวจพบ:**")
            for item in analysis.get('current_furniture', []):
                st.markdown(f"<span class='analysis-badge'>{item}</span>", unsafe_allow_html=True)
            st.markdown(f"**สีผนังเดิม:** `{analysis.get('wall_color', 'N/A')}`")
            st.markdown(f"**แสงธรรมชาติ:** `{analysis.get('natural_light_direction', 'N/A')}`")

    # --- Step 2: Style Selection ---
    if st.session_state.room_analysis:
        st.markdown("---")
        st.markdown("### 🎨 ขั้นตอนที่ 2: เลือกสไตล์การออกแบบ")
        
        col_style, col_custom = st.columns(2)
        with col_style:
            room_type_options = ["Living Room", "Bedroom", "Kitchen", "Bathroom", "Office", "Dining Room", "Gaming Room"]
            current_type = st.session_state.room_analysis.get("room_type", "Living Room")
            if current_type not in room_type_options:
                room_type_options.insert(0, current_type)
            
            selected_room_type = st.selectbox("ประเภทห้องที่ต้องการออกแบบ", room_type_options)
            selected_style = st.selectbox(
                "เลือกสไตล์การตกแต่งภายใน",
                ("Minimal", "Modern Luxury", "Scandinavian", "Gaming Room", "Japanese Muji", "Industrial", "Bohemian", "Coastal")
            )
        
        with col_custom:
            custom_prompt_input = st.text_area(
                "เพิ่มคำแนะนำพิเศษ (ไม่บังคับ)",
                placeholder="เช่น: 'เน้นโทนสีขาว-ไม้', 'เพิ่มต้นไม้ฟอกอากาศ', 'รักษาตำแหน่งเตียงไว้'",
                height=115
            )

        if st.button("✨ สร้างการออกแบบห้องใหม่"):
            with st.spinner("AI กำลังเนรมิตห้องใหม่ให้คุณ..."):
                # Build design prompt
                design_prompt = build_design_prompt(
                    room_type=selected_room_type,
                    current_furniture=st.session_state.room_analysis.get("current_furniture", []),
                    free_space=st.session_state.room_analysis.get("free_space", "unknown"),
                    wall_color=st.session_state.room_analysis.get("wall_color", "unknown"),
                    natural_light_direction=st.session_state.room_analysis.get("natural_light_direction", "unknown"),
                    interior_style=selected_style,
                    custom_prompt=f"{custom_prompt_input}. Architectural features to maintain: {st.session_state.room_analysis.get('architectural_features', 'none')}"
                )
                
                # Generate redesigned room image
                st.session_state.redesigned_image_url = generate_design(design_prompt)
                # Recommend furniture and color palette
                st.session_state.explanation_text = recommend_furniture_and_palette(design_prompt)
                st.session_state.design_recommendations = parse_ai_explanation(st.session_state.explanation_text)

    # --- Step 3: Results Display ---
    if st.session_state.redesigned_image_url:
        st.markdown("---")
        st.markdown("### ✨ ผลลัพธ์การออกแบบห้องของคุณ")
        
        col_before, col_after = st.columns(2)
        with col_before:
            st.image(image, caption="ห้องเดิมของคุณ", use_container_width=True)
        with col_after:
            st.image(st.session_state.redesigned_image_url, caption=f"ห้องใหม่สไตล์ {selected_style}", use_container_width=True)
        
        st.markdown("#### 💡 คำแนะนำจาก AI Designer")
        
        tab1, tab2, tab3 = st.tabs(["📖 แนวคิดการออกแบบ", "🛋️ เฟอร์นิเจอร์แนะนำ", "🎨 จานสี (Color Palette)"])
        
        with tab1:
            st.write(st.session_state.explanation_text)
            st.markdown("**คำแนะนำการจัดวาง:**")
            for advice in st.session_state.design_recommendations.get("optimized_layout_advice", []):
                st.markdown(f"✅ {advice}")
                
        with tab2:
            cols = st.columns(len(st.session_state.design_recommendations.get("suggested_furniture", [])) or 1)
            for idx, item in enumerate(st.session_state.design_recommendations.get("suggested_furniture", [])):
                with cols[idx % len(cols)]:
                    st.info(f"**{item}**")
                    
        with tab3:
            st.write("โทนสีที่แนะนำสำหรับการตกแต่ง:")
            for color in st.session_state.design_recommendations.get("color_palette", []):
                st.markdown(f"- {color}")
        
        st.markdown("---")
        st.download_button(
            label="📥 ดาวน์โหลดรูปภาพการออกแบบ",
            data=st.session_state.redesigned_image_url,
            file_name="ai_room_design.jpg",
            mime="image/jpeg"
        )

# Clean up temporary image file if it exists
if st.session_state.image_path and os.path.exists(st.session_state.image_path):
    pass

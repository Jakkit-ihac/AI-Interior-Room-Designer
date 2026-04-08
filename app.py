
import streamlit as st
from PIL import Image
import os
import io

from prompt_utils import build_design_prompt, parse_ai_explanation
from vision_utils import analyze_room
from image_gen_utils import generate_design, recommend_furniture_and_palette

# --- UI Configuration ---
st.set_page_config(page_title="AI Interior Room Designer", layout="wide")
st.title("🛋️ AI Interior Room Designer")
st.markdown("อัปโหลดรูปห้องของคุณ เลือกสไตล์ที่ต้องการ แล้วให้ AI ออกแบบห้องในฝันของคุณ!")

# --- Initialize Session State ---
if 'room_analysis' not in st.session_state:
    st.session_state.room_analysis = None
if 'image_path' not in st.session_state:
    st.session_state.image_path = None
if 'redesigned_image_url' not in st.session_state:
    st.session_state.redesigned_image_url = None
if 'explanation_text' not in st.session_state:
    st.session_state.explanation_text = None
if 'design_recommendations' not in st.session_state:
    st.session_state.design_recommendations = None

# --- Main Application Logic ---

# 1. User Upload Room Image
uploaded_file = st.file_uploader("อัปโหลดรูปห้องของคุณ", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Save the uploaded image temporarily
    image = Image.open(uploaded_file)
    st.image(image, caption="รูปห้องของคุณ", use_column_width=True)

    # Create a temporary file to save the image
    temp_image_path = "temp_room_image.jpg"
    with open(temp_image_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    st.session_state.image_path = temp_image_path

    st.subheader("ขั้นตอนที่ 1: วิเคราะห์ห้องของคุณ")
    
    # เพิ่มปุ่มสำหรับส่งข้อมูลเพื่อเริ่มวิเคราะห์
    if st.button("🚀 เริ่มวิเคราะห์ห้องนี้"):
        if "GOOGLE_API_KEY" not in os.environ:
            st.error("กรุณาตั้งค่า GOOGLE_API_KEY ใน Streamlit Secrets")
        else:
            with st.spinner("AI กำลังวิเคราะห์ห้องของคุณ..."):
                st.session_state.room_analysis = analyze_room(st.session_state.image_path)
                st.success("วิเคราะห์ห้องเสร็จสมบูรณ์!")

    # แสดงผลการวิเคราะห์ถ้ามีข้อมูลใน Session State
    if st.session_state.room_analysis:
        st.json(st.session_state.room_analysis)

        # 2. User Selects Interior Style and other options
        st.subheader("ขั้นตอนที่ 2: เลือกสไตล์การออกแบบ")
        col1, col2 = st.columns(2)
        with col1:
            room_type_options = [st.session_state.room_analysis.get("room_type", "unknown"), "Living Room", "Bedroom", "Kitchen", "Bathroom", "Office", "Dining Room", "Gaming Room"]
            selected_room_type = st.selectbox("ประเภทห้อง", list(set(room_type_options)))
            selected_style = st.selectbox(
                "เลือกสไตล์การตกแต่งภายใน",
                ("Minimal", "Modern Luxury", "Scandinavian", "Gaming Room", "Japanese Muji", "Industrial", "Bohemian", "Coastal")
            )
        with col2:
            custom_prompt_input = st.text_area(
                "เพิ่มคำแนะนำพิเศษสำหรับ AI (ไม่บังคับ)",
                placeholder="เช่น: 'คงตำแหน่งเตียงไว้ เพิ่มโต๊ะทำงานใกล้หน้าต่าง'"
            )

        if st.button("✨ สร้างการออกแบบห้องใหม่"):
            st.subheader("ขั้นตอนที่ 3: AI กำลังสร้างการออกแบบ...")
            with st.spinner("AI กำลังสร้าง prompt และออกแบบห้องใหม่..."):
                # Build design prompt
                design_prompt = build_design_prompt(
                    room_type=selected_room_type,
                    current_furniture=st.session_state.room_analysis.get("current_furniture", []),
                    free_space=st.session_state.room_analysis.get("free_space", "unknown"),
                    wall_color=st.session_state.room_analysis.get("wall_color", "unknown"),
                    natural_light_direction=st.session_state.room_analysis.get("natural_light_direction", "unknown"),
                    interior_style=selected_style,
                    custom_prompt=custom_prompt_input
                )
                
                # Generate redesigned room image
                st.session_state.redesigned_image_url = generate_design(design_prompt)

                # Recommend furniture and color palette
                st.session_state.explanation_text = recommend_furniture_and_palette(design_prompt)
                st.session_state.design_recommendations = parse_ai_explanation(st.session_state.explanation_text)

        # แสดงผลลัพธ์การออกแบบถ้ามีข้อมูลใน Session State
        if st.session_state.redesigned_image_url:
            st.success("การออกแบบห้องใหม่เสร็จสมบูรณ์!")
            st.subheader("✨ ผลลัพธ์การออกแบบห้องของคุณ ✨")

            col_before, col_after = st.columns(2)
            with col_before:
                st.image(image, caption="ก่อนออกแบบ", use_column_width=True)
            with col_after:
                st.image(st.session_state.redesigned_image_url, caption="หลังออกแบบ (AI Generated)", use_column_width=True)

            st.subheader("💡 คำอธิบายการออกแบบและคำแนะนำ")
            st.write("**AI Explanation:**")
            st.write(st.session_state.explanation_text)

            st.write("**เฟอร์นิเจอร์แนะนำ:**")
            for item in st.session_state.design_recommendations.get("suggested_furniture", []):
                st.markdown(f"- {item}")

            st.write("**จานสี:**")
            for color in st.session_state.design_recommendations.get("color_palette", []):
                st.markdown(f"- {color}")

            st.write("**คำแนะนำการจัดวางที่เหมาะสม:**")
            for advice in st.session_state.design_recommendations.get("optimized_layout_advice", []):
                st.markdown(f"- {advice}")

            st.markdown(f"**ดาวน์โหลดรูปภาพที่ออกแบบ:** [คลิกที่นี่]({st.session_state.redesigned_image_url})")

            # --- Validation Metrics (Sample) ---
            st.subheader("📊 ตัวชี้วัดการประเมิน (ตัวอย่าง)")
            st.markdown(
                """
                - **คะแนนความพึงพอใจของผู้ใช้:** 4.5/5
                - **ความเกี่ยวข้องของการออกแบบ:** สูง
                - **ลดเวลาในการตัดสินใจ:** 70%
                """
            )

# Clean up temporary image file if it exists
if st.session_state.image_path and os.path.exists(st.session_state.image_path):
    # Keep the file for processing but cleanup could be handled differently if needed
    pass

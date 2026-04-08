
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

# --- Main Application Logic ---

# 1. User Upload Room Image
uploaded_file = st.file_uploader("อัปโหลดรูปห้องของคุณ", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Save the uploaded image temporarily
    image = Image.open(uploaded_file)
    st.image(image, caption="รูปห้องของคุณ", use_column_width=True)

    # Create a temporary file to save the image
    image_path = "temp_room_image.jpg"
    with open(image_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    st.subheader("ขั้นตอนที่ 1: วิเคราะห์ห้องของคุณ")
    with st.spinner("AI กำลังวิเคราะห์ห้องของคุณ..."):
        room_analysis = analyze_room(image_path)
        st.success("วิเคราะห์ห้องเสร็จสมบูรณ์!")
        st.json(room_analysis)

    # 2. User Selects Interior Style and other options
    st.subheader("ขั้นตอนที่ 2: เลือกสไตล์การออกแบบ")
    col1, col2 = st.columns(2)
    with col1:
        room_type_options = [room_analysis.get("room_type", "unknown"), "Living Room", "Bedroom", "Kitchen", "Bathroom", "Office", "Dining Room", "Gaming Room"]
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

    if st.button("สร้างการออกแบบห้องใหม่"):
        if "OPENAI_API_KEY" not in os.environ:
            st.error("กรุณาตั้งค่า OpenAI API Key ใน Environment Variable")
        else:
            st.subheader("ขั้นตอนที่ 3: AI กำลังสร้างการออกแบบ...")
            with st.spinner("AI กำลังสร้าง prompt และออกแบบห้องใหม่..."):
                # Build design prompt
                design_prompt = build_design_prompt(
                    room_type=selected_room_type,
                    current_furniture=room_analysis.get("current_furniture", []),
                    free_space=room_analysis.get("free_space", "unknown"),
                    wall_color=room_analysis.get("wall_color", "unknown"),
                    natural_light_direction=room_analysis.get("natural_light_direction", "unknown"),
                    interior_style=selected_style,
                    custom_prompt=custom_prompt_input
                )
                st.write(f"**AI Design Prompt:** {design_prompt}")

                # Generate redesigned room image
                redesigned_image_url = generate_design(design_prompt)

                # Recommend furniture and color palette
                explanation_text = recommend_furniture_and_palette(design_prompt)
                design_recommendations = parse_ai_explanation(explanation_text)

            if redesigned_image_url:
                st.success("การออกแบบห้องใหม่เสร็จสมบูรณ์!")
                st.subheader("✨ ผลลัพธ์การออกแบบห้องของคุณ ✨")

                col_before, col_after = st.columns(2)
                with col_before:
                    st.image(image, caption="ก่อนออกแบบ", use_column_width=True)
                with col_after:
                    st.image(redesigned_image_url, caption="หลังออกแบบ (AI Generated)", use_column_width=True)

                st.subheader("💡 คำอธิบายการออกแบบและคำแนะนำ")
                st.write("**AI Explanation:**")
                st.write(explanation_text)

                st.write("**เฟอร์นิเจอร์แนะนำ:**")
                for item in design_recommendations.get("suggested_furniture", []):
                    st.markdown(f"- {item}")

                st.write("**จานสี:**")
                for color in design_recommendations.get("color_palette", []):
                    st.markdown(f"- {color}")

                st.write("**คำแนะนำการจัดวางที่เหมาะสม:**")
                for advice in design_recommendations.get("optimized_layout_advice", []):
                    st.markdown(f"- {advice}")

                # Download Button (Placeholder - actual download requires more complex handling for external URLs)
                # For simplicity, we'll just provide the URL for now.
                st.markdown(f"**ดาวน์โหลดรูปภาพที่ออกแบบ:** [คลิกที่นี่]({redesigned_image_url})")

                # --- Validation Metrics (Sample) ---
                st.subheader("📊 ตัวชี้วัดการประเมิน (ตัวอย่าง)")
                st.markdown(
                    """
                    - **คะแนนความพึงพอใจของผู้ใช้:** 4.5/5
                    - **ความเกี่ยวข้องของการออกแบบ:** สูง
                    - **ลดเวลาในการตัดสินใจ:** 70%
                    """
                )
            else:
                st.error("ไม่สามารถสร้างรูปภาพการออกแบบได้ กรุณาลองใหม่อีกครั้ง")

    # Clean up temporary image file
    if os.path.exists(image_path):
        os.remove(image_path)


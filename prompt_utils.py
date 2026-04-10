import json

def build_design_prompt(
    room_type: str,
    interior_style: str,
    furniture_list: list,
    wall_info: str,
    lighting_info: str,
    detailed_narrative: str
) -> str:
    """
    สร้าง prompt สำหรับ AI เพื่อเน้นการเปลี่ยนเฟอร์นิเจอร์และเพิ่มของตกแต่ง (Interior Styling)
    โดยรักษาโครงสร้างห้องเดิม (ผนัง พื้น เพดาน ประตู หน้าต่าง) ไว้ 100% และทำหน้าที่เป็นผู้ช่วยออกแบบส่วนตัว
    """
    
    # สร้างรายละเอียดของเฟอร์นิเจอร์เดิมและตำแหน่ง
    furniture_desc = ", ".join(furniture_list) if furniture_list else "basic furniture"
    
    # สร้าง Prompt ที่เน้นการตกแต่ง (Styling-focused Prompt) และ Structural Anchoring
    # เน้นย้ำเรื่องการรักษาโครงสร้างเดิม (Structural Integrity) และความเป็นผู้ช่วยออกแบบส่วนตัว
    base_prompt = f"Act as a professional interior design assistant. Your task is to redesign a {room_type} in a {interior_style} style. "
    base_prompt += f"The current room is a {room_type} with the following characteristics: {detailed_narrative}. "
    base_prompt += f"Existing furniture includes: {furniture_desc}. "
    
    base_prompt += "STRICTLY PRESERVE THE ORIGINAL ROOM'S ARCHITECTURE AND GEOMETRY: "
    base_prompt += "DO NOT alter the position or structure of walls, windows, doors, floor, or ceiling. "
    base_prompt += "Maintain the exact layout and dimensions of the room. "
    
    base_prompt += f"Your design should focus on replacing existing furniture with new {interior_style} style pieces, ensuring they are placed in the SAME POSITIONS as the original furniture. "
    base_prompt += "Introduce new decorative elements such as: "
    base_prompt += "- Wall art and mirrors that complement the chosen style. "
    base_prompt += "- Indoor plants to add life and freshness. "
    base_prompt += "- Stylish rugs that define zones and add texture. "
    base_prompt += "- Decorative lighting fixtures (e.g., pendant lights, floor lamps, table lamps) to enhance ambiance. "
    base_prompt += f"Update the color palette and textures to perfectly match the {interior_style} aesthetic for this {room_type}. "
    base_prompt += f"The current wall color is {wall_info}. Integrate this or suggest a complementary {interior_style} wall treatment. "
    
    # รายละเอียดแสงและคุณภาพของภาพ (Hyper-Realistic)
    base_prompt += f"Maintain the natural light from {lighting_info}. "
    base_prompt += "The final image should be a high-end architectural photograph, showcasing realistic PBR textures, volumetric lighting, ray-traced reflections, and cinematic color grading. "
    base_prompt += "Render in 8k resolution with a professional interior design portfolio style. "
    base_prompt += "Ensure the generated image is indistinguishable from a real photograph, emphasizing depth, shadow, and material fidelity."

    return base_prompt

def parse_ai_explanation(explanation_text: str) -> dict:
    """
    แยกวิเคราะห์ข้อความอธิบายจาก AI เพื่อดึงข้อมูลเฟอร์นิเจอร์, จานสี และคำแนะนำเค้าโครง
    """
    furniture_list = []
    color_palette = []
    layout_advice = []

    lines = explanation_text.split('\n')
    current_section = None

    for line in lines:
        line = line.strip()
        if not line: continue
        
        if "furniture" in line.lower() or "item" in line.lower():
            current_section = "furniture"
            continue
        elif "color" in line.lower() or "palette" in line.lower():
            current_section = "color"
            continue
        elif "layout" in line.lower() or "advice" in line.lower():
            current_section = "layout"
            continue

        if current_section == "furniture":
            furniture_list.append(line.strip("- *"))
        elif current_section == "color":
            color_palette.append(line.strip("- *"))
        elif current_section == "layout":
            layout_advice.append(line.strip("- *"))

    return {
        "suggested_furniture": furniture_list,
        "color_palette": color_palette,
        "optimized_layout_advice": layout_advice
    }

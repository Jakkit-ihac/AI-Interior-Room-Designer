
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
    โดยรักษาโครงสร้างห้องเดิม (ผนัง พื้น เพดาน ประตู หน้าต่าง) ไว้ 100%
    """
    
    # สร้างรายละเอียดของเฟอร์นิเจอร์เดิมและตำแหน่ง
    furniture_desc = ", ".join(furniture_list) if furniture_list else "basic furniture"
    
    # สร้าง Prompt ที่เน้นการตกแต่ง (Styling-focused Prompt)
    # เน้นย้ำเรื่องการรักษาโครงสร้างเดิม (Structural Integrity)
    base_prompt = f"Professional interior styling and decoration of an existing {room_type} into {interior_style} style. "
    base_prompt += "STRICTLY PRESERVE the original room's architecture: DO NOT move or change walls, windows, doors, floor, or ceiling. "
    base_prompt += f"The current room layout is: {detailed_narrative}. "
    base_prompt += f"Current furniture and positions: {furniture_desc}. "
    
    # คำสั่งหลัก: เปลี่ยนเฟอร์นิเจอร์และเพิ่มของตกแต่ง
    base_prompt += f"TASK: Replace existing furniture with new {interior_style} style pieces in the SAME POSITIONS. "
    base_prompt += "ADD decorative elements: wall art, indoor plants, stylish rugs, and decorative lighting fixtures to enhance the space. "
    base_prompt += f"Update the color palette and textures to match {interior_style} while keeping the room's geometry identical. "
    
    # รายละเอียดแสงและคุณภาพของภาพ
    base_prompt += f"Maintain the natural light from {lighting_info}. "
    base_prompt += "High-end architectural photography, realistic textures, 8k resolution, cinematic lighting, professional interior design portfolio style."

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


import json

def build_design_prompt(
    room_type: str,
    current_furniture: list,
    free_space: str,
    wall_color: str,
    natural_light_direction: str,
    interior_style: str,
    custom_prompt: str = None
) -> str:
    """
    สร้าง prompt สำหรับ AI เพื่อสร้างการออกแบบห้องใหม่ โดยเน้นการรักษาเค้าโครงเดิม (Spatial Layout)
    """
    # สร้างรายละเอียดของเฟอร์นิเจอร์เดิมและตำแหน่ง (ถ้ามีข้อมูล)
    furniture_desc = ", ".join(current_furniture) if current_furniture else "basic furniture"
    
    # สร้าง Prompt ที่เน้นการรีโนเวท (Renovation-focused Prompt)
    # เน้นคำว่า "Renovation" และ "In-place decoration" เพื่อให้ AI ไม่วาดห้องใหม่ทั้งหมด
    base_prompt = f"Interior design renovation of an existing {room_type} into {interior_style} style. "
    base_prompt += f"STRICTLY MAINTAIN the original room's architecture, door/window positions, and floor layout. "
    base_prompt += f"The current setup has {furniture_desc}. "
    base_prompt += f"TASK: Only change the wall colors from {wall_color} to {interior_style} palette, and add decorative elements like plants or art in the existing spaces. "
    base_prompt += f"Keep all existing furniture in their exact current positions but re-style their surfaces. "
    base_prompt += f"Preserve the natural light coming from {natural_light_direction}. "
    base_prompt += "Realistic photo, high quality, 8k, architectural photography, soft cinematic lighting."

    if custom_prompt:
        base_prompt += f" Additional requirements: {custom_prompt}"
        
    return base_prompt

def parse_ai_explanation(explanation_text: str) -> dict:
    """
    แยกวิเคราะห์ข้อความอธิบายจาก AI เพื่อดึงข้อมูลเฟอร์นิเจอร์, จานสี และคำแนะนำเค้าโครง
    """
    # นี่คือตัวอย่างการแยกวิเคราะห์อย่างง่าย อาจต้องใช้ regex หรือการประมวลผลภาษาธรรมชาติที่ซับซ้อนมากขึ้น
    # ขึ้นอยู่กับรูปแบบผลลัพธ์ของ AI
    furniture_list = []
    color_palette = []
    layout_advice = []

    lines = explanation_text.split('\n')
    current_section = None

    for line in lines:
        line = line.strip()
        if line.lower().startswith("suggested furniture:"):
            current_section = "furniture"
            continue
        elif line.lower().startswith("color palette:"):
            current_section = "color"
            continue
        elif line.lower().startswith("optimized layout advice:"):
            current_section = "layout"
            continue

        if current_section == "furniture" and line and not line.lower().startswith("color palette:"):
            furniture_list.append(line.replace("- ", ""))
        elif current_section == "color" and line and not line.lower().startswith("optimized layout advice:"):
            color_palette.append(line.replace("- ", ""))
        elif current_section == "layout" and line:
            layout_advice.append(line)

    return {
        "suggested_furniture": furniture_list,
        "color_palette": color_palette,
        "optimized_layout_advice": layout_advice
    }


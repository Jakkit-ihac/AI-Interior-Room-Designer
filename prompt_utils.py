
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
    สร้าง prompt สำหรับ AI เพื่อสร้างการออกแบบห้องใหม่
    """
    base_prompt = f"""Redesign this {room_type} into a {interior_style} style.
    Current furniture includes: {", ".join(current_furniture)}.
    There is {free_space} free space.
    The current wall color is {wall_color}.
    Natural light comes from the {natural_light_direction}.
    """

    if custom_prompt:
        base_prompt += f" {custom_prompt}"

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


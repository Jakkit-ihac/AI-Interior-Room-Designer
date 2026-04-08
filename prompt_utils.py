
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
    
    # สร้าง Prompt ที่เน้นโครงสร้าง (Structural-focused Prompt)
    base_prompt = f"Professional interior design photography of a {room_type} redesigned in {interior_style} style. "
    base_prompt += f"CRITICAL: Maintain the exact same architectural layout, wall positions, and spatial structure of the original room. "
    base_prompt += f"The room currently has {furniture_desc}. "
    base_prompt += f"Keep the main furniture in their original positions but upgrade them to match the {interior_style} aesthetic. "
    base_prompt += f"The wall color should be updated from {wall_color} to a palette suitable for {interior_style}. "
    base_prompt += f"Natural light from {natural_light_direction} must be preserved. "
    base_prompt += "High quality, 8k resolution, photorealistic, architectural digest style, cinematic lighting."

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



import os
import google.generativeai as genai
from PIL import Image
import json

def analyze_room(image_path: str) -> dict:
    """
    ใช้ Google Gemini 2.0 Flash เพื่อวิเคราะห์รูปภาพห้องและดึงข้อมูลที่เกี่ยวข้อง
    """
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        return {
            "room_type": "error",
            "current_furniture": ["Please set GOOGLE_API_KEY"],
            "free_space": "unknown",
            "wall_color": "unknown",
            "natural_light_direction": "unknown"
        }

    genai.configure(api_key=api_key)
    # ใช้โมเดล gemini-2.0-flash ล่าสุด
    model = genai.GenerativeModel("gemini-2.0-flash")

    prompt = """
    Analyze this room image. Identify:
    1. Room type (e.g., Living Room, Bedroom, etc.)
    2. List of existing furniture
    3. Approximate free space (e.g., 'a lot', 'some', 'limited')
    4. Dominant wall color
    5. Natural light direction (e.g., 'from the left', 'from the right', 'overhead', 'none')

    Provide the output strictly in a valid JSON format like:
    {
        "room_type": "",
        "current_furniture": [],
        "free_space": "",
        "wall_color": "",
        "natural_light_direction": ""
    }
    """

    try:
        img = Image.open(image_path)
        response = model.generate_content([prompt, img])
        
        # Extract JSON from the response text
        text_response = response.text
        if "```json" in text_response:
            text_response = text_response.split("```json")[1].split("```")[0].strip()
        elif "```" in text_response:
            text_response = text_response.split("```")[1].split("```")[0].strip()
        
        return json.loads(text_response)
    except Exception as e:
        print(f"Error in analyze_room: {e}")
        return {
            "room_type": "unknown",
            "current_furniture": [],
            "free_space": "unknown",
            "wall_color": "unknown",
            "natural_light_direction": "unknown"
        }

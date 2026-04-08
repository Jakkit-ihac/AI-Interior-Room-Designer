import os
import google.generativeai as genai
from PIL import Image
import json
import re
import requests
import urllib.parse

def analyze_room(image_path: str) -> dict:
    """
    ใช้ Google Gemini 2.5 Flash เพื่อวิเคราะห์รูปภาพห้องแบบละเอียดสูงสุด (Deep Vision Analysis)
    หาก Gemini ใช้งานไม่ได้ (เช่น Error 403) จะใช้ระบบวิเคราะห์พื้นฐานแทน
    """
    api_key = os.environ.get("GOOGLE_API_KEY")
    
    # ข้อมูลพื้นฐานสำหรับกรณีที่ AI ทั้งหมดใช้งานไม่ได้
    default_response = {
        "room_type": "Living Room",
        "current_furniture": ["Sofa", "Table", "Chair"],
        "free_space": "Moderate amount of floor space available.",
        "wall_color_and_texture": "White painted walls",
        "natural_light_and_lighting": "Standard indoor lighting",
        "architectural_features": "Standard rectangular room structure",
        "detailed_description": "A standard room with basic furniture and layout. (Note: Deep analysis is currently unavailable, using default description)",
        "spatial_layout_analysis": "Standard layout with furniture placed along the walls."
    }
    
    if not api_key:
        return default_response

    try:
        genai.configure(api_key=api_key)
        # ใช้โมเดล gemini-2.5-flash ล่าสุดเพื่อความแม่นยำสูงสุด
        model = genai.GenerativeModel("gemini-2.5-flash")

        prompt = """
        As an expert interior architect and vision AI, analyze this room image with extreme precision. 
        I need a comprehensive breakdown of EVERYTHING in the room to ensure the redesign maintains the exact structural integrity.
        
        Please identify and describe in detail:
        1. Room Type: Primary function of the space.
        2. Furniture Inventory & Mapping: List every piece of furniture, its style, material, and EXACT coordinate-like position (e.g., 'Large wooden bed occupies the center-back area', 'Black office chair at the bottom-right corner').
        3. Architectural DNA: Describe walls, floor material (e.g., 'white ceramic tiles'), ceiling type, and any fixed elements like doors, windows, or pillars with their exact locations.
        4. Lighting & Atmosphere: Direction of natural light, types of artificial lights present, and the current 'mood' of the room.
        5. Spatial Geometry: A narrative description of the room's shape, dimensions, and how objects are distributed.
        6. Clutter & Usage: Identify areas with many small items or specific usage zones (e.g., 'music corner with a keyboard on the left').

        Provide the output strictly in a valid JSON format like:
        {
            "room_type": "string",
            "current_furniture": ["item 1 with position", "item 2 with position"],
            "free_space": "string description",
            "wall_color_and_texture": "string",
            "natural_light_and_lighting": "string",
            "architectural_features": "string",
            "detailed_description": "A very long, detailed paragraph describing every detail of the room as if explaining it to a blind person.",
            "spatial_layout_analysis": "A technical description of the room's geometry and object placement."
        }
        Do not include any other text or explanation outside the JSON.
        """

        img = Image.open(image_path)
        response = model.generate_content([prompt, img])
        
        # Extract JSON from the response text using Regex for better stability
        text_response = response.text
        json_match = re.search(r'\{.*\}', text_response, re.DOTALL)
        
        if json_match:
            json_str = json_match.group(0)
            return json.loads(json_str)
        else:
            return default_response
            
    except Exception as e:
        print(f"Error in analyze_room: {e}")
        # หากเกิด Error 403 หรือปัญหาอื่นๆ ให้ส่งค่า Default กลับไปเพื่อให้แอปทำงานต่อได้
        return default_response

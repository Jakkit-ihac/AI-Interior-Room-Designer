import os
import google.generativeai as genai
from PIL import Image
import json
import re
import requests
import urllib.parse
import io

def analyze_room(image_input) -> dict:
    """
    ใช้ Google Gemini 2.5 Flash เพื่อวิเคราะห์รูปภาพห้องแบบละเอียดสูงสุด (Deep Structural Analysis)
    รองรับทั้ง image_path (str) และ PIL Image object
    """
    # ใช้ API Key ที่ผู้ใช้ระบุ หรือดึงจาก Environment Variable
    api_key = os.environ.get("GOOGLE_API_KEY")
    
    # ข้อมูลพื้นฐานสำหรับกรณีที่ AI ทั้งหมดใช้งานไม่ได้
    default_response = {
        "room_metadata": {
            "room_type": "Living Room",
            "estimated_dimensions": "Standard size",
            "camera_perspective": "Eye-level, wide angle"
        },
        "structural_elements": {
            "walls": "White painted walls",
            "floor": "Standard flooring",
            "ceiling": "Flat white ceiling",
            "fixed_features": ["Door", "Window"]
        },
        "furniture_mapping": [
            {"item": "Sofa", "position": "Center", "style": "Modern"},
            {"item": "Table", "position": "Front of sofa", "style": "Minimalist"}
        ],
        "lighting_and_atmosphere": {
            "natural_light": "Standard",
            "artificial_light": "Ceiling lights",
            "mood": "Neutral"
        },
        "spatial_geometry": {
            "corners_detected": "4 main corners",
            "focal_point": "Center of the room",
            "clutter_level": "Low"
        },
        "detailed_narrative": "A standard room with basic furniture and layout. (Note: Deep analysis is currently unavailable, using default description)"
    }
    
    if not api_key:
        return default_response

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.5-flash")

        prompt = """
        As an expert interior architect and vision AI, perform a DEEP STRUCTURAL ANALYSIS of this room. 
        Your goal is to create a digital twin blueprint in JSON format to ensure 100% structural preservation during redesign.

        Analyze and provide the following in a STRICT JSON format:
        1. room_metadata: Type, estimated dimensions (width/length/height ratio), and camera perspective (e.g., 'low-angle looking up', 'wide-angle from corner').
        2. structural_elements: Detailed description of walls (color/texture), floor (material/pattern), ceiling (type/features), and EXACT locations of fixed elements like doors, windows, pillars, or built-in cabinets.
        3. furniture_mapping: A list of objects. For each object, specify: 'item', 'style', 'material', and 'position' using a 3x3 grid reference (e.g., 'Top-Left', 'Center-Bottom', 'Back-Right').
        4. lighting_and_atmosphere: Direction and intensity of natural light, types of artificial light sources, and the current color temperature/mood.
        5. spatial_geometry: Identify the room's corners, focal point, and any unique architectural angles or slopes.
        6. detailed_narrative: A technical, highly descriptive paragraph explaining the room's layout as if for a 3D modeler.

        Output MUST be ONLY the JSON object. No markdown formatting, no preamble.
        {
            "room_metadata": { ... },
            "structural_elements": { ... },
            "furniture_mapping": [ { ... }, ... ],
            "lighting_and_atmosphere": { ... },
            "spatial_geometry": { ... },
            "detailed_narrative": "..."
        }
        """

        # รองรับทั้ง path และ PIL Image
        if isinstance(image_input, str):
            img = Image.open(image_input)
        else:
            img = image_input
            
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
        return default_response

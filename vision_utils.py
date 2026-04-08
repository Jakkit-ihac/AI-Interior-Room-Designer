import os
import google.generativeai as genai
from PIL import Image
import json
import re

def analyze_room(image_path: str) -> dict:
    """
    ใช้ Google Gemini 1.5 Flash เพื่อวิเคราะห์รูปภาพห้องและดึงข้อมูลที่เกี่ยวข้อง
    """
    api_key = os.environ.get("GOOGLE_API_KEY")
    default_response = {
        "room_type": "Living Room",
        "current_furniture": ["furniture"],
        "free_space": "some",
        "wall_color": "white",
        "natural_light_direction": "unknown",
        "architectural_features": "standard room"
    }
    
    if not api_key:
        return default_response

    try:
        genai.configure(api_key=api_key)
        # ใช้โมเดล gemini-1.5-flash ที่เสถียรกว่าในการวิเคราะห์ภาพ
        model = genai.GenerativeModel("gemini-1.5-flash")

        prompt = """
        Analyze this room image in detail for an interior design task. Identify:
        1. Room type (e.g., Living Room, Bedroom, etc.)
        2. List of existing furniture with their relative positions (e.g., 'bed in the center', 'desk on the left')
        3. Approximate free space (e.g., 'a lot', 'some', 'limited')
        4. Dominant wall color and texture
        5. Natural light direction and source (e.g., 'large window on the right')
        6. Key architectural features (e.g., 'slanted ceiling', 'door on the back wall')

        Provide the output strictly in a valid JSON format like:
        {
            "room_type": "string",
            "current_furniture": ["string", "string"],
            "free_space": "string",
            "wall_color": "string",
            "natural_light_direction": "string",
            "architectural_features": "string"
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
            # Fallback if no JSON found
            print(f"No JSON found in response: {text_response}")
            return default_response
            
    except Exception as e:
        print(f"Error in analyze_room: {e}")
        return default_response

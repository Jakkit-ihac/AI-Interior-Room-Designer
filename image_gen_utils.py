import os
import google.generativeai as genai
import urllib.parse
import random

def generate_design(design_prompt: str) -> str:
    """
    สร้างรูปภาพการออกแบบห้องใหม่โดยใช้ AI Image Generation (Pollinations.ai)
    """
    # ใช้ urllib.parse.quote เพื่อจัดการอักขระพิเศษให้ถูกต้องตามมาตรฐาน URL
    encoded_prompt = urllib.parse.quote(design_prompt)
    
    # สุ่มค่า seed เพื่อให้การสร้างรูปภาพมีความหลากหลายในแต่ละครั้ง
    seed = random.randint(1, 1000000)
    
    # ใช้โดเมน image.pollinations.ai/prompt/ เพื่อดึงไฟล์รูปภาพโดยตรง (Direct Image File)
    image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=768&seed={seed}&model=flux"
    return image_url

def recommend_furniture_and_palette(design_prompt: str) -> str:
    """
    ใช้ Google Gemini เพื่ออธิบายการออกแบบและแนะนำเฟอร์นิเจอร์
    """
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        return "Error: Please set GOOGLE_API_KEY in Streamlit Secrets."

    try:
        genai.configure(api_key=api_key)
        
        # ใช้ gemini-1.5-flash เป็นหลักเพื่อความเสถียรสูงสุดในปัจจุบัน
        # เนื่องจาก gemini-2.5-flash อาจยังไม่เปิดให้เรียกใช้ผ่าน SDK ในบางพื้นที่
        model = genai.GenerativeModel("gemini-1.5-flash")

        prompt = f"""
        You are an AI interior designer. Based on this interior design prompt: "{design_prompt}"
        
        Please provide:
        1. A brief explanation of the design concept.
        2. A list of 3-5 suggested furniture items or decor pieces.
        3. A suggested color palette (hex codes or descriptive names).
        4. Optimized layout advice for the room.

        Format your response clearly with sections for:
        - Explanation: [Brief text]
        - Suggested Furniture: [Item 1, Item 2, Item 3]
        - Color Palette: [Color 1, Color 2, Color 3]
        - Optimized Layout Advice: [Point 1, Point 2]
        """

        response = model.generate_content(prompt)
        
        if response and response.text:
            return response.text
        else:
            return "Error: Gemini returned an empty response. Please try again."
            
    except Exception as e:
        error_msg = str(e)
        print(f"Error in recommend_furniture_and_palette: {error_msg}")
        return f"Error generating recommendations: {error_msg}. Please check your API Key and connection."

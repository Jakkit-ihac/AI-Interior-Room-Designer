
import os
import google.generativeai as genai
import urllib.parse
import random

def generate_design(design_prompt: str) -> str:
    """
    สร้างรูปภาพการออกแบบห้องใหม่โดยใช้ AI Image Generation (Pollinations.ai)
    """
    # ในโปรเจกต์นี้ เราจะใช้ Pollinations.ai ซึ่งเป็นบริการสร้างรูปภาพฟรีจาก Text
    # เพื่อให้แอปพลิเคชันทำงานได้โดยไม่ต้องใช้ OpenAI API Key
    # ใช้ urllib.parse.quote เพื่อจัดการอักขระพิเศษให้ถูกต้องตามมาตรฐาน URL
    encoded_prompt = urllib.parse.quote(design_prompt)
    
    # สุ่มค่า seed เพื่อให้การสร้างรูปภาพมีความหลากหลายในแต่ละครั้ง
    seed = random.randint(1, 1000000)
    
    # ใช้โดเมน image.pollinations.ai/prompt/ เพื่อดึงไฟล์รูปภาพโดยตรง (Direct Image File)
    # วิธีนี้จะเสถียรกว่าการใช้ /p/ path ซึ่งบางครั้งอาจส่งกลับมาเป็นหน้า HTML
    image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=768&seed={seed}&model=flux"
    return image_url

def recommend_furniture_and_palette(design_prompt: str) -> str:
    """
    ใช้ Google Gemini 2.5 Flash เพื่ออธิบายการออกแบบและแนะนำเฟอร์นิเจอร์
    """
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        return "Please set GOOGLE_API_KEY in Streamlit Secrets to get design recommendations."

    genai.configure(api_key=api_key)
    # ใช้โมเดล gemini-2.5-flash ล่าสุดเพื่อประสิทธิภาพสูงสุด
    model = genai.GenerativeModel("gemini-2.5-flash")

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

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Error in recommend_furniture_and_palette: {e}")
        return "Could not generate recommendations at this time."

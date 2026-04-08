
import os
import google.generativeai as genai

def generate_design(design_prompt: str) -> str:
    """
    สร้างรูปภาพการออกแบบห้องใหม่โดยใช้ AI Image Generation (Pollinations.ai)
    """
    # ในโปรเจกต์นี้ เราจะใช้ Pollinations.ai ซึ่งเป็นบริการสร้างรูปภาพฟรีจาก Text
    # เพื่อให้แอปพลิเคชันทำงานได้โดยไม่ต้องใช้ OpenAI API Key
    encoded_prompt = design_prompt.replace(" ", "%20")
    image_url = f"https://pollinations.ai/p/{encoded_prompt}?width=1024&height=768&seed=42&model=flux"
    return image_url

def recommend_furniture_and_palette(design_prompt: str) -> str:
    """
    ใช้ Google Gemini 2.0 Flash เพื่ออธิบายการออกแบบและแนะนำเฟอร์นิเจอร์
    """
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        return "Please set GOOGLE_API_KEY in Streamlit Secrets to get design recommendations."

    genai.configure(api_key=api_key)
    # ใช้โมเดล gemini-2.0-flash ล่าสุด
    model = genai.GenerativeModel("gemini-2.0-flash")

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

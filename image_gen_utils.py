import os
import google.generativeai as genai
import requests
import time
import random
import urllib.parse

def generate_design(design_prompt: str, image_url: str = None, width: int = 1024, height: int = 768) -> str:
    """
    สร้างรูปภาพการออกแบบห้องใหม่โดยใช้ Replicate API (ControlNet Canny)
    เพื่อรักษาโครงสร้างห้องเดิม (Structural Preservation) 100%
    และรักษาสัดส่วนภาพ (Aspect Ratio) ให้เท่ากับรูปต้นฉบับ
    """
    replicate_api_token = os.environ.get("REPLICATE_API_TOKEN")
    
    # ปรับขนาดภาพให้เหมาะสมกับโมเดล (SDXL ทำงานได้ดีที่ประมาณ 1024px)
    # แต่ยังคงสัดส่วนเดิมไว้
    max_dim = 1024
    if width > height:
        new_width = max_dim
        new_height = int((height / width) * max_dim)
    else:
        new_height = max_dim
        new_width = int((width / height) * max_dim)
    
    # ปรับให้หารด้วย 8 ลงตัว (ข้อกำหนดของโมเดลส่วนใหญ่)
    new_width = (new_width // 8) * 8
    new_height = (new_height // 8) * 8

    # หากไม่มี Token หรือไม่มีรูปภาพต้นฉบับ ให้กลับไปใช้ Pollinations.ai เป็นทางเลือกสำรอง (Fallback)
    if not replicate_api_token or not image_url:
        encoded_prompt = urllib.parse.quote(design_prompt)
        seed = random.randint(1, 1000000)
        return f"https://image.pollinations.ai/prompt/{encoded_prompt}?width={new_width}&height={new_height}&seed={seed}&model=flux"

    # ใช้โมเดล ControlNet Canny (SDXL) ที่รักษาเส้นโครงสร้างได้แม่นยำที่สุด
    model_id = "lucataco/controlnet-canny-sdxl:06d718b34f2142a3583d33967a99a209b9c2800291931057d25f9a21d78266ac"
    
    headers = {
        "Authorization": f"Token {replicate_api_token}",
        "Content-Type": "application/json"
    }

    payload = {
        "version": "06d718b34f2142a3583d33967a99a209b9c2800291931057d25f9a21d78266ac",
        "input": {
            "image": image_url,
            "prompt": f"Professional interior design, {design_prompt}, high quality, realistic, 8k, architectural photography, clean lines, sharp focus",
            "negative_prompt": "low quality, blurry, distorted, messy, bad proportions, changed room structure, moved walls, changed window position, changed door position, changed floor layout, noise, grainy, artifacts",
            "num_inference_steps": 35, # เพิ่มขั้นตอนเพื่อให้ภาพเนียนขึ้น
            "controlnet_conditioning_scale": 0.85, # ปรับลดลงมาที่ 0.85 เพื่อลดปัญหาภาพแตก (Distortion) แต่ยังรักษาโครงสร้างได้ดี
            "guidance_scale": 7.5,
            "width": new_width,
            "height": new_height
        }
    }

    try:
        response = requests.post(
            "https://api.replicate.com/v1/predictions",
            headers=headers,
            json=payload,
            timeout=15
        )
        prediction = response.json()
        
        if "urls" not in prediction:
            return generate_design(design_prompt, None, width, height)
            
        get_url = prediction["urls"]["get"]

        start_time = time.time()
        while time.time() - start_time < 60:
            res = requests.get(get_url, headers=headers, timeout=10)
            res_json = res.json()
            status = res_json["status"]
            
            if status == "succeeded":
                output = res_json.get("output")
                if isinstance(output, list):
                    return output[-1]
                return output
            elif status == "failed":
                return generate_design(design_prompt, None, width, height)
            
            time.sleep(3)
            
        return generate_design(design_prompt, None, width, height)

    except Exception as e:
        print(f"Replicate Error: {e}")
        return generate_design(design_prompt, None, width, height)

def recommend_furniture_and_palette(design_prompt: str) -> str:
    """
    ใช้ Google Gemini 2.5 Flash เพื่ออธิบายการออกแบบและแนะนำเฟอร์นิเจอร์
    หาก Gemini ใช้งานไม่ได้ (เช่น Error 403) จะใช้ Pollinations.ai (Text) เป็นทางเลือกสำรอง
    """
    api_key = os.environ.get("GOOGLE_API_KEY")
    
    prompt_text = f"""
    You are a professional interior designer. Based on this design concept: "{design_prompt}"
    
    Please provide:
    1. A brief explanation of the design concept.
    2. A list of 3-5 specific furniture items or decor pieces that fit this style.
    3. A suggested color palette (with hex codes).
    4. Practical layout advice to improve the room's flow.

    Format your response clearly with sections:
    - Design Concept: [Text]
    - Suggested Furniture: [Item 1, Item 2, Item 3]
    - Color Palette: [Color 1, Color 2, Color 3]
    - Layout Advice: [Point 1, Point 2]
    """

    # ลองใช้ Gemini ก่อน
    if api_key:
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-2.5-flash")
            response = model.generate_content(prompt_text)
            if response and response.text:
                return response.text
        except Exception as e:
            print(f"Gemini Error: {e}")

    # Fallback: ใช้ Pollinations.ai (Text API)
    try:
        encoded_prompt = urllib.parse.quote(prompt_text)
        url = f"https://text.pollinations.ai/{encoded_prompt}"
        res = requests.get(url, timeout=15)
        if res.status_code == 200:
            return res.text + "\n\n(Note: Generated using fallback AI engine)"
    except Exception as e:
        print(f"Pollinations Text Error: {e}")

    return "Sorry, I couldn't generate recommendations at this time. Please check your API settings."

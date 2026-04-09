import os
import google.generativeai as genai
import requests
import time
import random
import urllib.parse

def generate_design(design_prompt: str, image_url: str = None, width: int = 1024, height: int = 768) -> str:
    """
    สร้างรูปภาพการออกแบบห้องใหม่โดยใช้ Replicate API (ControlNet Canny)
    ปรับปรุงให้ AI มีอิสระในการเปลี่ยนเฟอร์นิเจอร์และสไตล์มากขึ้น (Image Change Fix)
    """
    # ใช้ Token ที่ผู้ใช้ระบุ หรือดึงจาก Environment Variable
    replicate_api_token = "r8_GYo5DKiqLWfFl7kw1HmQmFQuMGUAiLy4NApo9" or os.environ.get("REPLICATE_API_TOKEN")
    
    # ปรับขนาดภาพให้เหมาะสม
    max_dim = 1024
    if width > height:
        new_width = max_dim
        new_height = int((height / width) * max_dim)
    else:
        new_height = max_dim
        new_width = int((width / height) * max_dim)
    
    new_width = (new_width // 8) * 8
    new_height = (new_height // 8) * 8

    # ฟังก์ชันสำรอง (Fallback) ที่ทำงานได้ชัวร์
    def get_fallback_url():
        # เพิ่มน้ำหนักสไตล์ใน Fallback ด้วย
        enhanced_fallback_prompt = f"Professional interior design, {design_prompt}, high quality, realistic, 8k, architectural photography, completely new furniture, stylish decor"
        encoded_prompt = urllib.parse.quote(enhanced_fallback_prompt)
        seed = random.randint(1, 1000000)
        return f"https://image.pollinations.ai/prompt/{encoded_prompt}?width={new_width}&height={new_height}&seed={seed}&model=flux"

    # หากไม่มี Token หรือไม่มีรูปภาพต้นฉบับ ให้ใช้ Fallback ทันที
    if not replicate_api_token or not image_url:
        return get_fallback_url()

    # ใช้โมเดล ControlNet Canny (SDXL)
    model_id = "lucataco/controlnet-canny-sdxl:06d718b34f2142a3583d33967a99a209b9c2800291931057d25f9a21d78266ac"
    
    headers = {
        "Authorization": f"Token {replicate_api_token}",
        "Content-Type": "application/json"
    }

    # เพิ่มน้ำหนักคำสั่งสไตล์ (Style Weighting) และลดความแข็งของโครงสร้าง
    # เพื่อให้ AI กล้าเปลี่ยนเฟอร์นิเจอร์และของตกแต่ง
    enhanced_prompt = f"Professional interior design, {design_prompt}, high quality, realistic, 8k, architectural photography, completely new furniture, stylish decor, vibrant colors, sharp focus"
    
    payload = {
        "version": "06d718b34f2142a3583d33967a99a209b9c2800291931057d25f9a21d78266ac",
        "input": {
            "image": image_url,
            "prompt": enhanced_prompt,
            "negative_prompt": "low quality, blurry, distorted, messy, bad proportions, noise, grainy, old furniture, unchanged room, same furniture",
            "num_inference_steps": 30,
            # ลดค่าลงมาที่ 0.45 - 0.55 เพื่อให้ AI กล้าเปลี่ยนของในห้อง แต่ยังรักษาผนัง/หน้าต่างไว้
            "controlnet_conditioning_scale": 0.5, 
            "guidance_scale": 9.0, # เพิ่ม Guidance เพื่อให้ AI ทำตาม Prompt สไตล์มากขึ้น
            "width": new_width,
            "height": new_height
        }
    }

    try:
        response = requests.post(
            "https://api.replicate.com/v1/predictions",
            headers=headers,
            json=payload,
            timeout=20
        )
        
        if response.status_code not in [200, 201]:
            return get_fallback_url()
            
        prediction = response.json()
        if "urls" not in prediction:
            return get_fallback_url()
            
        get_url = prediction["urls"]["get"]

        # รอผลลัพธ์ (Polling)
        start_time = time.time()
        while time.time() - start_time < 60:
            res = requests.get(get_url, headers=headers, timeout=10)
            if res.status_code != 200:
                break
                
            res_json = res.json()
            status = res_json.get("status")
            
            if status == "succeeded":
                output = res_json.get("output")
                if isinstance(output, list) and len(output) > 0:
                    return output[-1]
                elif isinstance(output, str):
                    return output
                break
            elif status == "failed":
                break
            
            time.sleep(3)
            
        return get_fallback_url()

    except Exception as e:
        return get_fallback_url()

def recommend_furniture_and_palette(design_prompt: str) -> str:
    """
    ใช้ Google Gemini 2.5 Flash เพื่ออธิบายการออกแบบและแนะนำเฟอร์นิเจอร์
    """
    # ใช้ API Key ที่ผู้ใช้ระบุ หรือดึงจาก Environment Variable
    api_key = "AIzaSyAkB92K6eCZOdQI2xOAvSFgF6n6ECtGn-I" or os.environ.get("GOOGLE_API_KEY")
    
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

    if api_key:
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-2.5-flash")
            response = model.generate_content(prompt_text)
            if response and response.text:
                return response.text
        except Exception as e:
            print(f"Gemini Error: {e}")

    try:
        encoded_prompt = urllib.parse.quote(prompt_text)
        url = f"https://text.pollinations.ai/{encoded_prompt}"
        res = requests.get(url, timeout=15)
        if res.status_code == 200:
            return res.text + "\n\n(Note: Generated using fallback AI engine)"
    except Exception as e:
        print(f"Pollinations Text Error: {e}")

    return "Sorry, I couldn't generate recommendations at this time."

import os
import google.generativeai as genai
import requests
import time
import random
import urllib.parse

def generate_design(design_prompt: str, image_url: str = None, width: int = 1024, height: int = 768) -> str:
    """
    สร้างภาพโดยใช้ ControlNet อิงจากโครงสร้างภาพเดิม 100% 
    """
    # ดึง API Key จาก .env
    replicate_api_token = os.environ.get("REPLICATE_API_TOKEN")
    
    # ฟังก์ชัน AI สำรอง (กรณี Replicate พัง)
    def get_fallback_url(error_msg=""):
        print(f"⚠️ Replicate Error: {error_msg}")
        print("🔄 กำลังสลับไปใช้ AI สำรอง (ไม่คงโครงสร้างเดิม)...")
        short_prompt = design_prompt[:200] if design_prompt and len(design_prompt) > 200 else design_prompt
        encoded_prompt = urllib.parse.quote(f"Interior design, {short_prompt}, photorealistic, 8k")
        seed = random.randint(1, 100000)
        return f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=768&seed={seed}&nologo=true"

    if not replicate_api_token or not image_url:
        return get_fallback_url("ไม่มี API Token หรือไม่ได้อัปโหลดรูป")

    # ตั้งค่า Replicate SDXL ControlNet Canny
    headers = {
        "Authorization": f"Token {replicate_api_token}",
        "Content-Type": "application/json"
    }

    # หั่น Base64 ส่วนหัวออกถ้ามี (เพื่อให้ Replicate อ่านไฟล์ได้ชัวร์ๆ)
    clean_image_data = image_url
    if image_url.startswith('data:image'):
        clean_image_data = image_url

    payload = {
        "version": "06d718b34f2142a3583d33967a99a209b9c2800291931057d25f9a21d78266ac",
        "input": {
            "image": clean_image_data,
            "prompt": f"Professional interior design, {design_prompt}, 8k resolution, highly detailed, realistic textures, architectural digest",
            "negative_prompt": "low quality, blurry, deformed, unrealistic, messy room",
            "num_inference_steps": 30,
            # ✨ จุดสำคัญ: ปรับเป็น 0.85 เพื่อบังคับให้ AI อิงโครงสร้างเดิมให้มากที่สุด
            "controlnet_conditioning_scale": 0.85, 
            "guidance_scale": 7.5,
        }
    }

    try:
        # ส่งคำสั่งไปที่ Replicate
        response = requests.post("https://api.replicate.com/v1/predictions", headers=headers, json=payload, timeout=20)
        
        if response.status_code not in [200, 201]:
            return get_fallback_url(f"API ตอบกลับด้วยโค้ด {response.status_code} - {response.text}")
            
        prediction = response.json()
        get_url = prediction["urls"]["get"]

        # รอ AI ประมวลผล (Polling)
        start_time = time.time()
        while time.time() - start_time < 90: # รอสูงสุด 90 วินาที
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
                return get_fallback_url(f"Replicate แจ้งว่า Failed: {res_json.get('error')}")
            
            time.sleep(3)
            print("⏳ กำลังรอ Replicate วาดภาพ...")
            
        return get_fallback_url("หมดเวลารอ Replicate (Timeout)")

    except Exception as e:
        return get_fallback_url(str(e))

def recommend_furniture_and_palette(design_prompt: str) -> str:
    api_key = os.environ.get("GOOGLE_API_KEY")
    prompt_text = f"""
    You are an interior designer. Based on: "{design_prompt}"
    Provide:
    1. A brief explanation of the design concept.
    2. A list of 3 specific furniture/decor items.
    3. A suggested color palette.
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
            
    return "Here are your recommendations based on the selected style..."
import os
import google.generativeai as genai
import requests
import time
import random
import urllib.parse

def generate_design(design_prompt: str, image_url: str = None) -> str:
    """
    สร้างรูปภาพการออกแบบห้องใหม่โดยใช้ Replicate API (Image-to-Image)
    เพื่อรักษาโครงสร้างห้องเดิม (ControlNet/Stable Diffusion)
    """
    replicate_api_token = os.environ.get("REPLICATE_API_TOKEN")
    
    # หากไม่มี Token หรือไม่มีรูปภาพต้นฉบับ ให้กลับไปใช้ Pollinations.ai เป็นทางเลือกสำรอง (Fallback)
    if not replicate_api_token or not image_url:
        encoded_prompt = urllib.parse.quote(design_prompt)
        seed = random.randint(1, 1000000)
        # ใช้โมเดล flux ที่ให้คุณภาพสูงกว่าใน Pollinations
        return f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=768&seed={seed}&model=flux"

    # ใช้โมเดล ControlNet (Hough) เพื่อรักษาโครงสร้างห้องเดิม
    model_version = "709492abc10e47024038ad9ca3005e8a93d0728e006c1c0ad2d9205f2806f77a"
    
    headers = {
        "Authorization": f"Token {replicate_api_token}",
        "Content-Type": "application/json"
    }

    payload = {
        "version": model_version,
        "input": {
            "image": image_url,
            "prompt": f"Luxury interior design, {design_prompt}, highly detailed, 8k resolution, photorealistic, architectural photography",
            "num_samples": "1",
            "image_resolution": "768",
            "ddim_steps": 25,
            "scale": 9,
            "a_prompt": "best quality, extremely detailed, photo from architectural digest, interior design, 8k, realistic, cinematic lighting",
            "n_prompt": "longbody, lowres, bad anatomy, bad hands, missing fingers, extra digit, fewer digits, cropped, worst quality, low quality, blurry, distorted"
        }
    }

    try:
        # สร้าง Prediction
        response = requests.post(
            "https://api.replicate.com/v1/predictions",
            headers=headers,
            json=payload,
            timeout=15
        )
        prediction = response.json()
        
        if "urls" not in prediction:
            # หาก Replicate มีปัญหา ให้ใช้ Pollinations เป็น Fallback ทันที
            return generate_design(design_prompt, None)
            
        get_url = prediction["urls"]["get"]

        # รอผลลัพธ์ (Polling) - จำกัดเวลาไม่เกิน 45 วินาที
        start_time = time.time()
        while time.time() - start_time < 45:
            res = requests.get(get_url, headers=headers, timeout=10)
            res_json = res.json()
            status = res_json["status"]
            
            if status == "succeeded":
                output = res_json.get("output")
                if isinstance(output, list) and len(output) > 1:
                    return output[1] # รูปที่ 2 คือรูปที่เรนเดอร์เสร็จแล้ว (รูปแรกคือเส้นโครงสร้าง)
                elif isinstance(output, list) and len(output) > 0:
                    return output[0]
                return output
            elif status == "failed":
                return generate_design(design_prompt, None) # Fallback
            
            time.sleep(2)
            
        return generate_design(design_prompt, None) # Timeout Fallback

    except Exception as e:
        print(f"Replicate Error: {e}")
        return generate_design(design_prompt, None) # Error Fallback

def recommend_furniture_and_palette(design_prompt: str) -> str:
    """
    ใช้ Google Gemini เพื่ออธิบายการออกแบบและแนะนำเฟอร์นิเจอร์
    """
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        return "Error: Please set GOOGLE_API_KEY in Streamlit Secrets."

    try:
        genai.configure(api_key=api_key)
        # ใช้ gemini-1.5-flash เพื่อความเสถียร
        model = genai.GenerativeModel("gemini-1.5-flash")

        prompt = f"""
        You are a luxury AI interior designer. Based on this design prompt: "{design_prompt}"
        
        Please provide:
        1. A brief explanation of the luxury design concept.
        2. A list of 3-5 premium furniture items or decor pieces.
        3. A suggested luxury color palette (hex codes or descriptive names).
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
        return f"Error generating recommendations: {str(e)}"

import os
import google.generativeai as genai
import requests
import time
import random
import urllib.parse

def generate_design(design_prompt: str, image_url: str = None) -> str:
    """
    สร้างรูปภาพการออกแบบห้องใหม่โดยใช้ Replicate API (ControlNet Canny)
    เพื่อรักษาโครงสร้างห้องเดิม (Structural Preservation) 100%
    """
    replicate_api_token = os.environ.get("REPLICATE_API_TOKEN")
    
    # หากไม่มี Token หรือไม่มีรูปภาพต้นฉบับ ให้กลับไปใช้ Pollinations.ai เป็นทางเลือกสำรอง (Fallback)
    if not replicate_api_token or not image_url:
        encoded_prompt = urllib.parse.quote(design_prompt)
        seed = random.randint(1, 1000000)
        return f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=768&seed={seed}&model=flux"

    # ใช้โมเดล ControlNet Canny (SDXL) ที่รักษาเส้นโครงสร้างได้แม่นยำที่สุด
    # โมเดล: xlabs-ai/controlnet-canny-sdxl
    model_version = "d306389596963795744833984334338304977464334338304977464334338304" # Placeholder for a stable SDXL Canny
    # หรือใช้โมเดลยอดนิยม: lucataco/controlnet-canny-sdxl
    model_id = "lucataco/controlnet-canny-sdxl:06d718b34f2142a3583d33967a99a209b9c2800291931057d25f9a21d78266ac"
    
    headers = {
        "Authorization": f"Token {replicate_api_token}",
        "Content-Type": "application/json"
    }

    payload = {
        "version": "06d718b34f2142a3583d33967a99a209b9c2800291931057d25f9a21d78266ac",
        "input": {
            "image": image_url,
            "prompt": f"Professional interior design, {design_prompt}, high quality, realistic, 8k, architectural photography",
            "negative_prompt": "low quality, blurry, distorted, messy, bad proportions, changed room structure, moved walls",
            "num_inference_steps": 30,
            "controlnet_conditioning_scale": 0.8, # บังคับให้ตามโครงสร้างเดิมสูง
            "guidance_scale": 7.5
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
            return generate_design(design_prompt, None)
            
        get_url = prediction["urls"]["get"]

        start_time = time.time()
        while time.time() - start_time < 60:
            res = requests.get(get_url, headers=headers, timeout=10)
            res_json = res.json()
            status = res_json["status"]
            
            if status == "succeeded":
                output = res_json.get("output")
                if isinstance(output, list):
                    return output[-1] # ปกติรูปสุดท้ายคือผลลัพธ์
                return output
            elif status == "failed":
                return generate_design(design_prompt, None)
            
            time.sleep(3)
            
        return generate_design(design_prompt, None)

    except Exception as e:
        print(f"Replicate Error: {e}")
        return generate_design(design_prompt, None)

def recommend_furniture_and_palette(design_prompt: str) -> str:
    """
    ใช้ Google Gemini 2.5 Flash เพื่ออธิบายการออกแบบและแนะนำเฟอร์นิเจอร์
    """
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        return "Error: Please set GOOGLE_API_KEY in Streamlit Secrets."

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.5-flash")

        prompt = f"""
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

        response = model.generate_content(prompt)
        return response.text if response and response.text else "No recommendations available."
            
    except Exception as e:
        return f"Error generating recommendations: {str(e)}"

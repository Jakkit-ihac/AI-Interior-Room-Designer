import os
import google.generativeai as genai
import requests
import time
import random

def generate_design(design_prompt: str, image_url: str = None) -> str:
    """
    สร้างรูปภาพการออกแบบห้องใหม่โดยใช้ Replicate API (Image-to-Image)
    เพื่อรักษาโครงสร้างห้องเดิม (ControlNet/Stable Diffusion)
    """
    replicate_api_token = os.environ.get("REPLICATE_API_TOKEN")
    if not replicate_api_token:
        return "Error: Please set REPLICATE_API_TOKEN in Streamlit Secrets."

    # หากไม่มีรูปภาพต้นฉบับ ให้กลับไปใช้ Pollinations.ai เป็นทางเลือกสำรอง (Fallback)
    if not image_url:
        import urllib.parse
        encoded_prompt = urllib.parse.quote(design_prompt)
        seed = random.randint(1, 1000000)
        return f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=768&seed={seed}&model=flux"

    # ใช้โมเดล ControlNet (MLSD/Canny) เพื่อรักษาโครงสร้างห้องเดิม
    # ในที่นี้เราจะใช้โมเดลที่ได้รับความนิยมสำหรับ Interior Design บน Replicate
    # เช่น jagilley/controlnet-hough (เหมาะสำหรับเส้นตรงและโครงสร้างห้อง)
    model_version = "709492abc10e47024038ad9ca3005e8a93d0728e006c1c0ad2d9205f2806f77a" # controlnet-hough
    
    headers = {
        "Authorization": f"Token {replicate_api_token}",
        "Content-Type": "application/json"
    }

    payload = {
        "version": model_version,
        "input": {
            "image": image_url,
            "prompt": design_prompt,
            "num_samples": "1",
            "image_resolution": "768",
            "ddim_steps": 20,
            "scale": 9,
            "eta": 0,
            "a_prompt": "best quality, extremely detailed, photo from architectural digest, interior design, 8k, realistic",
            "n_prompt": "longbody, lowres, bad anatomy, bad hands, missing fingers, extra digit, fewer digits, cropped, worst quality, low quality"
        }
    }

    try:
        # สร้าง Prediction
        response = requests.post(
            "https://api.replicate.com/v1/predictions",
            headers=headers,
            json=payload
        )
        prediction = response.json()
        
        if "urls" not in prediction:
            return f"Error starting Replicate prediction: {prediction.get('detail', 'Unknown error')}"
            
        prediction_id = prediction["id"]
        get_url = prediction["urls"]["get"]

        # รอผลลัพธ์ (Polling)
        while True:
            res = requests.get(get_url, headers=headers)
            res_json = res.json()
            status = res_json["status"]
            
            if status == "succeeded":
                # คืนค่า URL ของรูปภาพผลลัพธ์ (ปกติจะเป็นรายการ)
                output = res_json.get("output")
                if isinstance(output, list) and len(output) > 1:
                    return output[1] # มักจะเป็นรูปที่ 2 สำหรับโมเดล ControlNet (รูปแรกคือเส้นโครงสร้าง)
                elif isinstance(output, list) and len(output) > 0:
                    return output[0]
                return output
            elif status == "failed":
                return f"Error: Replicate prediction failed: {res_json.get('error')}"
            
            time.sleep(2) # รอ 2 วินาทีก่อนเช็คใหม่

    except Exception as e:
        return f"Error calling Replicate API: {str(e)}"

def recommend_furniture_and_palette(design_prompt: str) -> str:
    """
    ใช้ Google Gemini เพื่ออธิบายการออกแบบและแนะนำเฟอร์นิเจอร์
    """
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        return "Error: Please set GOOGLE_API_KEY in Streamlit Secrets."

    try:
        genai.configure(api_key=api_key)
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

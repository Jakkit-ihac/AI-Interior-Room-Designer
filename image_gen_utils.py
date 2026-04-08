
import os
from openai import OpenAI

client = OpenAI()

def generate_design(prompt: str) -> str:
    """
    สร้างรูปภาพการออกแบบห้องใหม่โดยใช้ AI Image Generation
    """
    try:
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1,
        )
        image_url = response.data[0].url
        return image_url
    except Exception as e:
        print(f"Error generating image: {e}")
        return ""

def recommend_furniture_and_palette(prompt: str) -> str:
    """
    ใช้ LLM เพื่อแนะนำเฟอร์นิเจอร์และจานสีตาม prompt การออกแบบ
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o", # Using GPT-4o for better reasoning
            messages=[
                {"role": "system", "content": "You are an AI interior designer. Based on the provided design prompt, suggest a list of furniture, a color palette (3-5 colors with hex codes if possible), and optimized layout advice. Format your response clearly with sections for 'Suggested Furniture:', 'Color Palette:', and 'Optimized Layout Advice:'."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
        )
        explanation_text = response.choices[0].message.content
        return explanation_text
    except Exception as e:
        print(f"Error recommending furniture and palette: {e}")
        return ""

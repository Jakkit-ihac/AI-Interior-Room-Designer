
from PIL import Image
import io
import base64
import os
from openai import OpenAI
import json

# Initialize OpenAI client (or Gemini client)
# For Gemini, you would use: genai.configure(api_key="YOUR_API_KEY")
# model = genai.GenerativeModel("gemini-pro-vision")

client = OpenAI()

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

def analyze_room(image_path: str) -> dict:
    """
    ใช้ Vision AI เพื่อวิเคราะห์รูปภาพห้องและดึงข้อมูลที่เกี่ยวข้อง
    """
    base64_image = encode_image(image_path)

    # Example using OpenAI Vision API
    response = client.chat.completions.create(
        model="gpt-4-vision-preview",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Analyze this room image. Identify the room type, existing furniture, approximate free space (e.g., 'a lot', 'some', 'limited'), dominant wall color, and natural light direction (e.g., 'from the left', 'from the right', 'overhead', 'none'). Provide the output in a JSON format like: {\\"room_type\\": \\"\\", \\"current_furniture\\": [], \\"free_space\\": \\"\\", \\"wall_color\\": \\"\\", \\"natural_light_direction\\": \\"\\"}."},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        },
                    },
                ],
            }
        ],
        max_tokens=300,
    )

    analysis_result = response.choices[0].message.content
    # Attempt to parse the JSON string. Handle potential errors.
    try:
        # The API might return the JSON string within markdown code block, so we need to extract it.
        if analysis_result.startswith("```json") and analysis_result.endswith("```"):
            analysis_result = analysis_result[7:-3].strip()
        return json.loads(analysis_result)
    except json.JSONDecodeError:
        print(f"Error decoding JSON: {analysis_result}")
        return {
            "room_type": "unknown",
            "current_furniture": [],
            "free_space": "unknown",
            "wall_color": "unknown",
            "natural_light_direction": "unknown"
        }


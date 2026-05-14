import os

# Updated import - handle deprecated google.generativeai
try:
    import google.generativeai as genai
except ImportError:
    try:
        from google import genai as genai_module
        genai = genai_module
    except ImportError:
        genai = None

from PIL import Image
import json
import re
import io
from typing import List, Dict, Optional

# Mock product database - สามารถแก้ไขเป็น API จริงได้
PRODUCT_DATABASE = {
    "sofa": [
        {"id": "sofa_001", "name": "Modern Gray Sofa", "price": 15999, "store": "Shopee", "link": "https://shopee.co.th/search?keyword=modern+gray+sofa"},
        {"id": "sofa_002", "name": "Minimalist White Sofa", "price": 12999, "store": "Lazada", "link": "https://www.lazada.co.th/catalog/?q=minimalist+white+sofa"},
        {"id": "sofa_003", "name": "Scandinavian Wooden Sofa", "price": 19999, "store": "Furniture Zone", "link": "https://www.furniture.co.th"},
    ],
    "table": [
        {"id": "table_001", "name": "Wooden Dining Table", "price": 8999, "store": "Shopee", "link": "https://shopee.co.th/search?keyword=wooden+dining+table"},
        {"id": "table_002", "name": "Marble Coffee Table", "price": 6999, "store": "Lazada", "link": "https://www.lazada.co.th/catalog/?q=marble+coffee+table"},
        {"id": "table_003", "name": "Glass Side Table", "price": 3999, "store": "Facebook Marketplace", "link": "https://www.facebook.com/marketplace"},
    ],
    "chair": [
        {"id": "chair_001", "name": "Ergonomic Office Chair", "price": 4999, "store": "Shopee", "link": "https://shopee.co.th/search?keyword=ergonomic+office+chair"},
        {"id": "chair_002", "name": "Scandinavian Dining Chair", "price": 2999, "store": "Lazada", "link": "https://www.lazada.co.th/catalog/?q=scandinavian+chair"},
        {"id": "chair_003", "name": "Minimalist White Chair", "price": 3499, "store": "Furniture Zone", "link": "https://www.furniture.co.th"},
    ],
    "lamp": [
        {"id": "lamp_001", "name": "Modern Floor Lamp", "price": 2499, "store": "Shopee", "link": "https://shopee.co.th/search?keyword=modern+floor+lamp"},
        {"id": "lamp_002", "name": "Pendant Ceiling Lamp", "price": 1999, "store": "Lazada", "link": "https://www.lazada.co.th/catalog/?q=pendant+ceiling+lamp"},
        {"id": "lamp_003", "name": "Smart LED Lamp", "price": 1499, "store": "Thailand Tech", "link": "https://www.thaitech.co.th"},
    ],
    "shelf": [
        {"id": "shelf_001", "name": "Wooden Wall Shelf", "price": 1999, "store": "Shopee", "link": "https://shopee.co.th/search?keyword=wooden+wall+shelf"},
        {"id": "shelf_002", "name": "Industrial Shelving Unit", "price": 3999, "store": "Lazada", "link": "https://www.lazada.co.th/catalog/?q=industrial+shelving"},
        {"id": "shelf_003", "name": "Floating Shelf Set", "price": 2499, "store": "Furniture Zone", "link": "https://www.furniture.co.th"},
    ],
    "rug": [
        {"id": "rug_001", "name": "Modern Area Rug", "price": 4999, "store": "Shopee", "link": "https://shopee.co.th/search?keyword=modern+area+rug"},
        {"id": "rug_002", "name": "Scandinavian Pattern Rug", "price": 3999, "store": "Lazada", "link": "https://www.lazada.co.th/catalog/?q=scandinavian+rug"},
        {"id": "rug_003", "name": "Minimalist Carpet", "price": 5999, "store": "Home Decor Plus", "link": "https://www.homedecor.co.th"},
    ],
    "curtain": [
        {"id": "curtain_001", "name": "Modern Blackout Curtain", "price": 1299, "store": "Shopee", "link": "https://shopee.co.th/search?keyword=blackout+curtain"},
        {"id": "curtain_002", "name": "Minimalist White Curtain", "price": 999, "store": "Lazada", "link": "https://www.lazada.co.th/catalog/?q=white+curtain"},
        {"id": "curtain_003", "name": "Premium Linen Curtain", "price": 2499, "store": "Textile Store", "link": "https://www.textile.co.th"},
    ],
    "plant": [
        {"id": "plant_001", "name": "Indoor Green Plant", "price": 399, "store": "Shopee", "link": "https://shopee.co.th/search?keyword=indoor+plant"},
        {"id": "plant_002", "name": "Monstera Plant", "price": 599, "store": "Lazada", "link": "https://www.lazada.co.th/catalog/?q=monstera+plant"},
        {"id": "plant_003", "name": "Plant Pot Set", "price": 799, "store": "Garden Store", "link": "https://www.garden.co.th"},
    ],
    "art": [
        {"id": "art_001", "name": "Modern Wall Art", "price": 999, "store": "Shopee", "link": "https://shopee.co.th/search?keyword=modern+wall+art"},
        {"id": "art_002", "name": "Canvas Painting", "price": 1499, "store": "Lazada", "link": "https://www.lazada.co.th/catalog/?q=canvas+painting"},
        {"id": "art_003", "name": "Minimalist Poster", "price": 599, "store": "Art Gallery", "link": "https://www.artgallery.co.th"},
    ],
    "mirror": [
        {"id": "mirror_001", "name": "Wall Mirror", "price": 1999, "store": "Shopee", "link": "https://shopee.co.th/search?keyword=wall+mirror"},
        {"id": "mirror_002", "name": "Decorative Mirror", "price": 2999, "store": "Lazada", "link": "https://www.lazada.co.th/catalog/?q=decorative+mirror"},
        {"id": "mirror_003", "name": "Full Length Mirror", "price": 1499, "store": "Home Plus", "link": "https://www.homeplus.co.th"},
    ],
}

def detect_products_in_room(image_input) -> Dict:
    """
    ใช้ Gemini Vision API เพื่อตรวจจับสินค้า/เฟอร์นิเจอร์ในห้อง
    ส่งคืน dict ที่มีรายชื่อผลิตภัณฑ์ที่พบ
    
    Args:
        image_input: PIL Image, bytes, หรือ file path
    
    Returns:
        dict: {
            "detected_products": [
                {
                    "name": "Sofa",
                    "category": "sofa",
                    "description": "Gray modern sofa...",
                    "position": "center-left",
                    "confidence": 0.95
                },
                ...
            ],
            "room_description": "Modern living room with...",
            "total_items": 5
        }
    """
    api_key = os.environ.get("GOOGLE_API_KEY")
    
    default_response = {
        "detected_products": [
            {"name": "Sofa", "category": "sofa", "description": "Comfortable seating", "position": "center", "confidence": 0.85},
            {"name": "Coffee Table", "category": "table", "description": "Wooden center table", "position": "center", "confidence": 0.80},
            {"name": "Floor Lamp", "category": "lamp", "description": "Modern standing lamp", "position": "corner", "confidence": 0.75},
        ],
        "room_description": "Modern styled room",
        "total_items": 3
    }
    
    if not api_key:
        print("⚠️ GOOGLE_API_KEY not found - using default products")
        return default_response
    
    if not genai:
        print("⚠️ genai module not available - using default products")
        return default_response
    
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.5-flash")
        
        # Convert image input to PIL Image
        if isinstance(image_input, bytes):
            img = Image.open(io.BytesIO(image_input))
        elif isinstance(image_input, str):
            img = Image.open(image_input)
        else:
            img = image_input
        
        # Gemini prompt for product detection
        prompt = """
        Analyze this room image and identify ALL furniture and decorative items visible.
        
        IMPORTANT: Return ONLY valid JSON, no markdown or extra text.
        
        For each item detected, provide:
        - name: the name of the item (e.g., "Sofa", "Table", "Lamp")
        - category: simplified category (sofa, table, chair, lamp, shelf, rug, curtain, plant, art, mirror)
        - description: brief description of what you see
        - position: where in the room (e.g., "center", "left", "corner", "above wall")
        - confidence: confidence level 0-1
        
        Return JSON format:
        {
            "detected_products": [
                {
                    "name": "item name",
                    "category": "category",
                    "description": "description",
                    "position": "position",
                    "confidence": 0.95
                }
            ],
            "room_description": "overall room description",
            "total_items": number
        }
        """
        
        response = model.generate_content([prompt, img])
        response_text = response.text.strip()
        
        # Remove markdown code blocks if present
        if response_text.startswith("```"):
            response_text = response_text.split("```")[1]
            if response_text.startswith("json"):
                response_text = response_text[4:]
        response_text = response_text.strip()
        
        # Parse JSON response
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            result = json.loads(json_match.group(0))
            return result
        else:
            print("⚠️ Could not parse JSON response")
            return default_response
            
    except Exception as e:
        print(f"⚠️ Error detecting products: {e}")
        return default_response


def get_product_suggestions(detected_products: List[Dict], limit: int = 5) -> Dict:
    """
    จากสินค้าที่ตรวจจับได้ ให้ตรงกับผลิตภัณฑ์ในฐานข้อมูล
    
    Args:
        detected_products: list of detected products from detect_products_in_room()
        limit: maximum products to suggest per category
    
    Returns:
        dict: {
            "sofa": [product1, product2, ...],
            "table": [product1, product2, ...],
            ...
        }
    """
    suggestions = {}
    
    for product in detected_products:
        category = product.get("category", "").lower()
        
        # ถ้า category อยู่ในฐานข้อมูล
        if category in PRODUCT_DATABASE:
            suggestions[category] = PRODUCT_DATABASE[category][:limit]
        else:
            # ค้นหาเฉพาะ category ที่มีชื่อใกล้เคียง
            for db_category in PRODUCT_DATABASE.keys():
                if db_category in category or category in db_category:
                    suggestions[category] = PRODUCT_DATABASE[db_category][:limit]
                    break
    
    return suggestions


def calculate_total_budget(shopping_cart: List[Dict]) -> Dict:
    """
    คำนวณงบประมาณรวมและส่วนแบ่งต่อประเภท
    
    Args:
        shopping_cart: list of selected products [{"id": "...", "price": ...}, ...]
    
    Returns:
        dict: {"total": 50000, "by_category": {"sofa": 15999, ...}, "items_count": 5}
    """
    total = 0
    by_category = {}
    
    for item in shopping_cart:
        price = item.get("price", 0)
        total += price
        
        # หา category จาก ID
        category = next((cat for cat in PRODUCT_DATABASE.keys() 
                        if item.get("id", "").startswith(cat[:4])), "other")
        
        by_category[category] = by_category.get(category, 0) + price
    
    return {
        "total": total,
        "by_category": by_category,
        "items_count": len(shopping_cart),
        "average_per_item": total / len(shopping_cart) if shopping_cart else 0
    }


def get_product_by_id(product_id: str) -> Optional[Dict]:
    """
    ค้นหาผลิตภัณฑ์จาก ID
    """
    for category, products in PRODUCT_DATABASE.items():
        for product in products:
            if product["id"] == product_id:
                return product
    return None

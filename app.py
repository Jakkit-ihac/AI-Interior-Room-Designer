import streamlit as st
from PIL import Image
import os, base64, io, requests
from dotenv import load_dotenv
import google.generativeai as genai
import urllib.parse
import time
from product_shopping_utils import detect_products_in_room, get_product_suggestions, calculate_total_budget, get_product_by_id

# Try importing Replicate
try:
    import replicate
    REPLICATE_AVAILABLE = True
except ImportError:
    REPLICATE_AVAILABLE = False

# Optional: for background removal
try:
    from rembg import remove
    REMBG_AVAILABLE = True
except ImportError:
    REMBG_AVAILABLE = False

# โหลด Environment Variables
load_dotenv()

st.set_page_config(
    page_title="AI Room Designer | Create Your Empty Room", 
    page_icon="🛋️", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- Professional CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');
    
    /* Base styling */
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }
    
    html, body {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        scroll-behavior: smooth;
    }
    
    /* Color palette */
    :root {
        --primary: #6366f1;
        --primary-light: #818cf8;
        --primary-dark: #4f46e5;
        --secondary: #ec4899;
        --success: #10b981;
        --warning: #f59e0b;
        --danger: #ef4444;
        --info: #3b82f6;
        --light: #f8fafc;
        --lighter: #f1f5f9;
        --dark: #1e293b;
        --gray: #64748b;
    }
    
    /* Main container */
    .main {
        max-width: 100%;
        padding: 0 !important;
    }
    
    /* === TYPOGRAPHY === */
    .main-title {
        font-size: 3rem;
        font-weight: 900;
        background: linear-gradient(135deg, #6366f1 0%, #ec4899 50%, #06b6d4 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-align: center;
        margin: 1.5rem 0 0.3rem 0;
        letter-spacing: -2px;
        animation: fadeInDown 0.6s ease;
    }
    
    .subtitle {
        text-align: center;
        color: #64748b;
        font-size: 1.15rem;
        margin-bottom: 2rem;
        font-weight: 500;
        animation: fadeInUp 0.6s ease 0.1s both;
    }
    
    .step-title {
        font-size: 1.35rem;
        font-weight: 700;
        color: #1e293b;
        margin: 1.8rem 0 1.2rem 0;
        padding-bottom: 1rem;
        border-bottom: 3px solid #6366f1;
        display: inline-block;
        transition: all 0.3s ease;
    }
    
    .step-title:hover {
        transform: translateX(4px);
        border-color: #ec4899;
    }
    
    h1, h2, h3 {
        color: #1e293b;
        font-weight: 700;
        margin-top: 1rem;
    }
    
    h1 { font-size: 2rem; }
    h2 { font-size: 1.5rem; }
    h3 { font-size: 1.2rem; }
    
    /* === LAYOUT === */
    [data-testid="column"] {
        padding: 0 0.5rem !important;
    }
    
    .element-container {
        margin: 0.8rem 0 !important;
    }
    
    .stForm {
        border-radius: 12px;
    }
    
    /* === CONTAINERS & CARDS === */
    [data-testid="stVerticalBlock"] > [data-testid="stVerticalBlock"] {
        background: transparent !important;
        padding: 0 !important;
    }
    
    .stContainer {
        border-radius: 12px;
        padding: 1.5rem;
        background: white;
        border: 1px solid #e2e8f0;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
        transition: all 0.3s ease;
    }
    
    .stContainer:hover {
        border-color: #cbd5e1;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
    }
    
    /* === BUTTONS === */
    .stButton > button {
        width: 100%;
        border-radius: 10px;
        height: 3em;
        font-weight: 600;
        font-size: 1rem;
        border: none;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 2px 8px rgba(99, 102, 241, 0.15);
        letter-spacing: 0.3px;
        text-transform: uppercase;
        cursor: pointer;
    }
    
    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 20px rgba(99, 102, 241, 0.3);
    }
    
    .stButton > button:active {
        transform: translateY(-1px);
    }
    
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%) !important;
        color: white !important;
        font-weight: 700;
    }
    
    .stButton > button[kind="secondary"] {
        background: linear-gradient(135deg, #ec4899 0%, #db2777 100%) !important;
        color: white !important;
    }
    
    /* === INPUT FIELDS === */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div > select,
    .stTextArea textarea,
    .stColorPicker > div > div > input {
        background: #f8fafc !important;
        border: 2px solid #e2e8f0 !important;
        border-radius: 10px !important;
        font-size: 1rem !important;
        padding: 0.9rem 1.1rem !important;
        transition: all 0.3s ease !important;
        color: #1e293b !important;
        font-family: 'Inter', sans-serif !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus,
    .stSelectbox > div > div > select:focus,
    .stTextArea textarea:focus,
    .stColorPicker > div > div > input:focus {
        border-color: #6366f1 !important;
        background: white !important;
        box-shadow: 0 0 0 4px rgba(99, 102, 241, 0.1) !important;
    }
    
    .stTextArea textarea {
        resize: vertical !important;
        min-height: 100px !important;
    }
    
    /* === CHECKBOXES === */
    .stCheckbox {
        margin: 1rem 0 !important;
        padding: 0.8rem;
        border-radius: 8px;
        transition: all 0.3s ease;
        background: #f8fafc;
        border-radius: 8px;
    }
    
    .stCheckbox:hover {
        background: #f1f5f9;
    }
    
    .stCheckbox > label {
        font-weight: 500;
        color: #1e293b;
        cursor: pointer;
    }
    
    /* === SLIDERS === */
    .stSlider {
        margin: 1.8rem 0 !important;
        padding: 1rem 0;
    }
    
    .stSlider > div {
        padding: 0 !important;
    }
    
    /* === EXPANDER === */
    .stExpander {
        border: 1px solid #e2e8f0 !important;
        border-radius: 10px !important;
        overflow: hidden;
        transition: all 0.3s ease;
    }
    
    .stExpander:hover {
        border-color: #cbd5e1;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
    }
    
    /* === MESSAGES === */
    .stInfo {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(59, 130, 246, 0.05) 100%) !important;
        border-left: 4px solid #6366f1 !important;
        border-radius: 10px !important;
        padding: 1.2rem !important;
        margin: 1rem 0 !important;
    }
    
    .stWarning {
        background: linear-gradient(135deg, rgba(245, 158, 11, 0.1) 0%, rgba(251, 191, 36, 0.05) 100%) !important;
        border-left: 4px solid #f59e0b !important;
        border-radius: 10px !important;
        padding: 1.2rem !important;
        margin: 1rem 0 !important;
    }
    
    .stError {
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.1) 0%, rgba(248, 113, 113, 0.05) 100%) !important;
        border-left: 4px solid #ef4444 !important;
        border-radius: 10px !important;
        padding: 1.2rem !important;
        margin: 1rem 0 !important;
    }
    
    .stSuccess {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(52, 211, 153, 0.05) 100%) !important;
        border-left: 4px solid #10b981 !important;
        border-radius: 10px !important;
        padding: 1.2rem !important;
        margin: 1rem 0 !important;
    }
    
    /* === SIDEBAR === */
    .stSidebar {
        background: linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%) !important;
        border-right: 1px solid #e2e8f0;
    }
    
    .stSidebar [data-testid="stSidebarNav"] {
        padding: 2rem 1rem;
    }
    
    /* === TABS === */
    .stTabs [data-baseweb="tab-list"] {
        gap: 1rem;
        border-bottom: 2px solid #e2e8f0;
        padding-bottom: 0;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 10px 10px 0 0;
        background: #f8fafc;
        border: 2px solid transparent;
        transition: all 0.3s ease;
        font-weight: 600;
    }
    
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
        color: white !important;
        border-color: #6366f1;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: #e2e8f0;
    }
    
    /* === DIVIDER === */
    hr {
        margin: 2rem 0 !important;
        border: none;
        height: 2px;
        background: linear-gradient(90deg, transparent 0%, #e2e8f0 50%, transparent 100%);
    }
    
    /* === IMAGE STYLING === */
    [data-testid="stImage"] {
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
        transition: all 0.4s ease;
    }
    
    [data-testid="stImage"]:hover {
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.18);
        transform: scale(1.01);
    }
    
    img {
        border-radius: 10px;
        max-width: 100%;
        height: auto;
    }
    
    /* === METRIC === */
    [data-testid="metric-container"] {
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
        border-radius: 12px;
        padding: 1.5rem;
        border: 1px solid #e2e8f0;
        transition: all 0.3s ease;
    }
    
    [data-testid="metric-container"]:hover {
        border-color: #cbd5e1;
        box-shadow: 0 4px 12px rgba(99, 102, 241, 0.1);
    }
    
    /* === ANIMATIONS === */
    @keyframes fadeInDown {
        from {
            opacity: 0;
            transform: translateY(-20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateX(-20px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    .stMetricLabel {
        animation: fadeInUp 0.6s ease;
    }
    
    /* === SCROLLBAR STYLING === */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f5f9;
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(180deg, #6366f1 0%, #4f46e5 100%);
        border-radius: 10px;
        transition: all 0.3s ease;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(180deg, #4f46e5 0%, #4338ca 100%);
    }
    
    /* === SPACING & PADDING === */
    .stMarkdown {
        line-height: 1.6;
        color: #334155;
    }
    
    .stMarkdown p {
        margin: 0.8rem 0;
    }
    
    /* === RESPONSIVE === */
    @media (max-width: 640px) {
        .main-title {
            font-size: 2rem;
        }
        
        .subtitle {
            font-size: 1rem;
        }
        
        .step-title {
            font-size: 1.1rem;
        }
        
        .stButton > button {
            height: 2.8em;
            font-size: 0.9rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# 🔄 Session State - เก็บข้อมูลห้อง
session_defaults = {
    'room_type': None,
    'room_style': None,
    'color_theme': None,
    'furniture_list': [],  # ลิสต์ของเฟอร์นิเจอร์ที่เลือก
    'room_image': None,
    'room_description': "",
    'decoration_image': None,  # รูปตกแต่งที่อัพโหลด
    'decoration_removed_bg': None,  # รูปตกแต่งหลังตัดพื้นหลัง
    'detected_products': None,  # สินค้าที่ตรวจจับในห้อง
    'product_suggestions': None,  # ข้อเสนอสินค้า
    'shopping_cart': [],  # รถเข็นช้อปปิ้ง
    'show_shopping': False,  # แสดงหน้า Shopping
}

for key, default in session_defaults.items():
    if key not in st.session_state:
        st.session_state[key] = default

# ============================================================
# Helper Functions
# ============================================================
def remove_background(image_input) -> Image:
    """
    Remove background from decoration image using rembg
    """
    try:
        if isinstance(image_input, bytes):
            img = Image.open(io.BytesIO(image_input))
        else:
            img = image_input
        
        if not REMBG_AVAILABLE:
            st.warning("⚠️ rembg not installed - showing original image")
            return img
        
        # Convert to RGB if needed
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        st.write("🔄 กำลังตัดพื้นหลัง...")
        # Remove background
        output = remove(img)
        st.write("✅ ตัดพื้นหลังเสร็จแล้ว!")
        return output
    except Exception as e:
        st.warning(f"⚠️ ไม่สามารถตัดพื้นหลังได้: {e}")
        return Image.open(io.BytesIO(image_input)) if isinstance(image_input, bytes) else image_input

def show_product_card(product: dict, col):
    """
    แสดงการ์ดสินค้าในเมนูสั้น ๆ พร้อมปุ่มเพิ่มลงรถเข็น
    """
    with col:
        with st.container(border=True):
            st.markdown(f"<div style='padding: 0.5rem 0;'><b style='font-size: 1.1rem;'>{product['name']}</b></div>", unsafe_allow_html=True)
            st.markdown(f"<p style='color: #64748b; margin: 0.5rem 0; font-size: 0.95rem;'>฿{product['price']:,} • {product['store']}</p>", unsafe_allow_html=True)
            
            col1, col2 = st.columns([1, 1], gap="small")
            with col1:
                if st.button("🔗 ดูเพิ่มเติม", key=f"view_{product['id']}", use_container_width=True):
                    st.toast(f"เปิดลิงก์ {product['link']}")
            with col2:
                if st.button("🛒 เพิ่มลงรถเข็น", key=f"cart_{product['id']}", use_container_width=True):
                    if product not in st.session_state['shopping_cart']:
                        st.session_state['shopping_cart'].append(product)
                        st.toast(f"✅ เพิ่ม {product['name']} ลงรถเข็นแล้ว", icon="🛒")
                    else:
                        st.toast(f"⚠️ {product['name']} อยู่ในรถเข็นแล้ว", icon="ℹ️")

def overlay_decoration_on_room(room_img: Image, decoration_img: Image, position: tuple = (0.5, 0.5), scale: float = 0.3) -> Image:
    """
    Overlay decoration image onto room image
    
    Args:
        room_img: Original room image
        decoration_img: Decoration image with transparent background
        position: (x_ratio, y_ratio) where 0.5, 0.5 is center
        scale: Size of decoration relative to room (0.0-1.0)
    """
    try:
        # Ensure both images are in appropriate formats
        room = room_img.convert('RGBA') if isinstance(room_img, Image.Image) else room_img
        decor = decoration_img.convert('RGBA') if isinstance(decoration_img, Image.Image) else decoration_img
        
        # Calculate new size for decoration
        room_width, room_height = room.size
        decor_width = int(room_width * scale)
        aspect_ratio = decor.size[1] / decor.size[0]
        decor_height = int(decor_width * aspect_ratio)
        
        # Resize decoration
        decor_resized = decor.resize((decor_width, decor_height), Image.Resampling.LANCZOS)
        
        # Calculate position
        x = int(room_width * position[0] - decor_width / 2)
        y = int(room_height * position[1] - decor_height / 2)
        
        # Ensure position is within bounds
        x = max(0, min(x, room_width - decor_width))
        y = max(0, min(y, room_height - decor_height))
        
        # Overlay decoration
        room.paste(decor_resized, (x, y), decor_resized)
        
        return room.convert('RGB')
    except Exception as e:
        st.error(f"❌ ไม่สามารถเพิ่มตกแต่งได้: {e}")
        return room_img

def generate_with_replicate(prompt_text: str) -> Image:
    """
    Generate image using Replicate API (high quality, fast)
    Uses Stable Diffusion 3 or similar models
    """
    if not REPLICATE_AVAILABLE:
        st.warning("⚠️ Replicate library not installed")
        return None
    
    try:
        replicate_token = os.environ.get("REPLICATE_API_TOKEN")
        if not replicate_token:
            st.warning("⚠️ REPLICATE_API_TOKEN not found in .env")
            return None
        
        st.write("🎨 สร้างรูปด้วย Replicate API (Stable Diffusion 3)...")
        st.write("⏳ กำลังสร้าง... (อาจใช้เวลา 20-60 วินาที)")
        
        # Set API token
        replicate.Client(api_token=replicate_token)
        
        # ใช้ Stable Diffusion 3 model
        # รุ่น: stability-ai/stable-diffusion-3
        output = replicate.run(
            "stability-ai/stable-diffusion-3",
            input={
                "prompt": prompt_text,
                "negative_prompt": "blurry, low quality, distorted",
                "width": 1024,
                "height": 768,
                "num_outputs": 1,
                "guidance_scale": 7.5,
                "num_inference_steps": 50
            },
            timeout=600  # 10 minutes timeout
        )
        
        if output and len(output) > 0:
            image_url = output[0]
            st.write("✅ Replicate สร้างภาพสำเร็จ!")
            
            # ดาวน์โหลดรูปจาก URL
            response = requests.get(image_url, timeout=30)
            if response.status_code == 200:
                img = Image.open(io.BytesIO(response.content))
                return img
            else:
                st.error(f"❌ ไม่สามารถดาวน์โหลดรูป: {response.status_code}")
                return None
        else:
            st.error("❌ Replicate ไม่ส่งคืนรูป")
            return None
            
    except Exception as e:
        error_msg = str(e)
        st.warning(f"⚠️ Replicate error: {error_msg[:150]}")
        return None

def generate_with_fallback(prompt_text: str):
    """
    ลำดับการสร้างรูป:
    1️⃣ Gemini API (ถ้ามี quota)
    2️⃣ Replicate API (ถ้ามี token)
    3️⃣ Pollinations API (free fallback)
    """
    api_key = os.environ.get("GOOGLE_API_KEY")
    
    # 1️⃣ ลองใช้ Gemini ก่อน
    if api_key:
        try:
            st.write("🔄 ลองใช้ Gemini AI...")
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-2.5-flash")
            
            response = model.generate_content([
                prompt_text + "\n\nGenerate a photorealistic image. Provide only the image without any text."
            ])
            
            if response and response.text:
                st.write("✅ Gemini สร้างภาพสำเร็จ!")
                return response
        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg or "quota" in error_msg.lower():
                st.warning("⚠️ Gemini API quota exceeded - ลองใช้ Replicate ถัดไป...")
            else:
                st.warning(f"⚠️ Gemini error - ลองใช้ Replicate ถัดไป...")
    
    # 2️⃣ ลองใช้ Replicate
    replicate_token = os.environ.get("REPLICATE_API_TOKEN")
    if replicate_token and REPLICATE_AVAILABLE:
        result = generate_with_replicate(prompt_text)
        if result:
            return result
        st.info("⚠️ Replicate ไม่สำเร็จ - ลองใช้ Pollinations ถัดไป...")
    
    # 3️⃣ Fallback to Pollinations API (free)
    return generate_with_pollinations(prompt_text)

def generate_with_pollinations(prompt_text: str):
    """
    Generate image using Pollinations API (free fallback)
    """
    try:
        st.write("🎨 สร้างรูปด้วย Pollinations API (Free)...")
        
        # ย่อ prompt เพื่อให้เข้ากับ URL length
        summary = prompt_text[:200].replace("\n", " ").strip()
        
        # สร้าง image URL
        encoded = urllib.parse.quote(summary)
        image_url = f"https://image.pollinations.ai/prompt/{encoded}?width=1024&height=768&nologo=true"
        
        # ลองดึงรูป
        st.write(f"⏳ กำลังสร้าง... (นี่อาจใช้เวลา 10-30 วินาที)")
        response = requests.get(image_url, timeout=60)
        
        if response.status_code == 200:
            st.write("✅ Pollinations สร้างภาพสำเร็จ!")
            # แปลง bytes เป็นรูป
            img = Image.open(io.BytesIO(response.content))
            return img
        else:
            st.error(f"❌ Pollinations API error: {response.status_code}")
            return None
            
    except Exception as e:
        st.error(f"❌ ไม่สามารถสร้างรูปได้: {str(e)}")
        return None

# ============================================================
# Header
# ============================================================
st.markdown("""
<div style="padding: 2rem 0 1rem 0;">
    <h1 class="main-title">🛋️ AI Room Designer</h1>
    <p class="subtitle">สร้างห้องเปล่าของคุณเองให้เป็นพื้นที่สวยงาม</p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<style>
    .main { padding: 0 1rem; }
    [data-testid="stAppViewContainer"] { padding: 0 !important; }
    [data-testid="stMainBlockContainer"] { padding: 0 2rem !important; }
</style>
""", unsafe_allow_html=True)

# ============================================================
# Main Layout - 3 Columns
# ============================================================
col_form, col_preview, col_action = st.columns([1, 1.2, 0.8], gap="large")

# ============================================================
# LEFT COLUMN - Controls
# ============================================================
with col_form:
    st.markdown('<h2 style="margin-top: 0; margin-bottom: 1.5rem; color: #1e293b;">⚙️ การตั้งค่าห้อง</h2>', unsafe_allow_html=True)
    
    with st.container(border=True):
        st.markdown('<p style="margin: 0 0 0.8rem 0; font-weight: 600; color: #1e293b;">📐 ประเภทห้อง</p>', unsafe_allow_html=True)
        room_types = ["Living Room", "Bedroom", "Kitchen", "Bathroom", "Home Office", "Cafe", "Restaurant"]
        st.session_state['room_type'] = st.selectbox(
            "เลือก",
            room_types,
            index=0,
            label_visibility="collapsed"
        )
    
    st.markdown('<div style="height: 0.5rem;"></div>', unsafe_allow_html=True)
    
    with st.container(border=True):
        st.markdown('<p style="margin: 0 0 0.8rem 0; font-weight: 600; color: #1e293b;">🎨 สไตล์ห้อง</p>', unsafe_allow_html=True)
        room_styles = ["Modern", "Minimalist", "Japandi", "Industrial Loft", "Scandinavian", "Bohemian", "Vintage"]
        st.session_state['room_style'] = st.selectbox(
            "เลือก",
            room_styles,
            index=0,
            label_visibility="collapsed"
        )
    
    st.markdown('<div style="height: 0.5rem;"></div>', unsafe_allow_html=True)
    
    with st.container(border=True):
        st.markdown('<p style="margin: 0 0 0.8rem 0; font-weight: 600; color: #1e293b;">🌈 สีธีม</p>', unsafe_allow_html=True)
        color_themes = ["Warm (ร้อน)", "Cool (เย็น)", "Neutral (เป็นกลาง)", "Bold (โดดเด่น)", "Earthy (ธรรมชาติ)"]
        st.session_state['color_theme'] = st.selectbox(
            "เลือก",
            color_themes,
            index=0,
            label_visibility="collapsed"
        )
    
    st.markdown('<div style="height: 1.5rem;"></div>', unsafe_allow_html=True)
    st.markdown("---")
    st.markdown('<div style="height: 0.5rem;"></div>', unsafe_allow_html=True)
    
    with st.container(border=True):
        st.markdown('<p style="margin: 0 0 0.5rem 0; font-weight: 600; color: #1e293b;">🛋️ เฟอร์นิเจอร์ (สำหรับ Reference)</p>', unsafe_allow_html=True)
        st.caption("*เลือกประเภทเฟอร์นิเจอร์ที่คิดว่าจะเหมาะสม (ไม่บังคับ)*")
        
        st.markdown('<div style="height: 0.5rem;"></div>', unsafe_allow_html=True)
        
        furniture_options = {
            "Living Room": [
                "Sofa/Couch", "Coffee Table", "TV Stand", "Floor Lamp", "Bookshelf", 
                "Armchair", "Rug", "Wall Art", "Side Table", "Accent Pillows"
            ],
            "Bedroom": [
                "Bed", "Nightstand", "Wardrobe", "Dresser", "Bedside Lamp", 
                "Desk", "Chair", "Rug", "Wall Decor", "Curtains"
            ],
            "Kitchen": [
                "Dining Table", "Kitchen Chairs", "Pendant Light", "Counter Stools", "Shelving",
                "Appliances", "Sink", "Backsplash", "Floor Tiles", "Cabinet"
            ],
            "Home Office": [
                "Desk", "Office Chair", "Bookshelf", "Desk Lamp", "Monitor",
                "Filing Cabinet", "Rug", "Wall Art", "Plants", "Curtains"
            ]
        }
        
        selected_furnitures = furniture_options.get(st.session_state['room_type'], [
            "Sofa", "Table", "Chair", "Lamp", "Rug", "Plant", "Art", "Curtains", "Cabinet", "Storage"
        ])
        
        for furniture in selected_furnitures:
            if st.checkbox(furniture, value=furniture in st.session_state['furniture_list'], key=f"check_{furniture}", label_visibility="visible"):
                if furniture not in st.session_state['furniture_list']:
                    st.session_state['furniture_list'].append(furniture)
            else:
                if furniture in st.session_state['furniture_list']:
                    st.session_state['furniture_list'].remove(furniture)
    
    st.markdown('<div style="height: 1.5rem;"></div>', unsafe_allow_html=True)
    st.markdown("---")
    st.markdown('<div style="height: 0.5rem;"></div>', unsafe_allow_html=True)
    
    with st.container(border=True):
        st.markdown('<p style="margin: 0 0 0.8rem 0; font-weight: 600; color: #1e293b;">💭 รายละเอียดเพิ่มเติม</p>', unsafe_allow_html=True)
        additional_details = st.text_area(
            "คำอธิบาย",
            value=st.session_state['room_description'],
            height=100,
            placeholder="เช่น: แสงสดใส, ชอบสีเขียว, พื้นไม้",
            label_visibility="collapsed"
        )
        st.session_state['room_description'] = additional_details

# ============================================================
# CENTER COLUMN - Preview
# ============================================================
with col_preview:
    if not st.session_state['room_image']:
        st.markdown('<h2 style="margin-top: 0; margin-bottom: 1rem; color: #1e293b;">🖼️ อัพโหลดตกแต่ง/เฟอร์นิเจอร์</h2>', unsafe_allow_html=True)
        st.markdown('<p style="color: #64748b; margin: 0 0 1rem 0;">หลังจากสร้างห้อง นำรูปตกแต่งมาวาง</p>', unsafe_allow_html=True)
        
        uploaded_decoration = st.file_uploader(
            "เลือกไฟล์รูป",
            type=["png", "jpg", "jpeg"],
            key="decor_upload",
            label_visibility="collapsed"
        )
        
        if uploaded_decoration:
            st.session_state['decoration_image'] = uploaded_decoration.getvalue()
            
            col_check, col_btn = st.columns([1, 1])
            with col_check:
                bg_remove = st.checkbox("✂️ ตัดพื้นหลัง", value=True, key="bg_remove_checkbox")
            with col_btn:
                if bg_remove and st.button("🔄 ประมวลผล", key="process_decor", use_container_width=True):
                    with st.spinner("⏳ กำลังตัดพื้นหลัง..."):
                        decor_processed = remove_background(st.session_state['decoration_image'])
                        st.session_state['decoration_removed_bg'] = decor_processed
                        st.success("✅ เสร็จแล้ว!")
        
        # Preview
        if st.session_state['decoration_removed_bg']:
            st.image(st.session_state['decoration_removed_bg'], 
                    caption="✨ ตัดพื้นหลังแล้ว", 
                    use_container_width=True)
        elif st.session_state['decoration_image']:
            st.image(st.session_state['decoration_image'], 
                    caption="📸 รูปต้นฉบับ", 
                    use_container_width=True)
        else:
            st.info("📌 ยังไม่มีการอัพโหลดรูป")
    
    else:
        # Show room result
        st.markdown('<h2 style="margin-top: 0; margin-bottom: 1.2rem; color: #1e293b;">🏁 ห้องของคุณ</h2>', unsafe_allow_html=True)
        
        try:
            display_image = st.session_state['room_image'].copy() if isinstance(st.session_state['room_image'], Image.Image) else st.session_state['room_image']
            
            if st.session_state['decoration_removed_bg']:
                st.markdown('<p style="margin: 0.5rem 0 1rem 0; font-weight: 600; color: #1e293b;">ปรับตำแหน่งและขนาด:</p>', unsafe_allow_html=True)
                col_x, col_y, col_s = st.columns(3, gap="small")
                with col_x:
                    pos_x = st.slider("X", 0.0, 1.0, 0.5, 0.05, label_visibility="collapsed")
                with col_y:
                    pos_y = st.slider("Y", 0.0, 1.0, 0.5, 0.05, label_visibility="collapsed")
                with col_s:
                    scale = st.slider("Size", 0.1, 1.0, 0.3, 0.05, label_visibility="collapsed")
                
                if isinstance(display_image, Image.Image):
                    display_image = overlay_decoration_on_room(display_image, st.session_state['decoration_removed_bg'], (pos_x, pos_y), scale)
            
            st.image(display_image, use_container_width=True)
            
        except Exception as e:
            st.error(f"❌ ไม่สามารถแสดงรูปได้")

# ============================================================
# RIGHT COLUMN - Actions & Details
# ============================================================
with col_action:
    st.markdown('<h2 style="margin-top: 0; margin-bottom: 1.2rem; color: #1e293b;">⚡ การจัดการ</h2>', unsafe_allow_html=True)
    
    # Create button
    create_btn = st.button("🚀 สร้างห้อง", type="primary", use_container_width=True, key="create_main")
    
    if st.session_state['room_image']:
        st.markdown('<div style="height: 1.5rem;"></div>', unsafe_allow_html=True)
        st.markdown("---")
        st.markdown('<div style="height: 0.5rem;"></div>', unsafe_allow_html=True)
        
        # 🛍️ Shopping Section
        if st.session_state['show_shopping']:
            st.markdown('<h3 style="margin: 0 0 1.2rem 0; color: #1e293b;">🛍️ ซื้อสินค้า</h3>', unsafe_allow_html=True)
            
            # แสดงสินค้าที่ตรวจจับได้
            if st.session_state['detected_products']:
                with st.expander("📋 สินค้าที่พบในห้อง", expanded=False):
                    for idx, product in enumerate(st.session_state['detected_products'].get('detected_products', []), 1):
                        st.markdown(f"<p style='margin: 0.5rem 0; font-weight: 600;'>{idx}. {product.get('name')}</p>", unsafe_allow_html=True)
                        st.caption(f"📍 ตำแหน่ง: {product.get('position')} • ความมั่นใจ: {product.get('confidence', 0)*100:.0f}%")
            
            # แสดงสินค้าแนะนำ
            if st.session_state['product_suggestions']:
                st.markdown('<p style="margin: 1rem 0 0.8rem 0; font-weight: 600; color: #1e293b;">🎯 สินค้าแนะนำสำหรับห้องของคุณ</p>', unsafe_allow_html=True)
                
                for category, products in st.session_state['product_suggestions'].items():
                    with st.expander(f"📦 {category.upper()} ({len(products)} สินค้า)", expanded=len(st.session_state['product_suggestions']) <= 2):
                        cols = st.columns(2)
                        for idx, product in enumerate(products):
                            show_product_card(product, cols[idx % 2])
            
            st.markdown('<div style="height: 1.5rem;"></div>', unsafe_allow_html=True)
            st.markdown("---")
            st.markdown('<div style="height: 0.5rem;"></div>', unsafe_allow_html=True)
            
            # 🛒 Shopping Cart
            st.markdown('<h3 style="margin: 0 0 1.2rem 0; color: #1e293b;">🛒 รถเข็นช้อปปิ้ง</h3>', unsafe_allow_html=True)
            if st.session_state['shopping_cart']:
                st.markdown(f"<p style='margin: 0 0 1rem 0; font-weight: 600; color: #1e293b;'>รวม {len(st.session_state['shopping_cart'])} สินค้า</p>", unsafe_allow_html=True)
                
                cart_items = []
                for item in st.session_state['shopping_cart']:
                    col1, col2, col3 = st.columns([2, 1, 1])
                    with col1:
                        st.write(f"• {item['name']}")
                    with col2:
                        st.write(f"฿{item['price']}")
                    with col3:
                        if st.button("❌", key=f"remove_{item['id']}", use_container_width=True):
                            st.session_state['shopping_cart'].remove(item)
                            st.rerun()
                    cart_items.append(item)
                
                # คำนวณและแสดงบัญชี
                st.markdown("---")
                budget_info = calculate_total_budget(st.session_state['shopping_cart'])
                
                col_total, col_items = st.columns(2)
                with col_total:
                    st.metric("💰 รวมทั้งสิ้น", f"฿{budget_info['total']:,}")
                with col_items:
                    st.metric("📦 จำนวนสินค้า", budget_info['items_count'])
                
                # ปุ่มชำระเงิน
                st.markdown("---")
                if st.button("✅ ดำเนินการสั่งซื้อ", type="primary", use_container_width=True):
                    st.success(f"""
                    🎉 **สั่งซื้อสำเร็จ!**
                    
                    📦 **จำนวนสินค้า:** {budget_info['items_count']}
                    💰 **รวมทั้งสิ้น:** ฿{budget_info['total']:,}
                    
                    ✅ กำลังอัพเดตคำสั่งซื้อของคุณ...
                    """)
                    st.balloons()
                    
                    # Clear cart after purchase
                    st.session_state['shopping_cart'] = []
                    st.toast("ขอบคุณที่ช้อปปิ้งกับเรา! 🙏")
                
                if st.button("🗑️ ล้างรถเข็น", use_container_width=True):
                    st.session_state['shopping_cart'] = []
                    st.rerun()
            else:
                st.info("📭 รถเข็นว่างเปล่า")
                st.markdown('<p style="color: #64748b; margin: 0;">เลือกสินค้าข้างบนเพื่อเพิ่มลงรถเข็น!</p>', unsafe_allow_html=True)
            
            st.markdown('<div style="height: 1.5rem;"></div>', unsafe_allow_html=True)
            st.markdown("---")
        
        st.markdown('<h3 style="margin: 1.2rem 0 1rem 0; color: #1e293b;">📋 รายละเอียด</h3>', unsafe_allow_html=True)
        with st.container(border=True):
            st.markdown(f"<p style='margin: 0.5rem 0; font-weight: 600; color: #1e293b;'>ประเภท</p><p style='color: #64748b; margin: 0 0 0.8rem 0;'>{st.session_state['room_type']}</p>", unsafe_allow_html=True)
            st.markdown(f"<p style='margin: 0.5rem 0; font-weight: 600; color: #1e293b;'>สไตล์</p><p style='color: #64748b; margin: 0 0 0.8rem 0;'>{st.session_state['room_style']}</p>", unsafe_allow_html=True)
            st.markdown(f"<p style='margin: 0.5rem 0; font-weight: 600; color: #1e293b;'>สี</p><p style='color: #64748b; margin: 0;'>{st.session_state['color_theme']}</p>", unsafe_allow_html=True)
            
            if st.session_state['furniture_list']:
                st.markdown('<div style="height: 1rem;"></div>', unsafe_allow_html=True)
                st.markdown("---")
                st.markdown(f"<p style='margin: 1rem 0 0.8rem 0; font-weight: 600; color: #1e293b;'>ไอเดียเฟอร์นิเจอร์ ({len(st.session_state['furniture_list'])})</p>", unsafe_allow_html=True)
                for idx, item in enumerate(st.session_state['furniture_list'], 1):
                    st.write(f"• {item}")
        
        st.markdown("---")
        
        if st.button("💾 ดาวน์โหลด", use_container_width=True):
            st.success("✅ คลิกขวาบนรูปแล้วเลือก\n'Save image as...'")
        
        if st.button("🔄 ออกแบบใหม่", use_container_width=True):
            st.session_state['room_image'] = None
            st.session_state['decoration_removed_bg'] = None
            st.session_state['detected_products'] = None
            st.session_state['product_suggestions'] = None
            st.session_state['shopping_cart'] = []
            st.session_state['show_shopping'] = False
            st.rerun()
        
        if st.session_state['decoration_removed_bg']:
            if st.button("✏️ เปลี่ยนตกแต่ง", use_container_width=True):
                st.session_state['decoration_removed_bg'] = None
                st.session_state['decoration_image'] = None
                st.rerun()
    
    else:
        st.markdown("---")
        
        if st.button("🔄 รีเซต", use_container_width=True):
            for key in session_defaults:
                st.session_state[key] = session_defaults[key]
            st.rerun()

# ============================================================
# Handle room creation
# ============================================================
if create_btn:
    if not st.session_state['room_type']:
        st.error("⚠️ กรุณาเลือกประเภทห้อง")
    else:
        with st.status("🔮 AI กำลังสร้างห้องเปล่าของคุณ...", expanded=True):
            try:
                furniture_str = ", ".join(st.session_state['furniture_list'])
                
                prompt = f"""
                Create a photorealistic, beautifully designed COMPLETELY EMPTY {st.session_state['room_type']} 
                with {st.session_state['room_style']} style and {st.session_state['color_theme'].lower()} color theme.
                
                The room should be:
                - Completely bare - NO furniture inside
                - Well-lit and inviting
                - Professional interior design quality
                - High resolution (8K)
                - Photorealistic with attention to textures, walls, floor, and ceiling materials
                - Ready for user to add custom decorations
                
                Additional style notes: {st.session_state['room_description'] or "None"}
                """
                
                st.write("📝 สร้าง Prompt...")
                st.write(f"**ห้อง:** {st.session_state['room_type']}")
                st.write(f"**สไตล์:** {st.session_state['room_style']}")
                st.write(f"**สี:** {st.session_state['color_theme']}")
                st.write(f"📌 *ห้องเปล่าเพื่อให้คุณตกแต่งด้วยตัวเอง*")
                
                result = generate_with_fallback(prompt)
                
                if result:
                    st.write("✅ สร้างเสร็จแล้ว!")
                    st.session_state['room_image'] = result
                    
                    # 🔍 ตรวจจับสินค้า/เฟอร์นิเจอร์ในห้อง
                    st.write("🔍 ตรวจจับสินค้าในห้อง...")
                    with st.spinner("⏳ AI กำลังวิเคราะห์เฟอร์นิเจอร์ที่พบในห้อง..."):
                        detected = detect_products_in_room(result)
                        st.session_state['detected_products'] = detected
                        
                        # 🛍️ ค้นหาสินค้าที่ซื้อได้
                        if detected and detected.get('detected_products'):
                            suggestions = get_product_suggestions(detected['detected_products'])
                            st.session_state['product_suggestions'] = suggestions
                    
                    st.write("✨ พร้อมให้คุณซื้อสินค้า!")
                    st.session_state['show_shopping'] = True
                    st.rerun()
                else:
                    st.error("❌ ไม่สามารถสร้างรูปได้")
                    
            except Exception as e:
                st.error(f"❌ เกิดข้อผิดพลาด: {str(e)}")
                st.info("💡 Tips: ลองใช้ Prompt สั้นลงหรือเลือกเฟอร์นิเจอร์น้อยลง")
import streamlit as st
from PIL import Image, ImageOps
import os
import io
import requests
import urllib.parse
from dotenv import load_dotenv
import time

# ==========================================
# 📦 การนำเข้าโมดูล & การจัดการ Library
# ==========================================
try:
    from product_shopping_utils import detect_products_in_room, get_product_suggestions
    SHOPPING_READY = True
except ImportError:
    SHOPPING_READY = False

try:
    from rembg import remove
    REMBG_AVAILABLE = True
except ImportError:
    REMBG_AVAILABLE = False

load_dotenv()

# ==========================================
# ⚙️ การตั้งค่าหน้าเพจหลัก
# ==========================================
st.set_page_config(
    page_title="AI Interior Studio Pro",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==========================================
# 🎨 ADVANCED CSS
# ==========================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Kanit:wght@300;400;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Kanit', sans-serif; }
    
    /* ควบคุมขนาดรูปภาพไม่ให้ล้นจอ */
    [data-testid="stImage"] img {
        max-height: 65vh !important;
        object-fit: contain !important;
        border-radius: 12px;
        box-shadow: 0 8px 16px rgba(0,0,0,0.1);
    }
    .thumb-img [data-testid="stImage"] img { max-height: 250px !important; border: 2px solid #E2E8F0; }

    /* Headers */
    .main-header { font-size: 2.5rem; font-weight: 800; background: linear-gradient(135deg, #4F46E5 0%, #EC4899 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 0px; }
    .sub-header { font-size: 1.1rem; color: #64748B; margin-bottom: 30px; }
    .panel-title { color: #1E293B; font-weight: 700; font-size: 1.2rem; border-bottom: 2px solid #E2E8F0; padding-bottom: 8px; margin-bottom: 15px; margin-top: 20px; }

    /* การ์ดสินค้า */
    .product-card { padding: 15px; border-radius: 12px; border: 1px solid #E2E8F0; background: #FFFFFF; margin-bottom: 15px; transition: all 0.3s ease; position: relative; overflow: hidden; }
    .product-card:hover { transform: translateY(-5px); box-shadow: 0 10px 20px rgba(0,0,0,0.08); border-color: #6366f1; }
    .product-card::before { content: ''; position: absolute; top: 0; left: 0; width: 4px; height: 100%; background: linear-gradient(to bottom, #6366f1, #ec4899); }
    .product-name { font-weight: 700; font-size:1.05rem; color:#1e293b; margin-bottom: 5px; }
    .product-price { color: #EC4899; font-weight: 800; font-size: 1.25rem; margin: 5px 0; }
    .product-store { font-size: 0.85rem; color: #64748b; margin-bottom: 10px; }

    /* UI Elements */
    .stButton > button[kind="primary"] { background: linear-gradient(135deg, #6366f1 0%, #ec4899 100%) !important; border: none !important; border-radius: 10px !important; color: white !important; font-weight: bold !important; height: 3.2rem !important; font-size: 1.1rem !important; box-shadow: 0 4px 15px rgba(99, 102, 241, 0.4); }
    .stButton > button[kind="primary"]:hover { transform: scale(1.02); box-shadow: 0 6px 20px rgba(99, 102, 241, 0.6); }
    .control-box { background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 10px; padding: 15px; margin-bottom: 10px; }
    .edit-box { background: #EEF2FF; border: 1px solid #C7D2FE; border-radius: 12px; padding: 20px; margin-top: 15px; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 🛠️ HELPER FUNCTIONS
# ==========================================
def overlay_multiple_decorations(bg_img, decor_items, configs):
    """ฟังก์ชันซ้อนภาพเฟอร์นิเจอร์"""
    try:
        bg = bg_img.copy().convert('RGBA')
        for decor, config in zip(decor_items, configs):
            if decor is None: continue
            d_rgba = decor.convert('RGBA')
            scale, x_ratio, y_ratio = config.get('scale', 0.35), config.get('x', 0.5), config.get('y', 0.7)
            
            bg_w, bg_h = bg.size
            decor_w = int(bg_w * scale)
            decor_h = int(decor_w * (d_rgba.size[1] / d_rgba.size[0]))
            
            decor_resized = d_rgba.resize((decor_w, decor_h), Image.Resampling.LANCZOS)
            x, y = int(bg_w * x_ratio - decor_w / 2), int(bg_h * y_ratio - decor_h / 2)
            bg.paste(decor_resized, (x, y), decor_resized)
        return bg.convert('RGB')
    except Exception as e:
        return bg_img.convert('RGB')

def fix_image_orientation(image):
    try: return ImageOps.exif_transpose(image)
    except: return image

def calculate_auto_layout(num_items):
    """🤖 ระบบ Auto-Placement: คำนวณตำแหน่งให้กระจายกันอย่างสมดุล"""
    for i in range(num_items):
        st.session_state[f"x_{i}"] = 0.5 if num_items == 1 else 0.2 + (0.6 * (i / (num_items - 1)))
        st.session_state[f"y_{i}"] = 0.75 # วางไว้ระดับพื้น
        st.session_state[f"s_{i}"] = 0.35 # ขนาดมาตรฐาน

# ==========================================
# 💾 SESSION STATE
# ==========================================
default_states = {
    'base_room': None, 'ai_room_img': None, 'final_image': None,
    'decor_items': [], 'uploaded_decor_names': [],
    'base_prompt': "", 'current_prompt': ""
}
for k, v in default_states.items():
    if k not in st.session_state: st.session_state[k] = v

# ==========================================
# 🏠 MAIN UI & LAYOUT
# ==========================================
st.markdown('<div class="main-header">🏠 AI Interior Studio Pro</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">อัพโหลดห้อง > เลือกสไตล์ > AI จัดวางเฟอร์นิเจอร์อัตโนมัติ > สั่งแก้รูปได้ดั่งใจ > ช้อปปิ้ง</div>', unsafe_allow_html=True)

left_panel, right_panel = st.columns([1, 2.3], gap="large")

# ==========================================
# 🎛️ ฝั่งซ้าย: แผงควบคุม (CONTROLS PANEL)
# ==========================================
with left_panel:
    st.markdown('<div class="panel-title">1️⃣ รูปห้องปัจจุบันของคุณ</div>', unsafe_allow_html=True)
    room_upload = st.file_uploader("ถ่ายรูปห้องเปล่า หรือห้องปัจจุบัน", type=['png', 'jpg', 'jpeg'])
    if room_upload:
        st.session_state.base_room = fix_image_orientation(Image.open(room_upload))
        st.markdown('<div class="thumb-img">', unsafe_allow_html=True)
        st.image(st.session_state.base_room, caption="รูปห้องต้นฉบับ", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="panel-title">2️⃣ เลือกสไตล์ที่ต้องการ</div>', unsafe_allow_html=True)
    col_s1, col_s2 = st.columns(2)
    with col_s1: room_style = st.selectbox("สไตล์ห้อง", ["Modern", "Japandi", "Minimalist", "Scandinavian", "Industrial Loft", "Luxury", "Vintage"])
    with col_s2: color_theme = st.selectbox("โทนสีหลัก", ["Warm", "Neutral", "Dark & Bold", "Earthy", "Pastel"])

    st.markdown('<div class="panel-title">3️⃣ อัพโหลดเฟอร์นิเจอร์เสริม</div>', unsafe_allow_html=True)
    st.caption("อัพโหลดได้หลายชิ้น (AI จะตัดพื้นหลัง & จัดวางให้อัตโนมัติ)")
    decor_uploads = st.file_uploader("ลากไฟล์มาวางตรงนี้", type=['png', 'jpg', 'jpeg'], accept_multiple_files=True)
    
    if decor_uploads:
        current_names = [f.name for f in decor_uploads]
        if current_names != st.session_state.uploaded_decor_names:
            st.session_state.uploaded_decor_names = current_names
            st.session_state.decor_items = [] 
            if REMBG_AVAILABLE:
                my_bar = st.progress(0, text="✂️ กำลังตัดพื้นหลังเฟอร์นิเจอร์...")
                for i, file in enumerate(decor_uploads):
                    st.session_state.decor_items.append(remove(fix_image_orientation(Image.open(file))))
                    my_bar.progress((i + 1) / len(decor_uploads), text=f"ตัดสำเร็จ {i+1}/{len(decor_uploads)} ชิ้น")
                time.sleep(0.5); my_bar.empty()
                # 🤖 สั่งให้ AI คำนวณ Auto-layout ทันทีที่อัพโหลดเสร็จ
                calculate_auto_layout(len(st.session_state.decor_items))
            else:
                st.error("⚠️ ขาด Library 'rembg'")
    elif not decor_uploads and st.session_state.decor_items:
        st.session_state.decor_items = []
        st.session_state.uploaded_decor_names = []

    if st.session_state.decor_items:
        d_cols = st.columns(min(len(st.session_state.decor_items), 4))
        for i, decor in enumerate(st.session_state.decor_items):
            with d_cols[i % 4]: st.image(decor, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🚀 เนรมิตห้องในฝัน", type="primary", use_container_width=True):
        if not st.session_state.base_room:
            st.warning("⚠️ โปรดอัพโหลดรูปห้องที่แผงซ้ายก่อนครับ", icon="👈")
        else:
            with st.spinner("🔮 AI กำลังสร้างห้อง และจัดวางเฟอร์นิเจอร์..."):
                # สร้าง Prompt เริ่มต้น
                prompt = f"Photorealistic interior design, beautiful {room_style} style room, {color_theme} color palette, cinematic lighting, ultra realistic, 8k resolution"
                st.session_state.base_prompt = prompt
                st.session_state.current_prompt = prompt
                
                url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(prompt)}?width=1280&height=720&nologo=true"
                try:
                    res = requests.get(url, timeout=60)
                    if res.status_code == 200: st.session_state.ai_room_img = Image.open(io.BytesIO(res.content))
                except Exception as e: st.error(f"⚠️ Error: {e}")

# ==========================================
# 🖼️ ฝั่งขวา: พื้นที่ทำงาน (WORKSPACE)
# ==========================================
with right_panel:
    if st.session_state.ai_room_img:
        st.markdown('<div class="panel-title" style="margin-top:0;">✨ ผลลัพธ์ห้องของคุณ (พร้อม Auto-Layout)</div>', unsafe_allow_html=True)
        
        # ------------------------------------------
        # 🤖 นำ Auto-Layout Configurations มาใช้ 
        # ------------------------------------------
        configs = []
        if st.session_state.decor_items:
            # เช็คว่ามีค่าใน Session State หรือยัง ถ้ายังให้คำนวณใหม่
            if f"x_0" not in st.session_state:
                calculate_auto_layout(len(st.session_state.decor_items))
                
            # สร้างตัวเลื่อนที่ซ่อนได้ เผื่อผู้ใช้ต้องการปรับแต่ง (Fine-tune)
            with st.expander("🛠️ ปรับแต่งตำแหน่งเฟอร์นิเจอร์เพิ่มเติม (คลิกเพื่อเปิด)"):
                st.caption("AI จัดวางตำแหน่งเริ่มต้นให้อัตโนมัติแล้ว คุณสามารถเลื่อนปรับความเนียนได้ตามต้องการ")
                for i, decor in enumerate(st.session_state.decor_items):
                    st.markdown(f'<div class="control-box"><strong>📌 ชิ้นที่ {i+1}</strong>', unsafe_allow_html=True)
                    cx, cy, cs = st.columns(3)
                    with cx: px = st.slider("↔️ X", 0.0, 1.0, key=f"x_{i}", label_visibility="collapsed")
                    with cy: py = st.slider("↕️ Y", 0.0, 1.0, key=f"y_{i}", label_visibility="collapsed")
                    with cs: scale = st.slider("🔍 Size", 0.1, 1.5, key=f"s_{i}", label_visibility="collapsed")
                    configs.append({'x': px, 'y': py, 'scale': scale})
                    st.markdown('</div>', unsafe_allow_html=True)
            
            # รวมภาพ
            st.session_state.final_image = overlay_multiple_decorations(st.session_state.ai_room_img, st.session_state.decor_items, configs)
        else:
            st.session_state.final_image = st.session_state.ai_room_img

        # 🖼️ โชว์ภาพไฟนอล
        st.image(st.session_state.final_image, use_container_width=True)
        
        # ------------------------------------------
        # 💬 ระบบสั่งแก้รูปภาพ (ITERATIVE EDITING)
        # ------------------------------------------
        st.markdown("""
        <div class="edit-box">
            <h4 style="margin-top:0; color:#4F46E5;">💬 สั่ง AI ให้แก้ไขรูปภาพนี้</h4>
            <p style="color:#64748B; font-size:0.95rem; margin-bottom:15px;">ไม่ถูกใจตรงไหนพิมพ์บอกได้เลย เช่น "เปลี่ยนพรมเป็นสีแดง", "เปลี่ยนเป็นบรรยากาศกลางคืน", "เพิ่มหน้าต่างบานใหญ่"</p>
        </div>
        """, unsafe_allow_html=True)
        
        # ช่องแชทสำหรับแก้ไข
        col_edit1, col_edit2 = st.columns([4, 1])
        with col_edit1:
            edit_instruction = st.text_input("พิมพ์คำสั่งที่ต้องการแก้ไข...", key="edit_input", label_visibility="collapsed", placeholder="เช่น เปลี่ยนโซฟาเป็นหนังสีดำ...")
        with col_edit2:
            update_btn = st.button("✨ อัปเดตห้อง", use_container_width=True)
            
        if update_btn and edit_instruction:
            with st.spinner(f"✨ AI กำลังปรับแก้รูปภาพตามคำสั่ง: '{edit_instruction}'..."):
                # นำ Prompt เดิม มาต่อท้ายด้วยคำสั่งใหม่ เพื่อให้คงความเกี่ยวเนื่องเดิมไว้
                new_prompt = st.session_state.current_prompt + f", AND apply this specific change: {edit_instruction}"
                st.session_state.current_prompt = new_prompt
                
                edit_url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(new_prompt)}?width=1280&height=720&nologo=true"
                try:
                    res = requests.get(edit_url, timeout=60)
                    if res.status_code == 200:
                        st.session_state.ai_room_img = Image.open(io.BytesIO(res.content))
                        st.rerun() # สั่งรีโหลดหน้าเพื่ออัปเดตภาพใหม่
                except Exception as e:
                    st.error("เกิดข้อผิดพลาดในการแก้ไขรูปภาพ")
        
        # ------------------------------------------
        # 🛒 ระบบช้อปปิ้งออนไลน์
        # ------------------------------------------
        st.markdown('<br><div class="panel-title">🛒 ช้อปปิ้งเฟอร์นิเจอร์ในห้อง (AI Recommendations)</div>', unsafe_allow_html=True)
        if SHOPPING_READY:
            with st.spinner("🤖 Gemini กำลังสแกนรูปเพื่อค้นหาสินค้า..."):
                detected = detect_products_in_room(st.session_state.final_image)
                suggestions = get_product_suggestions(detected.get('detected_products', []))
                
                if suggestions:
                    shop_cols = st.columns(3)
                    idx = 0
                    for cat, items in suggestions.items():
                        for item in items[:2]:
                            with shop_cols[idx % 3]:
                                st.markdown(f"""
                                <div class="product-card">
                                    <div class="product-name">🛋️ {item['name']}</div>
                                    <div class="product-price">฿{item['price']:,}</div>
                                    <div class="product-store">📍 {item['store']}</div>
                                </div>
                                """, unsafe_allow_html=True)
                                st.link_button("👉 สั่งซื้อสินค้านี้", item['link'], use_container_width=True)
                            idx += 1
                else:
                    st.info("ℹ️ ไม่พบสินค้าที่ตรงกับฐานข้อมูลในขณะนี้")
    else:
        st.info("👋 ยินดีต้อนรับ! กรุณาตั้งค่าห้องที่แผงควบคุมด้านซ้าย แล้วกดปุ่ม **'เนรมิตห้องในฝัน'** เพื่อเริ่มต้นครับ")
        st.markdown('<div style="text-align:center; padding: 50px; background:#F8FAFC; border-radius:15px; border:2px dashed #CBD5E1;"><h1 style="font-size:4rem; margin:0;">🛋️</h1><p style="color:#94A3B8; font-size:1.2rem;">พื้นที่แสดงผล (Canvas)</p></div>', unsafe_allow_html=True)
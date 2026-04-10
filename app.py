import streamlit as st
from PIL import Image
import os
import requests
import base64
import time
import json
import io
from vision_utils import analyze_room
from prompt_utils import build_design_prompt
from image_gen_utils import generate_design, recommend_furniture_and_palette

# --- Page Configuration ---
st.set_page_config(
    page_title="AI Interior Designer | Professional Design Studio",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- Premium Editorial CSS Styling ---
st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;800&family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    
    <style>
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }
    
    html, body, [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #faf8f6 0%, #f5f1ed 100%);
        font-family: 'Inter', sans-serif;
    }
    
    .main {
        background: transparent !important;
        padding: 0 !important;
    }
    

    
    /* Input Section */
    .input-section {
        padding: 3em 2em;
        max-width: 1600px;
        margin: 0 auto;
    }
    
    .section-header {
        font-family: 'Playfair Display', serif;
        font-size: 2em;
        font-weight: 700;
        color: #2c2c2c;
        margin-bottom: 2em;
        letter-spacing: -0.01em;
    }
    
    .input-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 3em;
        margin-bottom: 3em;
    }
    
    .input-card {
        background: white;
        border-radius: 12px;
        padding: 2.5em;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
        border: 1px solid rgba(0, 0, 0, 0.05);
        transition: all 0.3s ease;
    }
    
    .input-card:hover {
        box-shadow: 0 16px 48px rgba(0, 0, 0, 0.12);
        transform: translateY(-2px);
    }
    
    .card-title {
        font-family: 'Playfair Display', serif;
        font-size: 1.5em;
        font-weight: 700;
        color: #2c2c2c;
        margin-bottom: 1.5em;
        display: flex;
        align-items: center;
        gap: 0.5em;
    }
    
    .stFileUploader {
        background: linear-gradient(135deg, #f9f7f4 0%, #f5f1ed 100%);
        border-radius: 8px;
        padding: 1.5em;
        margin-bottom: 1.5em;
        border: 2px dashed #d4ccc4;
        transition: all 0.3s ease;
    }
    
    .stFileUploader:hover {
        border-color: #8b7355;
        background: linear-gradient(135deg, #faf8f6 0%, #f7f3ee 100%);
    }
    
    .stButton>button {
        width: 100%;
        height: 3em;
        border-radius: 8px;
        background: linear-gradient(135deg, #8b7355 0%, #6b5344 100%);
        color: white;
        font-weight: 600;
        border: none;
        font-size: 1em;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(139, 115, 85, 0.2);
    }
    
    .stButton>button:hover {
        background: linear-gradient(135deg, #6b5344 0%, #4b3334 100%);
        box-shadow: 0 8px 24px rgba(139, 115, 85, 0.3);
        transform: translateY(-2px);
    }
    
    .stSelectbox, .stTextArea {
        font-size: 0.95em;
    }
    
    /* Results Container */
    .results-container {
        display: grid;
        grid-template-columns: 1fr 1fr;
        min-height: 100vh;
        background: white;
        gap: 0;
    }
    
    .results-left {
        background: linear-gradient(135deg, #e8e4df 0%, #ddd9d4 100%);
        padding: 5em 3em;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        position: relative;
        overflow: hidden;
    }
    

    
    .results-left::after {
        content: '';
        position: absolute;
        bottom: -50%;
        right: -50%;
        width: 100%;
        height: 100%;
        background: radial-gradient(circle, rgba(255, 255, 255, 0.1) 0%, transparent 70%);
        pointer-events: none;
    }
    
    .images-gallery {
        display: flex;
        gap: 2.5em;
        justify-content: center;
        flex-wrap: wrap;
        position: relative;
        z-index: 2;
    }
    
    .image-showcase {
        flex: 0 1 320px;
        text-align: center;
    }
    
    .image-frame {
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
        background: white;
        margin-bottom: 1.2em;
        transition: all 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
        position: relative;
    }
    
    .image-frame:hover {
        transform: translateY(-12px);
        box-shadow: 0 30px 80px rgba(0, 0, 0, 0.25);
    }
    
    .image-frame img {
        width: 100%;
        height: auto;
        display: block;
    }
    
    .image-label {
        font-family: 'Inter', sans-serif;
        font-size: 0.8em;
        color: #666;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.1em;
    }
    
    .results-right {
        background: white;
        padding: 5em 3em;
        display: flex;
        flex-direction: column;
        justify-content: center;
        position: relative;
    }
    
    .results-right::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 1px;
        background: linear-gradient(90deg, transparent, #e0dcd7, transparent);
    }
    
    .result-title {
        font-family: 'Playfair Display', serif;
        font-size: 2.8em;
        font-weight: 800;
        color: #2c2c2c;
        margin-bottom: 1.5em;
        letter-spacing: -0.02em;
        line-height: 1.2;
    }
    
    .result-description {
        font-size: 0.95em;
        line-height: 1.9;
        color: #555;
        margin-bottom: 2em;
    }
    
    .result-description p {
        margin-bottom: 1.2em;
    }
    
    .result-description strong {
        color: #2c2c2c;
        font-weight: 600;
    }
    
    /* Specification Section */
    .specification-section {
        margin-top: 2.5em;
        padding-top: 2.5em;
        border-top: 2px solid #e0dcd7;
    }
    
    .spec-title {
        font-family: 'Playfair Display', serif;
        font-size: 1.3em;
        font-weight: 700;
        color: #2c2c2c;
        margin-bottom: 1.5em;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    .spec-item {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 1em;
        padding: 1em 0;
        border-bottom: 1px solid #f0ebe6;
        align-items: center;
    }
    
    .spec-item:last-child {
        border-bottom: none;
    }
    
    .spec-label {
        font-weight: 600;
        color: #2c2c2c;
        font-size: 0.9em;
    }
    
    .spec-value {
        color: #666;
        font-size: 0.9em;
    }
    
    .download-button {
        margin-top: 2.5em;
        padding: 1.2em 2em;
        background: linear-gradient(135deg, #8b7355 0%, #6b5344 100%);
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        font-size: 0.95em;
        cursor: pointer;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(139, 115, 85, 0.2);
    }
    
    .download-button:hover {
        background: linear-gradient(135deg, #6b5344 0%, #4b3334 100%);
        box-shadow: 0 8px 24px rgba(139, 115, 85, 0.3);
        transform: translateY(-2px);
    }
    
    /* Responsive */
    @media (max-width: 1200px) {
        .input-grid {
            grid-template-columns: 1fr;
        }
        
        .results-container {
            grid-template-columns: 1fr;
        }
        
        .results-left, .results-right {
            padding: 3em 2em;
            min-height: auto;
        }
        
        .header-title {
            font-size: 2.5em;
        }
        
        .result-title {
            font-size: 2em;
        }
    }
    
    @media (max-width: 768px) {
        .images-gallery {
            flex-direction: column;
        }
        
        .image-showcase {
            flex: 0 1 100%;
        }
        
        .spec-item {
            grid-template-columns: 1fr;
        }
    }
    </style>
    """, unsafe_allow_html=True)

# --- Session State Management ---
def init_session():
    if 'image_bytes' not in st.session_state:
        st.session_state['image_bytes'] = None
    if 'last_file_name' not in st.session_state:
        st.session_state['last_file_name'] = None
    if 'analysis' not in st.session_state:
        st.session_state['analysis'] = None
    if 'imgbb_url' not in st.session_state:
        st.session_state['imgbb_url'] = None
    if 'result_image' not in st.session_state:
        st.session_state['result_image'] = None
    if 'recommendations' not in st.session_state:
        st.session_state['recommendations'] = None
    if 'image_dims' not in st.session_state:
        st.session_state['image_dims'] = (1024, 768)
    if 'selected_style' not in st.session_state:
        st.session_state['selected_style'] = None

init_session()

# --- Helper Function: Upload Image to ImgBB ---
def upload_to_imgbb(image_bytes):
    if not image_bytes:
        return None
    
    api_keys = [
        "533f07276d994ec8350b6177fb133a0d",
        "6d207e021112d492d03f842280a32101",
        "c8798933668868868868868868868868",
        "e1f2g3h4i5j6k7l8m9n0o1p2q3r4s5t6",
        "u7v8w9x0y1z2a3b4c5d6e7f8g9h0i1j2"
    ]
    
    for api_key in api_keys:
        try:
            url = "https://api.imgbb.com/1/upload"
            payload = {
                "key": api_key,
                "image": base64.b64encode(image_bytes),
            }
            res = requests.post(url, payload, timeout=15)
            if res.status_code == 200:
                return res.json()["data"]["url"]
            elif res.status_code == 400 and "quota exceeded" in res.text.lower():
                continue
            else:
                continue
        except:
            continue
            
    st.error("❌ ไม่สามารถอัปโหลดรูปภาพได้ กรุณาลองใหม่อีกครั้ง")
    return None



# --- Main Content ---
st.markdown('<div class="input-section">', unsafe_allow_html=True)

st.markdown('<h2 class="section-header">Design Your Space</h2>', unsafe_allow_html=True)

st.markdown('<div class="input-grid">', unsafe_allow_html=True)

# Left Column
st.markdown('<div class="input-card">', unsafe_allow_html=True)
st.markdown('<div class="card-title">📸 Step 1: Upload Your Room</div>', unsafe_allow_html=True)

uploaded_file = st.file_uploader("Choose an image of your room (JPG, PNG)", type=["jpg", "jpeg", "png"], label_visibility="collapsed")

if uploaded_file:
    if uploaded_file.name != st.session_state['last_file_name']:
        st.session_state['image_bytes'] = uploaded_file.getvalue()
        st.session_state['last_file_name'] = uploaded_file.name
        st.session_state['analysis'] = None
        st.session_state['imgbb_url'] = None
        st.session_state['result_image'] = None
        st.session_state['recommendations'] = None
        
        img = Image.open(io.BytesIO(st.session_state['image_bytes']))
        st.session_state['image_dims'] = img.size
        st.rerun()

if st.session_state['image_bytes']:
    st.image(st.session_state['image_bytes'], caption="Original Room", use_container_width=True)
    
    room_type_options = ["Living Room", "Bedroom", "Kitchen", "Bathroom", "Office", "Dining Room", "Studio"]
    selected_room_type = st.selectbox("Room Type", room_type_options, label_visibility="collapsed")
    
    if st.button("🔍 Analyze Room"):
        with st.spinner("Analyzing room structure..."):
            img_obj = Image.open(io.BytesIO(st.session_state['image_bytes']))
            analysis = analyze_room(img_obj)
            
            if "room_metadata" in analysis:
                analysis["room_metadata"]["room_type"] = selected_room_type
            
            st.session_state['analysis'] = analysis
            st.session_state['imgbb_url'] = upload_to_imgbb(st.session_state['image_bytes'])
            st.success("✅ Analysis Complete!")

st.markdown('</div>', unsafe_allow_html=True)

# Right Column
st.markdown('<div class="input-card">', unsafe_allow_html=True)
st.markdown('<div class="card-title">✨ Step 2: Choose Style & Design</div>', unsafe_allow_html=True)

if st.session_state['analysis']:
    analysis = st.session_state['analysis']
    room_type = analysis.get("room_metadata", {}).get("room_type", "unknown")
    
    st.markdown(f"**✓ Detected Room:** {room_type}")
    
    with st.expander("📋 View Analysis Details", expanded=False):
        st.json(analysis)
    
    st.markdown("---")
    
    interior_style = st.selectbox(
        "Design Style",
        ["Minimalist", "Modern Luxury", "Industrial", "Scandinavian", "Japanese Zen", "Bohemian"],
        label_visibility="collapsed"
    )
    st.session_state['selected_style'] = interior_style
    
    custom_prompt = st.text_area("Additional Notes (Optional)", placeholder="e.g., 'Focus on white and wood', 'Add more plants'", height=80, label_visibility="collapsed")
    
    if st.button("✨ Generate Design"):
        if not st.session_state['imgbb_url']:
            with st.spinner("Uploading image..."):
                st.session_state['imgbb_url'] = upload_to_imgbb(st.session_state['image_bytes'])
        
        if st.session_state['imgbb_url']:
            with st.spinner(f"Creating {interior_style} design..."):
                metadata = analysis.get("room_metadata", {})
                detailed_narrative = analysis.get("detailed_narrative", "")
                furniture_list = [f"{f.get('item')} at {f.get('position')}" for f in analysis.get("furniture_mapping", [])]
                
                design_prompt = build_design_prompt(
                    metadata.get("room_type", "room"),
                    interior_style,
                    furniture_list,
                    analysis.get("structural_elements", {}).get("walls", "white"),
                    analysis.get("lighting_and_atmosphere", {}).get("natural_light", "unknown"),
                    f"{custom_prompt}. {detailed_narrative}"
                )
                
                width, height = st.session_state['image_dims']
                result_url = generate_design(design_prompt, st.session_state['imgbb_url'], width, height)
                
                if result_url:
                    st.session_state['result_image'] = result_url
                    st.session_state['recommendations'] = recommend_furniture_and_palette(design_prompt)
                    st.rerun()
                else:
                    st.error("Unable to generate design. Please try again.")
        else:
            st.error("❌ Failed to upload image")

else:
    st.info("📌 Upload an image and click 'Analyze Room' to get started")

st.markdown('</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# --- Results Display ---
if st.session_state['result_image']:
    st.markdown('<div class="results-container">', unsafe_allow_html=True)
    
    # Left Side
    st.markdown('<div class="results-left">', unsafe_allow_html=True)
    st.markdown('<div class="images-gallery">', unsafe_allow_html=True)
    
    st.markdown('<div class="image-showcase">', unsafe_allow_html=True)
    st.markdown('<div class="image-frame">', unsafe_allow_html=True)
    st.image(st.session_state['image_bytes'], use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div class="image-label">BEFORE</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="image-showcase">', unsafe_allow_html=True)
    st.markdown('<div class="image-frame">', unsafe_allow_html=True)
    st.image(st.session_state['result_image'], use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div class="image-label">AFTER</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Right Side
    st.markdown('<div class="results-right">', unsafe_allow_html=True)
    
    st.markdown('<h2 class="result-title">Design Solution</h2>', unsafe_allow_html=True)
    
    if st.session_state['recommendations']:
        st.markdown(f'<div class="result-description">{st.session_state["recommendations"]}</div>', unsafe_allow_html=True)
    
    st.markdown("""
        <div class="specification-section">
            <h3 class="spec-title">Design Specifications</h3>
            <div class="spec-item">
                <span class="spec-label">Design Style</span>
                <span class="spec-value">""" + st.session_state.get('selected_style', 'N/A') + """</span>
            </div>
            <div class="spec-item">
                <span class="spec-label">Room Type</span>
                <span class="spec-value">""" + st.session_state.get('analysis', {}).get('room_metadata', {}).get('room_type', 'N/A') + """</span>
            </div>
            <div class="spec-item">
                <span class="spec-label">Design Tool</span>
                <span class="spec-value">AI Interior Studio v1.0</span>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f'<a href="{st.session_state["result_image"]}" target="_blank"><button class="download-button">📥 Download Design</button></a>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.title("⚙️ Settings")
    
    if st.button("🔄 Clear All Data"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
    
    st.markdown("---")
    st.markdown("**About This App**")
    st.markdown("""
    **AI Interior Design Studio** is a professional tool that helps you:
    - 📸 Upload photos of your room
    - 🤖 Analyze room structure with AI
    - 🎨 Choose from multiple design styles
    - ✨ Generate beautiful interior designs
    - 💾 Download high-quality results
    """)

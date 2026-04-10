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
    page_title="AI Interior Designer",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- Premium Interior Design Studio CSS Styling ---
st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;800;900&family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    
    <style>
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }
    
    html, body, [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #fafafa 0%, #ffffff 100%);
        font-family: 'Inter', sans-serif;
    }
    
    .main {
        background: linear-gradient(135deg, #fafafa 0%, #ffffff 100%) !important;
        padding: 0 !important;
    }
    
    /* Hero Section */
    .hero-section {
        background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
        color: white;
        padding: 6em 2em;
        text-align: center;
        border-bottom: 1px solid rgba(212, 175, 110, 0.3);
    }
    
    .hero-title {
        font-family: 'Playfair Display', serif;
        font-size: 3.5em;
        font-weight: 900;
        margin-bottom: 0.8em;
        letter-spacing: -0.02em;
        background: linear-gradient(135deg, #d4af6e 0%, #e8c547 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .hero-subtitle {
        font-size: 1.3em;
        font-weight: 300;
        color: #cccccc;
        margin-bottom: 2em;
        letter-spacing: 0.05em;
    }
    
    /* AI Analysis Section */
    .analysis-section {
        background: linear-gradient(135deg, #f9f7f4 0%, #ffffff 100%);
        padding: 3em 2em;
        margin: 2em 0;
        border-radius: 20px;
        border-left: 5px solid #d4af6e;
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.08);
    }
    
    .analysis-title {
        font-family: 'Playfair Display', serif;
        font-size: 1.5em;
        font-weight: 800;
        color: #1a1a1a !important;
        margin-bottom: 1.5em;
        display: flex;
        align-items: center;
        gap: 0.8em;
    }
    
    .analysis-content {
        font-size: 0.95em;
        line-height: 1.8;
        color: #333333 !important;
    }
    
    .analysis-content p {
        margin-bottom: 1em;
    }
    
    .analysis-highlight {
        background: linear-gradient(135deg, rgba(212, 175, 110, 0.1) 0%, rgba(232, 197, 71, 0.1) 100%);
        padding: 1.5em;
        border-radius: 12px;
        margin: 1.5em 0;
        border-left: 3px solid #d4af6e;
    }
    
    .hero-cta {
        display: inline-block;
        padding: 1em 2.5em;
        background: linear-gradient(135deg, #d4af6e 0%, #e8c547 100%);
        color: #1a1a1a;
        border: none;
        border-radius: 50px;
        font-weight: 700;
        font-size: 1.1em;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 10px 30px rgba(212, 175, 110, 0.3);
    }
    
    .hero-cta:hover {
        transform: translateY(-3px);
        box-shadow: 0 15px 40px rgba(212, 175, 110, 0.4);
    }
    
    /* Steps Guide */
    .steps-guide {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 2em;
        padding: 4em 2em;
        max-width: 1400px;
        margin: 0 auto;
        background: linear-gradient(135deg, #fafafa 0%, #ffffff 100%);
    }
    
    .step-card {
        background: white;
        border-radius: 16px;
        padding: 2.5em;
        text-align: center;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
        border: 1px solid #f0f0f0;
        transition: all 0.3s ease;
        position: relative;
    }
    
    .step-card::before {
        content: attr(data-step);
        position: absolute;
        top: -15px;
        left: 50%;
        transform: translateX(-50%);
        width: 40px;
        height: 40px;
        background: linear-gradient(135deg, #d4af6e 0%, #e8c547 100%);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        color: #1a1a1a;
        font-size: 1.2em;
    }
    
    .step-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.12);
        border-color: #d4af6e;
    }
    
    .step-icon {
        font-size: 3em;
        margin-bottom: 1em;
    }
    
    .step-title {
        font-family: 'Playfair Display', serif;
        font-size: 1.5em;
        font-weight: 700;
        color: #1a1a1a;
        margin-bottom: 0.8em;
    }
    
    .step-description {
        font-size: 0.95em;
        color: #666666;
        line-height: 1.6;
    }
    
    /* Input Section */
    .input-section {
        padding: 3em 2em;
        max-width: 1400px;
        margin: 0 auto;
        background: linear-gradient(135deg, #fafafa 0%, #ffffff 100%);
    }
    
    .section-header {
        font-family: 'Playfair Display', serif;
        font-size: 2.5em;
        font-weight: 800;
        color: #1a1a1a !important;
        margin-bottom: 2.5em;
        letter-spacing: -0.01em;
        line-height: 1.2;
        text-align: center;
    }
    
    .section-header::after {
        content: '';
        display: block;
        width: 60px;
        height: 3px;
        background: linear-gradient(135deg, #d4af6e 0%, #e8c547 100%);
        margin: 1em auto 0;
        border-radius: 2px;
    }
    
    .input-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 3em;
        margin-bottom: 2em;
    }
    
    .input-card {
        background: white;
        border-radius: 20px;
        padding: 3em;
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.08);
        border: 2px solid #f5f5f5;
        transition: all 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
        position: relative;
        overflow: hidden;
    }
    
    .input-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(212, 175, 110, 0.1), transparent);
        transition: left 0.5s ease;
    }
    
    .input-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 20px 50px rgba(0, 0, 0, 0.12);
        border-color: #d4af6e;
    }
    
    .input-card:hover::before {
        left: 100%;
    }
    
    .card-title {
        font-family: 'Playfair Display', serif;
        font-size: 1.8em;
        font-weight: 800;
        color: #1a1a1a !important;
        margin-bottom: 1.5em;
        display: flex;
        align-items: center;
        gap: 0.8em;
    }
    
    .stFileUploader {
        background: linear-gradient(135deg, #fafafa 0%, #f5f5f5 100%);
        border-radius: 16px;
        padding: 2.5em;
        margin-bottom: 1.5em;
        border: 2px dashed #d4af6e;
        transition: all 0.3s ease;
    }
    
    .stFileUploader:hover {
        border-color: #e8c547;
        background: linear-gradient(135deg, #ffffff 0%, #fafafa 100%);
        box-shadow: 0 8px 20px rgba(212, 175, 110, 0.15);
    }
    
    .stButton>button {
        width: 100%;
        height: 3.5em;
        border-radius: 12px;
        background: linear-gradient(135deg, #d4af6e 0%, #e8c547 100%);
        color: #1a1a1a;
        font-weight: 700;
        border: none;
        font-size: 1em;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 8px 25px rgba(212, 175, 110, 0.25);
    }
    
    .stButton>button:hover {
        background: linear-gradient(135deg, #e8c547 0%, #d4af6e 100%);
        box-shadow: 0 12px 35px rgba(212, 175, 110, 0.35);
        transform: translateY(-2px);
    }
    
    .stSelectbox, .stTextArea {
        font-size: 0.95em;
    }
    
    .stSelectbox>div>div {
        background: white;
        border: 2px solid #e8e8e8;
        border-radius: 10px;
        color: #1a1a1a !important;
    }
    
    .stTextArea>div>div {
        background: white;
        border: 2px solid #e8e8e8;
        border-radius: 10px;
        color: #1a1a1a !important;
    }
    
    /* Info Box */
    .stInfo {
        background: linear-gradient(135deg, #f0f4ff 0%, #f5f0ff 100%);
        border-left: 4px solid #d4af6e;
        border-radius: 12px;
        padding: 1.5em;
        margin: 1.5em 0;
    }
    
    .stSuccess {
        background: linear-gradient(135deg, #f0fdf4 0%, #f5fff0 100%);
        border-left: 4px solid #22c55e;
        border-radius: 12px;
        padding: 1.5em;
        margin: 1.5em 0;
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
        background: linear-gradient(135deg, #f5f5f5 0%, #ffffff 100%);
        padding: 5em 3em;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        position: relative;
        overflow: hidden;
        border-right: 2px solid #e8e8e8;
    }
    
    .results-left::after {
        content: '';
        position: absolute;
        bottom: -50%;
        right: -50%;
        width: 100%;
        height: 100%;
        background: radial-gradient(circle, rgba(212, 175, 110, 0.08) 0%, transparent 70%);
        pointer-events: none;
    }
    
    .images-gallery {
        display: flex;
        gap: 3em;
        justify-content: center;
        flex-wrap: wrap;
        position: relative;
        z-index: 2;
    }
    
    .image-showcase {
        flex: 0 1 340px;
        text-align: center;
    }
    
    .image-frame {
        border-radius: 20px;
        overflow: hidden;
        box-shadow: 0 25px 70px rgba(0, 0, 0, 0.18);
        background: white;
        margin-bottom: 1.5em;
        transition: all 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
        position: relative;
        border: 2px solid #f0f0f0;
    }
    
    .image-frame:hover {
        transform: translateY(-15px);
        box-shadow: 0 35px 90px rgba(0, 0, 0, 0.25);
    }
    
    .image-frame img {
        width: 100%;
        height: auto;
        display: block;
    }
    
    .image-label {
        font-family: 'Playfair Display', serif;
        font-size: 0.9em;
        color: #1a1a1a !important;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.15em;
        margin-top: 1em;
        background: linear-gradient(135deg, #d4af6e 0%, #e8c547 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .results-right {
        background: white;
        padding: 5em 3em;
        display: flex;
        flex-direction: column;
        justify-content: center;
        position: relative;
        overflow-y: auto;
    }
    
    .result-title {
        font-family: 'Playfair Display', serif;
        font-size: 3em;
        font-weight: 800;
        color: #1a1a1a !important;
        margin-bottom: 1.5em;
        letter-spacing: -0.02em;
        line-height: 1.2;
    }
    
    .result-description {
        font-size: 1em;
        line-height: 2;
        color: #333333 !important;
        margin-bottom: 2.5em;
    }
    
    .result-description p {
        margin-bottom: 1.5em;
    }
    
    .result-description strong {
        color: #1a1a1a !important;
        font-weight: 700;
    }
    
    /* Specification Section */
    .specification-section {
        margin-top: 3em;
        padding-top: 3em;
        border-top: 2px solid #e8e8e8;
    }
    
    .spec-title {
        font-family: 'Playfair Display', serif;
        font-size: 1.3em;
        font-weight: 700;
        color: #1a1a1a !important;
        margin-bottom: 2em;
        text-transform: uppercase;
        letter-spacing: 0.08em;
    }
    
    .spec-item {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 1.5em;
        padding: 1.2em 0;
        border-bottom: 1px solid #f0f0f0;
        align-items: center;
    }
    
    .spec-item:last-child {
        border-bottom: none;
    }
    
    .spec-label {
        font-weight: 700;
        color: #1a1a1a !important;
        font-size: 0.95em;
    }
    
    .spec-value {
        color: #666666 !important;
        font-size: 0.95em;
    }
    
    .download-button {
        margin-top: 3em;
        padding: 1.3em 2.5em;
        background: linear-gradient(135deg, #d4af6e 0%, #e8c547 100%);
        color: #1a1a1a;
        border: none;
        border-radius: 12px;
        font-weight: 700;
        font-size: 1em;
        cursor: pointer;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        transition: all 0.3s ease;
        box-shadow: 0 8px 25px rgba(212, 175, 110, 0.25);
    }
    
    .download-button:hover {
        background: linear-gradient(135deg, #e8c547 0%, #d4af6e 100%);
        box-shadow: 0 12px 35px rgba(212, 175, 110, 0.35);
        transform: translateY(-2px);
    }
    
    h1, h2, h3, h4, h5, h6 {
        color: #1a1a1a !important;
        font-weight: 700 !important;
    }
    
    [data-testid="stMarkdownContainer"] h1,
    [data-testid="stMarkdownContainer"] h2,
    [data-testid="stMarkdownContainer"] h3 {
        color: #1a1a1a !important;
    }
    
    .stMarkdown {
        color: #333333 !important;
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
        
        .result-title {
            font-size: 2.2em;
        }
        
        .steps-guide {
            grid-template-columns: 1fr;
        }
        
        .hero-title {
            font-size: 2.5em;
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
        
        .section-header {
            font-size: 1.8em;
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
    if 'selected_style' not in st.session_state:
        st.session_state['selected_style'] = None
    if 'selected_room_type' not in st.session_state:
        st.session_state['selected_room_type'] = None
    if 'show_hero' not in st.session_state:
        st.session_state['show_hero'] = True

init_session()

# --- Hero Section ---
if st.session_state['show_hero'] and not st.session_state['result_image']:
    st.markdown("""
        <div class="hero-section">
            <h1 class="hero-title">AI Interior Studio</h1>
            <p class="hero-subtitle">Transform Your Space with Intelligent Design</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Steps Guide
    st.markdown("""
        <div class="steps-guide">
            <div class="step-card" data-step="1">
                <div class="step-icon">📸</div>
                <h3 class="step-title">Upload Your Room</h3>
                <p class="step-description">Share a photo of your space and let our AI analyze every detail</p>
            </div>
            <div class="step-card" data-step="2">
                <div class="step-icon">✨</div>
                <h3 class="step-title">Choose Your Style</h3>
                <p class="step-description">Select from curated design styles that match your vision</p>
            </div>
            <div class="step-card" data-step="3">
                <div class="step-icon">🎨</div>
                <h3 class="step-title">Get Your Design</h3>
                <p class="step-description">Receive AI-generated design proposals with recommendations</p>
            </div>
        </div>
    """, unsafe_allow_html=True)

# --- Input Section ---
st.markdown('<div class="input-section">', unsafe_allow_html=True)
    st.markdown('<h2 class="section-header">Transform Your Real Space</h2>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #666; font-size: 1.05em; margin-bottom: 2em;">Your personal AI design assistant analyzes your actual room structure and creates a custom design that preserves your space while transforming its style.</p>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="input-card">', unsafe_allow_html=True)
    st.markdown('<h3 class="card-title">📸 Upload Your Real Space</h3>', unsafe_allow_html=True)
    st.markdown('<p style="color: #666; font-size: 0.9em; margin-bottom: 1em;">Upload a clear photo of your room. Our AI will analyze the structure, lighting, and existing elements.</p>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Choose a room image", type=["jpg", "jpeg", "png"], label_visibility="collapsed")
    
    if uploaded_file:
        st.session_state['image_bytes'] = uploaded_file.getvalue()
        st.session_state['last_file_name'] = uploaded_file.name
        st.success("✓ Image uploaded successfully!")
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="input-card">', unsafe_allow_html=True)
    st.markdown('<h3 class="card-title">✨ Select Your Design Vision</h3>', unsafe_allow_html=True)
    st.markdown('<p style="color: #666; font-size: 0.9em; margin-bottom: 1em;">Choose a style that matches your vision. Our AI will adapt it to your actual room.</p>', unsafe_allow_html=True)
    
    col_style, col_room = st.columns(2)
    with col_style:
        selected_style = st.selectbox(
            "Design Style",
            ["Modern", "Minimalist", "Luxury", "Scandinavian", "Industrial", "Bohemian"],
            label_visibility="collapsed"
        )
        st.session_state['selected_style'] = selected_style
    
    with col_room:
        selected_room_type = st.selectbox(
            "Room Type",
            ["Bedroom", "Living Room", "Kitchen", "Bathroom", "Office", "Dining Room"],
            label_visibility="collapsed"
        )
        st.session_state['selected_room_type'] = selected_room_type
    
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# --- Analyze and Generate Button ---
if st.session_state['image_bytes']:
    col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
    with col_btn2:
        if st.button("🚀 Analyze & Design", use_container_width=True):
            st.session_state['show_hero'] = False
            
            with st.spinner("🔍 Analyzing your real space..."):
                try:
                    analysis = analyze_room(st.session_state['image_bytes'])
                    st.session_state['analysis'] = analysis
                    
                    # Display AI Analysis Insights
                    st.markdown('<div class="analysis-section">', unsafe_allow_html=True)
                    st.markdown('<h3 class="analysis-title">🔍 AI Analysis of Your Space</h3>', unsafe_allow_html=True)
                    
                    analysis_text = analysis.get('room_description', 'Analyzing your room...')
                    st.markdown(f'<div class="analysis-content">{analysis_text}</div>', unsafe_allow_html=True)
                    
                    if 'room_metadata' in analysis:
                        metadata = analysis['room_metadata']
                        st.markdown('<div class="analysis-highlight">', unsafe_allow_html=True)
                        st.markdown('<strong>Key Room Characteristics:</strong>', unsafe_allow_html=True)
                        if 'lighting' in metadata:
                            st.markdown(f"<p>💡 <strong>Lighting:</strong> {metadata['lighting']}</p>", unsafe_allow_html=True)
                        if 'wall_color' in metadata:
                            st.markdown(f"<p>🎨 <strong>Wall Color:</strong> {metadata['wall_color']}</p>", unsafe_allow_html=True)
                        if 'room_size' in metadata:
                            st.markdown(f"<p>📐 <strong>Room Size:</strong> {metadata['room_size']}</p>", unsafe_allow_html=True)
                        st.markdown('</div>', unsafe_allow_html=True)
                    
                    st.markdown('</div>', unsafe_allow_html=True)
                    st.markdown('---')
                    
                except Exception as e:
                    st.error(f"Error analyzing room: {str(e)}")
                    st.stop()
            
            with st.spinner("🎨 Generating your personalized design..."):
                try:
                    # Extract necessary data from analysis
                    room_type = st.session_state['selected_room_type']
                    interior_style = st.session_state['selected_style']
                    furniture_list = analysis.get('furniture_list', [])
                    wall_info = analysis.get('room_metadata', {}).get('wall_color', 'neutral walls')
                    lighting_info = analysis.get('room_metadata', {}).get('lighting', 'natural light')
                    detailed_narrative = analysis.get('room_description', 'modern room')
                    
                    # Show detailed prompt generation status
                    st.info(f"🤖 **AI Design Assistant is working...**\n\n" +
                           f"Analyzing your {room_type} with {lighting_info}...\n" +
                           f"Generating {interior_style} design while preserving your room's structure...\n" +
                           f"Creating hyper-realistic visualization...")
                    
                    prompt = build_design_prompt(
                        room_type,
                        interior_style,
                        furniture_list,
                        wall_info,
                        lighting_info,
                        detailed_narrative
                    )
                    result_image_url = generate_design(prompt, st.session_state['image_bytes'])
                    st.session_state['result_image'] = result_image_url
                except Exception as e:
                    st.error(f"Error generating design: {str(e)}")
                    st.stop()
            
            with st.spinner("💡 Creating recommendations..."):
                try:
                    recommendations = recommend_furniture_and_palette(analysis, st.session_state['selected_style'])
                    st.session_state['recommendations'] = recommendations
                except Exception as e:
                    st.warning("Could not generate recommendations, but design is ready!")
            
            st.rerun()

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
    if st.session_state['result_image']:
        try:
            st.image(st.session_state['result_image'], use_container_width=True)
        except Exception as e:
            st.error(f"Unable to load After image: {str(e)}")
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div class="image-label">AFTER</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Right Side
    st.markdown('<div class="results-right">', unsafe_allow_html=True)
    
    st.markdown('<h2 class="result-title">Your Personalized Design</h2>', unsafe_allow_html=True)
    st.markdown('<p style="color: #666; font-size: 1em; margin-bottom: 1.5em;">Based on your real space analysis, here is your AI-generated design proposal that preserves your room\'s structure while transforming its style.</p>', unsafe_allow_html=True)
    
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
                <span class="spec-value">""" + st.session_state.get('selected_room_type', 'N/A') + """</span>
            </div>
            <div class="spec-item">
                <span class="spec-label">Design Tool</span>
                <span class="spec-value">AI Interior Studio v2.0</span>
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
        st.session_state['image_bytes'] = None
        st.session_state['last_file_name'] = None
        st.session_state['analysis'] = None
        st.session_state['imgbb_url'] = None
        st.session_state['result_image'] = None
        st.session_state['recommendations'] = None
        st.session_state['selected_style'] = None
        st.session_state['selected_room_type'] = None
        st.session_state['show_hero'] = True
        st.rerun()
    
    st.markdown("---")
    st.markdown("### About")
    st.markdown("""
    **AI Interior Studio** is a professional interior design tool powered by advanced AI models.
    
    - 📸 AI-powered room analysis
    - 🎨 Intelligent design generation
    - ✨ Personalized recommendations
    """)

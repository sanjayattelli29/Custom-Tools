
import streamlit as st
import os
import sys
from datetime import datetime, timedelta
import pandas as pd
import uuid
from PIL import Image
import io
import base64
import json
import qrcode
import requests

# Set page config - MUST BE THE FIRST STREAMLIT COMMAND
st.set_page_config(
    page_title="Advanced QR Code Generator",
    page_icon="🔶",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add the current directory to the path so imports work on Streamlit Cloud
import sys
from pathlib import Path

# Get the absolute path of the current file's directory
file_path = Path(__file__).parent.absolute()
# Add the frontend directory to the Python path
sys.path.append(str(file_path))

# Import modules
from frontend.utils.db import init_all_databases
from frontend.pages.qr_generator import qr_generator_page
from frontend.pages.url_shortener import url_shortener_page
from frontend.pages.app_links import app_links_page
from frontend.pages.analytics import analytics_page

# Import new feature pages
from frontend.pages.youtube_downloader import youtube_downloader_page
from frontend.pages.instagram_downloader import instagram_downloader_page
from frontend.pages.image_converter import image_converter_page
from frontend.pages.pdf_tools import pdf_tools_page

# Initialize databases
init_all_databases()

# Apply custom CSS for modern UI
st.markdown("""
<style>
    /* Main container styling */
    .main .block-container {
        padding-top: 1.5rem;
        padding-bottom: 1.5rem;
        max-width: 1200px;
    }
    
    /* Global styling */
    .stApp {
        background: linear-gradient(135deg, #121212, #1E1E1E);
        color: #FFFFFF;
    }
    
    /* Card styling with glass morphism effect */
    .css-1r6slb0, .css-1y4p8pa, .css-1vq4p4l, .css-1v3fvcr {
        background-color: rgba(46, 46, 46, 0.7) !important;
        border-radius: 15px !important;
        padding: 1.5rem !important;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2) !important;
        backdrop-filter: blur(10px) !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        margin-bottom: 1.5rem !important;
    }
    
    /* Card header styling */
    .card-header {
        color: #4ECDC4;
        font-size: 1.3rem;
        font-weight: bold;
        margin-bottom: 1.2rem;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        padding-bottom: 0.8rem;
    }
    
    /* Button styling */
    .stButton>button {
        border-radius: 8px !important;
        font-weight: 500 !important;
        padding: 0.5rem 1.5rem !important;
        background: linear-gradient(90deg, #4B79A1, #283E51) !important;
        color: white !important;
        border: none !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1) !important;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15) !important;
    }
    
    .stButton>button:active {
        transform: translateY(0) !important;
    }
    
    /* Form elements styling */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > div {
        background-color: rgba(30, 30, 30, 0.7) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 8px !important;
        color: white !important;
        padding: 0.75rem !important;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1) !important;
        transition: all 0.3s ease !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus,
    .stSelectbox > div:focus-within {
        border-color: #4B79A1 !important;
        box-shadow: 0 0 0 2px rgba(75, 121, 161, 0.3) !important;
    }
    
    /* Slider styling */
    .stSlider > div > div > div > div {
        background-color: #4B79A1 !important;
    }
    
    /* Metric styling */
    .css-1xarl3l, .css-1offfwp {
        background: linear-gradient(135deg, rgba(75, 121, 161, 0.1), rgba(40, 62, 81, 0.1)) !important;
        border-radius: 10px !important;
        padding: 1rem !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
    }
    
    /* Footer styling */
    .footer {
        text-align: center;
        padding: 1.5rem;
        color: #A0A0A0;
        font-size: 0.9rem;
        margin-top: 3rem;
        border-top: 1px solid rgba(255, 255, 255, 0.05);
        background: linear-gradient(90deg, rgba(40, 62, 81, 0.5), rgba(75, 121, 161, 0.5));
        border-radius: 10px;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: rgba(30, 30, 30, 0.7) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.05) !important;
        padding-top: 1.5rem !important;
    }
    
    /* Sidebar navigation styling */
    .css-6qob1r {
        background-color: rgba(46, 46, 46, 0.5) !important;
        border-radius: 8px !important;
        margin-bottom: 0.5rem !important;
        padding: 0.5rem !important;
        transition: all 0.3s ease !important;
    }
    
    .css-6qob1r:hover {
        background-color: rgba(75, 121, 161, 0.3) !important;
        transform: translateX(3px) !important;
    }
</style>
""", unsafe_allow_html=True)

# Create a modern header with gradient background
def create_header():
    st.markdown("""
    <div style="background: linear-gradient(90deg, #4B79A1, #283E51); padding: 1.5rem; border-radius: 15px; margin-bottom: 1.5rem; text-align: center; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
        <div style="display: flex; justify-content: center; align-items: center;">
            <div style="font-size: 2.5rem; margin-right: 15px;">🔶</div>
            <h1 style="color: white; margin: 0; font-weight: 600; font-size: 2.2rem; text-shadow: 1px 1px 3px rgba(0,0,0,0.2);">Advanced QR Code Generator</h1>
        </div>
        <p style="color: #E0E0E0; margin-top: 10px; font-size: 1.1rem;">Create, customize, and track QR codes with ease</p>
    </div>
    """, unsafe_allow_html=True)

# Main app function
def main():
    # Initialize session state for navigation
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "Home"
        
    # Define all available pages
    available_pages = {
        "QR Generator": qr_generator_page,
        "URL Shortener": url_shortener_page,
        "App Links": app_links_page,
        "Analytics": analytics_page,
        "YouTube Downloader": youtube_downloader_page,
        "Instagram Downloader": instagram_downloader_page,
        "Image Converter": image_converter_page,
        "PDF Tools": pdf_tools_page
    }
    
    # Define icons for each page
    page_icons = {
        "QR Generator": "🔶",
        "URL Shortener": "🔗",
        "App Links": "📱",
        "Analytics": "📊",
        "YouTube Downloader": "🎥",
        "Instagram Downloader": "📸",
        "Image Converter": "🖼️",
        "PDF Tools": "📄"
    }
    
    # Display header
    create_header()
    
    # Add custom CSS for feature buttons
    st.markdown("""
    <style>
    /* Feature button styling */
    .feature-button {
        background: linear-gradient(135deg, rgba(75, 121, 161, 0.7), rgba(40, 62, 81, 0.7));
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        margin-bottom: 20px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.05);
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
    }
    
    .feature-button:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 20px rgba(0, 0, 0, 0.2);
        background: linear-gradient(135deg, rgba(255, 107, 107, 0.7), rgba(255, 142, 142, 0.7));
    }
    
    .feature-icon {
        font-size: 3rem;
        margin-bottom: 10px;
    }
    
    .feature-title {
        font-size: 1.2rem;
        font-weight: 600;
        margin-bottom: 10px;
        color: white;
    }
    
    .feature-description {
        font-size: 0.9rem;
        color: #E0E0E0;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Check if we're on the home page or a feature page
    if st.session_state.current_page == "Home":
        # Display feature buttons in two rows
        st.subheader("Core Features")
        
        # First row - 4 features
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="feature-button" onclick="window.location.href='#'" id="qr-generator-btn">
                <div class="feature-icon">{page_icons['QR Generator']}</div>
                <div class="feature-title">QR Generator</div>
                <div class="feature-description">Create custom QR codes for any content</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Open QR Generator", key="btn_qr", use_container_width=True):
                st.session_state.current_page = "QR Generator"
                st.rerun()
        
        with col2:
            st.markdown(f"""
            <div class="feature-button" onclick="window.location.href='#'" id="url-shortener-btn">
                <div class="feature-icon">{page_icons['URL Shortener']}</div>
                <div class="feature-title">URL Shortener</div>
                <div class="feature-description">Create short links for easy sharing and tracking</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Open URL Shortener", key="btn_url", use_container_width=True):
                st.session_state.current_page = "URL Shortener"
                st.rerun()
        
        with col3:
            st.markdown(f"""
            <div class="feature-button" onclick="window.location.href='#'" id="app-links-btn">
                <div class="feature-icon">{page_icons['App Links']}</div>
                <div class="feature-title">App Links</div>
                <div class="feature-description">Generate deep links for mobile apps</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Open App Links", key="btn_app", use_container_width=True):
                st.session_state.current_page = "App Links"
                st.rerun()
        
        with col4:
            st.markdown(f"""
            <div class="feature-button" onclick="window.location.href='#'" id="analytics-btn">
                <div class="feature-icon">{page_icons['Analytics']}</div>
                <div class="feature-title">Analytics</div>
                <div class="feature-description">Track and analyze QR code usage and performance</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Open Analytics", key="btn_analytics", use_container_width=True):
                st.session_state.current_page = "Analytics"
                st.rerun()
        
        # Second row - 4 more features
        st.subheader("Media & Document Tools")
        col5, col6, col7, col8 = st.columns(4)
        
        with col5:
            st.markdown(f"""
            <div class="feature-button" onclick="window.location.href='#'" id="youtube-btn">
                <div class="feature-icon">{page_icons['YouTube Downloader']}</div>
                <div class="feature-title">YouTube Downloader</div>
                <div class="feature-description">Download videos and audio from YouTube</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Open YouTube Downloader", key="btn_youtube", use_container_width=True):
                st.session_state.current_page = "YouTube Downloader"
                st.rerun()
        
        with col6:
            st.markdown(f"""
            <div class="feature-button" onclick="window.location.href='#'" id="instagram-btn">
                <div class="feature-icon">{page_icons['Instagram Downloader']}</div>
                <div class="feature-title">Instagram Downloader</div>
                <div class="feature-description">Save reels and posts from Instagram</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Open Instagram Downloader", key="btn_instagram", use_container_width=True):
                st.session_state.current_page = "Instagram Downloader"
                st.rerun()
        
        with col7:
            st.markdown(f"""
            <div class="feature-button" onclick="window.location.href='#'" id="image-converter-btn">
                <div class="feature-icon">{page_icons['Image Converter']}</div>
                <div class="feature-title">Image Converter</div>
                <div class="feature-description">Convert images between different formats</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Open Image Converter", key="btn_image", use_container_width=True):
                st.session_state.current_page = "Image Converter"
                st.rerun()
        
        with col8:
            st.markdown(f"""
            <div class="feature-button" onclick="window.location.href='#'" id="pdf-tools-btn">
                <div class="feature-icon">{page_icons['PDF Tools']}</div>
                <div class="feature-title">PDF Tools</div>
                <div class="feature-description">Merge, split, and manipulate PDF files</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Open PDF Tools", key="btn_pdf", use_container_width=True):
                st.session_state.current_page = "PDF Tools"
                st.rerun()
    else:
        # Display the selected feature page
        # Add a back button to return to home
        if st.button("← Back to Home", key="back_home"):
            st.session_state.current_page = "Home"
            st.rerun()
            
        # Display the selected page content
        if st.session_state.current_page in available_pages:
            available_pages[st.session_state.current_page]()
    
    # Footer
    st.markdown("""
    <div class='footer'>
        <p>Advanced QR Code Generator | Developed with Streamlit | 2023</p>
    </div>
    """, unsafe_allow_html=True)

# Run the main app
if __name__ == "__main__":
    main()

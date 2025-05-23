
import streamlit as st
import requests
import re
import json
import os
import tempfile
from urllib.parse import urlparse
import time
import base64

def instagram_downloader_page():
    st.title("📱 Instagram Reel Downloader")
    
    # Create a card-like container for the downloader
    with st.container():
        st.markdown("""
        <div class="card-header">
            Download Instagram Reels Easily
        </div>
        """, unsafe_allow_html=True)
        
        st.write("Enter an Instagram reel URL to download it.")
        
        # Input for Instagram URL
        instagram_url = st.text_input("Instagram Reel URL", placeholder="https://www.instagram.com/reel/...")
        
        if instagram_url:
            # Validate URL
            if not is_valid_instagram_url(instagram_url):
                st.error("Please enter a valid Instagram reel URL.")
            else:
                try:
                    with st.spinner("Fetching reel information..."):
                        # Get the reel ID from the URL
                        reel_id = extract_reel_id(instagram_url)
                        
                        if not reel_id:
                            st.error("Could not extract reel ID from the URL.")
                        else:
                            # Use a public API to get the reel information
                            api_url = f"https://instagram-downloader-download-instagram-videos-stories.p.rapidapi.com/index"
                            querystring = {"url": instagram_url}
                            
                            headers = {
                                "X-RapidAPI-Key": st.secrets.get("RAPID_API_KEY", "demo_key"),
                                "X-RapidAPI-Host": "instagram-downloader-download-instagram-videos-stories.p.rapidapi.com"
                            }
                            
                            # Mock response for demo purposes (in a real app, you'd use the actual API)
                            # This is to avoid requiring an actual API key for the demo
                            if headers["X-RapidAPI-Key"] == "demo_key":
                                st.warning("Using demo mode. For full functionality, add your RapidAPI key to the app's secrets.")
                                # Show a demo UI
                                col1, col2 = st.columns([1, 2])
                                
                                with col1:
                                    st.image("https://via.placeholder.com/300x400?text=Instagram+Reel+Thumbnail", use_column_width=True)
                                
                                with col2:
                                    st.subheader("Sample Instagram Reel")
                                    st.write("**Creator:** @sample_creator")
                                    st.write("**Caption:** This is a sample Instagram reel caption...")
                                    st.write("**Likes:** 1,234")
                                
                                # Demo download button
                                if st.button("Download Reel", key="demo_download"):
                                    st.info("In demo mode, downloads are simulated. Add your RapidAPI key for actual downloads.")
                                    
                                    # Show a progress bar to simulate download
                                    progress_bar = st.progress(0)
                                    for i in range(100):
                                        time.sleep(0.01)
                                        progress_bar.progress(i + 1)
                                    
                                    st.success("Download simulation complete!")
                            else:
                                # Real API call
                                response = requests.get(api_url, headers=headers, params=querystring)
                                
                                if response.status_code == 200:
                                    data = response.json()
                                    
                                    if "media" in data and data["media"]:
                                        media = data["media"]
                                        
                                        # Display reel information
                                        col1, col2 = st.columns([1, 2])
                                        
                                        with col1:
                                            st.image(media.get("thumbnail", "https://via.placeholder.com/300x400?text=No+Thumbnail"), use_column_width=True)
                                        
                                        with col2:
                                            st.subheader(media.get("title", "Instagram Reel"))
                                            st.write(f"**Creator:** {media.get('author', 'Unknown')}")
                                            if "description" in media and media["description"]:
                                                st.write(f"**Caption:** {media['description'][:100]}...")
                                        
                                        # Download options
                                        if "video_url" in media and media["video_url"]:
                                            if st.button("Download Reel", key="reel_download"):
                                                with st.spinner("Downloading reel..."):
                                                    # Download the video
                                                    video_url = media["video_url"]
                                                    video_response = requests.get(video_url, stream=True)
                                                    
                                                    if video_response.status_code == 200:
                                                        # Create a temporary file
                                                        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp_file:
                                                            # Save the video to the temporary file
                                                            for chunk in video_response.iter_content(chunk_size=1024*1024):
                                                                if chunk:
                                                                    tmp_file.write(chunk)
                                                            
                                                            # Read the file
                                                            tmp_file.flush()
                                                            with open(tmp_file.name, "rb") as f:
                                                                video_bytes = f.read()
                                                            
                                                            # Remove the temporary file
                                                            os.unlink(tmp_file.name)
                                                        
                                                        # Create a download button
                                                        st.download_button(
                                                            label="Click to save",
                                                            data=video_bytes,
                                                            file_name=f"instagram_reel_{reel_id}.mp4",
                                                            mime="video/mp4"
                                                        )
                                                        
                                                        st.success("Reel downloaded successfully!")
                                                    else:
                                                        st.error("Failed to download the reel.")
                                        else:
                                            st.error("No video URL found for this reel.")
                                    else:
                                        st.error("No media information found for this reel.")
                                else:
                                    st.error(f"API Error: {response.status_code} - {response.text}")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
                    st.info("Please try again with a different reel URL.")
        
        # Tips section
        with st.expander("Tips for Instagram Downloads"):
            st.markdown("""
            - Make sure the reel is from a public account
            - Copy the URL directly from the Instagram app or website
            - Some reels may not be available for download due to privacy settings
            - Downloaded reels are for personal use only
            """)

def is_valid_instagram_url(url):
    """Check if the URL is a valid Instagram URL."""
    patterns = [
        r"^https?://(www\.)?instagram\.com/reel/[a-zA-Z0-9_-]+/?.*$",
        r"^https?://(www\.)?instagram\.com/p/[a-zA-Z0-9_-]+/?.*$",
        r"^https?://(www\.)?instagram\.com/tv/[a-zA-Z0-9_-]+/?.*$",
        r"^https?://(www\.)?instagram\.com/[a-zA-Z0-9_.]+/reel/[a-zA-Z0-9_-]+/?.*$",  # Handle username/reel format
        r"^https?://(www\.)?instagram\.com/[a-zA-Z0-9_.]+/p/[a-zA-Z0-9_-]+/?.*$"      # Handle username/post format
    ]
    
    for pattern in patterns:
        if re.match(pattern, url):
            return True
    
    return False

def extract_reel_id(url):
    """Extract the reel ID from the URL."""
    patterns = [
        r"instagram\.com/reel/([a-zA-Z0-9_-]+)",
        r"instagram\.com/p/([a-zA-Z0-9_-]+)",
        r"instagram\.com/tv/([a-zA-Z0-9_-]+)",
        r"instagram\.com/[a-zA-Z0-9_.]+/reel/([a-zA-Z0-9_-]+)",  # Handle username/reel format
        r"instagram\.com/[a-zA-Z0-9_.]+/p/([a-zA-Z0-9_-]+)"      # Handle username/post format
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    return None

if __name__ == "__main__":
    instagram_downloader_page()

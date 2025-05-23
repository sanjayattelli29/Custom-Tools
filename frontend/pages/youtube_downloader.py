
import streamlit as st
import os
import re
import requests
import time
import tempfile
import json
from urllib.parse import parse_qs, urlparse
from pytube import YouTube
import io

def extract_video_id(url):
    """Extract the video ID from a YouTube URL."""
    # Regular expression patterns for different YouTube URL formats
    patterns = [
        r'(?:youtube\.com/watch\?v=|youtu\.be/)([\w-]+)',  # Standard and shortened URLs
        r'youtube\.com/embed/([\w-]+)',                     # Embed URLs
        r'youtube\.com/v/([\w-]+)',                         # Old embed URLs
        r'youtube\.com/\?v=([\w-]+)',                       # Mobile URLs
        r'youtube\.com/watch\?.*\&v=([\w-]+)',              # URLs with parameters
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    # Try parsing the URL for query parameters
    parsed_url = urlparse(url)
    if parsed_url.netloc in ['youtube.com', 'www.youtube.com']:
        query_params = parse_qs(parsed_url.query)
        if 'v' in query_params:
            return query_params['v'][0]
    
    return None

def get_video_info(video_id):
    """Get video information using a public API."""
    try:
        # Use a public API to get video information
        api_url = f"https://yt-api.p.rapidapi.com/dl?id={video_id}"
        
        headers = {
            "X-RapidAPI-Key": st.secrets.get("RAPID_API_KEY", "demo_key"),
            "X-RapidAPI-Host": "yt-api.p.rapidapi.com"
        }
        
        # If using demo mode, return mock data
        if headers["X-RapidAPI-Key"] == "demo_key":
            # Return mock data for demonstration
            return {
                "status": "OK",
                "title": "Sample YouTube Video",
                "author": "Sample Channel",
                "lengthSeconds": 180,
                "viewCount": 10000,
                "thumbnail": {
                    "url": "https://via.placeholder.com/480x360?text=YouTube+Thumbnail"
                },
                "formats": [
                    {
                        "mimeType": "video/mp4",
                        "qualityLabel": "720p",
                        "width": 1280,
                        "height": 720,
                        "contentLength": 15000000,
                        "url": "https://example.com/video.mp4"
                    },
                    {
                        "mimeType": "video/mp4",
                        "qualityLabel": "480p",
                        "width": 854,
                        "height": 480,
                        "contentLength": 10000000,
                        "url": "https://example.com/video.mp4"
                    },
                    {
                        "mimeType": "video/mp4",
                        "qualityLabel": "360p",
                        "width": 640,
                        "height": 360,
                        "contentLength": 5000000,
                        "url": "https://example.com/video.mp4"
                    }
                ],
                "adaptiveFormats": [
                    {
                        "mimeType": "audio/mp4",
                        "bitrate": 128000,
                        "contentLength": 3000000,
                        "url": "https://example.com/audio.mp4"
                    },
                    {
                        "mimeType": "audio/mp4",
                        "bitrate": 64000,
                        "contentLength": 1500000,
                        "url": "https://example.com/audio.mp4"
                    }
                ]
            }
        
        # Make the API request
        response = requests.get(api_url, headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API Error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        st.error(f"Error getting video info: {str(e)}")
        return None

def format_file_size(size_bytes):
    """Format file size in bytes to a human-readable format."""
    if size_bytes is None:
        return "Unknown size"
    
    size_bytes = int(size_bytes)
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024 or unit == 'GB':
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024

def get_best_stream(streams, stream_type="video", quality_preference="high"):
    """Get the best stream based on resolution or audio quality.
    
    Args:
        streams: The pytube streams object
        stream_type: Either "video" or "audio"
        quality_preference: Either "high" or "medium" or "low"
        
    Returns:
        The best stream based on the quality preference
    """
    if stream_type == "video":
        # For highest quality, we might need to get video and audio separately
        if quality_preference == "high":
            # First try to get high quality progressive streams (with audio)
            progressive_streams = streams.filter(progressive=True).order_by('resolution').desc()
            if progressive_streams:
                # Get the highest resolution progressive stream
                highest_res = progressive_streams.first()
                # If it's at least 720p, return it
                if highest_res and '720p' in highest_res.resolution:
                    return highest_res
                
            # If no good progressive streams, get the highest resolution video
            # This will need to be combined with audio separately
            return streams.filter(only_video=True).order_by('resolution').desc().first()
        
        elif quality_preference == "medium":
            # Try to get a 720p stream first
            medium_streams = streams.filter(progressive=True, resolution="720p")
            if medium_streams:
                return medium_streams.first()
            # Otherwise get the best progressive stream
            return streams.filter(progressive=True).order_by('resolution').desc().first()
        
        else:  # low quality for slow connections
            # Try to get a 480p stream first
            low_streams = streams.filter(progressive=True, resolution="480p")
            if low_streams:
                return low_streams.first()
            # Otherwise get a lower resolution stream
            return streams.filter(progressive=True).order_by('resolution').asc().first()
    
    else:  # audio
        if quality_preference == "high":
            # Get highest bitrate audio
            return streams.filter(only_audio=True).order_by('abr').desc().first()
        elif quality_preference == "medium":
            # Try to get a medium quality audio (128kbps)
            medium_audio = streams.filter(only_audio=True, abr="128kbps")
            if medium_audio:
                return medium_audio.first()
            # Otherwise get the best available
            return streams.filter(only_audio=True).order_by('abr').desc().first()
        else:  # low quality
            # Get lowest bitrate audio to save bandwidth
            return streams.filter(only_audio=True).order_by('abr').asc().first()

def download_stream(stream, file_extension=None):
    """Download a stream to a bytes buffer.
    
    Args:
        stream: The pytube stream to download
        file_extension: Optional file extension override
        
    Returns:
        Tuple of (filename, bytes_data)
    """
    try:
        # Create a temporary file to save the stream
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file_extension or stream.subtype}") as tmp_file:
            stream.download(output_path=os.path.dirname(tmp_file.name), filename=os.path.basename(tmp_file.name))
            
            # Read the file into memory
            with open(tmp_file.name, "rb") as f:
                file_data = f.read()
            
            # Clean up the temporary file
            os.unlink(tmp_file.name)
            
            # Generate a filename
            title = stream.title
            # Sanitize the title for use as a filename
            title = re.sub(r'[^\w\-_\. ]', '_', title)
            filename = f"{title}.{file_extension or stream.subtype}"
            
            return filename, file_data
    except Exception as e:
        st.error(f"Error downloading stream: {str(e)}")
        return None, None

def youtube_downloader_page():
    st.title("🎥 YouTube Video Downloader")
    
    # Create a card-like container for the downloader
    with st.container():
        st.markdown("""
        <div class="card-header">
            Download YouTube Videos Easily
        </div>
        """, unsafe_allow_html=True)
        
        st.write("Enter a YouTube video URL to download it in your preferred format.")
        
        # Input for YouTube URL
        youtube_url = st.text_input("YouTube URL", placeholder="https://www.youtube.com/watch?v=...")
        
        if youtube_url:
            # Extract video ID
            video_id = extract_video_id(youtube_url)
            
            if not video_id:
                st.error("Could not extract video ID from the URL. Please enter a valid YouTube URL.")
            else:
                # Get video information
                video_info = get_video_info(video_id)
                
                if video_info and video_info.get("status") == "OK":
                    # Display video information
                    col1, col2 = st.columns([1, 2])
                    
                    with col1:
                        thumbnail_url = video_info.get("thumbnail", {}).get("url")
                        if thumbnail_url:
                            st.image(thumbnail_url, use_column_width=True)
                    
                    with col2:
                        st.subheader(video_info.get("title", "YouTube Video"))
                        st.write(f"**Channel:** {video_info.get('author', 'Unknown')}")
                        
                        # Format duration
                        length_seconds = video_info.get("lengthSeconds", 0)
                        minutes = length_seconds // 60
                        seconds = length_seconds % 60
                        st.write(f"**Duration:** {minutes}:{seconds:02d} minutes")
                        
                        # Format view count
                        view_count = video_info.get("viewCount", 0)
                        st.write(f"**Views:** {int(view_count):,}")
                    
                    # Options for download
                    st.subheader("Download Options")
                    
                    # Quality preference
                    quality_options = ["High (Best Quality)", "Medium (Balanced)", "Low (Faster Download)"]
                    quality_selection = st.radio("Select Quality Preference", quality_options, index=0)
                    
                    # Map selection to preference
                    quality_map = {
                        "High (Best Quality)": "high",
                        "Medium (Balanced)": "medium",
                        "Low (Faster Download)": "low"
                    }
                    quality_preference = quality_map[quality_selection]
                    
                    # Create tabs for video and audio
                    tab1, tab2 = st.tabs(["Video", "Audio Only"])
                    
                    # Initialize pytube YouTube object
                    try:
                        yt = YouTube(youtube_url)
                        
                        with tab1:
                            # Video download section
                            st.write("Download the video in your preferred quality:")
                            
                            if st.button("Prepare Video Download", key="prepare_video"):
                                with st.spinner("Preparing video for download..."):
                                    # Get the best video stream based on quality preference
                                    video_stream = get_best_stream(yt.streams, "video", quality_preference)
                                    
                                    if video_stream:
                                        # Show video details
                                        st.write(f"**Selected Quality:** {video_stream.resolution}")
                                        if hasattr(video_stream, 'filesize'):
                                            st.write(f"**File Size:** {format_file_size(video_stream.filesize)}")
                                        
                                        # Download the stream
                                        filename, file_data = download_stream(video_stream, "mp4")
                                        
                                        if filename and file_data:
                                            # Create download button
                                            st.download_button(
                                                label="Download Video",
                                                data=file_data,
                                                file_name=filename,
                                                mime="video/mp4",
                                                key="video_download"
                                            )
                                            st.success("Video prepared successfully! Click the button above to download.")
                                        else:
                                            st.error("Failed to prepare video download. Please try again.")
                                    else:
                                        st.error("No suitable video stream found for this video.")
                        
                        with tab2:
                            # Audio download section
                            st.write("Download just the audio track:")
                            
                            # Audio format selection
                            audio_format = st.selectbox(
                                "Select Audio Format",
                                ["mp3", "m4a", "wav"],
                                index=0
                            )
                            
                            if st.button("Prepare Audio Download", key="prepare_audio"):
                                with st.spinner("Preparing audio for download..."):
                                    # Get the best audio stream based on quality preference
                                    audio_stream = get_best_stream(yt.streams, "audio", quality_preference)
                                    
                                    if audio_stream:
                                        # Show audio details
                                        if hasattr(audio_stream, 'abr'):
                                            st.write(f"**Audio Bitrate:** {audio_stream.abr}")
                                        if hasattr(audio_stream, 'filesize'):
                                            st.write(f"**File Size:** {format_file_size(audio_stream.filesize)}")
                                        
                                        # Download the stream
                                        filename, file_data = download_stream(audio_stream, audio_format)
                                        
                                        if filename and file_data:
                                            # Create download button
                                            st.download_button(
                                                label="Download Audio",
                                                data=file_data,
                                                file_name=filename,
                                                mime=f"audio/{audio_format}",
                                                key="audio_download"
                                            )
                                            st.success("Audio prepared successfully! Click the button above to download.")
                                        else:
                                            st.error("Failed to prepare audio download. Please try again.")
                                    else:
                                        st.error("No suitable audio stream found for this video.")
                    
                    except Exception as e:
                        st.error(f"Error processing YouTube video: {str(e)}")
                        st.info("Try using a different video or check your internet connection.")
                
                else:
                    st.error("Could not retrieve video information. Please check the URL and try again.")
        
        # Tips section
        with st.expander("Tips for YouTube Downloads"):
            st.markdown("""
            - Make sure the video is not age-restricted or private
            - For best video quality, choose the "High" quality option
            - Audio-only downloads are great for music or podcasts
            - Some videos may not be available for download due to copyright restrictions
            - For full functionality, add your RapidAPI key in the app's secrets
            """)

if __name__ == "__main__":
    youtube_downloader_page()

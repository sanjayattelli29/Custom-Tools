
import streamlit as st
from PIL import Image
import io
import qrcode
from datetime import datetime
import uuid
from utils.qr import generate_qr_code, add_logo_to_qr

def app_links_page():
    st.title("📱 App Links Generator")
    
    # Create columns for layout
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Configure Your App Link")
        
        # App selection
        app_options = {
            "WhatsApp": {
                "icon": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6b/WhatsApp.svg/1200px-WhatsApp.svg.png",
                "prefix": "whatsapp://send?phone=",
                "description": "Open WhatsApp and start a conversation"
            },
            "Instagram": {
                "icon": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a5/Instagram_icon.png/2048px-Instagram_icon.png",
                "prefix": "instagram://user?username=",
                "description": "Open a profile on Instagram"
            },
            "Twitter/X": {
                "icon": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/57/X_logo_2023_%28white%29.png/800px-X_logo_2023_%28white%29.png",
                "prefix": "twitter://user?screen_name=",
                "description": "Open a profile on Twitter/X"
            },
            "Facebook": {
                "icon": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/05/Facebook_Logo_%282019%29.png/1200px-Facebook_Logo_%282019%29.png",
                "prefix": "fb://profile/",
                "description": "Open a profile on Facebook"
            },
            "LinkedIn": {
                "icon": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/ca/LinkedIn_logo_initials.png/800px-LinkedIn_logo_initials.png",
                "prefix": "linkedin://profile/",
                "description": "Open a profile on LinkedIn"
            },
            "TikTok": {
                "icon": "https://upload.wikimedia.org/wikipedia/en/thumb/a/a9/TikTok_logo.svg/1200px-TikTok_logo.svg.png",
                "prefix": "tiktok://user/",
                "description": "Open a profile on TikTok"
            },
            "YouTube": {
                "icon": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/09/YouTube_full-color_icon_%282017%29.svg/1024px-YouTube_full-color_icon_%282017%29.svg.png",
                "prefix": "youtube://",
                "description": "Open a video or channel on YouTube"
            },
            "Spotify": {
                "icon": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/19/Spotify_logo_without_text.svg/1024px-Spotify_logo_without_text.svg.png",
                "prefix": "spotify://",
                "description": "Open a track, album, or playlist on Spotify"
            },
            "Google Maps": {
                "icon": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/aa/Google_Maps_icon_%282020%29.svg/1200px-Google_Maps_icon_%282020%29.svg.png",
                "prefix": "comgooglemaps://?q=",
                "description": "Open a location on Google Maps"
            },
            "Custom": {
                "icon": "https://cdn-icons-png.flaticon.com/512/2991/2991148.png",
                "prefix": "",
                "description": "Create a custom app link"
            }
        }
        
        # App selection
        selected_app = st.selectbox(
            "Select App",
            options=list(app_options.keys()),
            format_func=lambda x: x
        )
        
        # Display app info
        app_info = app_options[selected_app]
        
        st.markdown(
            f"""
            <div style="display: flex; align-items: center; margin-bottom: 20px;">
                <img src="{app_info['icon']}" style="width: 40px; height: 40px; margin-right: 15px;">
                <div>
                    <p style="margin: 0; color: #4ECDC4;">{app_info['description']}</p>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # Input fields based on app
        if selected_app == "WhatsApp":
            phone = st.text_input("Phone Number (with country code)", placeholder="+1234567890")
            message = st.text_area("Message (optional)")
            
            content = app_info["prefix"] + phone.replace("+", "")
            if message:
                content += f"&text={message}"
                
        elif selected_app in ["Instagram", "Twitter/X", "TikTok"]:
            username = st.text_input("Username (without @)", placeholder="username")
            content = app_info["prefix"] + username
            
        elif selected_app in ["Facebook", "LinkedIn"]:
            profile_id = st.text_input("Profile ID", placeholder="profile.id")
            content = app_info["prefix"] + profile_id
            
        elif selected_app == "YouTube":
            link_type = st.radio("Link Type", ["Video", "Channel"])
            
            if link_type == "Video":
                video_id = st.text_input("Video ID", placeholder="dQw4w9WgXcQ")
                content = app_info["prefix"] + "watch?v=" + video_id
            else:
                channel_id = st.text_input("Channel ID", placeholder="UCxxxxxxxx")
                content = app_info["prefix"] + "channel/" + channel_id
                
        elif selected_app == "Spotify":
            link_type = st.radio("Link Type", ["Track", "Album", "Playlist"])
            
            if link_type == "Track":
                track_id = st.text_input("Track ID", placeholder="spotify:track:4cOdK2wGLETKBW3PvgPWqT")
                content = track_id if "spotify:" in track_id else app_info["prefix"] + "track:" + track_id
            elif link_type == "Album":
                album_id = st.text_input("Album ID", placeholder="spotify:album:4aawyAB9vmqN3uQ7FjRGTy")
                content = album_id if "spotify:" in album_id else app_info["prefix"] + "album:" + album_id
            else:
                playlist_id = st.text_input("Playlist ID", placeholder="spotify:playlist:37i9dQZEVXcIroVdJc5khL")
                content = playlist_id if "spotify:" in playlist_id else app_info["prefix"] + "playlist:" + playlist_id
                
        elif selected_app == "Google Maps":
            location = st.text_input("Location or Address", placeholder="Eiffel Tower, Paris")
            content = app_info["prefix"] + location
            
        elif selected_app == "Custom":
            scheme = st.text_input("App Scheme (e.g., myapp://)", placeholder="myapp://")
            path = st.text_input("Path and Parameters (optional)", placeholder="action?param=value")
            content = scheme + path
        
        # QR Code styling options
        st.subheader("QR Code Styling")
        
        qr_color = st.color_picker("QR Code Color", "#000000")
        bg_color = st.color_picker("Background Color", "#FFFFFF")
        
        # Logo options
        use_app_logo = st.checkbox("Add App Logo to QR Code", value=True)
        
        # Custom logo upload
        custom_logo = None
        if not use_app_logo:
            logo_file = st.file_uploader("Upload Custom Logo", type=['png', 'jpg', 'jpeg'])
            if logo_file:
                custom_logo = Image.open(logo_file)
    
    with col2:
        st.subheader("Preview & Download")
        
        # Generate button
        if st.button("Generate App Link QR", type="primary") and content:
            # Generate QR code
            qr_img = generate_qr_code(content, error_correction=qrcode.constants.ERROR_CORRECT_H)
            
            # Apply styling
            img = qr_img
            
            # Change colors
            if qr_color != "#000000" or bg_color != "#FFFFFF":
                img = img.convert("RGBA")
                data = img.getdata()
                new_data = []
                for item in data:
                    if item[0] == 0 and item[1] == 0 and item[2] == 0:  # Black pixels
                        new_data.append(tuple(int(qr_color[i:i+2], 16) for i in (1, 3, 5)) + (255,))
                    else:  # White pixels
                        new_data.append(tuple(int(bg_color[i:i+2], 16) for i in (1, 3, 5)) + (255,))
                img.putdata(new_data)
                img = img.convert("RGB")
            
            # Add logo
            if use_app_logo and selected_app != "Custom":
                # Download app logo
                try:
                    import requests
                    from io import BytesIO
                    
                    response = requests.get(app_info["icon"])
                    logo_img = Image.open(BytesIO(response.content))
                    img = add_logo_to_qr(img, logo_img)
                except Exception as e:
                    st.warning(f"Could not add app logo: {str(e)}")
            elif custom_logo is not None:
                img = add_logo_to_qr(img, custom_logo)
            
            # Display preview
            st.markdown("<div style='border: 3px solid #FF6B6B; border-radius: 15px; padding: 1rem; background-color: #333333; text-align: center; box-shadow: 0 5px 15px rgba(0,0,0,0.3);'>", unsafe_allow_html=True)
            st.image(img, caption="App Link QR Code", use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Save to session state for download
            if 'current_app_qr' not in st.session_state:
                st.session_state.current_app_qr = img
            else:
                st.session_state.current_app_qr = img
            
            # Display app link info
            st.subheader("App Link Information")
            st.code(content, language="")
            
            st.info("""
            📱 **How to Use**: 
            
            1. Scan this QR code with a mobile device
            2. It will automatically open the selected app if installed
            3. If the app is not installed, it may prompt to install it or open in a browser
            """)
            
            # Download Options
            st.subheader("Download Options")
            
            # PNG Download
            img_buffer = io.BytesIO()
            img.save(img_buffer, format='PNG')
            img_buffer.seek(0)
            
            st.download_button(
                label="📥 Download PNG",
                data=img_buffer.getvalue(),
                file_name=f"app_link_{selected_app.lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png",
                mime="image/png"
            )
            
            # Save to history
            if 'app_link_history' not in st.session_state:
                st.session_state.app_link_history = []
            
            # Add to history
            history_item = {
                'app': selected_app,
                'content': content,
                'image': img,
                'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'id': str(uuid.uuid4())[:8]
            }
            st.session_state.app_link_history.append(history_item)
        else:
            st.info("Configure your app link and click 'Generate App Link QR' to create a QR code that opens the selected app.")
            
            # Display example
            st.markdown("""
            ### Example Use Cases
            
            - **WhatsApp**: Create a QR code that opens a chat with your business
            - **Instagram/Twitter**: Link directly to your social media profile
            - **YouTube**: Direct users to your latest video
            - **Google Maps**: Help customers find your location
            - **Spotify**: Share your playlist or favorite song
            """)

if __name__ == "__main__":
    app_links_page()

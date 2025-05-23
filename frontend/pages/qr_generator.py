
import streamlit as st
from PIL import Image
import io
from datetime import datetime
import qrcode
import pandas as pd
import uuid
from utils.qr import generate_qr_code, add_logo_to_qr, add_frame_and_text, create_qr_for_type, create_svg_qr

def qr_generator_page():
    st.title("🔶 QR Code Generator")
    
    # Create columns for layout
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Configure Your QR Code")
        
        # QR Code Type Selection
        qr_types = [
            "URL/Link", "Text", "Email", "Phone Call", "SMS", "WhatsApp", 
            "Social Media", "WiFi", "Geolocation", "Calendar Event",
            "Contact", "Cryptocurrency"
        ]
        qr_type = st.selectbox("Select QR Code Type", qr_types)
        
        # Content input based on type
        if qr_type == "URL/Link":
            url = st.text_input("Enter URL", placeholder="https://example.com")
            content = url
        elif qr_type == "Text":
            text = st.text_area("Enter Text", height=100)
            content = text
        elif qr_type == "Email":
            st.subheader("Email Options")
            email = st.text_input("Email Address", placeholder="user@example.com")
            subject = st.text_input("Subject (optional)")
            body = st.text_area("Body (optional)", height=100)
            content = {
                'email': email,
                'subject': subject,
                'body': body
            }
        elif qr_type == "Phone Call":
            phone = st.text_input("Phone Number", placeholder="+1234567890")
            content = phone
        elif qr_type == "SMS":
            phone = st.text_input("Phone Number", placeholder="+1234567890")
            message = st.text_area("Message", height=100)
            content = {
                'number': phone,
                'message': message
            }
        elif qr_type == "WhatsApp":
            phone = st.text_input("Phone Number", placeholder="+1234567890")
            message = st.text_area("Message (optional)", height=100)
            content = {
                'number': phone,
                'message': message
            }
        elif qr_type == "Social Media":
            platform = st.selectbox("Platform", ["Instagram", "Twitter", "Facebook", "LinkedIn", "TikTok"])
            username = st.text_input("Username/ID")
            content = {
                'platform': platform,
                'username': username
            }
        elif qr_type == "WiFi":
            ssid = st.text_input("Network Name (SSID)")
            password = st.text_input("Password", type="password")
            security = st.selectbox("Security Type", ["WPA/WPA2", "WEP", "None"])
            hidden = st.checkbox("Hidden Network")
            content = {
                'ssid': ssid,
                'password': password,
                'security': security.split('/')[0],
                'hidden': hidden
            }
        elif qr_type == "Geolocation":
            latitude = st.text_input("Latitude")
            longitude = st.text_input("Longitude")
            content = {
                'latitude': latitude,
                'longitude': longitude
            }
        elif qr_type == "Calendar Event":
            summary = st.text_input("Event Title")
            start_date = st.date_input("Start Date")
            start_time = st.time_input("Start Time")
            end_date = st.date_input("End Date")
            end_time = st.time_input("End Time")
            location = st.text_input("Location (optional)")
            description = st.text_area("Description (optional)")
            
            # Format dates for QR code
            start_datetime = datetime.combine(start_date, start_time).strftime("%Y%m%dT%H%M%S")
            end_datetime = datetime.combine(end_date, end_time).strftime("%Y%m%dT%H%M%S")
            
            content = {
                'summary': summary,
                'start_date': start_datetime,
                'end_date': end_datetime,
                'location': location,
                'description': description
            }
        elif qr_type == "Contact":
            name = st.text_input("Full Name")
            phone = st.text_input("Phone Number")
            email = st.text_input("Email")
            company = st.text_input("Company (optional)")
            title = st.text_input("Job Title (optional)")
            website = st.text_input("Website (optional)")
            address = st.text_input("Address (optional)")
            
            content = {
                'name': name,
                'phone': phone,
                'email': email,
                'company': company,
                'title': title,
                'website': website,
                'address': address
            }
        elif qr_type == "Cryptocurrency":
            crypto_type = st.selectbox("Cryptocurrency", ["Bitcoin", "Ethereum", "Litecoin", "Bitcoin Cash"])
            address = st.text_input("Wallet Address")
            amount = st.text_input("Amount (optional)")
            
            content = f"{crypto_type.lower()}:{address}"
            if amount:
                content += f"?amount={amount}"
        else:
            content = ""
        
        # Styling options
        st.subheader("🎨 Styling Options")
        qr_color = st.color_picker("QR Code Color", "#000000")
        bg_color = st.color_picker("Background Color", "#FFFFFF")
        
        # Logo upload
        logo_file = st.file_uploader("Upload Logo", type=['png', 'jpg', 'jpeg'])
        if logo_file:
            logo_img = Image.open(logo_file)
        else:
            logo_img = None
        
        # Frame and text options
        use_frame = st.checkbox("Add Frame")
        if use_frame:
            frame_color = st.color_picker("Frame Color", "#FF6B6B")
            overlay_text = st.text_input("Overlay Text")
            text_color = st.color_picker("Text Color", "#000000")
        else:
            frame_color = None
            overlay_text = ""
            text_color = "#000000"
        
        # Error correction level
        error_levels = {
            "Low (7%)": qrcode.constants.ERROR_CORRECT_L,
            "Medium (15%)": qrcode.constants.ERROR_CORRECT_M,
            "Quartile (25%)": qrcode.constants.ERROR_CORRECT_Q,
            "High (30%)": qrcode.constants.ERROR_CORRECT_H
        }
        error_level = st.selectbox("Error Correction Level", list(error_levels.keys()), index=1)
    
    with col2:
        st.subheader("📱 Live Preview")
        
        # Generate button
        generate_button = st.button("Generate QR Code", type="primary")
        
        if generate_button and content:
            # Create QR data
            qr_data = create_qr_for_type(qr_type, content)
            
            # Generate QR code
            qr_img = generate_qr_code(qr_data, error_levels[error_level])
            
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
            if logo_img:
                img = add_logo_to_qr(img, logo_img)
            
            # Add frame and text
            if use_frame:
                img = add_frame_and_text(img, frame_color, overlay_text, text_color)
            
            # Display preview
            st.markdown("<div style='border: 3px solid #4ECDC4; border-radius: 15px; padding: 1rem; background-color: #333333; text-align: center; box-shadow: 0 5px 15px rgba(0,0,0,0.3);'>", unsafe_allow_html=True)
            st.image(img, caption="Live Preview", use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Save to session state for download
            if 'current_qr' not in st.session_state:
                st.session_state.current_qr = img
            else:
                st.session_state.current_qr = img
            
            # Download Options
            st.subheader("💾 Download Options")
            
            # PNG Download
            img_buffer = io.BytesIO()
            img.save(img_buffer, format='PNG')
            img_buffer.seek(0)
            
            st.download_button(
                label="📥 Download PNG",
                data=img_buffer.getvalue(),
                file_name=f"qr_code_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png",
                mime="image/png"
            )
            
            # Create SVG version
            svg_data = create_svg_qr(qr_data, qr_color, bg_color)
            st.download_button(
                label="📥 Download SVG",
                data=svg_data,
                file_name=f"qr_code_{datetime.now().strftime('%Y%m%d_%H%M%S')}.svg",
                mime="image/svg+xml"
            )
            
            # Save to history
            if 'history' not in st.session_state:
                st.session_state.history = []
            
            # Add to history
            history_item = {
                'type': qr_type,
                'content': content if isinstance(content, str) else str(content),
                'image': img,
                'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'id': str(uuid.uuid4())[:8]
            }
            st.session_state.history.append(history_item)

if __name__ == "__main__":
    qr_generator_page()
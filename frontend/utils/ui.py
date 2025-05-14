import streamlit as st
from PIL import Image
import io
import base64

def display_qr_code(qr_img, download_name="qr_code"):
    """Display QR code in Streamlit with download button"""
    # Convert PIL image to bytes
    img_byte_arr = io.BytesIO()
    qr_img.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)
    
    # Display the image
    st.image(qr_img, caption="Generated QR Code", use_column_width=True)
    
    # Create download button
    st.download_button(
        label="Download QR Code",
        data=img_byte_arr,
        file_name=f"{download_name}.png",
        mime="image/png"
    )

def display_svg_qr(svg_string, download_name="qr_code"):
    """Display SVG QR code in Streamlit with download button"""
    # Display the SVG
    st.markdown(f"<div style='text-align: center;'>{svg_string}</div>", unsafe_allow_html=True)
    
    # Create download button for SVG
    st.download_button(
        label="Download SVG QR Code",
        data=svg_string,
        file_name=f"{download_name}.svg",
        mime="image/svg+xml"
    )

def create_sidebar_menu():
    """Create a sidebar menu for navigation"""
    with st.sidebar:
        st.title("QR Code Generator")
        menu = st.radio(
            "Menu",
            ["Generate QR Code", "URL Shortener", "Analytics", "Settings"],
            index=0
        )
        
        st.markdown("---")
        st.markdown("### About")
        st.markdown("QR Code Generator with URL shortener and analytics.")
        
    return menu

def show_success_message(message):
    """Show a success message"""
    st.success(message)

def show_error_message(message):
    """Show an error message"""
    st.error(message)

def show_info_message(message):
    """Show an info message"""
    st.info(message)

def show_warning_message(message):
    """Show a warning message"""
    st.warning(message)

def create_qr_options_form():
    """Create a form for QR code options"""
    with st.expander("QR Code Options", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            error_correction = st.selectbox(
                "Error Correction",
                ["Low", "Medium", "High", "Highest"],
                index=1
            )
            
            box_size = st.slider(
                "Box Size",
                min_value=5,
                max_value=20,
                value=10
            )
        
        with col2:
            border = st.slider(
                "Border Size",
                min_value=1,
                max_value=10,
                value=4
            )
            
            version = st.selectbox(
                "QR Version",
                ["Auto"] + [str(i) for i in range(1, 41)],
                index=0
            )
    
    return {
        "error_correction": error_correction,
        "box_size": box_size,
        "border": border,
        "version": None if version == "Auto" else int(version)
    }

def create_customization_form():
    """Create a form for QR code customization"""
    with st.expander("Customize QR Code", expanded=False):
        # Colors
        st.subheader("Colors")
        col1, col2 = st.columns(2)
        with col1:
            fill_color = st.color_picker("Fill Color", "#000000")
        with col2:
            back_color = st.color_picker("Background Color", "#FFFFFF")
        
        # Logo options
        st.subheader("Logo")
        include_logo = st.checkbox("Include Logo", value=False)
        
        logo_options = {}
        if include_logo:
            col1, col2 = st.columns(2)
            with col1:
                logo_file = st.file_uploader("Upload Logo", type=["png", "jpg", "jpeg"])
                logo_shape = st.selectbox("Logo Shape", ["Square", "Circle"], index=0)
            
            with col2:
                logo_size = st.slider("Logo Size", min_value=5, max_value=50, value=20) / 100
                logo_border = st.checkbox("Add Logo Border", value=True)
            
            logo_options = {
                "file": logo_file,
                "shape": logo_shape.lower(),
                "size": logo_size,
                "border": logo_border
            }
        
        # Frame options
        st.subheader("Frame")
        include_frame = st.checkbox("Add Frame", value=False)
        
        frame_options = {}
        if include_frame:
            col1, col2 = st.columns(2)
            with col1:
                frame_color = st.color_picker("Frame Color", "#4CAF50")
                frame_style = st.selectbox("Frame Style", ["Square", "Rounded", "Circle"], index=1)
            
            with col2:
                frame_width = st.slider("Frame Width", min_value=10, max_value=100, value=50)
                frame_text = st.text_input("Frame Text", "Scan me!")
            
            frame_options = {
                "color": frame_color,
                "style": frame_style.lower(),
                "width": frame_width,
                "text": frame_text,
                "text_color": st.color_picker("Text Color", "#FFFFFF")
            }
    
    return {
        "fill_color": fill_color,
        "back_color": back_color,
        "logo": logo_options if include_logo else None,
        "frame": frame_options if include_frame else None
    }

def create_analytics_dashboard(analytics_data):
    """Create an analytics dashboard"""
    if not analytics_data:
        st.info("No analytics data available.")
        return
    
    # Summary metrics
    st.subheader("Summary")
    col1, col2, col3 = st.columns(3)
    
    total_scans = len(analytics_data)
    unique_qrs = len(set([item.get('qr_id') for item in analytics_data]))
    
    with col1:
        st.metric("Total Scans", total_scans)
    
    with col2:
        st.metric("Unique QR Codes", unique_qrs)
    
    with col3:
        # Get most recent scan
        if analytics_data:
            latest_scan = analytics_data[0].get('timestamp')
            st.metric("Latest Scan", latest_scan)
    
    # Device breakdown
    st.subheader("Device Breakdown")
    devices = {}
    for item in analytics_data:
        device = item.get('device', 'Unknown')
        devices[device] = devices.get(device, 0) + 1
    
    # Create a pie chart
    device_labels = list(devices.keys())
    device_values = list(devices.values())
    
    # Use Streamlit's native chart
    st.bar_chart(devices)
    
    # Detailed scan history
    st.subheader("Scan History")
    st.dataframe(analytics_data)

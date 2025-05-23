
import streamlit as st
from PIL import Image
import io
import os
import tempfile

def image_converter_page():
    st.title("🖼️ Image Converter")
    
    # Create a card-like container for the converter
    with st.container():
        st.markdown("""
        <div class="card-header">
            Convert Images Between Formats
        </div>
        """, unsafe_allow_html=True)
        
        st.write("Upload an image and convert it to your desired format.")
        
        # File uploader for image
        uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png", "webp", "bmp", "tiff", "gif"])
        
        if uploaded_file is not None:
            try:
                # Read the image
                image = Image.open(uploaded_file)
                
                # Display the uploaded image
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("Original Image")
                    st.image(image, use_column_width=True)
                    st.write(f"**Format:** {image.format}")
                    st.write(f"**Size:** {image.size[0]} x {image.size[1]} pixels")
                    st.write(f"**Mode:** {image.mode}")
                
                with col2:
                    st.subheader("Convert To")
                    
                    # Select target format
                    target_format = st.selectbox(
                        "Select target format",
                        ["PNG", "JPEG", "WEBP", "BMP", "TIFF", "GIF"],
                        index=0
                    )
                    
                    # Quality slider for formats that support it
                    quality = None
                    if target_format in ["JPEG", "WEBP"]:
                        quality = st.slider("Quality", 1, 100, 95)  # Default to higher quality
                    
                    # Additional options based on format
                    options = {}
                    
                    # Add high quality preservation checkbox
                    preserve_quality = st.checkbox("Preserve highest quality", True, 
                                                help="When enabled, the converter will prioritize quality over file size")
                    
                    if target_format == "PNG":
                        if preserve_quality:
                            compression_level = st.slider("Compression level", 0, 9, 0,
                                                        help="0 = no compression (best quality), 9 = max compression (smaller file)")
                        else:
                            compression_level = st.slider("Compression level", 0, 9, 6,
                                                        help="0 = no compression (best quality), 9 = max compression (smaller file)")
                        options["compress_level"] = compression_level
                        
                        # Add option to optimize for transparency
                        if image.mode == "RGBA":
                            optimize_transparency = st.checkbox("Optimize transparency", True,
                                                            help="Preserves transparent areas with high quality")
                            if optimize_transparency:
                                options["optimize"] = True
                    
                    elif target_format == "WEBP":
                        if preserve_quality:
                            lossless = st.checkbox("Lossless", True,
                                                help="Lossless compression preserves all image data but results in larger files")
                        else:
                            lossless = st.checkbox("Lossless", False,
                                                help="Lossless compression preserves all image data but results in larger files")
                        options["lossless"] = lossless
                        
                        if not lossless and quality:
                            options["quality"] = quality
                            
                        # Add method option for better quality
                        method_options = [0, 1, 2, 3, 4, 5, 6]
                        if preserve_quality:
                            method = st.selectbox("Encoding method", method_options, index=6,
                                                help="Higher values = better quality but slower encoding (0-6)")
                        else:
                            method = st.selectbox("Encoding method", method_options, index=4,
                                                help="Higher values = better quality but slower encoding (0-6)")
                        options["method"] = method
                    
                    elif target_format == "TIFF":
                        compression_options = ["None", "LZW", "DEFLATE", "JPEG"]
                        if preserve_quality:
                            compression = st.selectbox("Compression", compression_options, index=0,
                                                    help="'None' preserves highest quality, others compress the image")
                        else:
                            compression = st.selectbox("Compression", compression_options, index=1,
                                                    help="'None' preserves highest quality, others compress the image")
                        
                        if compression != "None":
                            options["compression"] = compression
                            
                        # Add resolution option for high-quality printing
                        if preserve_quality:
                            resolution = st.slider("Resolution (DPI)", 72, 600, 300,
                                                help="Higher DPI values result in better print quality")
                            options["resolution"] = resolution
                    
                    elif target_format == "JPEG":
                        # Add progressive and optimize options
                        if preserve_quality:
                            options["optimize"] = True
                            options["progressive"] = st.checkbox("Progressive loading", True,
                                                            help="Creates a progressive JPEG that loads gradually in browsers")
                        else:
                            options["optimize"] = st.checkbox("Optimize", True,
                                                        help="Optimize the JPEG file for smaller size while maintaining quality")
                            options["progressive"] = st.checkbox("Progressive loading", False,
                                                            help="Creates a progressive JPEG that loads gradually in browsers")
                    
                    # Convert button
                    if st.button("Convert Image"):
                        with st.spinner(f"Converting to {target_format}..."):
                            # Create a BytesIO object to store the converted image
                            output = io.BytesIO()
                            
                            # Convert image mode if needed
                            if target_format == "JPEG" and image.mode == "RGBA":
                                image = image.convert("RGB")
                            
                            # Save the image with the selected format and options
                            if target_format == "JPEG" and quality:
                                image.save(output, format=target_format, quality=quality, **options)
                            else:
                                image.save(output, format=target_format, **options)
                            
                            # Get the image data
                            converted_image_data = output.getvalue()
                            
                            # Display the converted image
                            st.subheader("Converted Image")
                            st.image(converted_image_data, use_column_width=True)
                            
                            # Create a download button
                            file_extension = target_format.lower()
                            if file_extension == "jpeg":
                                file_extension = "jpg"
                            
                            original_filename = uploaded_file.name.split(".")[0]
                            
                            st.download_button(
                                label=f"Download {target_format} Image",
                                data=converted_image_data,
                                file_name=f"{original_filename}.{file_extension}",
                                mime=f"image/{file_extension}"
                            )
                            
                            # Display file size comparison
                            original_size = len(uploaded_file.getvalue()) / 1024  # KB
                            converted_size = len(converted_image_data) / 1024  # KB
                            
                            st.write(f"**Original size:** {original_size:.2f} KB")
                            st.write(f"**Converted size:** {converted_size:.2f} KB")
                            
                            size_change = converted_size - original_size
                            if size_change > 0:
                                st.write(f"**Size change:** +{size_change:.2f} KB (increased)")
                            else:
                                st.write(f"**Size change:** {size_change:.2f} KB (reduced)")
            
            except Exception as e:
                st.error(f"Error: {str(e)}")
                st.info("Please upload a valid image file.")
        
        # Batch conversion
        st.markdown("---")
        st.subheader("Batch Conversion")
        st.write("Convert multiple images at once.")
        
        # File uploader for multiple images
        batch_files = st.file_uploader("Upload multiple images", type=["jpg", "jpeg", "png", "webp", "bmp", "tiff", "gif"], accept_multiple_files=True)
        
        if batch_files:
            # Select target format for batch conversion
            batch_format = st.selectbox(
                "Select target format for all images",
                ["PNG", "JPEG", "WEBP", "BMP", "TIFF", "GIF"],
                index=0,
                key="batch_format"
            )
            
            # Quality slider for formats that support it
            batch_quality = None
            if batch_format in ["JPEG", "WEBP"]:
                batch_quality = st.slider("Quality", 1, 100, 95, key="batch_quality")
                
            # Add high quality preservation checkbox for batch conversion
            preserve_batch_quality = st.checkbox("Preserve highest quality for all images", True, 
                                            help="When enabled, the converter will prioritize quality over file size")
            
            # Additional options based on format for batch conversion
            batch_options = {}
            
            if batch_format == "PNG":
                if preserve_batch_quality:
                    batch_compression = st.slider("Compression level", 0, 9, 0, key="batch_compression",
                                            help="0 = no compression (best quality), 9 = max compression (smaller file)")
                else:
                    batch_compression = st.slider("Compression level", 0, 9, 6, key="batch_compression",
                                            help="0 = no compression (best quality), 9 = max compression (smaller file)")
                batch_options["compress_level"] = batch_compression
                
                # Add option to optimize for transparency
                batch_options["optimize"] = True
            
            elif batch_format == "WEBP":
                if preserve_batch_quality:
                    batch_lossless = st.checkbox("Lossless", True, key="batch_lossless",
                                            help="Lossless compression preserves all image data but results in larger files")
                else:
                    batch_lossless = st.checkbox("Lossless", False, key="batch_lossless",
                                            help="Lossless compression preserves all image data but results in larger files")
                batch_options["lossless"] = batch_lossless
                
                if not batch_lossless and batch_quality:
                    batch_options["quality"] = batch_quality
                
                # Add method option for better quality
                if preserve_batch_quality:
                    batch_options["method"] = 6  # Best quality method
                
            elif batch_format == "TIFF":
                compression_options = ["None", "LZW", "DEFLATE", "JPEG"]
                if preserve_batch_quality:
                    batch_compression = st.selectbox("Compression", compression_options, index=0, key="batch_tiff_compression",
                                                help="'None' preserves highest quality, others compress the image")
                else:
                    batch_compression = st.selectbox("Compression", compression_options, index=1, key="batch_tiff_compression",
                                                help="'None' preserves highest quality, others compress the image")
                
                if batch_compression != "None":
                    batch_options["compression"] = batch_compression
                
                # Add resolution option for high-quality printing
                if preserve_batch_quality:
                    batch_options["resolution"] = 300  # Good print quality
            
            elif batch_format == "JPEG":
                # Add progressive and optimize options
                if preserve_batch_quality:
                    batch_options["optimize"] = True
                    batch_options["progressive"] = True
            
            # Convert button for batch
            if st.button("Convert All Images"):
                with st.spinner(f"Converting {len(batch_files)} images to {batch_format}..."):
                    # Create a temporary directory to store the converted images
                    with tempfile.TemporaryDirectory() as temp_dir:
                        # Convert each image
                        converted_files = []
                        
                        for i, file in enumerate(batch_files):
                            try:
                                # Read the image
                                image = Image.open(file)
                                
                                # Convert image mode if needed
                                if batch_format == "JPEG" and image.mode == "RGBA":
                                    image = image.convert("RGB")
                                
                                # Create a filename for the converted image
                                file_extension = batch_format.lower()
                                if file_extension == "jpeg":
                                    file_extension = "jpg"
                                
                                original_filename = os.path.splitext(file.name)[0]
                                output_filename = f"{original_filename}.{file_extension}"
                                output_path = os.path.join(temp_dir, output_filename)
                                
                                # Save the image with the selected format and options
                                if batch_format == "JPEG" and batch_quality:
                                    # Apply batch_options and quality
                                    save_options = batch_options.copy()
                                    save_options["quality"] = batch_quality
                                    image.save(output_path, format=batch_format, **save_options)
                                elif batch_format == "WEBP" and batch_quality and not batch_options.get("lossless", False):
                                    # Apply batch_options and quality for lossy WEBP
                                    save_options = batch_options.copy()
                                    save_options["quality"] = batch_quality
                                    image.save(output_path, format=batch_format, **save_options)
                                else:
                                    # Apply batch_options
                                    image.save(output_path, format=batch_format, **batch_options)
                                
                                # Add the converted file to the list
                                converted_files.append((output_filename, output_path))
                                
                                # Show progress
                                if (i + 1) % 5 == 0 or i == len(batch_files) - 1:
                                    st.text(f"Processed {i + 1} of {len(batch_files)} images")
                            
                            except Exception as e:
                                st.error(f"Error converting {file.name}: {str(e)}")
                        
                        # Create a download button for each converted image
                        if converted_files:
                            st.success(f"Successfully converted {len(converted_files)} of {len(batch_files)} images.")
                            
                            for filename, filepath in converted_files:
                                with open(filepath, "rb") as f:
                                    file_data = f.read()
                            
                                st.download_button(
                                    label=f"Download {filename}",
                                    data=file_data,
                                    file_name=filename,
                                    mime=f"image/{file_extension}",
                                    key=f"download_{filename}"
                            )
        
        # Tips section
        with st.expander("Tips for Image Conversion"):
            st.markdown("""
            - **JPEG**: Best for photographs and realistic images, lossy compression
            - **PNG**: Best for images with transparency, lossless compression
            - **WEBP**: Modern format with good compression and quality, supports transparency
            - **GIF**: Good for simple animations, limited to 256 colors
            - **TIFF**: High quality format often used for printing, supports layers
            - **BMP**: Uncompressed format, large file sizes but no quality loss
            
            For the best results:
            - Use PNG or TIFF for images that need editing
            - Use JPEG or WEBP for web images and photos
            - Adjust quality settings to balance file size and image quality
            """)

if __name__ == "__main__":
    image_converter_page()


import streamlit as st
import os
import tempfile
import io
from PyPDF2 import PdfReader, PdfWriter, PdfMerger
import img2pdf
from PIL import Image

def pdf_tools_page():
    st.title("📄 PDF Tools")
    
    # Create a card-like container for the PDF tools
    with st.container():
        st.markdown("""
        <div class="card-header">
            All-in-One PDF Toolkit
        </div>
        """, unsafe_allow_html=True)
        
        # Create tabs for different PDF operations
        tab1, tab2, tab3, tab4 = st.tabs(["Merge PDFs", "Split PDF", "Extract Images", "Images to PDF"])
        
        # Tab 1: Merge PDFs
        with tab1:
            st.subheader("Merge Multiple PDFs")
            st.write("Upload multiple PDF files and merge them into a single document.")
            
            # File uploader for multiple PDFs
            pdf_files = st.file_uploader("Upload PDF files", type=["pdf"], accept_multiple_files=True, key="merge_pdfs")
            
            if pdf_files:
                # Show the list of uploaded files
                st.write(f"Uploaded {len(pdf_files)} files:")
                for i, pdf in enumerate(pdf_files):
                    st.write(f"{i+1}. {pdf.name}")
                
                # Option to reorder files
                st.write("Drag and drop files to reorder them (coming soon)")
                
                # Merge button
                if st.button("Merge PDFs"):
                    if len(pdf_files) < 2:
                        st.warning("Please upload at least 2 PDF files to merge.")
                    else:
                        with st.spinner("Merging PDFs..."):
                            try:
                                # Create a PDF merger
                                merger = PdfMerger()
                                
                                # Add each PDF to the merger
                                for pdf in pdf_files:
                                    merger.append(pdf)
                                
                                # Create a BytesIO object to store the merged PDF
                                merged_pdf = io.BytesIO()
                                
                                # Write the merged PDF to the BytesIO object
                                merger.write(merged_pdf)
                                merger.close()
                                
                                # Reset the position to the beginning of the BytesIO object
                                merged_pdf.seek(0)
                                
                                # Create a download button for the merged PDF
                                st.download_button(
                                    label="Download Merged PDF",
                                    data=merged_pdf,
                                    file_name="merged.pdf",
                                    mime="application/pdf"
                                )
                                
                                st.success("PDFs merged successfully!")
                            except Exception as e:
                                st.error(f"Error merging PDFs: {str(e)}")
        
        # Tab 2: Split PDF
        with tab2:
            st.subheader("Split PDF into Pages")
            st.write("Upload a PDF file and split it into individual pages or custom ranges.")
            
            # File uploader for a single PDF
            pdf_file = st.file_uploader("Upload a PDF file", type=["pdf"], key="split_pdf")
            
            if pdf_file:
                try:
                    # Read the PDF
                    pdf_reader = PdfReader(pdf_file)
                    num_pages = len(pdf_reader.pages)
                    
                    st.write(f"PDF has {num_pages} pages.")
                    
                    # Options for splitting
                    split_option = st.radio(
                        "Split options",
                        ["Extract specific pages", "Split into individual pages"]
                    )
                    
                    if split_option == "Extract specific pages":
                        # Input for page ranges
                        page_ranges = st.text_input(
                            "Enter page ranges (e.g., 1-3, 5, 7-9)",
                            help="Specify page ranges separated by commas. For example, '1-3, 5, 7-9' will extract pages 1, 2, 3, 5, 7, 8, and 9."
                        )
                        
                        if st.button("Extract Pages"):
                            if not page_ranges:
                                st.warning("Please enter page ranges.")
                            else:
                                with st.spinner("Extracting pages..."):
                                    try:
                                        # Parse page ranges
                                        pages_to_extract = []
                                        for page_range in page_ranges.split(","):
                                            page_range = page_range.strip()
                                            if "-" in page_range:
                                                start, end = map(int, page_range.split("-"))
                                                pages_to_extract.extend(range(start, end + 1))
                                            else:
                                                pages_to_extract.append(int(page_range))
                                        
                                        # Adjust for 0-based indexing
                                        pages_to_extract = [p - 1 for p in pages_to_extract if 0 < p <= num_pages]
                                        
                                        if not pages_to_extract:
                                            st.warning("No valid pages specified.")
                                        else:
                                            # Create a PDF writer
                                            pdf_writer = PdfWriter()
                                            
                                            # Add the specified pages to the writer
                                            for page_num in pages_to_extract:
                                                pdf_writer.add_page(pdf_reader.pages[page_num])
                                            
                                            # Create a BytesIO object to store the extracted PDF
                                            extracted_pdf = io.BytesIO()
                                            
                                            # Write the extracted PDF to the BytesIO object
                                            pdf_writer.write(extracted_pdf)
                                            
                                            # Reset the position to the beginning of the BytesIO object
                                            extracted_pdf.seek(0)
                                            
                                            # Create a download button for the extracted PDF
                                            st.download_button(
                                                label="Download Extracted Pages",
                                                data=extracted_pdf,
                                                file_name="extracted_pages.pdf",
                                                mime="application/pdf"
                                            )
                                            
                                            st.success(f"Successfully extracted {len(pages_to_extract)} pages.")
                                    except Exception as e:
                                        st.error(f"Error extracting pages: {str(e)}")
                    
                    elif split_option == "Split into individual pages":
                        if st.button("Split PDF"):
                            with st.spinner("Splitting PDF..."):
                                try:
                                    # Create a temporary directory to store the split PDFs
                                    with tempfile.TemporaryDirectory() as temp_dir:
                                        # Split the PDF into individual pages
                                        for i in range(num_pages):
                                            # Create a PDF writer
                                            pdf_writer = PdfWriter()
                                            
                                            # Add the page to the writer
                                            pdf_writer.add_page(pdf_reader.pages[i])
                                            
                                            # Create a file path for the page
                                            output_path = os.path.join(temp_dir, f"page_{i+1}.pdf")
                                            
                                            # Write the page to a file
                                            with open(output_path, "wb") as output_file:
                                                pdf_writer.write(output_file)
                                        
                                        # Create a ZIP file containing all the split PDFs
                                        import zipfile
                                        zip_path = os.path.join(temp_dir, "split_pages.zip")
                                        
                                        with zipfile.ZipFile(zip_path, "w") as zip_file:
                                            for i in range(num_pages):
                                                page_path = os.path.join(temp_dir, f"page_{i+1}.pdf")
                                                zip_file.write(page_path, f"page_{i+1}.pdf")
                                        
                                        # Read the ZIP file
                                        with open(zip_path, "rb") as f:
                                            zip_data = f.read()
                                        
                                        # Create a download button for the ZIP file
                                        st.download_button(
                                            label="Download Split Pages (ZIP)",
                                            data=zip_data,
                                            file_name="split_pages.zip",
                                            mime="application/zip"
                                        )
                                        
                                        st.success(f"Successfully split PDF into {num_pages} pages.")
                                except Exception as e:
                                    st.error(f"Error splitting PDF: {str(e)}")
                except Exception as e:
                    st.error(f"Error reading PDF: {str(e)}")
        
        # Tab 3: Extract Images
        with tab3:
            st.subheader("Extract Images from PDF")
            st.write("Upload a PDF file and extract all images from it.")
            
            # File uploader for a single PDF
            pdf_file = st.file_uploader("Upload a PDF file", type=["pdf"], key="extract_images")
            
            if pdf_file:
                if st.button("Extract Images"):
                    with st.spinner("Extracting images..."):
                        try:
                            # Read the PDF
                            pdf_reader = PdfReader(pdf_file)
                            
                            # Create a temporary directory to store the extracted images
                            with tempfile.TemporaryDirectory() as temp_dir:
                                # Extract images from each page
                                image_count = 0
                                
                                for i, page in enumerate(pdf_reader.pages):
                                    for j, image_file_object in enumerate(page.images):
                                        # Save the image to a file
                                        image_path = os.path.join(temp_dir, f"image_{i+1}_{j+1}.{image_file_object.name.split('.')[-1]}")
                                        with open(image_path, "wb") as f:
                                            f.write(image_file_object.data)
                                        image_count += 1
                                
                                if image_count == 0:
                                    st.warning("No images found in the PDF.")
                                else:
                                    # Create a ZIP file containing all the extracted images
                                    import zipfile
                                    zip_path = os.path.join(temp_dir, "extracted_images.zip")
                                    
                                    with zipfile.ZipFile(zip_path, "w") as zip_file:
                                        for i, page in enumerate(pdf_reader.pages):
                                            for j, image_file_object in enumerate(page.images):
                                                image_path = os.path.join(temp_dir, f"image_{i+1}_{j+1}.{image_file_object.name.split('.')[-1]}")
                                                zip_file.write(image_path, f"image_{i+1}_{j+1}.{image_file_object.name.split('.')[-1]}")
                                    
                                    # Read the ZIP file
                                    with open(zip_path, "rb") as f:
                                        zip_data = f.read()
                                    
                                    # Create a download button for the ZIP file
                                    st.download_button(
                                        label="Download Extracted Images (ZIP)",
                                        data=zip_data,
                                        file_name="extracted_images.zip",
                                        mime="application/zip"
                                    )
                                    
                                    st.success(f"Successfully extracted {image_count} images from the PDF.")
                        except Exception as e:
                            st.error(f"Error extracting images: {str(e)}")
        
        # Tab 4: Images to PDF
        with tab4:
            st.subheader("Convert Images to PDF")
            st.write("Upload multiple images and convert them into a single PDF document.")
            
            # File uploader for multiple images
            image_files = st.file_uploader(
                "Upload images",
                type=["jpg", "jpeg", "png", "bmp", "webp"],
                accept_multiple_files=True,
                key="images_to_pdf"
            )
            
            if image_files:
                # Show the list of uploaded files
                st.write(f"Uploaded {len(image_files)} images:")
                for i, img in enumerate(image_files):
                    st.write(f"{i+1}. {img.name}")
                
                # Option to reorder images
                st.write("Drag and drop images to reorder them (coming soon)")
                
                # Convert button
                if st.button("Convert to PDF"):
                    with st.spinner("Converting images to PDF..."):
                        try:
                            # Create a temporary directory to store the images
                            with tempfile.TemporaryDirectory() as temp_dir:
                                # Save each image to the temporary directory
                                image_paths = []
                                for i, img_file in enumerate(image_files):
                                    # Read the image
                                    img = Image.open(img_file)
                                    
                                    # Convert to RGB if needed
                                    if img.mode != "RGB":
                                        img = img.convert("RGB")
                                    
                                    # Save the image to a file
                                    img_path = os.path.join(temp_dir, f"image_{i+1}.jpg")
                                    img.save(img_path, "JPEG")
                                    image_paths.append(img_path)
                                
                                # Convert the images to a PDF
                                pdf_data = img2pdf.convert(image_paths)
                                
                                # Create a download button for the PDF
                                st.download_button(
                                    label="Download PDF",
                                    data=pdf_data,
                                    file_name="images_to_pdf.pdf",
                                    mime="application/pdf"
                                )
                                
                                st.success(f"Successfully converted {len(image_files)} images to PDF.")
                        except Exception as e:
                            st.error(f"Error converting images to PDF: {str(e)}")
        
        # Tips section
        with st.expander("Tips for PDF Tools"):
            st.markdown("""
            - **Merge PDFs**: Useful for combining multiple documents into one
            - **Split PDF**: Extract specific pages or split a large PDF into smaller ones
            - **Extract Images**: Get all images from a PDF document
            - **Images to PDF**: Convert multiple images into a single PDF file
            
            For the best results:
            - Make sure your PDF files are not password-protected
            - For merging, ensure all PDFs have the same orientation
            - When converting images to PDF, use high-quality images for better results
            """)

if __name__ == "__main__":
    pdf_tools_page()

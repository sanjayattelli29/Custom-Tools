
import streamlit as st
import pandas as pd
from datetime import datetime
from utils.shortener import create_short_url
from utils.qr import generate_qr_code
from utils.db import get_all_short_urls, update_original_url

def url_shortener_page():
    st.title("🔗 URL Shortener")
    
    # Create two columns - one for the form, one for the result
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Create Short URL")
        
        # URL input
        long_url = st.text_input("Enter long URL to shorten", placeholder="https://example.com/very/long/path")
        
        # Generate button
        if st.button("Generate Short URL", type="primary") and long_url:
            # URL will be validated inside create_short_url function
            with st.spinner("Generating short URL..."):
                short_url = create_short_url(long_url)
            
            if short_url:
                st.success("✅ Short URL generated successfully!")
                
                # Display the short URL in a highlighted box
                st.markdown(
                    f"""<div style='background-color: #2E4053; padding: 10px; border-radius: 5px; margin-bottom: 10px;'>
                    <h3 style='margin: 0; color: #4ECDC4;'>Your Short URL:</h3>
                    <a href='{short_url}' target='_blank' style='color: #FF6B6B; font-size: 16px; word-break: break-all;'>{short_url}</a>
                    </div>""", 
                    unsafe_allow_html=True
                )
                
                # Display as code for easy copying
                st.code(short_url, language="")
                
                # Create a copy button for the short URL
                if 'JS_EVAL_AVAILABLE' in globals() and JS_EVAL_AVAILABLE:
                    if st.button("📋 Copy to Clipboard"):
                        streamlit_js_eval.copy_to_clipboard(short_url)
                        st.success("Copied to clipboard!")
                
                # Add QR code for the short URL
                qr_img = generate_qr_code(short_url)
                st.image(qr_img, width=150, caption="Scan to use shortened URL")
                
                # Add to history
                if 'url_history' not in st.session_state:
                    st.session_state.url_history = []
                
                st.session_state.url_history.append({
                    'original_url': long_url,
                    'short_url': short_url,
                    'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
            else:
                st.error("❌ Failed to generate short URL. Please try again.")
    
    with col2:
        st.subheader("URL History")
        
        # URL History Tab
        if 'url_history' in st.session_state and st.session_state.url_history:
            # Create a DataFrame for better display
            history_data = st.session_state.url_history
            df = pd.DataFrame(history_data)
            
            # Display the table with formatting
            st.dataframe(
                df[['original_url', 'short_url', 'created_at']].rename(
                    columns={
                        'original_url': 'Original URL', 
                        'short_url': 'Short URL',
                        'created_at': 'Created At'
                    }
                ),
                column_config={
                    "Short URL": st.column_config.LinkColumn(),
                    "Original URL": st.column_config.TextColumn(width="large"),
                },
                use_container_width=True
            )
            
            # Clear history button
            if st.button("Clear History"):
                st.session_state.url_history = []
                st.success("URL history cleared!")
                st.rerun()
        else:
            st.info("No shortened URLs in your history yet. Create one using the form on the left.")
    
    # URL Management Section
    st.subheader("Manage Shortened URLs")
    
    # Get all shortened URLs from database
    short_urls = get_all_short_urls()
    
    if short_urls:
        # Create a DataFrame for better display
        columns = ['Short ID', 'Original URL', 'Created At', 'Scans', 'Short URL']
        df = pd.DataFrame(short_urls, columns=columns)
        
        # Display the table
        st.dataframe(
            df[['Short URL', 'Original URL', 'Created At', 'Scans']],
            column_config={
                "Short URL": st.column_config.LinkColumn(),
                "Original URL": st.column_config.TextColumn(width="large"),
            },
            use_container_width=True
        )
        
        # Allow editing of URLs
        st.subheader("Edit Destination URL")
        
        # Select a URL to edit
        selected_id = st.selectbox("Select URL to edit", df['Short ID'].tolist())
        
        if selected_id:
            original_url = df[df['Short ID'] == selected_id]['Original URL'].iloc[0]
            new_url = st.text_input("New destination URL", value=original_url)
            
            if st.button("Update URL") and new_url != original_url:
                # Update in database
                if update_original_url(selected_id, new_url):
                    st.success("URL updated successfully!")
                    st.rerun()
                else:
                    st.error("Error updating URL. Please try again.")
    else:
        st.info("No shortened URLs found in the database. Create some using the form above.")

if __name__ == "__main__":
    url_shortener_page()


import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from utils.db import get_analytics_data

def analytics_page():
    st.title("📊 Analytics Dashboard")
    
    # Get analytics data from database
    data_list = get_analytics_data()
    
    # Process the data to get metrics
    total_scans = len(data_list)
    
    # Calculate scans today
    today = datetime.now().strftime("%Y-%m-%d")
    scans_today = sum(1 for item in data_list if item.get('timestamp', '').startswith(today))
    
    # Calculate unique visitors
    unique_ips = set(item.get('ip_address') for item in data_list if item.get('ip_address'))
    unique_visitors = len(unique_ips)
    
    # Calculate average scans per day
    if total_scans > 0:
        # Get all dates
        dates = [item.get('timestamp', '').split(' ')[0] for item in data_list if ' ' in item.get('timestamp', '')]
        unique_dates = len(set(dates)) if dates else 1
        avg_scans_per_day = total_scans / unique_dates
    else:
        avg_scans_per_day = 0
    
    # Calculate last 7 days vs previous 7 days
    today_date = datetime.now().date()
    last_7_days = set([(today_date - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7)])
    previous_7_days = set([(today_date - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7, 14)])
    
    scans_last_7_days = sum(1 for item in data_list if item.get('timestamp', '').split(' ')[0] in last_7_days)
    scans_previous_7_days = sum(1 for item in data_list if item.get('timestamp', '').split(' ')[0] in previous_7_days)
    
    # Create metrics row
    st.subheader("Key Metrics")
    
    # Create a row of metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Scans", 
            value=total_scans,
            delta=f"{scans_today} today"
        )
    
    with col2:
        st.metric(
            label="Unique Visitors", 
            value=unique_visitors,
            delta=None
        )
    
    with col3:
        avg_scans = round(avg_scans_per_day, 1) if avg_scans_per_day else 0
        st.metric(
            label="Avg. Scans/Day", 
            value=avg_scans,
            delta=None
        )
    
    with col4:
        # Calculate trend (last 7 days vs previous 7 days)
        if scans_last_7_days > 0 and scans_previous_7_days > 0:
            trend_pct = round(((scans_last_7_days - scans_previous_7_days) / scans_previous_7_days) * 100)
            delta = f"{trend_pct}% vs previous"
        else:
            delta = None
            
        st.metric(
            label="Last 7 Days", 
            value=scans_last_7_days,
            delta=delta
        )
    
    # Create tabs for different charts
    tab1, tab2, tab3 = st.tabs(["Daily Scans", "QR Code Performance", "User Devices"])
    
    with tab1:
        st.subheader("Daily Scan Activity")
        
        # Create daily scans chart
        if data_list:
            # Process data to get daily scans
            daily_scans = {}
            for item in data_list:
                if 'timestamp' in item and item['timestamp']:
                    date_str = item['timestamp'].split(' ')[0]  # Extract date part
                    daily_scans[date_str] = daily_scans.get(date_str, 0) + 1
            
            # Convert to DataFrame
            df_daily = pd.DataFrame({
                'Date': list(daily_scans.keys()),
                'Scans': list(daily_scans.values())
            })
            
            # Convert date string to datetime
            df_daily['Date'] = pd.to_datetime(df_daily['Date'])
            
            # Sort by date
            df_daily = df_daily.sort_values('Date')
            
            # Create chart
            fig = px.line(
                df_daily, 
                x='Date', 
                y='Scans',
                markers=True,
                line_shape='linear',
                template='plotly_dark'
            )
            
            # Customize
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='#FFFFFF',
                height=400,
                margin=dict(l=20, r=20, t=30, b=20),
                hovermode='x unified'
            )
            
            # Add moving average
            if len(df_daily) > 3:
                df_daily['7-Day MA'] = df_daily['Scans'].rolling(window=7, min_periods=1).mean()
                fig.add_scatter(
                    x=df_daily['Date'], 
                    y=df_daily['7-Day MA'],
                    mode='lines',
                    name='7-Day Moving Avg',
                    line=dict(color='#4ECDC4', width=2, dash='dot')
                )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No daily scan data available yet. Start using your QR codes to collect data.")
    
    with tab2:
        st.subheader("QR Code Performance")
        
        # Create QR code performance chart
        if data_list:
            # Process data to get QR code performance
            qr_performance = {}
            for item in data_list:
                if 'qr_id' in item and item['qr_id']:
                    qr_id = item['qr_id']
                    qr_performance[qr_id] = qr_performance.get(qr_id, 0) + 1
            
            # Convert to DataFrame
            df_qr = pd.DataFrame({
                'QR Code': list(qr_performance.keys()),
                'Scans': list(qr_performance.values())
            })
            
            # Sort by scans
            df_qr = df_qr.sort_values('Scans', ascending=False)
            
            # Create chart
            fig = px.bar(
                df_qr,
                x='QR Code',
                y='Scans',
                color='Scans',
                color_continuous_scale=px.colors.sequential.Viridis,
                template='plotly_dark'
            )
            
            # Customize
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='#FFFFFF',
                height=400,
                margin=dict(l=20, r=20, t=30, b=20),
                coloraxis_showscale=False
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No QR code performance data available yet.")
    
    with tab3:
        st.subheader("User Devices")
        
        # Create device distribution chart
        if data_list:
            # Process data to get device distribution
            device_distribution = {}
            for item in data_list:
                if 'device' in item and item['device']:
                    device = item['device']
                    device_distribution[device] = device_distribution.get(device, 0) + 1
            
            # If no device data, provide a default
            if not device_distribution:
                device_distribution = {'Unknown': 1}
                
            # Convert to DataFrame
            df_devices = pd.DataFrame({
                'Device': list(device_distribution.keys()),
                'Count': list(device_distribution.values())
            })
            
            # Sort by count
            df_devices = df_devices.sort_values('Count', ascending=False)
            
            # Create chart
            fig = px.pie(
                df_devices,
                values='Count',
                names='Device',
                hole=0.4,
                color_discrete_sequence=px.colors.sequential.Viridis,
                template='plotly_dark'
            )
            
            # Customize
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='#FFFFFF',
                height=400,
                margin=dict(l=20, r=20, t=30, b=20),
                legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5)
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No device data available yet.")
    
    # URL Shortener Analytics
    st.subheader("URL Shortener Analytics")
    
    # Get URL shortener data from database
    try:
        import sqlite3
        conn = sqlite3.connect('url_shortener.db')
        c = conn.cursor()
        c.execute('''SELECT short_id, original_url, scans, created_at, short_url FROM short_urls ORDER BY scans DESC''')
        url_rows = c.fetchall()
        conn.close()
        
        if url_rows:
            # Convert to DataFrame
            df_urls = pd.DataFrame(url_rows, columns=['Short ID', 'Original URL', 'Scans', 'Created At', 'Short URL'])
            
            # Format the table
            st.dataframe(
                df_urls,
                column_config={
                    "Short URL": st.column_config.LinkColumn(),
                    "Original URL": st.column_config.TextColumn(width="large"),
                },
                use_container_width=True
            )
            
            # Create chart of top URLs
            top_urls = df_urls.sort_values('Scans', ascending=False).head(10)
            
            fig = px.bar(
                top_urls,
                x='Short ID',
                y='Scans',
                color='Scans',
                color_continuous_scale=px.colors.sequential.Viridis,
                template='plotly_dark',
                title="Top 10 Shortened URLs by Scans"
            )
            
            # Customize
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='#FFFFFF',
                height=400,
                margin=dict(l=20, r=20, t=50, b=20),
                coloraxis_showscale=False
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No URL shortener analytics available yet. Create some shortened URLs to see data here.")
    except Exception as e:
        st.error(f"Error retrieving URL shortener data: {str(e)}")
        st.info("No URL shortener analytics available yet. Create some shortened URLs to see data here.")
        
    # Export options
    st.subheader("Export Data")
    
    export_type = st.radio("Select Export Format", ["CSV", "Excel", "JSON"], horizontal=True)
    
    if st.button("Export Analytics Data"):
        # Prepare data for export
        # Process data to get daily scans for export
        daily_scans_df = None
        if data_list:
            daily_scans = {}
            for item in data_list:
                if 'timestamp' in item and item['timestamp']:
                    date_str = item['timestamp'].split(' ')[0]  # Extract date part
                    daily_scans[date_str] = daily_scans.get(date_str, 0) + 1
            
            # Convert to DataFrame
            daily_scans_df = pd.DataFrame({
                'Date': list(daily_scans.keys()),
                'Scans': list(daily_scans.values())
            })
        else:
            daily_scans_df = pd.DataFrame()
            
        # Process data to get QR code performance for export
        qr_performance_df = None
        if data_list:
            qr_performance = {}
            for item in data_list:
                if 'qr_id' in item and item['qr_id']:
                    qr_id = item['qr_id']
                    qr_performance[qr_id] = qr_performance.get(qr_id, 0) + 1
            
            # Convert to DataFrame
            qr_performance_df = pd.DataFrame({
                'QR Code': list(qr_performance.keys()),
                'Scans': list(qr_performance.values())
            })
        else:
            qr_performance_df = pd.DataFrame()
            
        # Process data to get device distribution for export
        device_distribution_df = None
        if data_list:
            device_distribution = {}
            for item in data_list:
                if 'device' in item and item['device']:
                    device = item['device']
                    device_distribution[device] = device_distribution.get(device, 0) + 1
            
            # Convert to DataFrame
            device_distribution_df = pd.DataFrame({
                'Device': list(device_distribution.keys()),
                'Count': list(device_distribution.values())
            })
        else:
            device_distribution_df = pd.DataFrame()
            
        # Get URL shortener data for export
        url_analytics_df = None
        try:
            import sqlite3
            conn = sqlite3.connect('url_shortener.db')
            c = conn.cursor()
            c.execute('''SELECT short_id, original_url, scans, created_at, short_url FROM short_urls ORDER BY scans DESC''')
            url_rows = c.fetchall()
            conn.close()
            
            if url_rows:
                url_analytics_df = pd.DataFrame(url_rows, columns=['Short ID', 'Original URL', 'Scans', 'Created At', 'Short URL'])
            else:
                url_analytics_df = pd.DataFrame()
        except Exception:
            url_analytics_df = pd.DataFrame()
            
        export_data = {
            'daily_scans': daily_scans_df,
            'qr_performance': qr_performance_df,
            'device_distribution': device_distribution_df,
            'url_analytics': url_analytics_df
        }
        
        if export_type == "CSV":
            # Create a zip file with multiple CSVs
            import io
            import zipfile
            
            buffer = io.BytesIO()
            with zipfile.ZipFile(buffer, 'w') as zip_file:
                for name, df in export_data.items():
                    if not df.empty:
                        csv_buffer = io.StringIO()
                        df.to_csv(csv_buffer, index=False)
                        zip_file.writestr(f"{name}.csv", csv_buffer.getvalue())
            
            buffer.seek(0)
            st.download_button(
                label="Download CSV Files (ZIP)",
                data=buffer,
                file_name=f"qr_analytics_export_{datetime.now().strftime('%Y%m%d')}.zip",
                mime="application/zip"
            )
            
        elif export_type == "Excel":
            # Create an Excel file with multiple sheets
            import io
            
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                for name, df in export_data.items():
                    if not df.empty:
                        df.to_excel(writer, sheet_name=name, index=False)
            
            buffer.seek(0)
            st.download_button(
                label="Download Excel File",
                data=buffer,
                file_name=f"qr_analytics_export_{datetime.now().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            
        elif export_type == "JSON":
            # Create a JSON file
            import json
            
            json_data = {
                'metadata': {
                    'exported_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'total_scans': data['total_scans'],
                    'unique_visitors': data['unique_visitors']
                }
            }
            
            for name, df in export_data.items():
                if not df.empty:
                    json_data[name] = df.to_dict(orient='records')
            
            st.download_button(
                label="Download JSON File",
                data=json.dumps(json_data, indent=2),
                file_name=f"qr_analytics_export_{datetime.now().strftime('%Y%m%d')}.json",
                mime="application/json"
            )

if __name__ == "__main__":
    analytics_page()

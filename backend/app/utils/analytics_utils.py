from app.utils.db_utils import store_scan, get_scans
from datetime import datetime

def log_qr_scan(qr_id, user_agent=None, ip_address=None):
    """Log QR code scan with user agent and IP address"""
    return store_scan(qr_id, "", user_agent, ip_address)

def get_analytics_data(qr_id=None):
    """Get analytics data for QR code scans"""
    scans = get_scans(qr_id)
    
    # Process data to extract device information
    processed_data = []
    for scan in scans:
        # Extract device info from user agent
        device = "Unknown"
        if scan.get('user_agent'):
            user_agent = str(scan.get('user_agent', '')).lower()
            if "mobile" in user_agent or "android" in user_agent or "iphone" in user_agent:
                device = "Mobile"
            elif "tablet" in user_agent or "ipad" in user_agent:
                device = "Tablet"
            else:
                device = "Desktop"
        
        processed_data.append({
            'qr_id': scan.get('qr_id'),
            'url': scan.get('url', ''),
            'timestamp': scan.get('timestamp'),
            'user_agent': scan.get('user_agent'),
            'ip_address': scan.get('ip_address'),
            'device': device
        })
    
    return processed_data

def get_scan_count(qr_id=None):
    """Get the total number of scans for a QR code or all QR codes"""
    scans = get_scans(qr_id)
    return len(scans)

def get_unique_devices(qr_id=None):
    """Get the number of unique devices that scanned a QR code"""
    data = get_analytics_data(qr_id)
    
    devices = {}
    for item in data:
        device = item.get('device', 'Unknown')
        devices[device] = devices.get(device, 0) + 1
    
    return devices

def get_scan_timeline(qr_id=None):
    """Get timeline data for QR code scans"""
    data = get_analytics_data(qr_id)
    
    # Group by date
    timeline = {}
    for item in data:
        timestamp = item.get('timestamp', '')
        date = timestamp.split(' ')[0] if ' ' in timestamp else timestamp
        
        timeline[date] = timeline.get(date, 0) + 1
    
    # Sort by date
    sorted_timeline = {k: timeline[k] for k in sorted(timeline.keys())}
    
    return sorted_timeline

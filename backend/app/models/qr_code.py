from datetime import datetime

class QRCode:
    """QR Code model for representing QR code data"""
    
    def __init__(self, qr_id, data, image_url=None, created_at=None, scan_count=0):
        self.qr_id = qr_id
        self.data = data
        self.image_url = image_url
        self.created_at = created_at or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.scan_count = scan_count
    
    def to_dict(self):
        """Convert QR code object to dictionary"""
        return {
            'qr_id': self.qr_id,
            'data': self.data,
            'image_url': self.image_url,
            'created_at': self.created_at,
            'scan_count': self.scan_count
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create QR code object from dictionary"""
        return cls(
            qr_id=data.get('qr_id'),
            data=data.get('data'),
            image_url=data.get('image_url'),
            created_at=data.get('created_at'),
            scan_count=data.get('scan_count', 0)
        )

class QRScan:
    """QR Scan model for representing QR code scan data"""
    
    def __init__(self, qr_id, timestamp=None, user_agent=None, ip_address=None, device=None):
        self.qr_id = qr_id
        self.timestamp = timestamp or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.user_agent = user_agent
        self.ip_address = ip_address
        self.device = device or "Unknown"
    
    def to_dict(self):
        """Convert QR scan object to dictionary"""
        return {
            'qr_id': self.qr_id,
            'timestamp': self.timestamp,
            'user_agent': self.user_agent,
            'ip_address': self.ip_address,
            'device': self.device
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create QR scan object from dictionary"""
        return cls(
            qr_id=data.get('qr_id'),
            timestamp=data.get('timestamp'),
            user_agent=data.get('user_agent'),
            ip_address=data.get('ip_address'),
            device=data.get('device')
        )

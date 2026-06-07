import json
import base64
import qrcode
from io import BytesIO
from .encryption import EncryptionUtils

class ColdStorage:
    """Utility functions for cold storage and paper wallets"""
    
    @staticmethod
    def generate_paper_wallet(address: str, private_key: str, network: str) -> str:
        """Generate paper wallet HTML"""
        import datetime
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Zeontrust Wallet - Paper Wallet</title>
            <style>
                body {{
                    font-family: 'Courier New', monospace;
                    padding: 40px;
                    background: #fff;
                    color: #000;
                }}
                .container {{
                    max-width: 800px;
                    margin: 0 auto;
                    border: 2px solid #000;
                    padding: 20px;
                }}
                .header {{
                    text-align: center;
                    border-bottom: 1px solid #ccc;
                    padding-bottom: 20px;
                }}
                .address-box, .key-box {{
                    background: #f5f5f5;
                    padding: 15px;
                    margin: 20px 0;
                    border: 1px solid #ddd;
                    word-break: break-all;
                }}
                .warning {{
                    background: #ffebee;
                    border: 1px solid #ef5350;
                    padding: 15px;
                    margin: 20px 0;
                    color: #c62828;
                }}
                .footer {{
                    text-align: center;
                    margin-top: 30px;
                    font-size: 12px;
                    color: #666;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🌌 Zeontrust Wallet - Paper Wallet</h1>
                    <p>Network: {network.upper()}</p>
                </div>
                
                <div class="address-box">
                    <strong>📤 Public Address:</strong><br>
                    <code>{address}</code>
                </div>
                
                <div class="key-box">
                    <strong>🔑 Private Key (KEEP SECRET!):</strong><br>
                    <code>{private_key}</code>
                </div>
                
                <div class="warning">
                    ⚠️ IMPORTANT SECURITY WARNINGS:<br><br>
                    1. Never share your private key with anyone!<br>
                    2. Store this paper wallet in a secure physical location.<br>
                    3. Consider making multiple copies and storing in different secure locations.<br>
                    4. Do not store this file digitally - print it and delete the digital copy.<br>
                    5. Anyone with access to this private key controls your funds!
                </div>
                
                <div class="footer">
                    Generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br>
                    Zeontrust Wallet - Secure Multi-Chain Wallet
                </div>
            </div>
        </body>
        </html>
        """
        return html
    
    @staticmethod
    def generate_qr_code(data: str) -> str:
        """Generate QR code as base64 image"""
        qr = qrcode.QRCode(version=1, box_size=10, border=4)
        qr.add_data(data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        
        return base64.b64encode(buffer.getvalue()).decode()
    
    @staticmethod
    def create_encrypted_backup(mnemonic: str, password: str) -> str:
        """Create encrypted backup file content"""
        encrypted = EncryptionUtils.encrypt_with_password(mnemonic, password)
        backup_data = {
            'version': '1.0',
            'type': 'mnemonic_backup',
            'data': encrypted,
            'created_at': datetime.now().isoformat()
        }
        return json.dumps(backup_data, indent=2)
    
    @staticmethod
    def restore_from_encrypted_backup(backup_json: str, password: str) -> str:
        """Restore mnemonic from encrypted backup"""
        data = json.loads(backup_json)
        encrypted = data.get('data')
        if not encrypted:
            raise ValueError('Invalid backup file')
        return EncryptionUtils.decrypt_with_password(encrypted, password)
    
    @staticmethod
    def generate_cold_storage_instructions() -> str:
        """Generate cold storage instructions"""
        return """
        🔐 COLD STORAGE INSTRUCTIONS
        
        1. Generate wallet on an air-gapped computer (no internet)
        2. Print the paper wallet or write down the private key
        3. Store in a safe, waterproof, fireproof location
        4. Create multiple copies in different secure locations
        5. Never take a photo of your private key
        6. Never store private key digitally on any connected device
        7. Use a hardware wallet for everyday transactions
        8. Only restore cold storage when you need to access funds
        """
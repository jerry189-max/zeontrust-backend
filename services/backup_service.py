import json
import base64
import hashlib
from models.security_models import BackupHistoryModel

class BackupService:
    
    @staticmethod
    def backup_mnemonic(mnemonic: str, password: str) -> dict:
        encrypted = base64.b64encode(f"{mnemonic}:{password}".encode()).decode()
        return {'encrypted_data': encrypted, 'algorithm': 'base64'}
    
    @staticmethod
    def restore_mnemonic(backup_data: dict, password: str) -> str:
        decrypted = base64.b64decode(backup_data['encrypted_data']).decode()
        stored_mnemonic, stored_password = decrypted.rsplit(':', 1)
        if stored_password != password:
            raise ValueError('Invalid password')
        return stored_mnemonic
    
    @staticmethod
    def export_backup_to_file(mnemonic: str, password: str, filepath: str) -> None:
        backup_data = BackupService.backup_mnemonic(mnemonic, password)
        with open(filepath, 'w') as f:
            json.dump(backup_data, f)
    
    @staticmethod
    def import_backup_from_file(filepath: str, password: str) -> str:
        with open(filepath, 'r') as f:
            backup_data = json.load(f)
        return BackupService.restore_mnemonic(backup_data, password)
    
    @staticmethod
    def generate_qr_code(data: str) -> str:
        return f"data:image/png;base64,{base64.b64encode(data.encode()).decode()}"
    
    @staticmethod
    def verify_backup_integrity(mnemonic: str, stored_hash: str) -> bool:
        current_hash = hashlib.sha256(mnemonic.encode()).hexdigest()
        return current_hash == stored_hash
    
    @staticmethod
    def create_paper_wallet(address: str, private_key: str) -> str:
        return f"""
        <html>
        <head><title>Zeontrust Wallet - Paper Wallet</title></head>
        <body style="font-family: monospace; padding: 20px;">
            <h1>Zeontrust Wallet - Paper Wallet</h1>
            <p><strong>Address:</strong> {address}</p>
            <p><strong>Private Key:</strong> {private_key}</p>
            <p>Created: {datetime.now().isoformat()}</p>
            <p>Store this securely!</p>
        </body>
        </html>
        """
    
    @staticmethod
    def record_backup_history(user_id: int, wallet_id: int, backup_type: str) -> int:
        return BackupHistoryModel.create(user_id, wallet_id, backup_type)
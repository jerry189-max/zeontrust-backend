import base64
import hashlib
import secrets

class EncryptionService:
    
    @staticmethod
    def encrypt_private_key(private_key: str, password: str) -> str:
        salt = secrets.token_hex(16)
        key = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
        encrypted = base64.b64encode(f"{private_key}:{salt}".encode()).decode()
        return encrypted
    
    @staticmethod
    def decrypt_private_key(encrypted_key: str, password: str) -> str:
        decrypted = base64.b64decode(encrypted_key.encode()).decode()
        private_key, salt = decrypted.rsplit(':', 1)
        return private_key
    
    @staticmethod
    def encrypt_data(data: str, password: str) -> str:
        salt = secrets.token_hex(16)
        encrypted = base64.b64encode(f"{data}:{salt}".encode()).decode()
        return encrypted
    
    @staticmethod
    def decrypt_data(encrypted_data: str, password: str) -> str:
        decrypted = base64.b64decode(encrypted_data.encode()).decode()
        data, salt = decrypted.rsplit(':', 1)
        return data
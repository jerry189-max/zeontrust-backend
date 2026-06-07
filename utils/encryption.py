import hashlib
import base64
import secrets
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
from cryptography.hazmat.primitives import hashes

class EncryptionUtils:
    """Utility functions for encryption/decryption"""
    
    @staticmethod
    def generate_key() -> bytes:
        """Generate a new encryption key"""
        return Fernet.generate_key()
    
    @staticmethod
    def derive_key(password: str, salt: bytes = None, iterations: int = 100000) -> tuple:
        """Derive encryption key from password"""
        if salt is None:
            salt = secrets.token_bytes(16)
        
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=iterations,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key, salt
    
    @staticmethod
    def encrypt_data(data: str, key: bytes) -> str:
        """Encrypt data using Fernet"""
        f = Fernet(key)
        encrypted = f.encrypt(data.encode())
        return base64.b64encode(encrypted).decode()
    
    @staticmethod
    def decrypt_data(encrypted_data: str, key: bytes) -> str:
        """Decrypt data using Fernet"""
        f = Fernet(key)
        decrypted = f.decrypt(base64.b64decode(encrypted_data))
        return decrypted.decode()
    
    @staticmethod
    def encrypt_with_password(data: str, password: str) -> str:
        """Encrypt data with password"""
        key, salt = EncryptionUtils.derive_key(password)
        encrypted = EncryptionUtils.encrypt_data(data, key)
        return base64.b64encode(salt + encrypted.encode()).decode()
    
    @staticmethod
    def decrypt_with_password(encrypted_data: str, password: str) -> str:
        """Decrypt data with password"""
        data = base64.b64decode(encrypted_data)
        salt = data[:16]
        encrypted = data[16:].decode()
        key, _ = EncryptionUtils.derive_key(password, salt)
        return EncryptionUtils.decrypt_data(encrypted, key)
    
    @staticmethod
    def hash_data(data: str, algorithm: str = 'sha256') -> str:
        """Hash data using specified algorithm"""
        if algorithm == 'sha256':
            return hashlib.sha256(data.encode()).hexdigest()
        elif algorithm == 'sha512':
            return hashlib.sha512(data.encode()).hexdigest()
        elif algorithm == 'md5':
            return hashlib.md5(data.encode()).hexdigest()
        else:
            return hashlib.sha256(data.encode()).hexdigest()
    
    @staticmethod
    def verify_hash(data: str, hash_value: str, algorithm: str = 'sha256') -> bool:
        """Verify data against hash"""
        return EncryptionUtils.hash_data(data, algorithm) == hash_value
    
    @staticmethod
    def generate_mnemonic_hash(mnemonic: str) -> str:
        """Generate hash for mnemonic verification"""
        return hashlib.pbkdf2_hmac('sha256', mnemonic.encode(), b'mnemonic_salt', 100000).hex()
    
    @staticmethod
    def encrypt_private_key(private_key: str, password: str) -> str:
        """Encrypt private key with password"""
        return EncryptionUtils.encrypt_with_password(private_key, password)
    
    @staticmethod
    def decrypt_private_key(encrypted_key: str, password: str) -> str:
        """Decrypt private key with password"""
        return EncryptionUtils.decrypt_with_password(encrypted_key, password)
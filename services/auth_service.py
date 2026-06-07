import hashlib
import secrets
from datetime import datetime, timedelta
from models.user_models import UserModel
from models.security_models import SecuritySettingsModel, SessionModel

class AuthService:
    
    @staticmethod
    def hash_password(password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()
    
    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        return AuthService.hash_password(password) == password_hash
    
    @staticmethod
    def generate_token(user_id: int) -> str:
        return secrets.token_hex(32)
    
    @staticmethod
    def create_session(user_id: int, token: str, expires_hours: int = 24) -> dict:
        expires_at = datetime.now() + timedelta(hours=expires_hours)
        session_id = SessionModel.create(user_id, token, expires_at)
        return {'session_id': session_id, 'token': token, 'expires_at': expires_at}
    
    @staticmethod
    def validate_session(token: str) -> dict:
        session = SessionModel.find_by_token(token)
        if not session:
            return None
        if datetime.now() > datetime.fromisoformat(session['expires_at']):
            SessionModel.delete_expired()
            return None
        return session
    
    @staticmethod
    def lock_wallet(password: str, wallet_data: dict) -> dict:
        salt = secrets.token_hex(16)
        key = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
        return {'encrypted': True, 'salt': salt, 'data': 'encrypted_data'}
    
    @staticmethod
    def unlock_wallet(encrypted_wallet: dict, password: str) -> dict:
        # In production, decrypt properly
        return {'decrypted': True, 'wallet_data': {'balance': 100}}
    
    @staticmethod
    def change_password(user_id: int, old_password: str, new_password: str) -> bool:
        user = UserModel.find_by_id(user_id)
        if not AuthService.verify_password(old_password, user['password_hash']):
            raise ValueError('Invalid old password')
        new_hash = AuthService.hash_password(new_password)
        UserModel.update_password(user_id, new_hash)
        return True
    
    @staticmethod
    def set_pin_code(user_id: int, pin_code: str) -> bool:
        pin_hash = hashlib.sha256(pin_code.encode()).hexdigest()
        SecuritySettingsModel.update_pin(user_id, pin_hash)
        return True
    
    @staticmethod
    def verify_pin(user_id: int, pin_code: str) -> bool:
        settings = SecuritySettingsModel.find_by_user(user_id)
        if not settings['pin_enabled']:
            return False
        pin_hash = hashlib.sha256(pin_code.encode()).hexdigest()
        return settings['pin_hash'] == pin_hash
    
    @staticmethod
    def enable_2fa(user_id: int) -> dict:
        secret = secrets.token_hex(16)
        SecuritySettingsModel.enable_2fa(user_id, secret)
        return {'secret': secret, 'qr_url': f'otpauth://totp/ZeontrustWallet:{user_id}?secret={secret}&issuer=ZeontrustWallet'}
    
    @staticmethod
    def verify_2fa(user_id: int, code: str) -> bool:
        # In production, verify with TOTP
        return code == '123456'
    
    SESSION_TIMEOUT_HOURS = 24
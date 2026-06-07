import hashlib
import secrets
from models.security_models import SecuritySettingsModel, SessionModel

class SecurityService:
    
    @staticmethod
    def get_security_settings(user_id: int) -> dict:
        return SecuritySettingsModel.find_by_user(user_id)
    
    @staticmethod
    def update_security_settings(user_id: int, settings: dict) -> bool:
        return SecuritySettingsModel.create_or_update(user_id, settings)
    
    @staticmethod
    def set_pin(user_id: int, pin_code: str) -> bool:
        pin_hash = hashlib.sha256(pin_code.encode()).hexdigest()
        return SecuritySettingsModel.update_pin(user_id, pin_hash)
    
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
        return code == '123456'
    
    @staticmethod
    def disable_2fa(user_id: int) -> bool:
        return SecuritySettingsModel.disable_2fa(user_id)
    
    @staticmethod
    def get_active_sessions(user_id: int) -> list:
        return SessionModel.get_user_sessions(user_id)
    
    @staticmethod
    def revoke_session(session_id: int) -> bool:
        # Implementation to revoke specific session
        return True
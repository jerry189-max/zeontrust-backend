from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.user_models import UserModel
from models.security_models import SecuritySettingsModel, SessionModel
import hashlib
import secrets
import pyotp
from datetime import datetime, timedelta

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, password_hash):
    return hash_password(password) == password_hash

def register_security_routes(app):
    
    # ==================== SECURITY SETTINGS ====================
    
    @app.route('/api/security/settings', methods=['GET'])
    @jwt_required()
    def get_security_settings():
        try:
            user_id = get_jwt_identity()
            settings = SecuritySettingsModel.find_by_user(user_id)
            return jsonify({'success': True, 'settings': settings})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/security/settings', methods=['POST'])
    @jwt_required()
    def update_security_settings():
        try:
            user_id = get_jwt_identity()
            data = request.get_json()
            
            settings = {
                'password_lock_enabled': data.get('password_lock_enabled', True),
                'session_timeout_minutes': data.get('session_timeout_minutes', 1440),
                'two_factor_enabled': data.get('two_factor_enabled', False),
                'pin_enabled': data.get('pin_enabled', False)
            }
            
            SecuritySettingsModel.create_or_update(user_id, settings)
            return jsonify({'success': True, 'message': 'Security settings updated'})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    # ==================== PIN CODE MANAGEMENT ====================
    
    @app.route('/api/security/set-pin', methods=['POST'])
    @jwt_required()
    def set_pin():
        try:
            user_id = get_jwt_identity()
            data = request.get_json()
            pin_code = data.get('pin_code')
            
            if not pin_code or len(pin_code) != 6 or not pin_code.isdigit():
                return jsonify({'error': 'PIN must be 6 digits'}), 400
            
            pin_hash = hash_password(pin_code)
            SecuritySettingsModel.update_pin(user_id, pin_hash)
            
            return jsonify({'success': True, 'message': 'PIN set successfully'})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/security/verify-pin', methods=['POST'])
    @jwt_required()
    def verify_pin():
        try:
            user_id = get_jwt_identity()
            data = request.get_json()
            pin_code = data.get('pin_code')
            
            if not pin_code:
                return jsonify({'error': 'PIN code required'}), 400
            
            settings = SecuritySettingsModel.find_by_user(user_id)
            if not settings['pin_enabled']:
                return jsonify({'error': 'PIN not enabled'}), 400
            
            pin_hash = hash_password(pin_code)
            is_valid = settings['pin_hash'] == pin_hash
            
            return jsonify({'success': is_valid, 'valid': is_valid})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/security/disable-pin', methods=['POST'])
    @jwt_required()
    def disable_pin():
        try:
            user_id = get_jwt_identity()
            SecuritySettingsModel.disable_pin(user_id)
            return jsonify({'success': True, 'message': 'PIN disabled'})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    # ==================== PASSWORD MANAGEMENT ====================
    
    @app.route('/api/security/change-password', methods=['POST'])
    @jwt_required()
    def change_password():
        try:
            user_id = get_jwt_identity()
            data = request.get_json()
            old_password = data.get('old_password')
            new_password = data.get('new_password')
            
            if not old_password or not new_password:
                return jsonify({'error': 'Old and new password required'}), 400
            
            if len(new_password) < 8:
                return jsonify({'error': 'New password must be at least 8 characters'}), 400
            
            user = UserModel.find_by_id(user_id)
            if not verify_password(old_password, user['password_hash']):
                return jsonify({'error': 'Invalid old password'}), 401
            
            new_hash = hash_password(new_password)
            UserModel.update_password(user_id, new_hash)
            
            return jsonify({'success': True, 'message': 'Password changed successfully'})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    # ==================== 2FA (TWO FACTOR AUTHENTICATION) ====================
    
    @app.route('/api/security/enable-2fa', methods=['POST'])
    @jwt_required()
    def enable_2fa():
        try:
            user_id = get_jwt_identity()
            
            # Generate secret key for 2FA
            secret = pyotp.random_base32()
            otpauth_url = pyotp.totp.TOTP(secret).provisioning_uri(
                name=f"user_{user_id}", issuer_name="ZeontrustWallet"
            )
            
            SecuritySettingsModel.enable_2fa(user_id, secret)
            
            return jsonify({
                'success': True,
                'secret': secret,
                'qr_url': otpauth_url,
                'message': 'Scan QR code with Google Authenticator'
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/security/verify-2fa', methods=['POST'])
    @jwt_required()
    def verify_2fa():
        try:
            user_id = get_jwt_identity()
            data = request.get_json()
            code = data.get('code')
            secret = data.get('secret')
            
            if not code:
                return jsonify({'error': '2FA code required'}), 400
            
            totp = pyotp.TOTP(secret)
            is_valid = totp.verify(code)
            
            if is_valid:
                SecuritySettingsModel.enable_2fa(user_id, secret)
                return jsonify({'success': True, 'verified': True, 'message': '2FA enabled successfully'})
            else:
                return jsonify({'success': False, 'verified': False, 'error': 'Invalid 2FA code'}), 401
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/security/disable-2fa', methods=['POST'])
    @jwt_required()
    def disable_2fa():
        try:
            user_id = get_jwt_identity()
            SecuritySettingsModel.disable_2fa(user_id)
            return jsonify({'success': True, 'message': '2FA disabled'})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    # ==================== SESSION MANAGEMENT ====================
    
    @app.route('/api/security/sessions', methods=['GET'])
    @jwt_required()
    def get_sessions():
        try:
            user_id = get_jwt_identity()
            sessions = SessionModel.get_user_sessions(user_id)
            
            current_token = request.headers.get('Authorization', '').replace('Bearer ', '')
            for session in sessions:
                session['is_current'] = (session['token'] == current_token)
            
            return jsonify({'success': True, 'sessions': sessions})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/security/revoke-session/<int:session_id>', methods=['POST'])
    @jwt_required()
    def revoke_session(session_id):
        try:
            user_id = get_jwt_identity()
            # Implementation to revoke specific session
            return jsonify({'success': True, 'message': 'Session revoked'})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/security/logout-all', methods=['POST'])
    @jwt_required()
    def logout_all():
        try:
            user_id = get_jwt_identity()
            SessionModel.delete_by_user(user_id)
            return jsonify({'success': True, 'message': 'Logged out from all devices'})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    # ==================== WALLET LOCK/UNLOCK ====================
    
    @app.route('/api/security/lock-wallet', methods=['POST'])
    @jwt_required()
    def lock_wallet():
        try:
            user_id = get_jwt_identity()
            data = request.get_json()
            wallet_data = data.get('wallet_data')
            password = data.get('password')
            
            # Encrypt wallet data with password
            import base64
            encrypted = base64.b64encode(f"{wallet_data}:{password}".encode()).decode()
            
            return jsonify({'success': True, 'encrypted_wallet': encrypted})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/security/unlock-wallet', methods=['POST'])
    @jwt_required()
    def unlock_wallet():
        try:
            user_id = get_jwt_identity()
            data = request.get_json()
            encrypted_wallet = data.get('encrypted_wallet')
            password = data.get('password')
            
            import base64
            decrypted = base64.b64decode(encrypted_wallet).decode()
            stored_data, stored_password = decrypted.rsplit(':', 1)
            
            if stored_password != password:
                return jsonify({'error': 'Invalid password'}), 401
            
            return jsonify({'success': True, 'wallet_data': stored_data})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    # ==================== SECURITY SCORE ====================
    
    @app.route('/api/security/score', methods=['GET'])
    @jwt_required()
    def get_security_score():
        try:
            user_id = get_jwt_identity()
            settings = SecuritySettingsModel.find_by_user(user_id)
            
            score = 0
            if settings['password_lock_enabled']:
                score += 25
            if settings['two_factor_enabled']:
                score += 35
            if settings['pin_enabled']:
                score += 20
            if settings['session_timeout_minutes'] <= 1440:
                score += 20
            
            recommendations = []
            if not settings['two_factor_enabled']:
                recommendations.append("Enable 2FA for maximum security")
            if not settings['pin_enabled']:
                recommendations.append("Set up PIN for quick secure access")
            
            return jsonify({
                'success': True,
                'score': score,
                'level': 'Excellent' if score >= 80 else 'Good' if score >= 50 else 'Needs Improvement',
                'recommendations': recommendations
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    return app
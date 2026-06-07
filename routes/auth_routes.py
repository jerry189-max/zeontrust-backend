from flask import request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from models.user_models import UserModel
from models.security_models import SessionModel
import hashlib
from datetime import datetime, timedelta

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, password_hash):
    return hash_password(password) == password_hash

def register_auth_routes(app):
    
    @app.route('/api/auth/register', methods=['POST'])
    def register():
        try:
            data = request.get_json()
            username = data.get('username')
            email = data.get('email')
            password = data.get('password')
            
            if not username or not email or not password:
                return jsonify({'error': 'All fields are required'}), 400
            
            if len(password) < 6:
                return jsonify({'error': 'Password must be at least 6 characters'}), 400
            
            existing = UserModel.find_by_email(email)
            if existing:
                return jsonify({'error': 'Email already registered'}), 400
            
            existing_username = UserModel.find_by_username(username)
            if existing_username:
                return jsonify({'error': 'Username already taken'}), 400
            
            password_hash = hash_password(password)
            user_id = UserModel.create(username, email, password_hash)
            
            return jsonify({'success': True, 'message': 'User registered successfully', 'user_id': user_id}), 201
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/auth/login', methods=['POST'])
    def login():
        try:
            data = request.get_json()
            email = data.get('email')
            password = data.get('password')
            
            if not email or not password:
                return jsonify({'error': 'Email and password are required'}), 400
            
            user = UserModel.find_by_email(email)
            if not user or not verify_password(password, user['password_hash']):
                return jsonify({'error': 'Invalid email or password'}), 401
            
            if not user['is_active']:
                return jsonify({'error': 'Account is blocked. Contact admin.'}), 403
            
            access_token = create_access_token(identity=user['id'], expires_delta=timedelta(hours=24))
            
            expires_at = datetime.now() + timedelta(hours=24)
            SessionModel.create(user['id'], access_token, expires_at)
            UserModel.update_last_login(user['id'])
            
            return jsonify({
                'success': True,
                'token': access_token,
                'user': {
                    'id': user['id'],
                    'username': user['username'],
                    'email': user['email'],
                    'is_admin': user['is_admin']
                }
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/auth/logout', methods=['POST'])
    @jwt_required()
    def logout():
        try:
            auth_header = request.headers.get('Authorization', '')
            token = auth_header.replace('Bearer ', '')
            SessionModel.delete_expired()
            return jsonify({'success': True, 'message': 'Logged out successfully'})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/auth/verify', methods=['GET'])
    @jwt_required()
    def verify_token():
        try:
            user_id = get_jwt_identity()
            user = UserModel.find_by_id(user_id)
            if not user:
                return jsonify({'error': 'User not found'}), 404
            if not user['is_active']:
                return jsonify({'error': 'Account is blocked'}), 403
            return jsonify({'success': True, 'user': {'id': user['id'], 'username': user['username'], 'email': user['email'], 'is_admin': user['is_admin']}})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/auth/change-password', methods=['POST'])
    @jwt_required()
    def change_password():
        try:
            user_id = get_jwt_identity()
            data = request.get_json()
            old_password = data.get('old_password')
            new_password = data.get('new_password')
            
            if not old_password or not new_password:
                return jsonify({'error': 'Old and new password are required'}), 400
            
            if len(new_password) < 6:
                return jsonify({'error': 'New password must be at least 6 characters'}), 400
            
            user = UserModel.find_by_id(user_id)
            if not verify_password(old_password, user['password_hash']):
                return jsonify({'error': 'Invalid old password'}), 401
            
            new_password_hash = hash_password(new_password)
            UserModel.update_password(user_id, new_password_hash)
            
            return jsonify({'success': True, 'message': 'Password changed successfully'})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    return app
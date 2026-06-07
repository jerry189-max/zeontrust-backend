from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from dotenv import load_dotenv
import sqlite3
import os
import hashlib
import json
import random
import time
import secrets
from datetime import datetime, timedelta

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'zeontrust-wallet-secret-key-2024')
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'zeontrust-jwt-secret-key-2024')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)

# CORS Configuration
CORS(app, origins=[
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:3001",
    "http://127.0.0.1:3001",
    "https://zeontrust.net",
    "https://www.zeontrust.net",
    "https://zeontrust-backend.onrender.com"
], supports_credentials=True)

jwt = JWTManager(app)

# ==================== DATABASE HELPER ====================

def get_db():
    db_path = os.path.join(os.path.dirname(__file__), 'database', 'zeontrust_wallet.db')
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, password_hash):
    return hash_password(password) == password_hash

# ==================== ROOT & STATIC ROUTES ====================

@app.route('/')
def home():
    return jsonify({
        'message': 'Zeontrust Wallet API is running!',
        'status': 'healthy',
        'version': '1.0.0',
        'endpoints': {
            'health': '/api/health',
            'auth': {
                'register': 'POST /api/auth/register',
                'login': 'POST /api/auth/login',
                'verify': 'GET /api/auth/verify'
            },
            'wallets': {
                'list': 'GET /api/wallets',
                'create': 'POST /api/wallets/create',
                'detail': 'GET /api/wallets/<id>'
            }
        }
    })

@app.route('/<path:path>')
def serve_static(path):
    """Serve static HTML, CSS, JS files"""
    if os.path.exists(path) and os.path.isfile(path):
        return send_from_directory('.', path)
    return jsonify({'error': 'File not found'}), 404

# ==================== HEALTH ROUTE ====================

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'message': 'Zeontrust Wallet API is running!'})

# ==================== AUTH ROUTES ====================

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
        
        password_hash = hash_password(password)
        
        conn = get_db()
        cursor = conn.cursor()
        
        # Create tables if not exists
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                is_active BOOLEAN DEFAULT 1,
                is_admin BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP
            )
        ''')
        
        cursor.execute('SELECT id FROM users WHERE email = ?', (email,))
        if cursor.fetchone():
            conn.close()
            return jsonify({'error': 'Email already registered'}), 400
        
        cursor.execute('INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)',
                       (username, email, password_hash))
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()
        
        return jsonify({'success': True, 'message': 'User registered successfully', 'user_id': user_id}), 201
    except Exception as e:
        print(f"Registration error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT id, username, email, password_hash, is_admin, is_active FROM users WHERE email = ?', (email,))
        user = cursor.fetchone()
        conn.close()
        
        if not user or not verify_password(password, user['password_hash']):
            return jsonify({'error': 'Invalid email or password'}), 401
        
        if not user['is_active']:
            return jsonify({'error': 'Account is blocked. Contact admin.'}), 403
        
        access_token = create_access_token(identity=str(user['id']))
        
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

# ==================== WALLET ROUTES ====================

@app.route('/api/wallets', methods=['GET'])
@jwt_required()
def get_wallets():
    try:
        user_id = get_jwt_identity()
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS wallets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                wallet_name TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        
        cursor.execute('SELECT id, wallet_name, created_at FROM wallets WHERE user_id = ?', (user_id,))
        wallets = cursor.fetchall()
        conn.close()
        
        return jsonify({
            'success': True,
            'wallets': [{'id': w['id'], 'name': w['wallet_name'], 'created_at': w['created_at']} for w in wallets]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/wallets/create', methods=['POST'])
@jwt_required()
def create_wallet():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        wallet_name = data.get('wallet_name', 'My Wallet')
        
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS network_accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                wallet_id INTEGER NOT NULL,
                network TEXT NOT NULL,
                address TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (wallet_id) REFERENCES wallets(id)
            )
        ''')
        
        cursor.execute('INSERT INTO wallets (user_id, wallet_name) VALUES (?, ?)', (user_id, wallet_name))
        wallet_id = cursor.lastrowid
        
        # Generate unique addresses
        seed = f"{user_id}{wallet_id}{datetime.now()}{secrets.token_hex(8)}".encode()
        
        networks = ['tron', 'ethereum', 'bsc', 'polygon', 'bitcoin']
        addresses = [
            'T' + hashlib.sha256(seed).hexdigest()[:33].upper(),
            '0x' + hashlib.sha256(seed).hexdigest()[:40].lower(),
            '0x' + hashlib.sha256(seed).hexdigest()[:40].lower(),
            '0x' + hashlib.sha256(seed).hexdigest()[:40].lower(),
            '1' + hashlib.sha256(seed).hexdigest()[:33]
        ]
        
        for i, network in enumerate(networks):
            cursor.execute('INSERT INTO network_accounts (wallet_id, network, address) VALUES (?, ?, ?)',
                           (wallet_id, network, addresses[i]))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'wallet_id': wallet_id,
            'wallet_name': wallet_name,
            'addresses': {
                'tron': addresses[0],
                'ethereum': addresses[1],
                'bsc': addresses[2],
                'polygon': addresses[3],
                'bitcoin': addresses[4]
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/wallets/<int:wallet_id>', methods=['GET'])
@jwt_required()
def get_wallet(wallet_id):
    try:
        user_id = get_jwt_identity()
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute('SELECT id, wallet_name, created_at FROM wallets WHERE id = ? AND user_id = ?', (wallet_id, user_id))
        wallet = cursor.fetchone()
        
        if not wallet:
            conn.close()
            return jsonify({'error': 'Wallet not found'}), 404
        
        cursor.execute('SELECT network, address FROM network_accounts WHERE wallet_id = ?', (wallet_id,))
        addresses = cursor.fetchall()
        conn.close()
        
        return jsonify({
            'success': True,
            'id': wallet['id'],
            'name': wallet['wallet_name'],
            'created_at': wallet['created_at'],
            'addresses': [{'network': a['network'], 'address': a['address']} for a in addresses]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== RUN SERVER ====================

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print("\n" + "="*50)
    print("🚀 Zeontrust Wallet Backend Server")
    print("="*50)
    print(f"📍 Running on: http://0.0.0.0:{port}")
    print("📍 API Health: /api/health")
    print("="*50 + "\n")
    
    app.run(debug=False, host='0.0.0.0', port=port)

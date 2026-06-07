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

# ==================== ROOT ROUTE ====================

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
            },
            'balance': 'GET /api/balance/<wallet_id>',
            'transactions': 'GET /api/transactions/<wallet_id>',
            'tokens': 'GET /api/tokens/list'
        }
    })

# ==================== SERVE STATIC FILES ====================

@app.route('/<path:path>')
def serve_static(path):
    """Serve static HTML, CSS, JS files"""
    # Check if file exists
    if os.path.exists(path):
        return send_from_directory('.', path)
    
    # Check if file exists in subdirectories
    possible_paths = [
        path,
        f'nova-wallet/{path}',
        f'admin/{path}',
        f'ZeontrustSwap/{path}',
        f'css/{path}',
        f'js/{path}',
        f'assets/{path}'
    ]
    
    for p in possible_paths:
        if os.path.exists(p):
            return send_from_directory(os.path.dirname(p) or '.', os.path.basename(p))
    
    return jsonify({'error': 'File not found'}), 404

# ==================== HEALTH ROUTE ====================

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'message': 'Zeontrust Wallet API is running!'})

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
        
        access_token = create_access_token(identity=user['id'])
        
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

@app.route('/api/auth/verify', methods=['GET'])
@jwt_required()
def verify_token():
    try:
        user_id = get_jwt_identity()
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT id, username, email, is_admin, is_active FROM users WHERE id = ?', (user_id,))
        user = cursor.fetchone()
        conn.close()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        if not user['is_active']:
            return jsonify({'error': 'Account is blocked'}), 403
        
        return jsonify({
            'success': True,
            'user': {
                'id': user['id'],
                'username': user['username'],
                'email': user['email'],
                'is_admin': user['is_admin']
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/verify-password', methods=['POST'])
@jwt_required()
def verify_password_route():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        password = data.get('password')
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT password_hash FROM users WHERE id = ?', (user_id,))
        user = cursor.fetchone()
        conn.close()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        if verify_password(password, user['password_hash']):
            return jsonify({'success': True, 'valid': True})
        else:
            return jsonify({'success': False, 'valid': False}), 401
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

# ==================== BALANCE ROUTES ====================

@app.route('/api/balance/<int:wallet_id>', methods=['GET'])
@jwt_required()
def get_balance(wallet_id):
    try:
        network = request.args.get('network', 'tron')
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT address FROM network_accounts WHERE wallet_id = ? AND network = ?', (wallet_id, network))
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            return jsonify({'error': 'Network address not found'}), 404
        
        symbols = {'tron': 'TRX', 'ethereum': 'ETH', 'bsc': 'BNB', 'polygon': 'MATIC', 'bitcoin': 'BTC'}
        mock_balance = round(random.uniform(10, 1000), 2)
        
        return jsonify({
            'success': True,
            'network': network,
            'address': result['address'],
            'balance': str(mock_balance),
            'symbol': symbols.get(network, 'TOKEN'),
            'usd_value': round(mock_balance * 0.10, 2)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== TRANSACTION ROUTES ====================

@app.route('/api/transaction/send', methods=['POST'])
@jwt_required()
def send_transaction():
    try:
        data = request.get_json()
        wallet_id = data.get('wallet_id')
        network = data.get('network')
        to_address = data.get('to_address')
        amount = data.get('amount')
        
        if not all([wallet_id, network, to_address, amount]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                wallet_id INTEGER NOT NULL,
                network TEXT NOT NULL,
                tx_hash TEXT UNIQUE NOT NULL,
                from_address TEXT NOT NULL,
                to_address TEXT NOT NULL,
                amount TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (wallet_id) REFERENCES wallets(id)
            )
        ''')
        
        cursor.execute('SELECT address FROM network_accounts WHERE wallet_id = ? AND network = ?', (wallet_id, network))
        result = cursor.fetchone()
        
        if not result:
            conn.close()
            return jsonify({'error': 'Network address not found'}), 404
        
        from_address = result['address']
        tx_hash = hashlib.sha256(f"{from_address}{to_address}{amount}{time.time()}".encode()).hexdigest()
        
        cursor.execute('INSERT INTO transactions (wallet_id, network, tx_hash, from_address, to_address, amount, status) VALUES (?, ?, ?, ?, ?, ?, ?)',
                       (wallet_id, network, tx_hash, from_address, to_address, str(amount), 'pending'))
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'tx_hash': tx_hash, 'message': 'Transaction submitted successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/transactions/<int:wallet_id>', methods=['GET'])
@jwt_required()
def get_transactions(wallet_id):
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM transactions WHERE wallet_id = ? ORDER BY timestamp DESC LIMIT 50', (wallet_id,))
        rows = cursor.fetchall()
        conn.close()
        
        transactions = []
        for row in rows:
            transactions.append({
                'id': row[0],
                'tx_hash': row[3],
                'from_address': row[4],
                'to_address': row[5],
                'amount': row[6],
                'status': row[7],
                'timestamp': row[8]
            })
        
        return jsonify({'success': True, 'transactions': transactions})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== TOKEN ROUTES ====================

@app.route('/api/tokens/list', methods=['GET'])
@jwt_required()
def get_token_list():
    try:
        network = request.args.get('network', 'tron')
        
        native_tokens = {
            'tron': {'symbol': 'TRX', 'name': 'TRON', 'is_native': True, 'decimals': 6},
            'ethereum': {'symbol': 'ETH', 'name': 'Ethereum', 'is_native': True, 'decimals': 18},
            'bsc': {'symbol': 'BNB', 'name': 'BNB Chain', 'is_native': True, 'decimals': 18},
            'polygon': {'symbol': 'MATIC', 'name': 'Polygon', 'is_native': True, 'decimals': 18},
            'bitcoin': {'symbol': 'BTC', 'name': 'Bitcoin', 'is_native': True, 'decimals': 8}
        }
        
        tokens = [native_tokens.get(network)]
        
        return jsonify({'success': True, 'network': network, 'tokens': tokens})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/tokens/custom', methods=['POST'])
@jwt_required()
def add_custom_token():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        network = data.get('network')
        contract_address = data.get('contract_address')
        token_name = data.get('token_name')
        token_symbol = data.get('token_symbol')
        decimals = data.get('decimals', 18)
        
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS custom_tokens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                network TEXT NOT NULL,
                contract_address TEXT NOT NULL,
                token_name TEXT NOT NULL,
                token_symbol TEXT NOT NULL,
                decimals INTEGER NOT NULL,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        
        cursor.execute('INSERT INTO custom_tokens (user_id, network, contract_address, token_name, token_symbol, decimals) VALUES (?, ?, ?, ?, ?, ?)',
                       (user_id, network, contract_address, token_name, token_symbol, decimals))
        token_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'token_id': token_id, 'message': 'Token added successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== SWAP ROUTES ====================

@app.route('/api/swap/quote', methods=['POST'])
@jwt_required()
def get_swap_quote():
    try:
        data = request.get_json()
        from_token = data.get('from_token', 'TRX')
        to_token = data.get('to_token', 'USDT')
        amount = float(data.get('amount', 0))
        
        rate = 0.10 if from_token == 'TRX' else 10
        to_amount = amount * rate
        fee = to_amount * 0.003
        
        return jsonify({
            'success': True,
            'quote': {
                'from_amount': amount,
                'to_amount': to_amount - fee,
                'rate': rate,
                'fee': fee,
                'fee_percent': 0.3
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== FLASH LOAN ROUTES ====================

@app.route('/api/flashloan/request', methods=['POST'])
@jwt_required()
def request_flashloan():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        amount = data.get('amount')
        
        if not amount:
            return jsonify({'error': 'Amount required'}), 400
        
        fee = float(amount) * 0.0009
        request_id = hashlib.sha256(f"{user_id}{amount}{time.time()}".encode()).hexdigest()[:16]
        
        return jsonify({
            'success': True,
            'request_id': request_id,
            'amount': amount,
            'fee': fee,
            'total_repay': float(amount) + fee,
            'status': 'pending',
            'message': 'Flash loan request submitted'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/flashloan/my-requests', methods=['GET'])
@jwt_required()
def get_my_requests():
    try:
        return jsonify({'success': True, 'requests': []})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== STAKING ROUTES ====================

@app.route('/api/staking/info', methods=['GET'])
@jwt_required()
def get_staking_info():
    return jsonify({'success': True, 'staking_info': {'total_staked': 0, 'apy': 4.5, 'positions': []}})

@app.route('/api/staking/stake', methods=['POST'])
@jwt_required()
def stake_trx():
    return jsonify({'success': True, 'position_id': 1, 'message': 'Staked successfully'})

# ==================== VOTING ROUTES ====================

@app.route('/api/vote/srs', methods=['GET'])
@jwt_required()
def get_super_representatives():
    srs = [
        {'address': 'TXXXXXXXXXX1', 'name': 'Binance Staking', 'votes': 125000000},
        {'address': 'TXXXXXXXXXX2', 'name': 'TronLink', 'votes': 98000000}
    ]
    return jsonify({'success': True, 'super_representatives': srs})

# ==================== ADMIN ROUTES ====================

@app.route('/api/admin/users', methods=['GET'])
@jwt_required()
def admin_get_users():
    try:
        admin_id = get_jwt_identity()
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute('SELECT is_admin FROM users WHERE id = ?', (admin_id,))
        admin = cursor.fetchone()
        
        if not admin or not admin['is_admin']:
            conn.close()
            return jsonify({'error': 'Admin access required'}), 403
        
        cursor.execute('SELECT id, username, email, is_active, is_admin, created_at FROM users')
        rows = cursor.fetchall()
        conn.close()
        
        users = []
        for row in rows:
            users.append({
                'id': row['id'],
                'username': row['username'],
                'email': row['email'],
                'is_active': bool(row['is_active']),
                'is_admin': bool(row['is_admin']),
                'created_at': row['created_at']
            })
        
        return jsonify({'success': True, 'users': users})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== RUN SERVER ====================

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    print("\n" + "="*50)
    print("🚀 Zeontrust Wallet Backend Server")
    print("="*50)
    print(f"📍 Running on: http://0.0.0.0:{port}")
    print("📍 API Health: /api/health")
    print("="*50 + "\n")
    
    app.run(debug=False, host='0.0.0.0', port=port)

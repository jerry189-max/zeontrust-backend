from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.token_models import CustomTokenModel, TokenVerificationRequestModel, VerifiedTokenModel
from models.user_models import UserModel
import requests
import json
import hashlib
import time

def register_token_routes(app):
    
    # ==================== GET TOKEN LIST ====================
    
    @app.route('/api/tokens/list', methods=['GET'])
    @jwt_required()
    def get_token_list():
        try:
            network = request.args.get('network', 'tron')
            user_id = get_jwt_identity()
            
            native_tokens = {
                'tron': {'symbol': 'TRX', 'name': 'TRON', 'is_native': True, 'decimals': 6, 'icon': '🌐'},
                'ethereum': {'symbol': 'ETH', 'name': 'Ethereum', 'is_native': True, 'decimals': 18, 'icon': '💎'},
                'bsc': {'symbol': 'BNB', 'name': 'BNB Chain', 'is_native': True, 'decimals': 18, 'icon': '🔶'},
                'polygon': {'symbol': 'MATIC', 'name': 'Polygon', 'is_native': True, 'decimals': 18, 'icon': '🟣'},
                'bitcoin': {'symbol': 'BTC', 'name': 'Bitcoin', 'is_native': True, 'decimals': 8, 'icon': '🟠'}
            }
            
            # Get verified tokens from database
            verified_tokens = VerifiedTokenModel.get_all_verified_tokens(network)
            
            # Get user's custom tokens
            custom_tokens = CustomTokenModel.find_by_user(user_id, network)
            
            # Combine all tokens
            tokens = []
            
            # Add native token
            if network in native_tokens:
                tokens.append(native_tokens.get(network))
            
            # Add verified tokens
            for token in verified_tokens:
                token['is_native'] = False
                token['is_verified'] = True
                tokens.append(token)
            
            # Add custom tokens
            for token in custom_tokens:
                token['is_native'] = False
                token['is_verified'] = False
                tokens.append(token)
            
            # Get token balances (mock for now)
            for token in tokens:
                token['balance'] = '0.00'
                token['usd_value'] = '0.00'
            
            return jsonify({'success': True, 'network': network, 'tokens': tokens, 'total': len(tokens)})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    # ==================== FETCH TOKEN METADATA FROM BLOCKCHAIN ====================
    
    @app.route('/api/tokens/metadata', methods=['POST'])
    @jwt_required()
    def fetch_token_metadata():
        try:
            data = request.get_json()
            contract_address = data.get('contract_address')
            network = data.get('network', 'tron')
            
            if not contract_address:
                return jsonify({'error': 'Contract address required'}), 400
            
            metadata = {
                'name': None,
                'symbol': None,
                'decimals': 18,
                'contract_address': contract_address,
                'network': network
            }
            
            # Fetch from blockchain based on network
            if network == 'tron':
                metadata = fetch_tron_token_metadata(contract_address)
            elif network in ['ethereum', 'bsc', 'polygon']:
                metadata = fetch_evm_token_metadata(contract_address, network)
            
            return jsonify({
                'success': True,
                'metadata': metadata
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    # ==================== ADD CUSTOM TOKEN ====================
    
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
            logo_url = data.get('logo_url')
            
            if not all([network, contract_address, token_name, token_symbol]):
                return jsonify({'error': 'Missing required fields'}), 400
            
            # Check if token already exists
            existing = CustomTokenModel.find_by_contract(user_id, contract_address, network)
            if existing:
                return jsonify({'error': 'Token already added'}), 400
            
            # Check if token is verified
            verified = VerifiedTokenModel.find_verified_token(contract_address, network)
            is_verified = verified is not None
            
            token_id = CustomTokenModel.create(user_id, network, contract_address, token_name, token_symbol, decimals, logo_url)
            
            return jsonify({
                'success': True, 
                'token_id': token_id, 
                'is_verified': is_verified,
                'message': 'Token added successfully'
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    # ==================== DELETE CUSTOM TOKEN ====================
    
    @app.route('/api/tokens/custom/<int:token_id>', methods=['DELETE'])
    @jwt_required()
    def delete_custom_token(token_id):
        try:
            user_id = get_jwt_identity()
            success = CustomTokenModel.delete_custom_token(token_id, user_id)
            if success:
                return jsonify({'success': True, 'message': 'Token removed successfully'})
            return jsonify({'error': 'Token not found'}), 404
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    # ==================== REQUEST TOKEN APPROVAL (USER SIDE) ====================
    
    @app.route('/api/tokens/request', methods=['POST'])
    @jwt_required()
    def request_token_approval():
        try:
            user_id = get_jwt_identity()
            data = request.get_json()
            
            network = data.get('network')
            contract_address = data.get('contract_address')
            token_name = data.get('token_name')
            token_symbol = data.get('token_symbol')
            decimals = data.get('decimals', 18)
            website = data.get('website')
            email = data.get('email')
            twitter = data.get('twitter')
            telegram = data.get('telegram')
            discord = data.get('discord')
            logo_url = data.get('logo_url')
            description = data.get('description')
            
            if not all([network, contract_address, token_name, token_symbol]):
                return jsonify({'error': 'Missing required fields'}), 400
            
            # Check if token already verified
            existing_verified = VerifiedTokenModel.find_verified_token(contract_address, network)
            if existing_verified:
                return jsonify({'error': 'Token is already verified'}), 400
            
            # Check if request already exists
            existing_requests = TokenVerificationRequestModel.find_pending_requests()
            for req in existing_requests:
                if req['contract_address'] == contract_address and req['network'] == network:
                    return jsonify({'error': 'Approval request already pending'}), 400
            
            request_id = TokenVerificationRequestModel.create(
                user_id, network, contract_address, token_name, token_symbol, decimals,
                website, email, twitter, telegram, discord, logo_url, description
            )
            
            # Send notification to admin (mock)
            print(f"New token approval request #{request_id}: {token_name} ({token_symbol}) on {network}")
            
            return jsonify({
                'success': True, 
                'request_id': request_id, 
                'message': 'Token approval request submitted. Admin will review shortly.'
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    # ==================== GET USER'S REQUEST STATUS ====================
    
    @app.route('/api/tokens/my-requests', methods=['GET'])
    @jwt_required()
    def get_my_token_requests():
        try:
            user_id = get_jwt_identity()
            
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM token_verification_requests 
                WHERE user_id = ? 
                ORDER BY submitted_at DESC
            ''', (user_id,))
            rows = cursor.fetchall()
            conn.close()
            
            requests = []
            for row in rows:
                requests.append({
                    'id': row[0],
                    'network': row[2],
                    'contract_address': row[3],
                    'token_name': row[4],
                    'token_symbol': row[5],
                    'status': row[13],
                    'admin_notes': row[14],
                    'submitted_at': row[15]
                })
            
            return jsonify({'success': True, 'requests': requests})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    # ==================== GET VERIFIED TOKENS (PUBLIC) ====================
    
    @app.route('/api/tokens/verified', methods=['GET'])
    @jwt_required()
    def get_verified_tokens():
        try:
            network = request.args.get('network')
            tokens = VerifiedTokenModel.get_all_verified_tokens(network)
            return jsonify({'success': True, 'tokens': tokens})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    # ==================== GET TOKEN DETAILS ====================
    
    @app.route('/api/tokens/<string:network>/<string:contract_address>', methods=['GET'])
    @jwt_required()
    def get_token_details(network, contract_address):
        try:
            # Check verified tokens
            token = VerifiedTokenModel.find_verified_token(contract_address, network)
            if not token:
                # Check custom tokens
                user_id = get_jwt_identity()
                token = CustomTokenModel.find_by_contract(user_id, contract_address, network)
            
            if not token:
                return jsonify({'error': 'Token not found'}), 404
            
            return jsonify({'success': True, 'token': token})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    # ==================== SEARCH TOKENS ====================
    
    @app.route('/api/tokens/search', methods=['GET'])
    @jwt_required()
    def search_tokens():
        try:
            query = request.args.get('q', '')
            network = request.args.get('network')
            
            if not query or len(query) < 2:
                return jsonify({'success': True, 'tokens': []})
            
            conn = get_db()
            cursor = conn.cursor()
            
            if network:
                cursor.execute('''
                    SELECT * FROM verified_tokens 
                    WHERE network = ? AND (token_name LIKE ? OR token_symbol LIKE ?)
                    LIMIT 20
                ''', (network, f'%{query}%', f'%{query}%'))
            else:
                cursor.execute('''
                    SELECT * FROM verified_tokens 
                    WHERE token_name LIKE ? OR token_symbol LIKE ?
                    LIMIT 20
                ''', (f'%{query}%', f'%{query}%'))
            
            rows = cursor.fetchall()
            conn.close()
            
            tokens = []
            for row in rows:
                tokens.append({
                    'id': row[0],
                    'network': row[1],
                    'contract_address': row[2],
                    'token_name': row[3],
                    'token_symbol': row[4],
                    'decimals': row[5],
                    'logo_url': row[6],
                    'category': row[8]
                })
            
            return jsonify({'success': True, 'tokens': tokens})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    return app


# ==================== HELPER FUNCTIONS ====================

def fetch_tron_token_metadata(contract_address: str) -> dict:
    """Fetch TRC-20 token metadata from TRON blockchain"""
    try:
        # TRONGrid API endpoint
        url = f"https://api.trongrid.io/v1/contracts/{contract_address}"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('data') and len(data['data']) > 0:
                contract_data = data['data'][0]
                return {
                    'name': contract_data.get('name', 'Unknown Token'),
                    'symbol': contract_data.get('symbol', 'UNKNOWN'),
                    'decimals': contract_data.get('decimals', 18),
                    'contract_address': contract_address,
                    'network': 'tron'
                }
    except Exception as e:
        print(f"Error fetching TRON token metadata: {e}")
    
    return {
        'name': 'Custom Token',
        'symbol': 'CTOKEN',
        'decimals': 18,
        'contract_address': contract_address,
        'network': 'tron'
    }


def fetch_evm_token_metadata(contract_address: str, network: str) -> dict:
    """Fetch ERC-20/BEP-20 token metadata from EVM blockchain"""
    try:
        # Use appropriate explorer API based on network
        explorers = {
            'ethereum': ('https://api.etherscan.io/api', 'etherscan'),
            'bsc': ('https://api.bscscan.com/api', 'bscscan'),
            'polygon': ('https://api.polygonscan.com/api', 'polygonscan')
        }
        
        base_url, _ = explorers.get(network, (None, None))
        
        if base_url:
            # Try to fetch token info from explorer
            params = {
                'module': 'token',
                'action': 'tokeninfo',
                'contractaddress': contract_address,
                'apikey': ''  # Add API key if available
            }
            response = requests.get(base_url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == '1' and data.get('result'):
                    token_info = data['result'][0]
                    return {
                        'name': token_info.get('name', 'Unknown Token'),
                        'symbol': token_info.get('symbol', 'UNKNOWN'),
                        'decimals': int(token_info.get('decimals', 18)),
                        'contract_address': contract_address,
                        'network': network
                    }
    except Exception as e:
        print(f"Error fetching EVM token metadata: {e}")
    
    return {
        'name': 'Custom Token',
        'symbol': 'CTOKEN',
        'decimals': 18,
        'contract_address': contract_address,
        'network': network
    }


def get_db():
    """Get database connection"""
    import sqlite3
    import os
    db_path = os.path.join(os.path.dirname(__file__), '..', 'database', 'Zeontrust_wallet.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn
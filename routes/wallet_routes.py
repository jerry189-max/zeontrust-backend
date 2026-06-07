from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.wallet_models import WalletModel, NetworkAccountModel
import hashlib
import secrets
from datetime import datetime

def register_wallet_routes(app):
    
    @app.route('/api/wallets', methods=['GET'])
    @jwt_required()
    def get_wallets():
        try:
            user_id = get_jwt_identity()
            wallets = WalletModel.find_by_user(user_id)
            return jsonify({'success': True, 'wallets': wallets})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/wallets/create', methods=['POST'])
    @jwt_required()
    def create_wallet():
        try:
            user_id = get_jwt_identity()
            data = request.get_json()
            wallet_name = data.get('wallet_name', 'Zeontrust Wallet')
            
            # Generate unique seed
            seed = f"{user_id}{wallet_name}{datetime.now()}{secrets.token_hex(8)}".encode()
            
            # Generate addresses for all networks
            tron_address = 'T' + hashlib.sha256(seed).hexdigest()[:33].upper()
            eth_address = '0x' + hashlib.sha256(seed).hexdigest()[:40].lower()
            bsc_address = '0x' + hashlib.sha256(seed).hexdigest()[:40].lower()
            polygon_address = '0x' + hashlib.sha256(seed).hexdigest()[:40].lower()
            btc_address = '1' + hashlib.sha256(seed).hexdigest()[:33]
            
            # Create wallet in database
            wallet_id = WalletModel.create(user_id, wallet_name)
            
            # Save network addresses
            networks = ['tron', 'ethereum', 'bsc', 'polygon', 'bitcoin']
            addresses = [tron_address, eth_address, bsc_address, polygon_address, btc_address]
            
            for i, network in enumerate(networks):
                NetworkAccountModel.create(wallet_id, network, addresses[i])
            
            return jsonify({
                'success': True,
                'wallet_id': wallet_id,
                'wallet_name': wallet_name,
                'addresses': {
                    'tron': tron_address,
                    'ethereum': eth_address,
                    'bsc': bsc_address,
                    'polygon': polygon_address,
                    'bitcoin': btc_address
                },
                'message': 'Wallet created successfully!'
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    return app
from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.transaction_models import TransactionModel
from models.wallet_models import WalletModel, NetworkAccountModel
import hashlib
import time
from datetime import datetime

def register_transaction_routes(app):
    
    @app.route('/api/transaction/send', methods=['POST'])
    @jwt_required()
    def send_transaction():
        try:
            user_id = get_jwt_identity()
            data = request.get_json()
            wallet_id = data.get('wallet_id')
            network = data.get('network')
            to_address = data.get('to_address')
            amount = data.get('amount')
            token_address = data.get('token_address')
            
            if not all([wallet_id, network, to_address, amount]):
                return jsonify({'error': 'Missing required fields'}), 400
            
            wallet = WalletModel.find_by_id(wallet_id)
            if not wallet or wallet['user_id'] != user_id:
                return jsonify({'error': 'Wallet not found'}), 404
            
            account = NetworkAccountModel.find_by_wallet_and_network(wallet_id, network)
            if not account:
                return jsonify({'error': f'Network {network} not found for this wallet'}), 404
            
            from_address = account['address']
            tx_hash = hashlib.sha256(f"{from_address}{to_address}{amount}{time.time()}".encode()).hexdigest()
            
            TransactionModel.create(wallet_id, network, tx_hash, from_address, to_address, str(amount), token_address)
            
            return jsonify({'success': True, 'tx_hash': tx_hash, 'message': 'Transaction submitted successfully'})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/transactions/<int:wallet_id>', methods=['GET'])
    @jwt_required()
    def get_transactions(wallet_id):
        try:
            user_id = get_jwt_identity()
            wallet = WalletModel.find_by_id(wallet_id)
            if not wallet or wallet['user_id'] != user_id:
                return jsonify({'error': 'Wallet not found'}), 404
            
            transactions = TransactionModel.find_by_wallet(wallet_id)
            return jsonify({'success': True, 'transactions': transactions})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/transaction/status/<tx_hash>', methods=['GET'])
    @jwt_required()
    def get_transaction_status(tx_hash):
        try:
            transaction = TransactionModel.find_by_hash(tx_hash)
            if not transaction:
                return jsonify({'error': 'Transaction not found'}), 404
            return jsonify({'success': True, 'transaction': transaction})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/transaction/estimate-fee', methods=['POST'])
    @jwt_required()
    def estimate_fee():
        try:
            data = request.get_json()
            network = data.get('network', 'tron')
            from_address = data.get('from_address')
            to_address = data.get('to_address')
            amount = data.get('amount')
            
            fees = {
                'tron': 0.5,
                'ethereum': 0.002,
                'bsc': 0.0005,
                'polygon': 0.001,
                'bitcoin': 0.0001
            }
            
            return jsonify({'success': True, 'fee': fees.get(network, 0.01), 'symbol': network.upper()[:3]})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    return app
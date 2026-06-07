from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.transaction_models import TransactionModel
import hashlib
import time

def register_broadcast_routes(app):
    
    @app.route('/api/transaction/build', methods=['POST'])
    @jwt_required()
    def build_transaction():
        try:
            data = request.get_json()
            from_address = data.get('from_address')
            to_address = data.get('to_address')
            amount = data.get('amount')
            network = data.get('network', 'tron')
            
            raw_tx = {
                'from': from_address,
                'to': to_address,
                'value': amount,
                'gas': 21000,
                'gasPrice': 10,
                'nonce': int(time.time()),
                'network': network
            }
            
            return jsonify({'success': True, 'raw_transaction': raw_tx, 'fee_estimate': {'fee': 0.01, 'symbol': 'TRX'}})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/transaction/sign', methods=['POST'])
    @jwt_required()
    def sign_transaction():
        try:
            data = request.get_json()
            raw_transaction = data.get('raw_transaction')
            private_key = data.get('private_key')
            
            signed_tx = {
                'raw': raw_transaction,
                'signature': hashlib.sha256(f"{raw_transaction}{private_key}".encode()).hexdigest(),
                'signed': True
            }
            
            return jsonify({'success': True, 'signed_transaction': signed_tx})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/transaction/broadcast', methods=['POST'])
    @jwt_required()
    def broadcast_transaction():
        try:
            data = request.get_json()
            signed_transaction = data.get('signed_transaction')
            wallet_id = data.get('wallet_id')
            
            tx_hash = hashlib.sha256(str(signed_transaction).encode()).hexdigest()
            
            if wallet_id:
                TransactionModel.update_status(tx_hash, 'pending')
            
            return jsonify({'success': True, 'tx_hash': tx_hash, 'status': 'broadcasted'})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/transaction/status/<tx_hash>', methods=['GET'])
    @jwt_required()
    def get_transaction_status(tx_hash):
        try:
            transaction = TransactionModel.find_by_hash(tx_hash)
            status = transaction['status'] if transaction else 'pending'
            return jsonify({'success': True, 'status': status})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    return app
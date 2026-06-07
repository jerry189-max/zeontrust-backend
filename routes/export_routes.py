from flask import request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.wallet_models import WalletModel, NetworkAccountModel
from models.transaction_models import TransactionModel
import json
import tempfile

def register_export_routes(app):
    
    @app.route('/api/export/private-key', methods=['POST'])
    @jwt_required()
    def export_private_key():
        try:
            user_id = get_jwt_identity()
            data = request.get_json()
            wallet_id = data.get('wallet_id')
            network = data.get('network')
            password = data.get('password')
            
            wallet = WalletModel.find_by_id(wallet_id)
            if not wallet or wallet['user_id'] != user_id:
                return jsonify({'error': 'Wallet not found'}), 404
            
            account = NetworkAccountModel.find_by_wallet_and_network(wallet_id, network)
            if not account:
                return jsonify({'error': f'Network {network} not found'}), 404
            
            # Mock private key
            private_key = f"0x{hashlib.sha256(f'{user_id}{wallet_id}{network}'.encode()).hexdigest()}"
            
            return jsonify({
                'success': True,
                'private_key': private_key,
                'network': network,
                'address': account['address'],
                'warning': 'Never share your private key!'
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/export/keystore', methods=['POST'])
    @jwt_required()
    def export_keystore():
        try:
            user_id = get_jwt_identity()
            data = request.get_json()
            wallet_id = data.get('wallet_id')
            network = data.get('network')
            
            keystore = {'version': 3, 'id': 'test-id', 'address': '0x...', 'crypto': {}}
            
            temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
            json.dump(keystore, temp_file)
            temp_file.close()
            
            return send_file(temp_file.name, as_attachment=True, download_name=f'keystore_{network}.json')
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/export/wallet-data', methods=['POST'])
    @jwt_required()
    def export_wallet_data():
        try:
            user_id = get_jwt_identity()
            data = request.get_json()
            wallet_id = data.get('wallet_id')
            
            wallet = WalletModel.find_by_id(wallet_id)
            if not wallet or wallet['user_id'] != user_id:
                return jsonify({'error': 'Wallet not found'}), 404
            
            accounts = NetworkAccountModel.find_by_wallet(wallet_id)
            transactions = TransactionModel.find_by_wallet(wallet_id)
            
            export_data = {
                'wallet': wallet,
                'addresses': accounts,
                'transactions': transactions,
                'exported_at': datetime.now().isoformat()
            }
            
            temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
            json.dump(export_data, temp_file, default=str)
            temp_file.close()
            
            return send_file(temp_file.name, as_attachment=True, download_name=f'wallet_export_{wallet_id}.json')
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    return app
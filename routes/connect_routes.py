from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.wallet_models import WalletModel, NetworkAccountModel
from models.dapp_models import ConnectionHistoryModel
import uuid

def register_connect_routes(app):
    
    @app.route('/api/connect/create', methods=['POST'])
    @jwt_required()
    def create_connection():
        try:
            user_id = get_jwt_identity()
            data = request.get_json()
            wallet_id = data.get('wallet_id')
            dapp_url = data.get('dapp_url')
            dapp_name = data.get('dapp_name')
            network = data.get('network', 'tron')
            
            wallet = WalletModel.find_by_id(wallet_id)
            if not wallet or wallet['user_id'] != user_id:
                return jsonify({'error': 'Wallet not found'}), 404
            
            account = NetworkAccountModel.find_by_wallet_and_network(wallet_id, network)
            if not account:
                return jsonify({'error': f'Network {network} not found'}), 404
            
            connection_id = str(uuid.uuid4())
            ConnectionHistoryModel.create(user_id, wallet_id, dapp_url, dapp_name, network, connection_id)
            
            return jsonify({
                'success': True,
                'connection_id': connection_id,
                'address': account['address'],
                'network': network
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/connect/connections', methods=['GET'])
    @jwt_required()
    def get_connections():
        try:
            user_id = get_jwt_identity()
            connections = ConnectionHistoryModel.find_active_by_user(user_id)
            return jsonify({'success': True, 'connections': connections})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/connect/disconnect', methods=['POST'])
    @jwt_required()
    def disconnect():
        try:
            data = request.get_json()
            connection_id = data.get('connection_id')
            
            ConnectionHistoryModel.disconnect(connection_id)
            return jsonify({'success': True, 'message': 'Disconnected successfully'})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/connect/status', methods=['GET'])
    @jwt_required()
    def get_connect_status():
        return jsonify({
            'success': True,
            'version': '1.0',
            'supported_methods': ['eth_sendTransaction', 'eth_sign', 'personal_sign', 'tron_signTransaction'],
            'supported_chains': ['tron', 'ethereum', 'bsc', 'polygon']
        })
    
    return app
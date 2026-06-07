from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.network_models import NetworkConfigModel, UserNetworkPreference

def register_network_routes(app):
    
    @app.route('/api/networks', methods=['GET'])
    @jwt_required()
    def get_networks():
        try:
            networks = NetworkConfigModel.find_all()
            return jsonify({'success': True, 'networks': networks})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/network/current', methods=['GET'])
    @jwt_required()
    def get_current_network():
        try:
            user_id = get_jwt_identity()
            preference = UserNetworkPreference.get_preference(user_id)
            network = NetworkConfigModel.find_by_id(preference['network_id'])
            return jsonify({'success': True, 'network': network, 'is_testnet': preference['is_testnet']})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/network/switch', methods=['POST'])
    @jwt_required()
    def switch_network():
        try:
            user_id = get_jwt_identity()
            data = request.get_json()
            network_id = data.get('network')
            testnet = data.get('testnet', False)
            
            network = NetworkConfigModel.find_by_id(network_id)
            if not network:
                return jsonify({'error': 'Network not found'}), 404
            
            UserNetworkPreference.set_preference(user_id, network_id, testnet)
            
            return jsonify({'success': True, 'network': network, 'is_testnet': testnet})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/network/status/<network_id>', methods=['GET'])
    @jwt_required()
    def get_network_status(network_id):
        try:
            return jsonify({'success': True, 'status': 'healthy', 'latency': 100})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    return app
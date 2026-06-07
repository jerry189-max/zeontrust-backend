from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.chain_models import ChainPreferenceModel

def register_chain_routes(app):
    
    @app.route('/api/chains', methods=['GET'])
    @jwt_required()
    def get_chains():
        chains = [
            {'id': 'tron', 'name': 'TRON', 'symbol': 'TRX', 'icon': '🌐', 'is_active': True, 'type': 'mainnet', 'block_time': 3},
            {'id': 'ethereum', 'name': 'Ethereum', 'symbol': 'ETH', 'icon': '💎', 'is_active': True, 'type': 'mainnet', 'block_time': 12},
            {'id': 'bsc', 'name': 'BNB Chain', 'symbol': 'BNB', 'icon': '🔶', 'is_active': True, 'type': 'mainnet', 'block_time': 3},
            {'id': 'polygon', 'name': 'Polygon', 'symbol': 'MATIC', 'icon': '🟣', 'is_active': True, 'type': 'mainnet', 'block_time': 2},
            {'id': 'bitcoin', 'name': 'Bitcoin', 'symbol': 'BTC', 'icon': '🟠', 'is_active': True, 'type': 'mainnet', 'block_time': 600}
        ]
        return jsonify({'success': True, 'chains': chains})
    
    @app.route('/api/chain/switch', methods=['POST'])
    @jwt_required()
    def switch_chain():
        try:
            user_id = get_jwt_identity()
            data = request.get_json()
            chain_id = data.get('chain_id')
            testnet = data.get('testnet', False)
            
            ChainPreferenceModel.set_preference(user_id, chain_id, testnet)
            
            chains = {'tron': {'name': 'TRON', 'symbol': 'TRX'}, 'ethereum': {'name': 'Ethereum', 'symbol': 'ETH'}}
            
            return jsonify({'success': True, 'chain': chains.get(chain_id, {'name': chain_id, 'symbol': chain_id.upper()[:3]})})
        except Exception as e:
            return jsonify({'error': str(e)}), 400
    
    @app.route('/api/chain/current', methods=['GET'])
    @jwt_required()
    def get_current_chain():
        try:
            user_id = get_jwt_identity()
            preference = ChainPreferenceModel.get_preference(user_id)
            return jsonify({'success': True, 'chain': {'id': preference['chain_id'], 'testnet': preference['is_testnet']}})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    return app
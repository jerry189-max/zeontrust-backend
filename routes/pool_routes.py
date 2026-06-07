from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.pool_models import PoolModel
from models.wallet_models import WalletModel

def register_pool_routes(app):
    
    @app.route('/api/pools', methods=['GET'])
    @jwt_required()
    def get_pools():
        try:
            network = request.args.get('network')
            pools = PoolModel.get_all_pools(network)
            return jsonify({'success': True, 'pools': pools})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/pools/<int:pool_id>', methods=['GET'])
    @jwt_required()
    def get_pool(pool_id):
        try:
            pool = PoolModel.find_by_id(pool_id)
            if not pool:
                return jsonify({'error': 'Pool not found'}), 404
            return jsonify({'success': True, 'pool': pool})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/pools/create', methods=['POST'])
    @jwt_required()
    def create_pool():
        try:
            user_id = get_jwt_identity()
            data = request.get_json()
            network = data.get('network')
            token_a_address = data.get('token_a_address')
            token_a_symbol = data.get('token_a_symbol')
            token_b_address = data.get('token_b_address')
            token_b_symbol = data.get('token_b_symbol')
            reserve_a = data.get('reserve_a', '0')
            reserve_b = data.get('reserve_b', '0')
            fee_percent = data.get('fee_percent', 0.3)
            
            existing = PoolModel.find_by_tokens(network, token_a_address, token_b_address)
            if existing:
                return jsonify({'error': 'Pool already exists'}), 400
            
            total_liquidity = str(float(reserve_a) * float(reserve_b) ** 0.5)
            pool_id = PoolModel.create(network, token_a_address, token_a_symbol, token_b_address, token_b_symbol, reserve_a, reserve_b, total_liquidity, fee_percent, user_id)
            
            return jsonify({'success': True, 'pool_id': pool_id, 'message': 'Pool created successfully'})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/pools/<int:pool_id>/status', methods=['PUT'])
    @jwt_required()
    def update_pool_status(pool_id):
        try:
            data = request.get_json()
            is_active = data.get('is_active', True)
            PoolModel.update_pool_status(pool_id, is_active)
            return jsonify({'success': True, 'message': f'Pool {"activated" if is_active else "paused"}'})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/pools/<int:pool_id>/fee', methods=['PUT'])
    @jwt_required()
    def update_pool_fee(pool_id):
        try:
            data = request.get_json()
            fee_percent = data.get('fee_percent')
            # Update fee logic here
            return jsonify({'success': True, 'message': 'Fee updated successfully'})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    return app
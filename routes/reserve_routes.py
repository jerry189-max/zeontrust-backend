from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.reserve_models import ReserveTokenModel, ReserveTransactionModel
from models.user_models import UserModel

def register_reserve_routes(app):
    
    @app.route('/api/reserve/tokens', methods=['GET'])
    @jwt_required()
    def get_reserve_tokens():
        try:
            tokens = ReserveTokenModel.get_all_reserve_tokens()
            return jsonify({'success': True, 'tokens': tokens})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/reserve/create', methods=['POST'])
    @jwt_required()
    def create_reserve_token():
        try:
            admin_id = get_jwt_identity()
            admin = UserModel.find_by_id(admin_id)
            if not admin or not admin['is_admin']:
                return jsonify({'error': 'Admin access required'}), 403
            
            data = request.get_json()
            network = data.get('network')
            contract_address = data.get('contract_address')
            token_name = data.get('token_name')
            token_symbol = data.get('token_symbol')
            decimals = data.get('decimals', 18)
            total_supply = data.get('total_supply')
            is_mintable = data.get('is_mintable', True)
            is_burnable = data.get('is_burnable', True)
            
            token_id = ReserveTokenModel.create(network, contract_address, token_name, token_symbol, decimals, total_supply, total_supply, is_mintable, is_burnable, admin_id)
            
            return jsonify({'success': True, 'token_id': token_id})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/reserve/mint', methods=['POST'])
    @jwt_required()
    def mint_reserve_tokens():
        try:
            admin_id = get_jwt_identity()
            admin = UserModel.find_by_id(admin_id)
            if not admin or not admin['is_admin']:
                return jsonify({'error': 'Admin access required'}), 403
            
            data = request.get_json()
            token_id = data.get('token_id')
            amount = data.get('amount')
            
            ReserveTokenModel.mint_tokens(token_id, amount)
            ReserveTransactionModel.create(token_id, 'mint', amount, None, None)
            
            return jsonify({'success': True, 'message': f'Minted {amount} tokens'})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/reserve/burn', methods=['POST'])
    @jwt_required()
    def burn_reserve_tokens():
        try:
            admin_id = get_jwt_identity()
            admin = UserModel.find_by_id(admin_id)
            if not admin or not admin['is_admin']:
                return jsonify({'error': 'Admin access required'}), 403
            
            data = request.get_json()
            token_id = data.get('token_id')
            amount = data.get('amount')
            
            ReserveTokenModel.burn_tokens(token_id, amount)
            ReserveTransactionModel.create(token_id, 'burn', amount, None, None)
            
            return jsonify({'success': True, 'message': f'Burned {amount} tokens'})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/reserve/transfer', methods=['POST'])
    @jwt_required()
    def transfer_reserve_tokens():
        try:
            admin_id = get_jwt_identity()
            admin = UserModel.find_by_id(admin_id)
            if not admin or not admin['is_admin']:
                return jsonify({'error': 'Admin access required'}), 403
            
            data = request.get_json()
            token_id = data.get('token_id')
            amount = data.get('amount')
            to_address = data.get('to_address')
            
            ReserveTokenModel.transfer_tokens(token_id, amount, to_address)
            ReserveTransactionModel.create(token_id, 'transfer', amount, None, to_address)
            
            return jsonify({'success': True, 'message': f'Transferred {amount} tokens to {to_address}'})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/reserve/stats', methods=['GET'])
    @jwt_required()
    def get_reserve_stats():
        try:
            total_value = ReserveTokenModel.get_total_reserve_value()
            return jsonify({'success': True, 'total_value': total_value, 'total_minted': 0, 'allocated': 0, 'available': total_value})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    return app
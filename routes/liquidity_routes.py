from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.pool_models import PoolModel, LiquidityPositionModel
from models.wallet_models import WalletModel

def register_liquidity_routes(app):
    
    @app.route('/api/liquidity/add', methods=['POST'])
    @jwt_required()
    def add_liquidity():
        try:
            user_id = get_jwt_identity()
            data = request.get_json()
            pool_id = data.get('pool_id')
            wallet_id = data.get('wallet_id')
            amount_a = float(data.get('amount_a'))
            amount_b = float(data.get('amount_b'))
            
            wallet = WalletModel.find_by_id(wallet_id)
            if not wallet or wallet['user_id'] != user_id:
                return jsonify({'error': 'Wallet not found'}), 404
            
            pool = PoolModel.find_by_id(pool_id)
            if not pool:
                return jsonify({'error': 'Pool not found'}), 404
            
            reserve_a = float(pool['reserve_a'])
            reserve_b = float(pool['reserve_b'])
            total_liquidity = float(pool['total_liquidity'])
            
            if total_liquidity == 0:
                lp_tokens = (amount_a * amount_b) ** 0.5
            else:
                lp_tokens = min((amount_a / reserve_a) * total_liquidity, (amount_b / reserve_b) * total_liquidity)
            
            new_reserve_a = reserve_a + amount_a
            new_reserve_b = reserve_b + amount_b
            new_total_liquidity = total_liquidity + lp_tokens
            
            PoolModel.update_reserves(pool_id, str(new_reserve_a), str(new_reserve_b), str(new_total_liquidity))
            
            position_id = LiquidityPositionModel.create(pool_id, user_id, wallet_id, str(lp_tokens), str(amount_a), str(amount_b))
            
            return jsonify({'success': True, 'position_id': position_id, 'lp_tokens': lp_tokens})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/liquidity/remove', methods=['POST'])
    @jwt_required()
    def remove_liquidity():
        try:
            user_id = get_jwt_identity()
            data = request.get_json()
            position_id = data.get('position_id')
            
            position = LiquidityPositionModel.find_by_id(position_id)
            if not position or position['user_id'] != user_id:
                return jsonify({'error': 'Position not found'}), 404
            
            pool = PoolModel.find_by_id(position['pool_id'])
            if not pool:
                return jsonify({'error': 'Pool not found'}), 404
            
            lp_tokens = float(position['lp_token_amount'])
            total_liquidity = float(pool['total_liquidity'])
            share = lp_tokens / total_liquidity
            
            amount_a = float(pool['reserve_a']) * share
            amount_b = float(pool['reserve_b']) * share
            
            new_reserve_a = float(pool['reserve_a']) - amount_a
            new_reserve_b = float(pool['reserve_b']) - amount_b
            new_total_liquidity = total_liquidity - lp_tokens
            
            PoolModel.update_reserves(pool['id'], str(new_reserve_a), str(new_reserve_b), str(new_total_liquidity))
            LiquidityPositionModel.delete_position(position_id, user_id)
            
            return jsonify({'success': True, 'amount_a': amount_a, 'amount_b': amount_b})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/liquidity/positions', methods=['GET'])
    @jwt_required()
    def get_liquidity_positions():
        try:
            user_id = get_jwt_identity()
            positions = LiquidityPositionModel.find_by_user(user_id)
            return jsonify({'success': True, 'positions': positions})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    return app
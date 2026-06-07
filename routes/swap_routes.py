from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.swap_models import SwapModel
from models.pool_models import PoolModel
from models.wallet_models import WalletModel

def register_swap_routes(app):
    
    @app.route('/api/swap/quote', methods=['POST'])
    @jwt_required()
    def get_quote():
        try:
            data = request.get_json()
            network = data.get('network', 'tron')
            from_token = data.get('from_token')
            to_token = data.get('to_token')
            amount = float(data.get('amount', 0))
            
            pool = PoolModel.find_by_tokens(network, from_token, to_token)
            if not pool:
                return jsonify({'error': 'Pool not found'}), 404
            
            reserve_a = float(pool['reserve_a'])
            reserve_b = float(pool['reserve_b'])
            
            if pool['token_a_address'] == from_token:
                amount_out = (amount * reserve_b) / (reserve_a + amount)
            else:
                amount_out = (amount * reserve_a) / (reserve_b + amount)
            
            fee = amount_out * (pool['fee_percent'] / 100)
            amount_out -= fee
            
            return jsonify({
                'success': True,
                'quote': {
                    'from_amount': amount,
                    'to_amount': amount_out,
                    'fee': fee,
                    'fee_percent': pool['fee_percent'],
                    'price': amount_out / amount,
                    'slippage': 0.5
                }
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/swap/execute', methods=['POST'])
    @jwt_required()
    def execute_swap():
        try:
            user_id = get_jwt_identity()
            data = request.get_json()
            wallet_id = data.get('wallet_id')
            network = data.get('network', 'tron')
            from_token = data.get('from_token')
            to_token = data.get('to_token')
            amount = float(data.get('amount'))
            slippage = data.get('slippage', 0.5)
            
            wallet = WalletModel.find_by_id(wallet_id)
            if not wallet or wallet['user_id'] != user_id:
                return jsonify({'error': 'Wallet not found'}), 404
            
            pool = PoolModel.find_by_tokens(network, from_token, to_token)
            if not pool:
                return jsonify({'error': 'Pool not found'}), 404
            
            reserve_a = float(pool['reserve_a'])
            reserve_b = float(pool['reserve_b'])
            
            if pool['token_a_address'] == from_token:
                amount_out = (amount * reserve_b) / (reserve_a + amount)
            else:
                amount_out = (amount * reserve_a) / (reserve_b + amount)
            
            fee = amount_out * (pool['fee_percent'] / 100)
            amount_out -= fee
            
            if pool['token_a_address'] == from_token:
                new_reserve_a = reserve_a + amount
                new_reserve_b = reserve_b - amount_out
            else:
                new_reserve_a = reserve_a - amount_out
                new_reserve_b = reserve_b + amount
            
            PoolModel.update_reserves(pool['id'], str(new_reserve_a), str(new_reserve_b), pool['total_liquidity'])
            
            swap_id = SwapModel.create(user_id, wallet_id, pool['id'], from_token, to_token, str(amount), str(amount_out), str(fee))
            
            return jsonify({'success': True, 'swap_id': swap_id, 'from_amount': amount, 'to_amount': amount_out, 'fee': fee})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/swap/history', methods=['GET'])
    @jwt_required()
    def get_swap_history():
        try:
            user_id = get_jwt_identity()
            swaps = SwapModel.find_by_user(user_id)
            return jsonify({'success': True, 'history': swaps})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/swap/tokens', methods=['GET'])
    @jwt_required()
    def get_swap_tokens():
        try:
            network = request.args.get('network', 'tron')
            pools = PoolModel.get_all_pools(network)
            tokens = set()
            for pool in pools:
                tokens.add(pool['token_a_symbol'])
                tokens.add(pool['token_b_symbol'])
            return jsonify({'success': True, 'tokens': list(tokens)})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    return app
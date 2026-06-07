from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.wallet_models import WalletModel, NetworkAccountModel
from models.chain_models import ChainPreferenceModel
import random

def register_multi_chain_ui_routes(app):
    
    @app.route('/api/multi-chain/balance', methods=['GET'])
    @jwt_required()
    def get_multi_chain_balance():
        try:
            user_id = get_jwt_identity()
            wallet_id = request.args.get('wallet_id')
            
            wallet = WalletModel.find_by_id(wallet_id)
            if not wallet or wallet['user_id'] != user_id:
                return jsonify({'error': 'Wallet not found'}), 404
            
            accounts = NetworkAccountModel.find_by_wallet(wallet_id)
            prices = {'TRX': 0.10, 'ETH': 3500, 'BNB': 600, 'MATIC': 0.80, 'BTC': 65000}
            symbols = {'tron': 'TRX', 'ethereum': 'ETH', 'bsc': 'BNB', 'polygon': 'MATIC', 'bitcoin': 'BTC'}
            
            chains = []
            total_usd = 0
            for account in accounts:
                balance = random.uniform(10, 1000)
                symbol = symbols.get(account['network'], 'TOKEN')
                usd_value = balance * prices.get(symbol, 1)
                total_usd += usd_value
                chains.append({
                    'chain_id': account['network'],
                    'chain_name': account['network'].capitalize(),
                    'balance': balance,
                    'symbol': symbol,
                    'usd_value': usd_value
                })
            
            return jsonify({
                'success': True,
                'summary': {'chains': chains, 'total_usd': total_usd}
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/multi-chain/switch-all', methods=['POST'])
    @jwt_required()
    def switch_all_chains():
        try:
            user_id = get_jwt_identity()
            data = request.get_json()
            testnet = data.get('testnet', False)
            
            ChainPreferenceModel.set_all_chains_testnet(user_id, testnet)
            return jsonify({'success': True, 'testnet': testnet})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    return app
from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.wallet_models import WalletModel, NetworkAccountModel
import random

def register_balance_routes(app):
    
    @app.route('/api/balance/<int:wallet_id>', methods=['GET'])
    @jwt_required()
    def get_balance(wallet_id):
        try:
            user_id = get_jwt_identity()
            network = request.args.get('network', 'tron')
            
            wallet = WalletModel.find_by_id(wallet_id)
            if not wallet or wallet['user_id'] != user_id:
                return jsonify({'error': 'Wallet not found'}), 404
            
            account = NetworkAccountModel.find_by_wallet_and_network(wallet_id, network)
            if not account:
                return jsonify({'error': f'Network {network} not found'}), 404
            
            symbols = {'tron': 'TRX', 'ethereum': 'ETH', 'bsc': 'BNB', 'polygon': 'MATIC', 'bitcoin': 'BTC'}
            prices = {'TRX': 0.10, 'ETH': 3500, 'BNB': 600, 'MATIC': 0.80, 'BTC': 65000}
            
            balance = round(random.uniform(10, 1000), 2)
            symbol = symbols.get(network, 'TOKEN')
            usd_value = balance * prices.get(symbol, 1)
            
            return jsonify({
                'success': True,
                'network': network,
                'address': account['address'],
                'balance': balance,
                'symbol': symbol,
                'usd_value': usd_value
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/balance/multi-network', methods=['POST'])
    @jwt_required()
    def get_multi_network_balance():
        try:
            user_id = get_jwt_identity()
            data = request.get_json()
            wallet_id = data.get('wallet_id')
            
            wallet = WalletModel.find_by_id(wallet_id)
            if not wallet or wallet['user_id'] != user_id:
                return jsonify({'error': 'Wallet not found'}), 404
            
            accounts = NetworkAccountModel.find_by_wallet(wallet_id)
            symbols = {'tron': 'TRX', 'ethereum': 'ETH', 'bsc': 'BNB', 'polygon': 'MATIC', 'bitcoin': 'BTC'}
            prices = {'TRX': 0.10, 'ETH': 3500, 'BNB': 600, 'MATIC': 0.80, 'BTC': 65000}
            
            networks = []
            total_usd = 0
            for account in accounts:
                balance = round(random.uniform(10, 1000), 2)
                symbol = symbols.get(account['network'], 'TOKEN')
                usd_value = balance * prices.get(symbol, 1)
                total_usd += usd_value
                networks.append({
                    'network': account['network'],
                    'address': account['address'],
                    'balance': balance,
                    'symbol': symbol,
                    'usd_value': usd_value
                })
            
            return jsonify({'success': True, 'networks': networks, 'total_usd': total_usd})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    return app
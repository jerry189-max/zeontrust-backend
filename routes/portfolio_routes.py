from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.wallet_models import WalletModel, NetworkAccountModel
import random

def register_portfolio_routes(app):
    
    @app.route('/api/portfolio/total', methods=['GET'])
    @jwt_required()
    def get_total_portfolio():
        try:
            user_id = get_jwt_identity()
            wallet_id = request.args.get('wallet_id')
            
            wallet = WalletModel.find_by_id(wallet_id)
            if not wallet or wallet['user_id'] != user_id:
                return jsonify({'error': 'Wallet not found'}), 404
            
            accounts = NetworkAccountModel.find_by_wallet(wallet_id)
            prices = {'TRX': 0.10, 'ETH': 3500, 'BNB': 600, 'MATIC': 0.80, 'BTC': 65000}
            
            total_value = 0
            for account in accounts:
                balance = random.uniform(10, 1000)
                symbol = {'tron': 'TRX', 'ethereum': 'ETH', 'bsc': 'BNB', 'polygon': 'MATIC', 'bitcoin': 'BTC'}.get(account['network'], 'TOKEN')
                total_value += balance * prices.get(symbol, 1)
            
            return jsonify({'success': True, 'total_value': total_value, 'currency': 'USD'})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/portfolio/history', methods=['GET'])
    @jwt_required()
    def get_portfolio_history():
        try:
            days = request.args.get('days', 30, type=int)
            
            history = []
            for i in range(days):
                history.append({
                    'date': f'2024-01-{i+1}',
                    'value': random.uniform(100, 1000)
                })
            
            return jsonify({'success': True, 'history': history})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    return app
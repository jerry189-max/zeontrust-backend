from flask import request, jsonify
from flask_jwt_extended import jwt_required
import requests

def register_price_routes(app):
    
    @app.route('/api/prices', methods=['GET'])
    def get_all_prices():
        try:
            prices = {
                'TRX': 0.10,
                'ETH': 3500,
                'BNB': 600,
                'MATIC': 0.80,
                'BTC': 65000,
                'USDT': 1.00,
                'USDC': 1.00,
                'DAI': 1.00
            }
            return jsonify({'success': True, 'prices': prices, 'source': 'local'})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/price/<symbol>', methods=['GET'])
    def get_token_price(symbol):
        try:
            prices = {
                'TRX': 0.10, 'ETH': 3500, 'BNB': 600, 'MATIC': 0.80,
                'BTC': 65000, 'USDT': 1.00, 'USDC': 1.00, 'DAI': 1.00
            }
            price = prices.get(symbol.upper(), 0)
            return jsonify({'success': True, 'symbol': symbol, 'price': price, 'currency': 'USD'})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/price/historical', methods=['GET'])
    @jwt_required()
    def get_historical_prices():
        try:
            token = request.args.get('token', 'TRX')
            days = request.args.get('days', 7, type=int)
            
            history = []
            for i in range(days):
                history.append({
                    'date': f'2024-01-{i+1}',
                    'price': round(0.10 + (i * 0.005), 4)
                })
            
            return jsonify({'success': True, 'history': history})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    return app
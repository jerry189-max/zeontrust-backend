from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.wallet_models import WalletModel, NetworkAccountModel

def register_resource_routes(app):
    
    @app.route('/api/resources/info', methods=['GET'])
    @jwt_required()
    def get_resource_info():
        try:
            user_id = get_jwt_identity()
            wallet_id = request.args.get('wallet_id')
            
            wallet = WalletModel.find_by_id(wallet_id)
            if not wallet or wallet['user_id'] != user_id:
                return jsonify({'error': 'Wallet not found'}), 404
            
            resources = {
                'energy': {'available': 150000, 'used': 50000, 'total': 200000, 'percentage': 25, 'frozen': 100},
                'bandwidth': {'available': 5000, 'used': 2000, 'total': 7000, 'percentage': 28.5, 'frozen': 50}
            }
            
            return jsonify({'success': True, 'resources': resources})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/resources/delegate', methods=['POST'])
    @jwt_required()
    def delegate_resource():
        try:
            data = request.get_json()
            to_address = data.get('to_address')
            amount = data.get('amount')
            resource_type = data.get('resource_type', 'ENERGY')
            
            return jsonify({'success': True, 'message': f'Delegated {amount} {resource_type} to {to_address}'})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/resources/prices', methods=['GET'])
    @jwt_required()
    def get_resource_prices():
        return jsonify({
            'success': True,
            'prices': {
                'energy': {'price_trx': 0.00042, 'price_usd': 0.000042},
                'bandwidth': {'price_trx': 0.001, 'price_usd': 0.0001}
            }
        })
    
    @app.route('/api/resources/recommend', methods=['POST'])
    @jwt_required()
    def get_resource_recommendation():
        data = request.get_json()
        daily_transactions = data.get('daily_transactions', 10)
        
        return jsonify({
            'success': True,
            'recommendation': {
                'daily_transactions': daily_transactions,
                'recommended': {
                    'energy': {'trx_to_stake': daily_transactions * 5, 'energy_received': daily_transactions * 65000, 'cost_usd': daily_transactions * 0.5},
                    'bandwidth': {'trx_to_stake': daily_transactions * 2, 'bandwidth_received': daily_transactions * 4000, 'cost_usd': daily_transactions * 0.2}
                },
                'alternative_buying': {'total_cost_trx': daily_transactions * 0.5}
            }
        })
    
    return app
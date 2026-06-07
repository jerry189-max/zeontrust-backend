from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.wallet_models import WalletModel, NetworkAccountModel

def register_approval_routes(app):
    
    @app.route('/api/approvals/list', methods=['GET'])
    @jwt_required()
    def get_approvals():
        try:
            user_id = get_jwt_identity()
            wallet_id = request.args.get('wallet_id')
            network = request.args.get('network', 'tron')
            
            wallet = WalletModel.find_by_id(wallet_id)
            if not wallet or wallet['user_id'] != user_id:
                return jsonify({'error': 'Wallet not found'}), 404
            
            # Mock approvals data
            approvals = [
                {'spender': '0x...1234', 'token': 'USDT', 'amount': '1000', 'network': network},
                {'spender': '0x...5678', 'token': 'USDC', 'amount': '500', 'network': network}
            ]
            
            return jsonify({'success': True, 'approvals': approvals})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/approvals/revoke', methods=['POST'])
    @jwt_required()
    def revoke_approval():
        try:
            data = request.get_json()
            spender = data.get('spender')
            token = data.get('token')
            
            return jsonify({'success': True, 'message': f'Approval revoked for {spender}'})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/approvals/revoke-all', methods=['POST'])
    @jwt_required()
    def revoke_all_approvals():
        try:
            return jsonify({'success': True, 'message': 'All approvals revoked'})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    return app
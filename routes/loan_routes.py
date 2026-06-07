from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.loan_models import LoanModel
from models.wallet_models import WalletModel

def register_loan_routes(app):
    
    @app.route('/api/loan/request', methods=['POST'])
    @jwt_required()
    def request_loan():
        try:
            user_id = get_jwt_identity()
            data = request.get_json()
            wallet_id = data.get('wallet_id')
            network = data.get('network')
            token = data.get('token')
            amount = data.get('amount')
            duration_days = data.get('duration_days')
            purpose = data.get('purpose')
            
            wallet = WalletModel.find_by_id(wallet_id)
            if not wallet or wallet['user_id'] != user_id:
                return jsonify({'error': 'Wallet not found'}), 404
            
            loan_id = LoanModel.create(user_id, wallet_id, network, token, amount, duration_days, purpose)
            
            return jsonify({'success': True, 'loan_id': loan_id, 'message': 'Loan request submitted'})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/loan/my-requests', methods=['GET'])
    @jwt_required()
    def get_my_loans():
        try:
            user_id = get_jwt_identity()
            loans = LoanModel.find_by_user(user_id)
            return jsonify({'success': True, 'loans': loans})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/loan/repay', methods=['POST'])
    @jwt_required()
    def repay_loan():
        try:
            user_id = get_jwt_identity()
            data = request.get_json()
            loan_id = data.get('loan_id')
            amount = data.get('amount')
            
            loan = LoanModel.find_by_id(loan_id)
            if not loan or loan['user_id'] != user_id:
                return jsonify({'error': 'Loan not found'}), 404
            
            LoanModel.mark_repaid(loan_id, amount)
            
            return jsonify({'success': True, 'message': 'Loan repaid successfully'})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    return app
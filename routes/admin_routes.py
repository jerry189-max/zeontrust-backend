from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.user_models import UserModel
from models.wallet_models import WalletModel
from models.transaction_models import TransactionModel
from models.token_models import TokenVerificationRequestModel, VerifiedTokenModel
from models.loan_models import LoanModel
from datetime import datetime

def register_admin_routes(app):
    
    @app.route('/api/admin/users', methods=['GET'])
    @jwt_required()
    def admin_get_users():
        try:
            admin_id = get_jwt_identity()
            admin = UserModel.find_by_id(admin_id)
            if not admin or not admin['is_admin']:
                return jsonify({'error': 'Admin access required'}), 403
            
            users = UserModel.get_all_users()
            return jsonify({'success': True, 'users': users})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/admin/users/<int:user_id>', methods=['GET'])
    @jwt_required()
    def admin_get_user(user_id):
        try:
            admin_id = get_jwt_identity()
            admin = UserModel.find_by_id(admin_id)
            if not admin or not admin['is_admin']:
                return jsonify({'error': 'Admin access required'}), 403
            
            user = UserModel.find_by_id(user_id)
            if not user:
                return jsonify({'error': 'User not found'}), 404
            
            wallets = WalletModel.find_by_user(user_id)
            return jsonify({'success': True, 'user': user, 'wallets': wallets})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/admin/users/<int:user_id>/block', methods=['POST'])
    @jwt_required()
    def admin_block_user(user_id):
        try:
            admin_id = get_jwt_identity()
            admin = UserModel.find_by_id(admin_id)
            if not admin or not admin['is_admin']:
                return jsonify({'error': 'Admin access required'}), 403
            
            UserModel.set_active_status(user_id, False)
            return jsonify({'success': True, 'message': 'User blocked successfully'})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/admin/users/<int:user_id>/unblock', methods=['POST'])
    @jwt_required()
    def admin_unblock_user(user_id):
        try:
            admin_id = get_jwt_identity()
            admin = UserModel.find_by_id(admin_id)
            if not admin or not admin['is_admin']:
                return jsonify({'error': 'Admin access required'}), 403
            
            UserModel.set_active_status(user_id, True)
            return jsonify({'success': True, 'message': 'User unblocked successfully'})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/admin/stats', methods=['GET'])
    @jwt_required()
    def admin_get_stats():
        try:
            admin_id = get_jwt_identity()
            admin = UserModel.find_by_id(admin_id)
            if not admin or not admin['is_admin']:
                return jsonify({'error': 'Admin access required'}), 403
            
            total_users = UserModel.get_user_count()
            total_wallets = WalletModel.get_wallet_count()
            total_transactions = TransactionModel.get_transaction_count()
            pending_approvals = len(TokenVerificationRequestModel.find_pending_requests())
            active_loans = len(LoanModel.find_active_loans())
            
            return jsonify({
                'success': True,
                'stats': {
                    'total_users': total_users,
                    'total_wallets': total_wallets,
                    'total_transactions': total_transactions,
                    'pending_approvals': pending_approvals,
                    'active_loans': active_loans
                }
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/admin/token-requests', methods=['GET'])
    @jwt_required()
    def admin_get_token_requests():
        try:
            admin_id = get_jwt_identity()
            admin = UserModel.find_by_id(admin_id)
            if not admin or not admin['is_admin']:
                return jsonify({'error': 'Admin access required'}), 403
            
            requests = TokenVerificationRequestModel.find_pending_requests()
            return jsonify({'success': True, 'requests': requests})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/admin/token-requests/<int:request_id>/approve', methods=['POST'])
    @jwt_required()
    def admin_approve_token(request_id):
        try:
            admin_id = get_jwt_identity()
            admin = UserModel.find_by_id(admin_id)
            if not admin or not admin['is_admin']:
                return jsonify({'error': 'Admin access required'}), 403
            
            data = request.get_json()
            category = data.get('category', 'DeFi')
            
            token_request = TokenVerificationRequestModel.find_by_id(request_id)
            if not token_request:
                return jsonify({'error': 'Request not found'}), 404
            
            VerifiedTokenModel.create_verified_token(
                token_request['network'], token_request['contract_address'],
                token_request['token_name'], token_request['token_symbol'],
                token_request['decimals'], token_request['logo_url'],
                token_request['website'], category
            )
            
            TokenVerificationRequestModel.update_status(request_id, 'approved', admin_id)
            
            return jsonify({'success': True, 'message': 'Token approved successfully'})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/admin/token-requests/<int:request_id>/reject', methods=['POST'])
    @jwt_required()
    def admin_reject_token(request_id):
        try:
            admin_id = get_jwt_identity()
            admin = UserModel.find_by_id(admin_id)
            if not admin or not admin['is_admin']:
                return jsonify({'error': 'Admin access required'}), 403
            
            data = request.get_json()
            notes = data.get('notes', '')
            
            TokenVerificationRequestModel.update_status(request_id, 'rejected', admin_id, notes)
            
            return jsonify({'success': True, 'message': 'Token rejected'})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    return app
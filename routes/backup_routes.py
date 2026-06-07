from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.wallet_models import WalletModel
from models.security_models import BackupHistoryModel

def register_backup_routes(app):
    
    @app.route('/api/backup/mnemonic', methods=['POST'])
    @jwt_required()
    def backup_mnemonic():
        try:
            user_id = get_jwt_identity()
            data = request.get_json()
            wallet_id = data.get('wallet_id')
            password = data.get('password')
            
            wallet = WalletModel.find_by_id(wallet_id)
            if not wallet or wallet['user_id'] != user_id:
                return jsonify({'error': 'Wallet not found'}), 404
            
            # In production, decrypt mnemonic with password
            mnemonic = "abandon ability able about above absent absorb abstract absurd accuse achieve acid"
            
            return jsonify({'success': True, 'mnemonic': mnemonic, 'warning': 'Store this securely!'})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/backup/status', methods=['GET'])
    @jwt_required()
    def get_backup_status():
        try:
            user_id = get_jwt_identity()
            wallet_id = request.args.get('wallet_id')
            
            wallet = WalletModel.find_by_id(wallet_id)
            if not wallet or wallet['user_id'] != user_id:
                return jsonify({'error': 'Wallet not found'}), 404
            
            last_backup = BackupHistoryModel.get_last_backup(user_id, wallet_id)
            
            return jsonify({
                'success': True,
                'is_backed_up': wallet['is_backed_up'],
                'last_backup': last_backup['created_at'] if last_backup else None
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/backup/history', methods=['GET'])
    @jwt_required()
    def get_backup_history():
        try:
            user_id = get_jwt_identity()
            history = BackupHistoryModel.find_by_user(user_id)
            return jsonify({'success': True, 'history': history})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    return app
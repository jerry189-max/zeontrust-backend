from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.user_models import UserModel
from models.wallet_models import WalletModel
from models.multisig_models import MultiSigWalletModel, ProposalModel
import uuid
import json
from datetime import datetime

def register_multisig_routes(app):
    
    # ==================== CREATE MULTISIG WALLET ====================
    
    @app.route('/api/multisig/create', methods=['POST'])
    @jwt_required()
    def create_multisig():
        try:
            user_id = get_jwt_identity()
            data = request.get_json()
            
            name = data.get('name')
            owners = data.get('owners', [])
            threshold = data.get('threshold', 2)
            network = data.get('network', 'tron')
            
            if len(owners) < 2:
                return jsonify({'error': 'At least 2 owners required'}), 400
            if threshold < 2 or threshold > len(owners):
                return jsonify({'error': f'Threshold must be between 2 and {len(owners)}'}), 400
            
            # Check if current user is in owners list
            user = UserModel.find_by_id(user_id)
            if user['username'] not in owners:
                owners.append(user['username'])
            
            wallet_id = f"MS_{uuid.uuid4().hex[:10]}"
            address = f"0x{hashlib.sha256(wallet_id.encode()).hexdigest()[:40]}"
            
            MultiSigWalletModel.create(wallet_id, name, owners, threshold, network, address, user_id)
            
            return jsonify({
                'success': True,
                'wallet_id': wallet_id,
                'name': name,
                'owners': owners,
                'threshold': threshold,
                'address': address,
                'message': 'Multi-signature wallet created successfully'
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    # ==================== GET USER'S MULTISIG WALLETS ====================
    
    @app.route('/api/multisig/list', methods=['GET'])
    @jwt_required()
    def get_multisig_list():
        try:
            user_id = get_jwt_identity()
            user = UserModel.find_by_id(user_id)
            
            # Get wallets where user is owner
            wallets = MultiSigWalletModel.find_by_owner(user['username'])
            
            # Also get wallets created by user
            created_wallets = MultiSigWalletModel.find_by_user(user_id)
            for wallet in created_wallets:
                if wallet not in wallets:
                    wallets.append(wallet)
            
            return jsonify({'success': True, 'multisig_wallets': wallets})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    # ==================== GET MULTISIG WALLET DETAILS ====================
    
    @app.route('/api/multisig/<wallet_id>', methods=['GET'])
    @jwt_required()
    def get_multisig_wallet(wallet_id):
        try:
            wallet = MultiSigWalletModel.find_by_id(wallet_id)
            if not wallet:
                return jsonify({'error': 'Wallet not found'}), 404
            
            # Get proposals for this wallet
            proposals = ProposalModel.find_by_multisig(wallet_id)
            
            return jsonify({
                'success': True,
                'wallet': wallet,
                'proposals': proposals,
                'proposal_count': len(proposals)
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    # ==================== UPDATE MULTISIG WALLET ====================
    
    @app.route('/api/multisig/<wallet_id>', methods=['PUT'])
    @jwt_required()
    def update_multisig_wallet(wallet_id):
        try:
            user_id = get_jwt_identity()
            user = UserModel.find_by_id(user_id)
            data = request.get_json()
            
            wallet = MultiSigWalletModel.find_by_id(wallet_id)
            if not wallet:
                return jsonify({'error': 'Wallet not found'}), 404
            
            # Check if user is owner
            if user['username'] not in wallet['owners']:
                return jsonify({'error': 'Only owners can update wallet'}), 403
            
            # Update wallet (only name can be updated)
            new_name = data.get('name')
            if new_name:
                # Update name in database
                conn = get_db()
                cursor = conn.cursor()
                cursor.execute('UPDATE multisig_wallets SET name = ? WHERE id = ?', (new_name, wallet_id))
                conn.commit()
                conn.close()
            
            return jsonify({'success': True, 'message': 'Wallet updated successfully'})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    # ==================== GET MULTISIG BALANCE ====================
    
    @app.route('/api/multisig/<wallet_id>/balance', methods=['GET'])
    @jwt_required()
    def get_multisig_balance(wallet_id):
        try:
            wallet = MultiSigWalletModel.find_by_id(wallet_id)
            if not wallet:
                return jsonify({'error': 'Wallet not found'}), 404
            
            # Mock balance - in production fetch from blockchain
            import random
            balance = round(random.uniform(100, 10000), 2)
            
            return jsonify({
                'success': True,
                'balance': balance,
                'symbol': 'TRX',
                'address': wallet['address']
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    return app
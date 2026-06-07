from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.user_models import UserModel
from models.multisig_models import MultiSigWalletModel, ProposalModel
import uuid
import json
from datetime import datetime

def register_proposal_routes(app):
    
    # ==================== CREATE PROPOSAL ====================
    
    @app.route('/api/multisig/proposal/create', methods=['POST'])
    @jwt_required()
    def create_proposal():
        try:
            user_id = get_jwt_identity()
            data = request.get_json()
            
            multisig_id = data.get('multisig_id')
            to_address = data.get('to_address')
            amount = data.get('amount')
            token_address = data.get('token_address')
            description = data.get('description')
            
            if not all([multisig_id, to_address, amount]):
                return jsonify({'error': 'Missing required fields'}), 400
            
            user = UserModel.find_by_id(user_id)
            wallet = MultiSigWalletModel.find_by_id(multisig_id)
            
            if not wallet:
                return jsonify({'error': 'Multi-signature wallet not found'}), 404
            
            # Check if user is owner
            if user['username'] not in wallet['owners']:
                return jsonify({'error': 'Only owners can create proposals'}), 403
            
            proposal_id = f"PROP_{uuid.uuid4().hex[:8]}"
            
            ProposalModel.create(
                proposal_id, multisig_id, user['username'], to_address,
                str(amount), description, token_address, wallet['threshold']
            )
            
            return jsonify({
                'success': True,
                'proposal_id': proposal_id,
                'message': 'Proposal created successfully'
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    # ==================== SIGN PROPOSAL ====================
    
    @app.route('/api/multisig/proposal/sign', methods=['POST'])
    @jwt_required()
    def sign_proposal():
        try:
            user_id = get_jwt_identity()
            data = request.get_json()
            proposal_id = data.get('proposal_id')
            
            if not proposal_id:
                return jsonify({'error': 'Proposal ID required'}), 400
            
            user = UserModel.find_by_id(user_id)
            proposal = ProposalModel.find_by_id(proposal_id)
            
            if not proposal:
                return jsonify({'error': 'Proposal not found'}), 404
            
            # Check if user is owner of the multisig wallet
            wallet = MultiSigWalletModel.find_by_id(proposal['multisig_id'])
            if user['username'] not in wallet['owners']:
                return jsonify({'error': 'Only owners can sign proposals'}), 403
            
            # Check if already signed
            if user['username'] in proposal['signatures']:
                return jsonify({'error': 'Already signed this proposal'}), 400
            
            ProposalModel.add_signature(proposal_id, user['username'])
            
            # Get updated proposal to check status
            updated_proposal = ProposalModel.find_by_id(proposal_id)
            signature_count = len(updated_proposal['signatures'])
            required = updated_proposal['required_signatures']
            
            message = f'Proposal signed. {signature_count}/{required} signatures collected'
            if signature_count >= required:
                message = 'Proposal is now ready for execution!'
            
            return jsonify({
                'success': True,
                'signature_count': signature_count,
                'required_signatures': required,
                'is_ready': signature_count >= required,
                'message': message
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    # ==================== UNSIGN PROPOSAL ====================
    
    @app.route('/api/multisig/proposal/unsign', methods=['POST'])
    @jwt_required()
    def unsign_proposal():
        try:
            user_id = get_jwt_identity()
            data = request.get_json()
            proposal_id = data.get('proposal_id')
            
            if not proposal_id:
                return jsonify({'error': 'Proposal ID required'}), 400
            
            user = UserModel.find_by_id(user_id)
            proposal = ProposalModel.find_by_id(proposal_id)
            
            if not proposal:
                return jsonify({'error': 'Proposal not found'}), 404
            
            if user['username'] not in proposal['signatures']:
                return jsonify({'error': 'You have not signed this proposal'}), 400
            
            # Remove signature
            signatures = proposal['signatures']
            signatures.remove(user['username'])
            
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute('UPDATE proposals SET signatures = ? WHERE id = ?', 
                          (json.dumps(signatures), proposal_id))
            conn.commit()
            conn.close()
            
            return jsonify({
                'success': True,
                'message': 'Signature removed successfully'
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    # ==================== EXECUTE PROPOSAL ====================
    
    @app.route('/api/multisig/proposal/execute', methods=['POST'])
    @jwt_required()
    def execute_proposal():
        try:
            user_id = get_jwt_identity()
            data = request.get_json()
            proposal_id = data.get('proposal_id')
            
            if not proposal_id:
                return jsonify({'error': 'Proposal ID required'}), 400
            
            user = UserModel.find_by_id(user_id)
            proposal = ProposalModel.find_by_id(proposal_id)
            
            if not proposal:
                return jsonify({'error': 'Proposal not found'}), 404
            
            # Check if proposal is ready
            if len(proposal['signatures']) < proposal['required_signatures']:
                return jsonify({'error': 'Not enough signatures to execute'}), 400
            
            # Check if already executed
            if proposal['status'] == 'executed':
                return jsonify({'error': 'Proposal already executed'}), 400
            
            # Execute proposal (mock transaction)
            import hashlib
            import time
            tx_hash = hashlib.sha256(f"{proposal_id}{time.time()}".encode()).hexdigest()
            
            ProposalModel.execute_proposal(proposal_id)
            
            return jsonify({
                'success': True,
                'tx_hash': tx_hash,
                'message': 'Proposal executed successfully'
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    # ==================== CANCEL PROPOSAL ====================
    
    @app.route('/api/multisig/proposal/cancel', methods=['POST'])
    @jwt_required()
    def cancel_proposal():
        try:
            user_id = get_jwt_identity()
            data = request.get_json()
            proposal_id = data.get('proposal_id')
            
            if not proposal_id:
                return jsonify({'error': 'Proposal ID required'}), 400
            
            user = UserModel.find_by_id(user_id)
            proposal = ProposalModel.find_by_id(proposal_id)
            
            if not proposal:
                return jsonify({'error': 'Proposal not found'}), 404
            
            # Only creator can cancel
            if proposal['creator'] != user['username']:
                return jsonify({'error': 'Only the creator can cancel this proposal'}), 403
            
            ProposalModel.cancel_proposal(proposal_id)
            
            return jsonify({
                'success': True,
                'message': 'Proposal cancelled successfully'
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    # ==================== GET PROPOSAL DETAILS ====================
    
    @app.route('/api/multisig/proposal/<proposal_id>', methods=['GET'])
    @jwt_required()
    def get_proposal(proposal_id):
        try:
            proposal = ProposalModel.find_by_id(proposal_id)
            if not proposal:
                return jsonify({'error': 'Proposal not found'}), 404
            
            wallet = MultiSigWalletModel.find_by_id(proposal['multisig_id'])
            
            return jsonify({
                'success': True,
                'proposal': proposal,
                'wallet_name': wallet['name'] if wallet else ''
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    # ==================== GET PROPOSALS FOR MULTISIG WALLET ====================
    
    @app.route('/api/multisig/<multisig_id>/proposals', methods=['GET'])
    @jwt_required()
    def get_multisig_proposals(multisig_id):
        try:
            status = request.args.get('status')
            proposals = ProposalModel.find_by_multisig(multisig_id, status)
            
            # Add signature count to each proposal
            for proposal in proposals:
                proposal['signature_count'] = len(proposal['signatures'])
                proposal['signatures_list'] = proposal['signatures']
                del proposal['signatures']
            
            return jsonify({'success': True, 'proposals': proposals})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    # ==================== GET MY PENDING PROPOSALS ====================
    
    @app.route('/api/multisig/my-pending', methods=['GET'])
    @jwt_required()
    def get_my_pending_proposals():
        try:
            user_id = get_jwt_identity()
            user = UserModel.find_by_id(user_id)
            
            # Get all multisig wallets where user is owner
            wallets = MultiSigWalletModel.find_by_owner(user['username'])
            
            pending_proposals = []
            for wallet in wallets:
                proposals = ProposalModel.find_by_multisig(wallet['id'], 'pending')
                for proposal in proposals:
                    # Check if user hasn't signed yet
                    if user['username'] not in proposal['signatures']:
                        proposal['wallet_name'] = wallet['name']
                        proposal['signature_count'] = len(proposal['signatures'])
                        proposal['required_signatures'] = proposal['required_signatures']
                        pending_proposals.append(proposal)
            
            return jsonify({'success': True, 'proposals': pending_proposals})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    return app


# Helper function
def get_db():
    import sqlite3
    import os
    db_path = os.path.join(os.path.dirname(__file__), '..', 'database', 'Zeontrust_wallet.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn
from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.multisig_models import ProposalModel, MultiSigWalletModel

def register_execute_routes(app):
    
    @app.route('/api/multisig/sign', methods=['POST'])
    @jwt_required()
    def sign_proposal():
        try:
            user_id = get_jwt_identity()
            data = request.get_json()
            proposal_id = data.get('proposal_id')
            
            user = UserModel.find_by_id(user_id)
            ProposalModel.add_signature(proposal_id, user['username'])
            
            return jsonify({'success': True, 'message': 'Proposal signed'})
        except Exception as e:
            return jsonify({'error': str(e)}), 400
    
    @app.route('/api/multisig/execute', methods=['POST'])
    @jwt_required()
    def execute_proposal():
        try:
            user_id = get_jwt_identity()
            data = request.get_json()
            proposal_id = data.get('proposal_id')
            
            proposal = ProposalModel.find_by_id(proposal_id)
            if not proposal:
                return jsonify({'error': 'Proposal not found'}), 404
            
            if len(proposal['signatures']) < proposal['required_signatures']:
                return jsonify({'error': 'Not enough signatures'}), 400
            
            ProposalModel.execute_proposal(proposal_id)
            
            return jsonify({'success': True, 'message': 'Proposal executed'})
        except Exception as e:
            return jsonify({'error': str(e)}), 400
    
    @app.route('/api/multisig/cancel', methods=['POST'])
    @jwt_required()
    def cancel_proposal():
        try:
            data = request.get_json()
            proposal_id = data.get('proposal_id')
            
            ProposalModel.cancel_proposal(proposal_id)
            return jsonify({'success': True, 'message': 'Proposal cancelled'})
        except Exception as e:
            return jsonify({'error': str(e)}), 400
    
    return app
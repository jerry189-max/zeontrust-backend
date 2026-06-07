from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

def register_rewards_routes(app):
    
    @app.route('/api/rewards/list', methods=['GET'])
    @jwt_required()
    def get_rewards():
        rewards = [{'id': 1, 'type': 'Staking', 'amount': 25, 'token': 'TRX'}]
        return jsonify({'success': True, 'rewards': rewards})
    
    @app.route('/api/rewards/claim', methods=['POST'])
    @jwt_required()
    def claim_rewards():
        return jsonify({'success': True, 'message': 'Rewards claimed'})
    
    return app
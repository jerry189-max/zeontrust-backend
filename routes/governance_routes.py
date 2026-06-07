from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

def register_governance_routes(app):
    
    @app.route('/api/governance/proposals', methods=['GET'])
    @jwt_required()
    def get_proposals():
        proposals = [{'id': 1, 'title': 'Reduce Fee', 'status': 'active', 'votes_for': 1000, 'votes_against': 100}]
        return jsonify({'success': True, 'proposals': proposals})
    
    @app.route('/api/governance/vote', methods=['POST'])
    @jwt_required()
    def cast_vote():
        return jsonify({'success': True, 'message': 'Vote cast'})
    
    return app
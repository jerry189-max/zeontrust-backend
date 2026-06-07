from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

def register_dao_routes(app):
    
    @app.route('/api/dao/proposals', methods=['GET'])
    @jwt_required()
    def get_dao_proposals():
        proposals = [{'id': 1, 'title': 'Treasury Allocation', 'votes_for': 1000, 'votes_against': 100}]
        return jsonify({'success': True, 'proposals': proposals})
    
    @app.route('/api/dao/vote', methods=['POST'])
    @jwt_required()
    def dao_vote():
        return jsonify({'success': True, 'message': 'Vote cast'})
    
    @app.route('/api/dao/treasury', methods=['GET'])
    @jwt_required()
    def get_treasury():
        return jsonify({'success': True, 'balance': 2500000, 'currency': 'USD'})
    
    return app
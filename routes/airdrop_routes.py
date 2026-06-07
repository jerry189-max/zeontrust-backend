from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

def register_airdrop_routes(app):
    
    @app.route('/api/airdrop/list', methods=['GET'])
    @jwt_required()
    def get_airdrops():
        airdrops = [{'id': 1, 'name': 'Zeontrust Airdrop', 'token': 'Zeontrust', 'amount': 100}]
        return jsonify({'success': True, 'airdrops': airdrops})
    
    @app.route('/api/airdrop/claim/<int:airdrop_id>', methods=['POST'])
    @jwt_required()
    def claim_airdrop(airdrop_id):
        return jsonify({'success': True, 'message': 'Airdrop claimed'})
    
    return app
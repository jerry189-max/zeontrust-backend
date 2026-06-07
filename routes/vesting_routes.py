from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

def register_vesting_routes(app):
    
    @app.route('/api/vesting/schedules', methods=['GET'])
    @jwt_required()
    def get_vesting_schedules():
        schedules = [{'id': 1, 'token': 'Zeontrust', 'total': 10000, 'claimable': 500}]
        return jsonify({'success': True, 'schedules': schedules})
    
    @app.route('/api/vesting/claim', methods=['POST'])
    @jwt_required()
    def claim_vesting():
        return jsonify({'success': True, 'message': 'Claimed'})
    
    return app
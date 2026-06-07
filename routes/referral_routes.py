from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

def register_referral_routes(app):
    
    @app.route('/api/referral/code', methods=['GET'])
    @jwt_required()
    def get_referral_code():
        user_id = get_jwt_identity()
        return jsonify({'success': True, 'code': f'Zeontrust{user_id}'})
    
    @app.route('/api/referral/earnings', methods=['GET'])
    @jwt_required()
    def get_earnings():
        return jsonify({'success': True, 'total': 50, 'referrals': 5})
    
    return app
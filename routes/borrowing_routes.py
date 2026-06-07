from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

def register_borrowing_routes(app):
    
    @app.route('/api/borrowing/positions', methods=['GET'])
    @jwt_required()
    def get_borrow_positions():
        return jsonify({'success': True, 'loans': []})
    
    @app.route('/api/borrowing/repay', methods=['POST'])
    @jwt_required()
    def repay():
        return jsonify({'success': True, 'message': 'Repaid'})
    
    return app
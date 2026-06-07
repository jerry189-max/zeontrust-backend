from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

def register_lending_routes(app):
    
    @app.route('/api/lending/markets', methods=['GET'])
    @jwt_required()
    def get_markets():
        markets = [{'token': 'USDT', 'apy': 5.2, 'liquidity': 1000000}]
        return jsonify({'success': True, 'markets': markets})
    
    @app.route('/api/lending/supply', methods=['POST'])
    @jwt_required()
    def supply():
        return jsonify({'success': True, 'message': 'Supplied'})
    
    @app.route('/api/lending/borrow', methods=['POST'])
    @jwt_required()
    def borrow():
        return jsonify({'success': True, 'message': 'Borrowed'})
    
    return app
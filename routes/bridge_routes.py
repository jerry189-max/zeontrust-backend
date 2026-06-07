from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

def register_bridge_routes(app):
    
    @app.route('/api/bridge/transfer', methods=['POST'])
    @jwt_required()
    def bridge_transfer():
        user_id = get_jwt_identity()
        data = request.get_json()
        return jsonify({'success': True, 'tx_hash': '0x' + __import__('hashlib').sha256(str(data).encode()).hexdigest()})
    
    @app.route('/api/bridge/status/<tx_hash>', methods=['GET'])
    @jwt_required()
    def bridge_status(tx_hash):
        return jsonify({'success': True, 'status': 'completed'})
    
    return app
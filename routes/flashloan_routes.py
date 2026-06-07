from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import hashlib
import time
from datetime import datetime

def register_flashloan_routes(app):
    
    @app.route('/api/flashloan/request', methods=['POST'])
    @jwt_required()
    def request_flashloan():
        try:
            user_id = get_jwt_identity()
            data = request.get_json()
            
            amount = data.get('amount')
            token = data.get('token', 'USDT')
            duration_days = data.get('duration_days', 90)
            recipient = data.get('recipient')
            network = data.get('network', 'tron')
            
            if not amount:
                return jsonify({'error': 'Amount required'}), 400
            
            fee = float(amount) * 0.0009
            request_id = hashlib.sha256(f"{user_id}{token}{amount}{time.time()}".encode()).hexdigest()[:16]
            
            return jsonify({
                'success': True,
                'request_id': request_id,
                'amount': amount,
                'token': token,
                'fee': fee,
                'total_repay': float(amount) + fee,
                'duration_days': duration_days,
                'recipient': recipient,
                'network': network,
                'status': 'pending',
                'message': 'Flash loan request submitted'
            })
        except Exception as e:
            print(f"Flash loan error: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/flashloan/my-requests', methods=['GET'])
    @jwt_required()
    def get_my_requests():
        try:
            # Mock data for testing
            return jsonify({
                'success': True,
                'requests': []
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    return app
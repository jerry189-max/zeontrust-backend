from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

def register_lottery_routes(app):
    
    @app.route('/api/lottery/info', methods=['GET'])
    @jwt_required()
    def get_lottery_info():
        return jsonify({'success': True, 'prize_pool': 10000, 'ticket_price': 10, 'tickets_sold': 500})
    
    @app.route('/api/lottery/buy', methods=['POST'])
    @jwt_required()
    def buy_ticket():
        return jsonify({'success': True, 'ticket_id': 1, 'message': 'Ticket purchased'})
    
    return app
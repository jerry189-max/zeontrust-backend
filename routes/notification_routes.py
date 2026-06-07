from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.notification_models import NotificationModel

def register_notification_routes(app):
    
    @app.route('/api/notifications', methods=['GET'])
    @jwt_required()
    def get_notifications():
        try:
            user_id = get_jwt_identity()
            limit = request.args.get('limit', 20, type=int)
            unread_only = request.args.get('unread_only', 'false').lower() == 'true'
            
            notifications = NotificationModel.find_by_user(user_id, limit, unread_only)
            unread_count = NotificationModel.get_unread_count(user_id)
            
            return jsonify({'success': True, 'notifications': notifications, 'unread_count': unread_count})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/notifications/<int:notification_id>/read', methods=['POST'])
    @jwt_required()
    def mark_read(notification_id):
        try:
            user_id = get_jwt_identity()
            NotificationModel.mark_as_read(notification_id, user_id)
            return jsonify({'success': True, 'message': 'Marked as read'})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/notifications/read-all', methods=['POST'])
    @jwt_required()
    def mark_all_read():
        try:
            user_id = get_jwt_identity()
            NotificationModel.mark_all_read(user_id)
            return jsonify({'success': True, 'message': 'All notifications marked as read'})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/notifications/<int:notification_id>', methods=['DELETE'])
    @jwt_required()
    def delete_notification(notification_id):
        try:
            user_id = get_jwt_identity()
            NotificationModel.delete(notification_id, user_id)
            return jsonify({'success': True, 'message': 'Notification deleted'})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    return app
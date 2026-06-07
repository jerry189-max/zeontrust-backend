from models.notification_models import NotificationModel

class NotificationService:
    
    @staticmethod
    def get_notifications(user_id: int, limit: int = 20, unread_only: bool = False) -> list:
        return NotificationModel.find_by_user(user_id, limit, unread_only)
    
    @staticmethod
    def get_unread_count(user_id: int) -> int:
        return NotificationModel.get_unread_count(user_id)
    
    @staticmethod
    def mark_as_read(notification_id: int, user_id: int) -> dict:
        NotificationModel.mark_as_read(notification_id, user_id)
        return {'success': True}
    
    @staticmethod
    def mark_all_read(user_id: int) -> dict:
        NotificationModel.mark_all_read(user_id)
        return {'success': True}
    
    @staticmethod
    def delete_notification(notification_id: int, user_id: int) -> dict:
        NotificationModel.delete(notification_id, user_id)
        return {'success': True}
    
    @staticmethod
    def send_transaction_notification(user_id: int, tx_hash: str, amount: str, status: str) -> int:
        return NotificationModel.create_transaction_notification(user_id, tx_hash, amount, status)
    
    @staticmethod
    def send_token_approval_notification(user_id: int, token_name: str, status: str, notes: str = None) -> int:
        return NotificationModel.create_token_approval_notification(user_id, token_name, status, notes)
    
    @staticmethod
    def send_loan_notification(user_id: int, loan_id: int, amount: str, status: str) -> int:
        return NotificationModel.create_loan_notification(user_id, loan_id, amount, status)
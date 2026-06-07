import uuid
from models.dapp_models import ConnectionHistoryModel

class WalletConnectService:
    
    @staticmethod
    def create_connection(dapp_url: str, dapp_name: str, wallet_address: str, network: str) -> dict:
        connection_id = str(uuid.uuid4())
        return {
            'connection_id': connection_id,
            'dapp_url': dapp_url,
            'dapp_name': dapp_name,
            'wallet_address': wallet_address,
            'network': network,
            'status': 'connected'
        }
    
    @staticmethod
    def get_connections_by_wallet(wallet_address: str) -> list:
        return []
    
    @staticmethod
    def disconnect(connection_id: str) -> bool:
        ConnectionHistoryModel.disconnect(connection_id)
        return True
    
    @staticmethod
    def create_transaction_request(connection_id: str, transaction_data: dict) -> str:
        request_id = str(uuid.uuid4())
        return request_id
    
    @staticmethod
    def get_pending_request(request_id: str) -> dict:
        return {'request_id': request_id, 'status': 'pending'}
    
    @staticmethod
    def approve_request(request_id: str, signed_transaction: dict) -> bool:
        return True
    
    @staticmethod
    def reject_request(request_id: str, reason: str) -> bool:
        return True
    
    @staticmethod
    def parse_transaction_request(raw_request: dict) -> dict:
        return {'to': raw_request.get('to'), 'value': raw_request.get('value'), 'data': raw_request.get('data')}
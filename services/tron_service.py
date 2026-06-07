class TronService:
    
    def __init__(self, api_key: str = None, testnet: bool = False):
        self.api_key = api_key
        self.testnet = testnet
        self.base_url = 'https://api.shasta.trongrid.io' if testnet else 'https://api.trongrid.io'
    
    def get_balance(self, address: str) -> float:
        return 100.0
    
    def get_trc20_balance(self, address: str, contract_address: str) -> float:
        return 1000.0
    
    def get_account_info(self, address: str) -> dict:
        return {'address': address, 'balance': 100, 'bandwidth': 5000, 'energy': 150000}
    
    def estimate_energy(self, from_address: str, to_address: str, amount: str) -> int:
        return 65000
    
    def create_transaction(self, from_address: str, to_address: str, amount: str) -> dict:
        return {'txID': 'mock_tx_hash', 'raw_data': {'contract': []}}
    
    def sign_transaction(self, transaction: dict, private_key: str) -> dict:
        return {'signature': ['mock_signature'], 'txID': transaction.get('txID')}
    
    def broadcast_transaction(self, signed_transaction: dict) -> dict:
        return {'result': True, 'txid': signed_transaction.get('txID')}
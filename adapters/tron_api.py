import requests

class TronAPI:
    """TRON Grid API wrapper"""
    
    def __init__(self, testnet: bool = False, api_key: str = None):
        self.testnet = testnet
        self.api_key = api_key
        self.base_url = 'https://api.shasta.trongrid.io' if testnet else 'https://api.trongrid.io'
        self.headers = {}
        if api_key:
            self.headers['TRON-PRO-API-KEY'] = api_key
    
    def _request(self, method: str, endpoint: str, params: dict = None, data: dict = None) -> dict:
        url = f"{self.base_url}{endpoint}"
        try:
            if method == 'GET':
                response = requests.get(url, headers=self.headers, params=params)
            else:
                response = requests.post(url, headers=self.headers, json=data)
            return response.json()
        except Exception as e:
            return {'Error': str(e)}
    
    def get_account(self, address: str) -> dict:
        """Get account information"""
        return self._request('GET', f'/v1/accounts/{address}')
    
    def get_account_balance(self, address: str) -> float:
        """Get TRX balance"""
        data = self.get_account(address)
        if data.get('data') and len(data['data']) > 0:
            return data['data'][0].get('balance', 0) / 1_000_000
        return 0.0
    
    def get_trc20_balance(self, address: str, contract: str) -> float:
        """Get TRC-20 token balance"""
        data = self._request('GET', f'/v1/accounts/{address}/trc20')
        for token in data.get('data', []):
            if token.get('tokenId', '').lower() == contract.lower():
                return float(token.get('balance', 0)) / 1_000_000
        return 0.0
    
    def get_transactions(self, address: str, limit: int = 20) -> list:
        """Get transaction history"""
        data = self._request('GET', f'/v1/accounts/{address}/transactions', params={'limit': limit})
        return data.get('data', [])
    
    def get_trc20_transactions(self, address: str, limit: int = 20) -> list:
        """Get TRC-20 transaction history"""
        data = self._request('GET', f'/v1/accounts/{address}/transactions/trc20', params={'limit': limit})
        return data.get('data', [])
    
    def get_transaction_by_id(self, tx_id: str) -> dict:
        """Get transaction by ID"""
        return self._request('GET', f'/v1/transactions/{tx_id}')
    
    def get_block(self, block_num: int) -> dict:
        """Get block information"""
        return self._request('GET', f'/v1/blocks/{block_num}')
    
    def get_latest_block(self) -> dict:
        """Get latest block"""
        return self._request('GET', '/v1/blocks/latest')
    
    def get_chain_parameters(self) -> dict:
        """Get chain parameters"""
        return self._request('GET', '/v1/chain/parameters')
    
    def get_super_representatives(self, limit: int = 100) -> list:
        """Get Super Representatives"""
        data = self._request('GET', '/v1/chain/listwitnesses')
        return data.get('witnesses', [])[:limit]
    
    def get_votes(self, address: str) -> list:
        """Get votes by address"""
        account = self.get_account(address)
        if account.get('data') and len(account['data']) > 0:
            return account['data'][0].get('votes', [])
        return []
    
    def broadcast_transaction(self, signed_tx: dict) -> dict:
        """Broadcast signed transaction"""
        return self._request('POST', '/wallet/broadcasttransaction', data=signed_tx)
    
    def estimate_energy(self, transaction: dict) -> int:
        """Estimate energy for transaction"""
        data = self._request('POST', '/wallet/estimateenergy', data=transaction)
        return data.get('energy_required', 0)
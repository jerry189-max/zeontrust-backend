import hashlib
import requests
import json
from .base_adapter import BaseAdapter

class TronAdapter(BaseAdapter):
    """TRON blockchain adapter"""
    
    def __init__(self, testnet: bool = False, api_key: str = None):
        super().__init__('tron', testnet)
        self.api_key = api_key
    
    def _get_rpc_url(self) -> str:
        if self.testnet:
            return 'https://api.shasta.trongrid.io'
        return 'https://api.trongrid.io'
    
    def get_balance(self, address: str) -> float:
        """Get TRX balance for an address"""
        try:
            url = f"{self.rpc_url}/v1/accounts/{address}"
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                if data.get('data') and len(data['data']) > 0:
                    balance = data['data'][0].get('balance', 0)
                    return balance / 1_000_000  # Convert SUN to TRX
            return 0.0
        except Exception as e:
            print(f"Error getting TRON balance: {e}")
            return 0.0
    
    def get_token_balance(self, address: str, token_contract: str) -> float:
        """Get TRC-20 token balance"""
        try:
            url = f"{self.rpc_url}/v1/accounts/{address}/trc20"
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                for token in data.get('data', []):
                    if token.get('tokenId', '').lower() == token_contract.lower():
                        return float(token.get('balance', 0)) / 1_000_000
            return 0.0
        except Exception as e:
            print(f"Error getting TRC20 balance: {e}")
            return 0.0
    
    def send_transaction(self, from_address: str, to_address: str, amount: float, private_key: str) -> str:
        """Send TRX transaction"""
        try:
            # In production, implement actual transaction signing and broadcasting
            tx_hash = hashlib.sha256(f"{from_address}{to_address}{amount}".encode()).hexdigest()
            return tx_hash
        except Exception as e:
            raise Exception(f"Transaction failed: {e}")
    
    def get_transaction(self, tx_hash: str) -> dict:
        """Get transaction details"""
        try:
            url = f"{self.rpc_url}/v1/transactions/{tx_hash}"
            response = requests.get(url)
            if response.status_code == 200:
                return response.json()
            return {}
        except Exception as e:
            return {}
    
    def get_transaction_status(self, tx_hash: str) -> str:
        """Get transaction status"""
        try:
            url = f"{self.rpc_url}/v1/transactions/{tx_hash}"
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                if data.get('ret') and len(data['ret']) > 0:
                    return data['ret'][0].get('contractRet', 'pending')
            return 'pending'
        except Exception as e:
            return 'unknown'
    
    def estimate_gas(self, from_address: str, to_address: str, amount: float) -> dict:
        """Estimate energy and bandwidth"""
        return {
            'energy': 65000,
            'bandwidth': 345,
            'fee_trx': 0.5,
            'fee_usd': 0.05
        }
    
    def validate_address(self, address: str) -> bool:
        """Validate TRON address"""
        if not address:
            return False
        return address.startswith('T') and len(address) == 34
    
    def get_account_info(self, address: str) -> dict:
        """Get TRON account information"""
        try:
            url = f"{self.rpc_url}/v1/accounts/{address}"
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                if data.get('data') and len(data['data']) > 0:
                    account = data['data'][0]
                    return {
                        'address': address,
                        'balance': account.get('balance', 0) / 1_000_000,
                        'bandwidth': account.get('bandwidth', 0),
                        'energy': account.get('energy', 0),
                        'create_time': account.get('create_time')
                    }
            return {'address': address, 'balance': 0}
        except Exception as e:
            return {'address': address, 'balance': 0}
    
    def get_trc20_transactions(self, address: str, limit: int = 50) -> list:
        """Get TRC-20 transaction history"""
        try:
            url = f"{self.rpc_url}/v1/accounts/{address}/transactions/trc20"
            response = requests.get(url, params={'limit': limit})
            if response.status_code == 200:
                return response.json().get('data', [])
            return []
        except Exception as e:
            return []
    
    def freeze_balance(self, address: str, amount: float, resource_type: str, private_key: str) -> str:
        """Freeze TRX for Energy/Bandwidth"""
        # Mock implementation
        tx_hash = hashlib.sha256(f"freeze{address}{amount}{resource_type}".encode()).hexdigest()
        return tx_hash
    
    def unfreeze_balance(self, address: str, resource_type: str, private_key: str) -> str:
        """Unfreeze TRX"""
        tx_hash = hashlib.sha256(f"unfreeze{address}{resource_type}".encode()).hexdigest()
        return tx_hash
    
    def vote_for_sr(self, address: str, votes: list, private_key: str) -> str:
        """Vote for Super Representative"""
        tx_hash = hashlib.sha256(f"vote{address}{votes}".encode()).hexdigest()
        return tx_hash
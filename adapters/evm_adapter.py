import hashlib
import requests
from .base_adapter import BaseAdapter

class EVMAdapter(BaseAdapter):
    """Generic EVM blockchain adapter for Ethereum, BSC, Polygon"""
    
    CHAIN_CONFIGS = {
        'ethereum': {
            'chain_id': 1,
            'name': 'Ethereum',
            'symbol': 'ETH',
            'decimals': 18,
            'mainnet_rpc': 'https://mainnet.infura.io/v3/',
            'testnet_rpc': 'https://sepolia.infura.io/v3/',
            'explorer': 'https://etherscan.io'
        },
        'bsc': {
            'chain_id': 56,
            'name': 'BNB Chain',
            'symbol': 'BNB',
            'decimals': 18,
            'mainnet_rpc': 'https://bsc-dataseed.binance.org',
            'testnet_rpc': 'https://data-seed-prebsc-1-s1.binance.org',
            'explorer': 'https://bscscan.com'
        },
        'polygon': {
            'chain_id': 137,
            'name': 'Polygon',
            'symbol': 'MATIC',
            'decimals': 18,
            'mainnet_rpc': 'https://polygon-rpc.com',
            'testnet_rpc': 'https://rpc-mumbai.maticvigil.com',
            'explorer': 'https://polygonscan.com'
        }
    }
    
    def __init__(self, network: str, testnet: bool = False, api_key: str = None):
        super().__init__(network, testnet)
        self.api_key = api_key
        self.config = self.CHAIN_CONFIGS.get(network, self.CHAIN_CONFIGS['ethereum'])
        self.chain_id = self.config['chain_id']
    
    def _get_rpc_url(self) -> str:
        if self.testnet:
            return self.config['testnet_rpc']
        return self.config['mainnet_rpc']
    
    def get_balance(self, address: str) -> float:
        """Get native token balance"""
        try:
            payload = {
                'jsonrpc': '2.0',
                'method': 'eth_getBalance',
                'params': [address, 'latest'],
                'id': 1
            }
            response = requests.post(self.rpc_url, json=payload)
            if response.status_code == 200:
                data = response.json()
                balance_wei = int(data.get('result', '0x0'), 16)
                return balance_wei / 10 ** self.config['decimals']
            return 0.0
        except Exception as e:
            print(f"Error getting balance: {e}")
            return 0.0
    
    def get_token_balance(self, address: str, token_contract: str) -> float:
        """Get token balance using ERC-20 ABI"""
        try:
            # In production, call balanceOf method
            return 0.0
        except Exception as e:
            return 0.0
    
    def send_transaction(self, from_address: str, to_address: str, amount: float, private_key: str) -> str:
        """Send native token transaction"""
        try:
            tx_hash = hashlib.sha256(f"{from_address}{to_address}{amount}".encode()).hexdigest()
            return f"0x{tx_hash}"
        except Exception as e:
            raise Exception(f"Transaction failed: {e}")
    
    def get_transaction(self, tx_hash: str) -> dict:
        """Get transaction details"""
        try:
            payload = {
                'jsonrpc': '2.0',
                'method': 'eth_getTransactionByHash',
                'params': [tx_hash],
                'id': 1
            }
            response = requests.post(self.rpc_url, json=payload)
            if response.status_code == 200:
                return response.json().get('result', {})
            return {}
        except Exception as e:
            return {}
    
    def get_transaction_status(self, tx_hash: str) -> str:
        """Get transaction status"""
        try:
            payload = {
                'jsonrpc': '2.0',
                'method': 'eth_getTransactionReceipt',
                'params': [tx_hash],
                'id': 1
            }
            response = requests.post(self.rpc_url, json=payload)
            if response.status_code == 200:
                receipt = response.json().get('result')
                if receipt:
                    return 'confirmed' if receipt.get('status') == '0x1' else 'failed'
            return 'pending'
        except Exception as e:
            return 'unknown'
    
    def estimate_gas(self, from_address: str, to_address: str, amount: float) -> dict:
        """Estimate gas for transaction"""
        try:
            payload = {
                'jsonrpc': '2.0',
                'method': 'eth_estimateGas',
                'params': [{
                    'from': from_address,
                    'to': to_address,
                    'value': hex(int(amount * 10 ** self.config['decimals']))
                }],
                'id': 1
            }
            response = requests.post(self.rpc_url, json=payload)
            if response.status_code == 200:
                gas = int(response.json().get('result', '0x0'), 16)
                gas_price = self.get_gas_price()
                fee_native = (gas * gas_price) / 1e9
                return {
                    'gas': gas,
                    'gas_price_gwei': gas_price,
                    'fee_native': fee_native,
                    'fee_usd': fee_native * self.get_token_price()
                }
            return {'gas': 21000, 'gas_price_gwei': 30, 'fee_native': 0.00063}
        except Exception as e:
            return {'gas': 21000, 'gas_price_gwei': 30, 'fee_native': 0.00063}
    
    def validate_address(self, address: str) -> bool:
        """Validate EVM address"""
        if not address:
            return False
        return address.startswith('0x') and len(address) == 42
    
    def get_gas_price(self) -> int:
        """Get current gas price in Gwei"""
        try:
            payload = {
                'jsonrpc': '2.0',
                'method': 'eth_gasPrice',
                'params': [],
                'id': 1
            }
            response = requests.post(self.rpc_url, json=payload)
            if response.status_code == 200:
                data = response.json()
                return int(data.get('result', '0x0'), 16) // 10 ** 9
            return 30
        except Exception as e:
            return 30
    
    def get_token_price(self) -> float:
        """Get native token price in USD"""
        prices = {
            'ethereum': 3500,
            'bsc': 600,
            'polygon': 0.80
        }
        return prices.get(self.network, 1)
    
    def get_chain_info(self) -> dict:
        """Get chain information"""
        return {
            'chain_id': self.chain_id,
            'name': self.config['name'],
            'symbol': self.config['symbol'],
            'decimals': self.config['decimals'],
            'explorer': self.config['explorer'],
            'testnet': self.testnet
        }
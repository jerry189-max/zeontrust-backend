import requests
import json

class EVMAPI:
    """EVM blockchain API wrapper for Ethereum, BSC, Polygon"""
    
    CHAINS = {
        'ethereum': {
            'mainnet_rpc': 'https://mainnet.infura.io/v3/',
            'testnet_rpc': 'https://sepolia.infura.io/v3/',
            'explorer_api': 'https://api.etherscan.io/api',
            'chain_id': 1
        },
        'bsc': {
            'mainnet_rpc': 'https://bsc-dataseed.binance.org',
            'testnet_rpc': 'https://data-seed-prebsc-1-s1.binance.org',
            'explorer_api': 'https://api.bscscan.com/api',
            'chain_id': 56
        },
        'polygon': {
            'mainnet_rpc': 'https://polygon-rpc.com',
            'testnet_rpc': 'https://rpc-mumbai.maticvigil.com',
            'explorer_api': 'https://api.polygonscan.com/api',
            'chain_id': 137
        }
    }
    
    def __init__(self, network: str = 'ethereum', testnet: bool = False, api_key: str = None):
        self.network = network
        self.testnet = testnet
        self.api_key = api_key
        self.config = self.CHAINS.get(network, self.CHAINS['ethereum'])
        
        if testnet:
            self.rpc_url = self.config['testnet_rpc']
        else:
            self.rpc_url = self.config['mainnet_rpc']
        
        if api_key and network == 'ethereum':
            self.rpc_url += api_key
    
    def _rpc_request(self, method: str, params: list) -> dict:
        """Make JSON-RPC request"""
        payload = {
            'jsonrpc': '2.0',
            'method': method,
            'params': params,
            'id': 1
        }
        try:
            response = requests.post(self.rpc_url, json=payload)
            return response.json()
        except Exception as e:
            return {'error': str(e)}
    
    def get_balance(self, address: str) -> float:
        """Get native token balance"""
        result = self._rpc_request('eth_getBalance', [address, 'latest'])
        if 'result' in result:
            return int(result['result'], 16) / 1e18
        return 0.0
    
    def get_transaction_count(self, address: str) -> int:
        """Get nonce for address"""
        result = self._rpc_request('eth_getTransactionCount', [address, 'latest'])
        if 'result' in result:
            return int(result['result'], 16)
        return 0
    
    def get_gas_price(self) -> int:
        """Get current gas price in Wei"""
        result = self._rpc_request('eth_gasPrice', [])
        if 'result' in result:
            return int(result['result'], 16)
        return 30 * 10**9
    
    def estimate_gas(self, tx: dict) -> int:
        """Estimate gas for transaction"""
        result = self._rpc_request('eth_estimateGas', [tx])
        if 'result' in result:
            return int(result['result'], 16)
        return 21000
    
    def get_transaction(self, tx_hash: str) -> dict:
        """Get transaction by hash"""
        result = self._rpc_request('eth_getTransactionByHash', [tx_hash])
        return result.get('result', {})
    
    def get_transaction_receipt(self, tx_hash: str) -> dict:
        """Get transaction receipt"""
        result = self._rpc_request('eth_getTransactionReceipt', [tx_hash])
        return result.get('result', {})
    
    def get_block_number(self) -> int:
        """Get current block number"""
        result = self._rpc_request('eth_blockNumber', [])
        if 'result' in result:
            return int(result['result'], 16)
        return 0
    
    def get_block(self, block_num: int) -> dict:
        """Get block by number"""
        result = self._rpc_request('eth_getBlockByNumber', [hex(block_num), True])
        return result.get('result', {})
    
    def call_contract(self, contract_address: str, data: str) -> str:
        """Call contract method"""
        result = self._rpc_request('eth_call', [{'to': contract_address, 'data': data}, 'latest'])
        return result.get('result', '0x')
    
    def get_token_balance(self, contract_address: str, wallet_address: str) -> float:
        """Get ERC-20 token balance"""
        # balanceOf selector: 0x70a08231
        data = f"0x70a08231{wallet_address[2:].zfill(64)}"
        result = self.call_contract(contract_address, data)
        if result and result != '0x':
            return int(result, 16) / 1e18
        return 0.0
    
    def get_token_decimals(self, contract_address: str) -> int:
        """Get token decimals"""
        # decimals selector: 0x313ce567
        result = self.call_contract(contract_address, '0x313ce567')
        if result and result != '0x':
            return int(result, 16)
        return 18
    
    def get_token_symbol(self, contract_address: str) -> str:
        """Get token symbol"""
        # symbol selector: 0x95d89b41
        result = self.call_contract(contract_address, '0x95d89b41')
        if result and result != '0x':
            hex_str = result[2:]
            return bytes.fromhex(hex_str).decode('utf-8').strip('\x00')
        return 'TOKEN'
    
    def get_token_name(self, contract_address: str) -> str:
        """Get token name"""
        # name selector: 0x06fdde03
        result = self.call_contract(contract_address, '0x06fdde03')
        if result and result != '0x':
            hex_str = result[2:]
            return bytes.fromhex(hex_str).decode('utf-8').strip('\x00')
        return 'Token'
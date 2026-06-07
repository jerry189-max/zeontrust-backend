import re

class ChainUtils:
    """Utility functions for blockchain operations"""
    
    # Network configurations
    NETWORKS = {
        'tron': {
            'name': 'TRON',
            'symbol': 'TRX',
            'decimals': 6,
            'address_pattern': r'^T[A-Za-z0-9]{33}$',
            'explorer': 'https://tronscan.org',
            'testnet_explorer': 'https://shasta.tronscan.org'
        },
        'ethereum': {
            'name': 'Ethereum',
            'symbol': 'ETH',
            'decimals': 18,
            'address_pattern': r'^0x[a-fA-F0-9]{40}$',
            'explorer': 'https://etherscan.io',
            'testnet_explorer': 'https://sepolia.etherscan.io'
        },
        'bsc': {
            'name': 'BNB Chain',
            'symbol': 'BNB',
            'decimals': 18,
            'address_pattern': r'^0x[a-fA-F0-9]{40}$',
            'explorer': 'https://bscscan.com',
            'testnet_explorer': 'https://testnet.bscscan.com'
        },
        'polygon': {
            'name': 'Polygon',
            'symbol': 'MATIC',
            'decimals': 18,
            'address_pattern': r'^0x[a-fA-F0-9]{40}$',
            'explorer': 'https://polygonscan.com',
            'testnet_explorer': 'https://mumbai.polygonscan.com'
        },
        'bitcoin': {
            'name': 'Bitcoin',
            'symbol': 'BTC',
            'decimals': 8,
            'address_pattern': r'^[13][a-km-zA-HJ-NP-Z0-9]{25,34}$|^bc1[a-zA-HJ-NP-Z0-9]{39,59}$',
            'explorer': 'https://blockstream.info',
            'testnet_explorer': 'https://blockstream.info/testnet'
        }
    }
    
    @classmethod
    def get_network_info(cls, network: str) -> dict:
        """Get network information"""
        return cls.NETWORKS.get(network, cls.NETWORKS['tron'])
    
    @classmethod
    def get_all_networks(cls) -> list:
        """Get all supported networks"""
        return list(cls.NETWORKS.keys())
    
    @classmethod
    def get_network_symbol(cls, network: str) -> str:
        """Get network token symbol"""
        info = cls.get_network_info(network)
        return info['symbol']
    
    @classmethod
    def get_network_decimals(cls, network: str) -> int:
        """Get network token decimals"""
        info = cls.get_network_info(network)
        return info['decimals']
    
    @classmethod
    def get_explorer_url(cls, network: str, tx_hash: str = None, address: str = None, testnet: bool = False) -> str:
        """Get blockchain explorer URL"""
        info = cls.get_network_info(network)
        base_url = info['testnet_explorer'] if testnet else info['explorer']
        
        if tx_hash:
            if network == 'tron':
                return f"{base_url}/#/transaction/{tx_hash}"
            return f"{base_url}/tx/{tx_hash}"
        elif address:
            if network == 'tron':
                return f"{base_url}/#/address/{address}"
            return f"{base_url}/address/{address}"
        return base_url
    
    @classmethod
    def format_address(cls, address: str, start: int = 6, end: int = 4) -> str:
        """Format address for display"""
        if not address:
            return ''
        if len(address) <= start + end:
            return address
        return f"{address[:start]}...{address[-end:]}"
    
    @classmethod
    def format_amount(cls, amount: float, network: str, decimals: int = None) -> str:
        """Format amount with proper decimals"""
        if decimals is None:
            decimals = cls.get_network_decimals(network)
        return f"{amount:.{decimals}f}"
    
    @classmethod
    def get_network_from_address(cls, address: str) -> str:
        """Detect network from address format"""
        if not address:
            return None
        
        if address.startswith('T') and len(address) == 34:
            return 'tron'
        elif address.startswith('0x') and len(address) == 42:
            return 'ethereum'  # Could be ETH, BSC, or Polygon
        elif address.startswith('1') or address.startswith('3') or address.startswith('bc1'):
            return 'bitcoin'
        
        return None
    
    @classmethod
    def get_rpc_url(cls, network: str, testnet: bool = False, api_key: str = None) -> str:
        """Get RPC URL for network"""
        rpcs = {
            'tron': 'https://api.trongrid.io' if not testnet else 'https://api.shasta.trongrid.io',
            'ethereum': f'https://mainnet.infura.io/v3/{api_key}' if not testnet else f'https://sepolia.infura.io/v3/{api_key}',
            'bsc': 'https://bsc-dataseed.binance.org' if not testnet else 'https://data-seed-prebsc-1-s1.binance.org',
            'polygon': 'https://polygon-rpc.com' if not testnet else 'https://rpc-mumbai.maticvigil.com',
            'bitcoin': 'https://blockstream.info/api' if not testnet else 'https://blockstream.info/testnet/api'
        }
        return rpcs.get(network, rpcs['tron'])
    
    @classmethod
    def get_chain_id(cls, network: str) -> int:
        """Get chain ID for EVM networks"""
        chain_ids = {
            'ethereum': 1,
            'bsc': 56,
            'polygon': 137,
            'tron': 1,
            'bitcoin': 0
        }
        return chain_ids.get(network, 1)
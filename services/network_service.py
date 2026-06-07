class NetworkService:
    
    NETWORKS = {
        'tron': {'name': 'TRON', 'symbol': 'TRX', 'decimals': 6, 'rpc': 'https://api.trongrid.io', 'explorer': 'https://tronscan.org'},
        'ethereum': {'name': 'Ethereum', 'symbol': 'ETH', 'decimals': 18, 'rpc': 'https://mainnet.infura.io/v3/', 'explorer': 'https://etherscan.io'},
        'bsc': {'name': 'BNB Chain', 'symbol': 'BNB', 'decimals': 18, 'rpc': 'https://bsc-dataseed.binance.org', 'explorer': 'https://bscscan.com'},
        'polygon': {'name': 'Polygon', 'symbol': 'MATIC', 'decimals': 18, 'rpc': 'https://polygon-rpc.com', 'explorer': 'https://polygonscan.com'},
        'bitcoin': {'name': 'Bitcoin', 'symbol': 'BTC', 'decimals': 8, 'rpc': 'https://blockstream.info/api', 'explorer': 'https://blockstream.info'}
    }
    
    def __init__(self, network: str, testnet: bool = False):
        self.network = network
        self.testnet = testnet
        self.config = self.NETWORKS.get(network, self.NETWORKS['tron'])
    
    def get_network_info(self) -> dict:
        return {
            'network': self.network,
            'name': self.config['name'],
            'symbol': self.config['symbol'],
            'decimals': self.config['decimals'],
            'rpc_url': self.config['rpc'],
            'explorer_url': self.config['explorer'],
            'is_testnet': self.testnet
        }
    
    def get_rpc_url(self) -> str:
        if self.testnet:
            testnet_rpcs = {
                'tron': 'https://api.shasta.trongrid.io',
                'ethereum': 'https://sepolia.infura.io/v3/',
                'bsc': 'https://data-seed-prebsc-1-s1.binance.org',
                'polygon': 'https://rpc-mumbai.maticvigil.com'
            }
            return testnet_rpcs.get(self.network, self.config['rpc'])
        return self.config['rpc']
    
    @staticmethod
    def get_all_networks() -> list:
        return [{'id': k, 'name': v['name'], 'symbol': v['symbol']} for k, v in NetworkService.NETWORKS.items()]
    
    @staticmethod
    def get_network_status(network_id: str) -> dict:
        return {'status': 'healthy', 'latency': 100, 'last_block': 1000000}
    
    @staticmethod
    def switch_network(network_id: str, testnet: bool = False):
        if network_id not in NetworkService.NETWORKS:
            raise ValueError(f'Network {network_id} not supported')
        return NetworkService(network_id, testnet)
class ChainSupportService:
    
    SUPPORTED_CHAINS = {
        'tron': {'name': 'TRON', 'symbol': 'TRX', 'icon': '🌐', 'is_active': True, 'type': 'mainnet', 'block_time': 3},
        'ethereum': {'name': 'Ethereum', 'symbol': 'ETH', 'icon': '💎', 'is_active': True, 'type': 'mainnet', 'block_time': 12},
        'bsc': {'name': 'BNB Chain', 'symbol': 'BNB', 'icon': '🔶', 'is_active': True, 'type': 'mainnet', 'block_time': 3},
        'polygon': {'name': 'Polygon', 'symbol': 'MATIC', 'icon': '🟣', 'is_active': True, 'type': 'mainnet', 'block_time': 2},
        'bitcoin': {'name': 'Bitcoin', 'symbol': 'BTC', 'icon': '🟠', 'is_active': True, 'type': 'mainnet', 'block_time': 600}
    }
    
    @staticmethod
    def get_all_chains() -> list:
        return [{'id': k, **v} for k, v in ChainSupportService.SUPPORTED_CHAINS.items()]
    
    @staticmethod
    def get_active_chains() -> list:
        return [{'id': k, **v} for k, v in ChainSupportService.SUPPORTED_CHAINS.items() if v['is_active']]
    
    @staticmethod
    def switch_chain(chain_id: str, testnet: bool = False) -> dict:
        if chain_id not in ChainSupportService.SUPPORTED_CHAINS:
            raise ValueError(f'Chain {chain_id} not supported')
        
        chain_info = ChainSupportService.SUPPORTED_CHAINS[chain_id].copy()
        chain_info['is_testnet'] = testnet
        return chain_info
    
    @staticmethod
    def get_chain_status(chain_id: str) -> dict:
        return {'status': 'healthy', 'latency': 100, 'chain_id': chain_id}
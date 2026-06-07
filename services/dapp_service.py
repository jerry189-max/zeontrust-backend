from models.dapp_models import DAppFavoriteModel

class DAppService:
    
    DAPPS = {
        'tron': [
            {'name': 'SUN.io', 'url': 'https://sun.io', 'icon': '☀️', 'category': 'DeFi'},
            {'name': 'JustSwap', 'url': 'https://justswap.io', 'icon': '🔄', 'category': 'DeFi'},
            {'name': 'TronLink', 'url': 'https://tronlink.org', 'icon': '🔗', 'category': 'Wallet'}
        ],
        'ethereum': [
            {'name': 'Uniswap', 'url': 'https://app.uniswap.org', 'icon': '🦄', 'category': 'DeFi'},
            {'name': 'OpenSea', 'url': 'https://opensea.io', 'icon': '🖼️', 'category': 'NFT'},
            {'name': 'Aave', 'url': 'https://aave.com', 'icon': '💧', 'category': 'Lending'}
        ],
        'bsc': [
            {'name': 'PancakeSwap', 'url': 'https://pancakeswap.finance', 'icon': '🥞', 'category': 'DeFi'},
            {'name': 'Venus', 'url': 'https://venus.io', 'icon': '🌟', 'category': 'Lending'}
        ],
        'polygon': [
            {'name': 'QuickSwap', 'url': 'https://quickswap.exchange', 'icon': '⚡', 'category': 'DeFi'}
        ]
    }
    
    @staticmethod
    def get_dapps(network: str, category: str = 'all') -> list:
        dapps = DAppService.DAPPS.get(network, [])
        if category != 'all':
            dapps = [d for d in dapps if d['category'] == category]
        return dapps
    
    @staticmethod
    def get_dapp_categories() -> list:
        return ['DeFi', 'NFT', 'Gaming', 'Lending', 'Wallet', 'Bridge']
    
    @staticmethod
    def search_dapps(query: str, network: str = None) -> list:
        results = []
        for net, dapps in DAppService.DAPPS.items():
            if network and net != network:
                continue
            for dapp in dapps:
                if query.lower() in dapp['name'].lower() or query.lower() in dapp['url'].lower():
                    results.append(dapp)
        return results
    
    @staticmethod
    def get_favorites(user_id: int, network: str = None) -> list:
        return DAppFavoriteModel.find_by_user(user_id, network)
    
    @staticmethod
    def add_favorite(user_id: int, dapp_data: dict) -> int:
        return DAppFavoriteModel.create(user_id, dapp_data['name'], dapp_data['url'], dapp_data['network'], dapp_data.get('icon'))
    
    @staticmethod
    def remove_favorite(user_id: int, favorite_id: int) -> bool:
        return DAppFavoriteModel.delete(favorite_id, user_id)
    
    @staticmethod
    def validate_dapp_url(url: str) -> bool:
        return url.startswith('https://') or url.startswith('http://')
    
    @staticmethod
    def get_dapp_info(url: str) -> dict:
        return {'name': url.split('//')[1].split('.')[0], 'url': url, 'icon': '🌐'}
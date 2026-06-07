from models.pool_models import PoolModel

class PoolService:
    
    @staticmethod
    def create_pool(network: str, token_a_address: str, token_a_symbol: str,
                   token_b_address: str, token_b_symbol: str, reserve_a: str, 
                   reserve_b: str, fee_percent: float = 0.3, created_by: int = None) -> int:
        existing = PoolModel.find_by_tokens(network, token_a_address, token_b_address)
        if existing:
            raise ValueError('Pool already exists')
        
        total_liquidity = str((float(reserve_a) * float(reserve_b)) ** 0.5)
        return PoolModel.create(network, token_a_address, token_a_symbol, token_b_address, 
                               token_b_symbol, reserve_a, reserve_b, total_liquidity, fee_percent, created_by)
    
    @staticmethod
    def get_pool(pool_id: int) -> dict:
        return PoolModel.find_by_id(pool_id)
    
    @staticmethod
    def get_all_pools(network: str = None) -> list:
        return PoolModel.get_all_pools(network)
    
    @staticmethod
    def get_pool_by_tokens(network: str, token_a: str, token_b: str) -> dict:
        return PoolModel.find_by_tokens(network, token_a, token_b)
    
    @staticmethod
    def update_pool_status(pool_id: int, is_active: bool) -> bool:
        return PoolModel.update_pool_status(pool_id, is_active)
    
    @staticmethod
    def get_pool_stats(pool_id: int) -> dict:
        pool = PoolModel.find_by_id(pool_id)
        if not pool:
            return None
        
        reserve_a = float(pool['reserve_a'])
        reserve_b = float(pool['reserve_b'])
        total_liquidity = float(pool['total_liquidity'])
        
        return {
            'reserve_a': reserve_a,
            'reserve_b': reserve_b,
            'total_liquidity': total_liquidity,
            'price_a': reserve_b / reserve_a if reserve_a > 0 else 0,
            'price_b': reserve_a / reserve_b if reserve_b > 0 else 0,
            'fee_percent': pool['fee_percent']
        }
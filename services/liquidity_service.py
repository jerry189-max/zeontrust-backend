from models.pool_models import PoolModel, LiquidityPositionModel
from models.wallet_models import WalletModel

class LiquidityService:
    
    @staticmethod
    def add_liquidity(user_id: int, wallet_id: int, pool_id: int, amount_a: float, amount_b: float) -> dict:
        wallet = WalletModel.find_by_id(wallet_id)
        if not wallet or wallet['user_id'] != user_id:
            raise ValueError('Wallet not found')
        
        pool = PoolModel.find_by_id(pool_id)
        if not pool:
            raise ValueError('Pool not found')
        
        reserve_a = float(pool['reserve_a'])
        reserve_b = float(pool['reserve_b'])
        total_liquidity = float(pool['total_liquidity'])
        
        if total_liquidity == 0:
            lp_tokens = (amount_a * amount_b) ** 0.5
        else:
            lp_tokens = min(
                (amount_a / reserve_a) * total_liquidity,
                (amount_b / reserve_b) * total_liquidity
            )
        
        new_reserve_a = reserve_a + amount_a
        new_reserve_b = reserve_b + amount_b
        new_total_liquidity = total_liquidity + lp_tokens
        
        PoolModel.update_reserves(pool_id, str(new_reserve_a), str(new_reserve_b), str(new_total_liquidity))
        
        position_id = LiquidityPositionModel.create(pool_id, user_id, wallet_id, str(lp_tokens), str(amount_a), str(amount_b))
        
        return {
            'position_id': position_id,
            'lp_tokens': lp_tokens,
            'share': (lp_tokens / new_total_liquidity) * 100 if new_total_liquidity > 0 else 100
        }
    
    @staticmethod
    def remove_liquidity(user_id: int, position_id: int) -> dict:
        position = LiquidityPositionModel.find_by_id(position_id)
        if not position or position['user_id'] != user_id:
            raise ValueError('Position not found')
        
        pool = PoolModel.find_by_id(position['pool_id'])
        if not pool:
            raise ValueError('Pool not found')
        
        lp_tokens = float(position['lp_token_amount'])
        total_liquidity = float(pool['total_liquidity'])
        share = lp_tokens / total_liquidity
        
        amount_a = float(pool['reserve_a']) * share
        amount_b = float(pool['reserve_b']) * share
        
        new_reserve_a = float(pool['reserve_a']) - amount_a
        new_reserve_b = float(pool['reserve_b']) - amount_b
        new_total_liquidity = total_liquidity - lp_tokens
        
        PoolModel.update_reserves(pool['id'], str(new_reserve_a), str(new_reserve_b), str(new_total_liquidity))
        LiquidityPositionModel.delete_position(position_id, user_id)
        
        return {
            'amount_a': amount_a,
            'amount_b': amount_b,
            'lp_tokens_burned': lp_tokens
        }
    
    @staticmethod
    def get_user_positions(user_id: int) -> list:
        return LiquidityPositionModel.find_by_user(user_id)
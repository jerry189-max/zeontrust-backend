from models.pool_models import PoolModel, SwapModel
from models.wallet_models import WalletModel

class SwapService:
    
    @staticmethod
    def get_quote(network: str, from_token: str, to_token: str, amount: float) -> dict:
        pool = PoolModel.find_by_tokens(network, from_token, to_token)
        if not pool:
            raise ValueError('Pool not found')
        
        reserve_a = float(pool['reserve_a'])
        reserve_b = float(pool['reserve_b'])
        
        if pool['token_a_address'] == from_token:
            amount_out = (amount * reserve_b) / (reserve_a + amount)
        else:
            amount_out = (amount * reserve_a) / (reserve_b + amount)
        
        fee = amount_out * (pool['fee_percent'] / 100)
        amount_out -= fee
        
        return {
            'from_amount': amount,
            'to_amount': amount_out,
            'fee': fee,
            'fee_percent': pool['fee_percent'],
            'price': amount_out / amount if amount > 0 else 0,
            'slippage': 0.5,
            'provider': 'ZeontrustSwap'
        }
    
    @staticmethod
    def execute_swap(user_id: int, wallet_id: int, network: str, from_token: str, 
                     to_token: str, amount: float, slippage: float = 0.5) -> dict:
        wallet = WalletModel.find_by_id(wallet_id)
        if not wallet or wallet['user_id'] != user_id:
            raise ValueError('Wallet not found')
        
        quote = SwapService.get_quote(network, from_token, to_token, amount)
        
        pool = PoolModel.find_by_tokens(network, from_token, to_token)
        if not pool:
            raise ValueError('Pool not found')
        
        reserve_a = float(pool['reserve_a'])
        reserve_b = float(pool['reserve_b'])
        to_amount = quote['to_amount']
        
        if pool['token_a_address'] == from_token:
            new_reserve_a = reserve_a + amount
            new_reserve_b = reserve_b - to_amount
        else:
            new_reserve_a = reserve_a - to_amount
            new_reserve_b = reserve_b + amount
        
        PoolModel.update_reserves(pool['id'], str(new_reserve_a), str(new_reserve_b), pool['total_liquidity'])
        
        swap_id = SwapModel.create(user_id, wallet_id, pool['id'], from_token, to_token, str(amount), str(to_amount), str(quote['fee']))
        
        return {
            'swap_id': swap_id,
            'from_amount': amount,
            'to_amount': to_amount,
            'fee': quote['fee'],
            'price': quote['price']
        }
    
    @staticmethod
    def get_swap_history(user_id: int) -> list:
        return SwapModel.find_by_user(user_id)
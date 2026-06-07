from models.reserve_models import ReserveTokenModel, ReserveTransactionModel

class ReserveService:
    
    @staticmethod
    def create_reserve_token(network: str, contract_address: str, token_name: str, 
                            token_symbol: str, decimals: int, total_supply: str, 
                            is_mintable: bool = True, is_burnable: bool = True, created_by: int = None) -> int:
        return ReserveTokenModel.create(network, contract_address, token_name, token_symbol, 
                                       decimals, total_supply, total_supply, is_mintable, is_burnable, created_by)
    
    @staticmethod
    def mint_tokens(token_id: int, amount: str, admin_id: int) -> dict:
        token = ReserveTokenModel.find_by_id(token_id)
        if not token:
            raise ValueError('Token not found')
        if not token['is_mintable']:
            raise ValueError('Token is not mintable')
        
        ReserveTokenModel.mint_tokens(token_id, amount)
        ReserveTransactionModel.create(token_id, 'mint', amount, None, None)
        
        return {'token_id': token_id, 'amount': amount, 'action': 'mint'}
    
    @staticmethod
    def burn_tokens(token_id: int, amount: str, admin_id: int) -> dict:
        token = ReserveTokenModel.find_by_id(token_id)
        if not token:
            raise ValueError('Token not found')
        if not token['is_burnable']:
            raise ValueError('Token is not burnable')
        
        ReserveTokenModel.burn_tokens(token_id, amount)
        ReserveTransactionModel.create(token_id, 'burn', amount, None, None)
        
        return {'token_id': token_id, 'amount': amount, 'action': 'burn'}
    
    @staticmethod
    def transfer_tokens(token_id: int, amount: str, to_address: str, admin_id: int) -> dict:
        ReserveTokenModel.transfer_tokens(token_id, amount, to_address)
        ReserveTransactionModel.create(token_id, 'transfer', amount, None, to_address)
        
        return {'token_id': token_id, 'amount': amount, 'to_address': to_address, 'action': 'transfer'}
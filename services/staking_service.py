from models.staking_models import StakingPositionModel
from models.wallet_models import WalletModel

class StakingService:
    
    APY = 4.5
    
    @staticmethod
    def stake_trx(user_id: int, wallet_id: int, amount: float, resource_type: str = 'ENERGY', duration_days: int = 90) -> dict:
        wallet = WalletModel.find_by_id(wallet_id)
        if not wallet or wallet['user_id'] != user_id:
            raise ValueError('Wallet not found')
        
        position_id = StakingPositionModel.create(user_id, wallet_id, 'tron', str(amount), resource_type, duration_days)
        
        resources_received = amount * 100000 if resource_type == 'ENERGY' else amount * 4000
        
        return {
            'position_id': position_id,
            'amount': amount,
            'resource_type': resource_type,
            'resources_received': resources_received,
            'duration_days': duration_days,
            'apy': StakingService.APY
        }
    
    @staticmethod
    def unstake_trx(user_id: int, position_id: int) -> dict:
        position = StakingPositionModel.find_by_id(position_id)
        if not position or position['user_id'] != user_id:
            raise ValueError('Position not found')
        
        StakingPositionModel.unstake_position(position_id)
        
        return {
            'position_id': position_id,
            'amount': position['amount'],
            'unlock_days': 14,
            'message': 'Unstaking initiated. TRX will be available in 14 days.'
        }
    
    @staticmethod
    def get_staking_info(user_id: int) -> dict:
        positions = StakingPositionModel.find_by_user(user_id)
        total_staked = sum(float(p['amount']) for p in positions if p['status'] == 'active')
        
        return {
            'positions': positions,
            'total_staked': total_staked,
            'apy': StakingService.APY,
            'estimated_yearly_reward': total_staked * (StakingService.APY / 100),
            'estimated_monthly_reward': total_staked * (StakingService.APY / 100) / 12
        }
    
    @staticmethod
    def calculate_rewards(user_id: int) -> dict:
        total_staked = StakingPositionModel.get_total_staked(user_id)
        daily_reward = total_staked * (StakingService.APY / 100) / 365
        monthly_reward = daily_reward * 30
        yearly_reward = total_staked * (StakingService.APY / 100)
        
        return {
            'daily': daily_reward,
            'monthly': monthly_reward,
            'yearly': yearly_reward,
            'total_staked': total_staked,
            'apy': StakingService.APY
        }
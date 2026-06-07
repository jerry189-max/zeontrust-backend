import math
from datetime import datetime, timedelta

class RewardsCalculator:
    """Rewards calculation utility for staking and farming"""
    
    @staticmethod
    def calculate_staking_rewards(amount: float, apr: float, duration_days: int) -> dict:
        """Calculate staking rewards"""
        yearly_reward = amount * (apr / 100)
        daily_reward = yearly_reward / 365
        total_reward = daily_reward * duration_days
        
        return {
            'amount': amount,
            'apr': apr,
            'duration_days': duration_days,
            'daily_reward': daily_reward,
            'total_reward': total_reward,
            'total_return': amount + total_reward
        }
    
    @staticmethod
    def calculate_compound_rewards(amount: float, apr: float, duration_days: int, compound_frequency: str = 'daily') -> dict:
        """Calculate compounded staking rewards"""
        # Convert to years
        years = duration_days / 365
        
        if compound_frequency == 'daily':
            periods = 365
        elif compound_frequency == 'weekly':
            periods = 52
        elif compound_frequency == 'monthly':
            periods = 12
        else:
            periods = 1
        
        rate = apr / 100 / periods
        total = amount * (1 + rate) ** (periods * years)
        total_reward = total - amount
        
        return {
            'initial_amount': amount,
            'apr': apr,
            'duration_days': duration_days,
            'compound_frequency': compound_frequency,
            'final_amount': total,
            'total_reward': total_reward,
            'effective_apy': ((1 + rate) ** periods - 1) * 100
        }
    
    @staticmethod
    def calculate_lp_rewards(lp_amount: float, pool_tvl: float, pool_volume: float, apr: float) -> dict:
        """Calculate LP rewards"""
        share = lp_amount / pool_tvl if pool_tvl > 0 else 0
        estimated_reward = share * pool_volume * (apr / 100)
        
        return {
            'lp_amount': lp_amount,
            'pool_share': share * 100,
            'estimated_daily_reward': estimated_reward / 365,
            'estimated_monthly_reward': estimated_reward / 12,
            'estimated_yearly_reward': estimated_reward
        }
    
    @staticmethod
    def calculate_vote_rewards(vote_count: float, total_votes: float, reward_pool: float) -> dict:
        """Calculate voting rewards"""
        share = vote_count / total_votes if total_votes > 0 else 0
        estimated_reward = reward_pool * share
        
        return {
            'vote_count': vote_count,
            'share_percent': share * 100,
            'estimated_reward': estimated_reward
        }
    
    @staticmethod
    def calculate_apy_from_rewards(amount: float, reward_amount: float, duration_days: int) -> float:
        """Calculate APY from rewards received"""
        if amount <= 0 or duration_days <= 0:
            return 0
        
        years = duration_days / 365
        total_return = amount + reward_amount
        apy = ((total_return / amount) ** (1 / years) - 1) * 100
        
        return apy
    
    @staticmethod
    def get_reward_schedule(amount: float, apr: float, days: int) -> list:
        """Generate daily reward schedule"""
        schedule = []
        daily_reward = (amount * (apr / 100)) / 365
        
        for i in range(days):
            date = (datetime.now() + timedelta(days=i + 1)).strftime('%Y-%m-%d')
            schedule.append({
                'day': i + 1,
                'date': date,
                'reward': daily_reward,
                'cumulative_reward': daily_reward * (i + 1)
            })
        
        return schedule
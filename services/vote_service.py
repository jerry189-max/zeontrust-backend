class VoteService:
    
    SUPER_REPRESENTATIVES = [
        {'address': 'TXXXXXXXXXX1', 'name': 'Binance Staking', 'votes': 125000000, 'url': 'https://binance.com'},
        {'address': 'TXXXXXXXXXX2', 'name': 'TronLink', 'votes': 98000000, 'url': 'https://tronlink.org'},
        {'address': 'TXXXXXXXXXX3', 'name': 'JustSwap', 'votes': 76000000, 'url': 'https://justswap.io'},
        {'address': 'TXXXXXXXXXX4', 'name': 'Poloniex', 'votes': 54000000, 'url': 'https://poloniex.com'},
        {'address': 'TXXXXXXXXXX5', 'name': 'SUN.io', 'votes': 43000000, 'url': 'https://sun.io'}
    ]
    
    @staticmethod
    def get_all_super_representatives(limit: int = 50):
        return VoteService.SUPER_REPRESENTATIVES[:limit]
    
    @staticmethod
    def get_sr_details(sr_address: str):
        for sr in VoteService.SUPER_REPRESENTATIVES:
            if sr['address'] == sr_address:
                return sr
        return None
    
    @staticmethod
    def cast_votes(voter_address: str, votes: list) -> dict:
        total_votes = sum(v['votes'] for v in votes)
        return {
            'success': True,
            'voter': voter_address,
            'votes': votes,
            'total_votes': total_votes,
            'tx_hash': f'0x{hash(str(votes)):x}'
        }
    
    @staticmethod
    def get_my_votes(voter_address: str) -> list:
        return [
            {'sr_address': 'TXXXXXXXXXX1', 'sr_name': 'Binance Staking', 'vote_count': 5000},
            {'sr_address': 'TXXXXXXXXXX2', 'sr_name': 'TronLink', 'vote_count': 3000}
        ]
    
    @staticmethod
    def get_voting_power(address: str) -> float:
        return 10000
    
    @staticmethod
    def search_sr(query: str) -> list:
        query_lower = query.lower()
        return [sr for sr in VoteService.SUPER_REPRESENTATIVES 
                if query_lower in sr['name'].lower() or query_lower in sr['address'].lower()]
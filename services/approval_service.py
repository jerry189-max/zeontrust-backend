class ApprovalService:
    
    @staticmethod
    def get_approvals(address: str, network: str) -> list:
        return [
            {'spender': '0x1234...', 'token': 'USDT', 'amount': '1000', 'network': network},
            {'spender': '0x5678...', 'token': 'USDC', 'amount': '500', 'network': network}
        ]
    
    @staticmethod
    def revoke_approval(address: str, spender: str, token: str, network: str) -> dict:
        return {'success': True, 'spender': spender, 'token': token, 'message': 'Approval revoked'}
    
    @staticmethod
    def revoke_all_approvals(address: str, network: str) -> dict:
        return {'success': True, 'message': 'All approvals revoked'}
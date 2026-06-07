from models.loan_models import LoanModel
from models.wallet_models import WalletModel

class LoanService:
    
    DEFAULT_INTEREST_RATE = 5.0
    
    @staticmethod
    def request_loan(user_id: int, wallet_id: int, network: str, token: str, 
                    amount: float, duration_days: int, purpose: str = None) -> dict:
        wallet = WalletModel.find_by_id(wallet_id)
        if not wallet or wallet['user_id'] != user_id:
            raise ValueError('Wallet not found')
        
        loan_id = LoanModel.create(user_id, wallet_id, network, token, str(amount), duration_days, purpose)
        
        return {'loan_id': loan_id, 'amount': amount, 'duration_days': duration_days, 'status': 'pending'}
    
    @staticmethod
    def approve_loan(loan_id: int, admin_id: int, interest_rate: float = None) -> dict:
        loan = LoanModel.find_by_id(loan_id)
        if not loan:
            raise ValueError('Loan not found')
        
        LoanModel.approve_loan(loan_id, admin_id)
        
        return {'loan_id': loan_id, 'status': 'approved', 'interest_rate': interest_rate or LoanService.DEFAULT_INTEREST_RATE}
    
    @staticmethod
    def reject_loan(loan_id: int, admin_id: int) -> dict:
        LoanModel.reject_loan(loan_id, admin_id)
        return {'loan_id': loan_id, 'status': 'rejected'}
    
    @staticmethod
    def repay_loan(loan_id: int, amount: float) -> dict:
        LoanModel.mark_repaid(loan_id, str(amount))
        return {'loan_id': loan_id, 'status': 'repaid', 'amount': amount}
    
    @staticmethod
    def get_loan_statistics() -> dict:
        return LoanModel.get_loan_statistics()
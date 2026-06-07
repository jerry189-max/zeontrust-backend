import uuid
from models.multisig_models import MultiSigWalletModel, ProposalModel

class MultiSigService:
    
    @staticmethod
    def create_wallet(user_id: int, owners: list, threshold: int, name: str, network: str = 'tron') -> dict:
        if len(owners) < 2:
            raise ValueError('At least 2 owners required')
        if threshold < 2 or threshold > len(owners):
            raise ValueError(f'Threshold must be between 2 and {len(owners)}')
        
        wallet_id = str(uuid.uuid4())
        address = f'MS{wallet_id[:10]}'
        
        MultiSigWalletModel.create(wallet_id, name, owners, threshold, network, address, user_id)
        
        return {'id': wallet_id, 'name': name, 'owners': owners, 'threshold': threshold, 'address': address}
    
    @staticmethod
    def get_wallet(wallet_id: str) -> dict:
        return MultiSigWalletModel.find_by_id(wallet_id)
    
    @staticmethod
    def get_user_wallets(user_id: int) -> list:
        return MultiSigWalletModel.find_by_user(user_id)
    
    @staticmethod
    def validate_owner(wallet_id: str, owner_address: str) -> bool:
        wallet = MultiSigWalletModel.find_by_id(wallet_id)
        if not wallet:
            return False
        return owner_address in wallet['owners']
    
    @staticmethod
    def create_proposal(wallet_id: str, creator: str, to_address: str, amount: float, 
                       token_address: str = None, description: str = None) -> dict:
        wallet = MultiSigWalletModel.find_by_id(wallet_id)
        if not wallet:
            raise ValueError('Multisig wallet not found')
        
        proposal_id = str(uuid.uuid4())
        ProposalModel.create(proposal_id, wallet_id, creator, to_address, str(amount), description, token_address, wallet['threshold'])
        
        return {'id': proposal_id, 'to_address': to_address, 'amount': amount, 'description': description}
    
    @staticmethod
    def sign_proposal(proposal_id: str, signer: str) -> dict:
        proposal = ProposalModel.find_by_id(proposal_id)
        if not proposal:
            raise ValueError('Proposal not found')
        
        ProposalModel.add_signature(proposal_id, signer)
        
        return {'proposal_id': proposal_id, 'signer': signer, 'signature_count': len(proposal['signatures']) + 1}
    
    @staticmethod
    def execute_proposal(proposal_id: str, executor: str) -> dict:
        proposal = ProposalModel.find_by_id(proposal_id)
        if not proposal:
            raise ValueError('Proposal not found')
        
        if len(proposal['signatures']) < proposal['required_signatures']:
            raise ValueError('Not enough signatures')
        
        ProposalModel.execute_proposal(proposal_id)
        
        return {'proposal_id': proposal_id, 'status': 'executed'}
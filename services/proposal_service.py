import uuid
from models.multisig_models import ProposalModel

class ProposalService:
    
    @staticmethod
    def create_proposal(multisig_id: str, creator: str, to_address: str, amount: float,
                       token_address: str = None, required_signatures: int = 2, description: str = None) -> dict:
        proposal_id = str(uuid.uuid4())
        ProposalModel.create(proposal_id, multisig_id, creator, to_address, str(amount), description, token_address, required_signatures)
        
        return {
            'id': proposal_id,
            'multisig_id': multisig_id,
            'creator': creator,
            'to_address': to_address,
            'amount': amount,
            'description': description,
            'status': 'pending',
            'signatures': []
        }
    
    @staticmethod
    def get_proposal(proposal_id: str) -> dict:
        return ProposalModel.find_by_id(proposal_id)
    
    @staticmethod
    def get_multisig_proposals(multisig_id: str, status: str = None) -> list:
        return ProposalModel.find_by_multisig(multisig_id, status)
    
    @staticmethod
    def get_my_pending_proposals(owner_address: str) -> list:
        proposals = []
        # Implementation to get proposals pending for owner
        return proposals
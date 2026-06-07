from models.multisig_models import ProposalModel

class SignatureService:
    
    @staticmethod
    def sign_proposal(proposal_id: str, signer: str) -> dict:
        proposal = ProposalModel.find_by_id(proposal_id)
        if not proposal:
            raise ValueError('Proposal not found')
        
        if signer in proposal['signatures']:
            raise ValueError('Already signed')
        
        ProposalModel.add_signature(proposal_id, signer)
        
        return {'proposal_id': proposal_id, 'signer': signer, 'signature_count': len(proposal['signatures']) + 1}
    
    @staticmethod
    def unsign_proposal(proposal_id: str, signer: str) -> dict:
        # Implementation to remove signature
        return {'proposal_id': proposal_id, 'signer': signer, 'removed': True}
    
    @staticmethod
    def execute_proposal(proposal_id: str, executor: str) -> dict:
        proposal = ProposalModel.find_by_id(proposal_id)
        if not proposal:
            raise ValueError('Proposal not found')
        
        if len(proposal['signatures']) < proposal['required_signatures']:
            raise ValueError('Not enough signatures')
        
        ProposalModel.execute_proposal(proposal_id)
        
        return {'proposal_id': proposal_id, 'status': 'executed'}
    
    @staticmethod
    def cancel_proposal(proposal_id: str, canceller: str) -> dict:
        ProposalModel.cancel_proposal(proposal_id)
        return {'proposal_id': proposal_id, 'status': 'cancelled'}
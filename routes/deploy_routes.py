from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.user_models import UserModel
from models.token_models import VerifiedTokenModel
import hashlib
import time

def register_deploy_routes(app):
    
    @app.route('/api/deploy/token', methods=['POST'])
    @jwt_required()
    def deploy_token():
        try:
            admin_id = get_jwt_identity()
            admin = UserModel.find_by_id(admin_id)
            if not admin or not admin['is_admin']:
                return jsonify({'error': 'Admin access required'}), 403
            
            data = request.get_json()
            network = data.get('network', 'tron')
            name = data.get('name')
            symbol = data.get('symbol')
            total_supply = data.get('total_supply')
            decimals = data.get('decimals', 18)
            owner = data.get('owner')
            
            # Generate mock contract address
            if network == 'tron':
                contract_address = 'T' + hashlib.sha256(f"{name}{symbol}{time.time()}".encode()).hexdigest()[:33]
            else:
                contract_address = '0x' + hashlib.sha256(f"{name}{symbol}{time.time()}".encode()).hexdigest()[:40]
            
            # Add to verified tokens
            VerifiedTokenModel.create_verified_token(network, contract_address, name, symbol, decimals)
            
            return jsonify({
                'success': True,
                'contract_address': contract_address,
                'tx_hash': '0x' + hashlib.sha256(f"{contract_address}{time.time()}".encode()).hexdigest(),
                'network': network,
                'name': name,
                'symbol': symbol,
                'total_supply': total_supply,
                'decimals': decimals
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/deploy/contracts', methods=['GET'])
    @jwt_required()
    def get_available_contracts():
        contracts = [
            {'name': 'ERC20 Token', 'type': 'standard', 'description': 'Standard ERC20 token'},
            {'name': 'Mintable Token', 'type': 'mintable', 'description': 'Token with minting capability'},
            {'name': 'Burnable Token', 'type': 'burnable', 'description': 'Token with burning capability'},
            {'name': 'Tax Token', 'type': 'tax', 'description': 'Token with buy/sell tax'},
            {'name': 'TRC20 Token', 'type': 'trc20', 'description': 'TRON TRC20 token'}
        ]
        return jsonify({'success': True, 'contracts': contracts})
    
    return app
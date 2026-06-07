from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.wallet_models import WalletModel

def register_vote_routes(app):
    
    @app.route('/api/vote/srs', methods=['GET'])
    @jwt_required()
    def get_super_representatives():
        try:
            # Mock Super Representatives data
            srs = [
                {'address': 'Txxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx', 'name': 'Binance Staking', 'votes': 125000000, 'url': 'https://binance.com'},
                {'address': 'Tyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy', 'name': 'TronLink', 'votes': 98000000, 'url': 'https://tronlink.org'},
                {'address': 'Tzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz', 'name': 'JustSwap', 'votes': 76000000, 'url': 'https://justswap.io'},
                {'address': 'Taaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa', 'name': 'Poloniex', 'votes': 54000000, 'url': 'https://poloniex.com'},
                {'address': 'Tbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb', 'name': 'SUN.io', 'votes': 43000000, 'url': 'https://sun.io'}
            ]
            return jsonify({'success': True, 'super_representatives': srs})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/vote/cast', methods=['POST'])
    @jwt_required()
    def cast_votes():
        try:
            user_id = get_jwt_identity()
            data = request.get_json()
            wallet_id = data.get('wallet_id')
            votes = data.get('votes')  # list of {sr_address, votes}
            
            wallet = WalletModel.find_by_id(wallet_id)
            if not wallet or wallet['user_id'] != user_id:
                return jsonify({'error': 'Wallet not found'}), 404
            
            total_votes = sum(v['votes'] for v in votes)
            
            return jsonify({'success': True, 'message': f'Successfully cast {total_votes} votes', 'votes': votes})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/vote/my-votes', methods=['GET'])
    @jwt_required()
    def get_my_votes():
        try:
            user_id = get_jwt_identity()
            # Mock user votes
            votes = [
                {'sr_address': 'Txxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx', 'sr_name': 'Binance Staking', 'vote_count': 5000},
                {'sr_address': 'Tyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy', 'sr_name': 'TronLink', 'vote_count': 3000}
            ]
            return jsonify({'success': True, 'votes': votes, 'total_votes': 8000})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/vote/power', methods=['GET'])
    @jwt_required()
    def get_voting_power():
        try:
            user_id = get_jwt_identity()
            wallet_id = request.args.get('wallet_id')
            # Mock voting power based on TRX balance
            voting_power = 10000  # 1 TRX = 1 vote approx
            return jsonify({'success': True, 'voting_power': voting_power})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    return app
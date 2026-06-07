from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.staking_models import StakingPositionModel
from models.wallet_models import WalletModel
from datetime import datetime

def register_staking_routes(app):
    
    @app.route('/api/staking/info', methods=['GET'])
    @jwt_required()
    def get_staking_info():
        try:
            user_id = get_jwt_identity()
            wallet_id = request.args.get('wallet_id')
            
            positions = StakingPositionModel.find_by_wallet(wallet_id)
            total_staked = StakingPositionModel.get_total_staked(user_id)
            apy = StakingPositionModel.get_staking_apy()
            
            return jsonify({
                'success': True,
                'staking_info': {
                    'positions': positions,
                    'total_staked': total_staked,
                    'apy': apy,
                    'estimated_rewards': total_staked * (apy / 100)
                }
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/staking/stake', methods=['POST'])
    @jwt_required()
    def stake_trx():
        try:
            user_id = get_jwt_identity()
            data = request.get_json()
            wallet_id = data.get('wallet_id')
            amount = data.get('amount')
            resource_type = data.get('resource_type', 'ENERGY')
            duration_days = data.get('duration_days', 90)
            
            wallet = WalletModel.find_by_id(wallet_id)
            if not wallet or wallet['user_id'] != user_id:
                return jsonify({'error': 'Wallet not found'}), 404
            
            position_id = StakingPositionModel.create(user_id, wallet_id, 'tron', str(amount), resource_type, duration_days)
            
            return jsonify({'success': True, 'position_id': position_id, 'message': f'Staked {amount} TRX for {resource_type}'})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/staking/unstake', methods=['POST'])
    @jwt_required()
    def unstake_trx():
        try:
            user_id = get_jwt_identity()
            data = request.get_json()
            position_id = data.get('position_id')
            
            position = StakingPositionModel.find_by_id(position_id)
            if not position or position['user_id'] != user_id:
                return jsonify({'error': 'Position not found'}), 404
            
            StakingPositionModel.unstake_position(position_id)
            
            return jsonify({'success': True, 'message': 'Unstaking initiated. TRX will be available in 14 days.'})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/staking/rewards', methods=['GET'])
    @jwt_required()
    def get_rewards():
        try:
            user_id = get_jwt_identity()
            total_staked = StakingPositionModel.get_total_staked(user_id)
            apy = StakingPositionModel.get_staking_apy()
            
            daily_reward = total_staked * (apy / 100) / 365
            monthly_reward = daily_reward * 30
            yearly_reward = total_staked * (apy / 100)
            
            return jsonify({
                'success': True,
                'rewards': {
                    'daily': daily_reward,
                    'monthly': monthly_reward,
                    'yearly': yearly_reward,
                    'total_staked': total_staked,
                    'apy': apy
                }
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    return app
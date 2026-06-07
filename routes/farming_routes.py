from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.user_models import UserModel
import sqlite3
import os
from datetime import datetime, timedelta

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'database', 'Zeontrust_wallet.db')

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def register_farming_routes(app):
    
    # ==================== GET ALL FARMS ====================
    
    @app.route('/api/farming/farms', methods=['GET'])
    @jwt_required()
    def get_farms():
        try:
            # Mock farms data
            farms = [
                {
                    'id': 1,
                    'name': 'TRX-USDT LP Farm',
                    'pool_address': '0x111...',
                    'lp_token': 'TRX-USDT LP',
                    'reward_token': 'Zeontrust',
                    'apr': 45.5,
                    'tvl': 250000,
                    'total_staked': 150000,
                    'daily_reward': 300,
                    'multiplier': 1,
                    'is_active': True,
                    'created_at': '2024-01-01'
                },
                {
                    'id': 2,
                    'name': 'ETH-USDT LP Farm',
                    'pool_address': '0x222...',
                    'lp_token': 'ETH-USDT LP',
                    'reward_token': 'Zeontrust',
                    'apr': 35.2,
                    'tvl': 180000,
                    'total_staked': 120000,
                    'daily_reward': 200,
                    'multiplier': 1,
                    'is_active': True,
                    'created_at': '2024-01-01'
                },
                {
                    'id': 3,
                    'name': 'BNB-USDT LP Farm',
                    'pool_address': '0x333...',
                    'lp_token': 'BNB-USDT LP',
                    'reward_token': 'Zeontrust',
                    'apr': 28.7,
                    'tvl': 120000,
                    'total_staked': 80000,
                    'daily_reward': 150,
                    'multiplier': 1,
                    'is_active': True,
                    'created_at': '2024-01-01'
                },
                {
                    'id': 4,
                    'name': 'Zeontrust Single Stake',
                    'pool_address': '0x444...',
                    'lp_token': 'Zeontrust',
                    'reward_token': 'Zeontrust',
                    'apr': 12.5,
                    'tvl': 500000,
                    'total_staked': 350000,
                    'daily_reward': 500,
                    'multiplier': 2,
                    'is_active': True,
                    'created_at': '2024-01-01'
                }
            ]
            
            return jsonify({'success': True, 'farms': farms})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    # ==================== STAKE IN FARM ====================
    
    @app.route('/api/farming/stake', methods=['POST'])
    @jwt_required()
    def stake_in_farm():
        try:
            user_id = get_jwt_identity()
            data = request.get_json()
            
            farm_id = data.get('farm_id')
            amount = data.get('amount')
            wallet_id = data.get('wallet_id')
            
            if not all([farm_id, amount, wallet_id]):
                return jsonify({'error': 'Missing required fields'}), 400
            
            # Create staking position
            conn = get_db()
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS farming_positions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    wallet_id INTEGER NOT NULL,
                    farm_id INTEGER NOT NULL,
                    amount TEXT NOT NULL,
                    reward_earned TEXT DEFAULT '0',
                    status TEXT DEFAULT 'active',
                    staked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_reward_calc TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            cursor.execute('''
                INSERT INTO farming_positions (user_id, wallet_id, farm_id, amount)
                VALUES (?, ?, ?, ?)
            ''', (user_id, wallet_id, farm_id, amount))
            
            position_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            return jsonify({
                'success': True,
                'position_id': position_id,
                'message': f'Staked {amount} LP tokens in farm'
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    # ==================== UNSTAKE FROM FARM ====================
    
    @app.route('/api/farming/unstake', methods=['POST'])
    @jwt_required()
    def unstake_from_farm():
        try:
            user_id = get_jwt_identity()
            data = request.get_json()
            
            position_id = data.get('position_id')
            amount = data.get('amount')
            
            if not position_id:
                return jsonify({'error': 'Position ID required'}), 400
            
            conn = get_db()
            cursor = conn.cursor()
            
            # Get position
            cursor.execute('SELECT * FROM farming_positions WHERE id = ? AND user_id = ?', (position_id, user_id))
            position = cursor.fetchone()
            
            if not position:
                return jsonify({'error': 'Position not found'}), 404
            
            # Calculate pending rewards
            pending_rewards = calculate_pending_rewards(position_id, position['farm_id'], position['amount'])
            
            # Update or delete position
            if amount == 'all' or float(amount) >= float(position['amount']):
                cursor.execute('UPDATE farming_positions SET status = "unstaked", amount = 0 WHERE id = ?', (position_id,))
            else:
                new_amount = float(position['amount']) - float(amount)
                cursor.execute('UPDATE farming_positions SET amount = ? WHERE id = ?', (new_amount, position_id))
            
            conn.commit()
            conn.close()
            
            return jsonify({
                'success': True,
                'unstaked_amount': amount,
                'pending_rewards': pending_rewards,
                'message': 'Unstaked successfully'
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    # ==================== HARVEST REWARDS ====================
    
    @app.route('/api/farming/harvest', methods=['POST'])
    @jwt_required()
    def harvest_rewards():
        try:
            user_id = get_jwt_identity()
            data = request.get_json()
            
            position_id = data.get('position_id')
            
            if not position_id:
                return jsonify({'error': 'Position ID required'}), 400
            
            conn = get_db()
            cursor = conn.cursor()
            
            # Get position
            cursor.execute('SELECT * FROM farming_positions WHERE id = ? AND user_id = ?', (position_id, user_id))
            position = cursor.fetchone()
            
            if not position:
                return jsonify({'error': 'Position not found'}), 404
            
            # Calculate rewards
            rewards = calculate_pending_rewards(position_id, position['farm_id'], position['amount'])
            
            # Update rewards earned
            new_reward_earned = float(position['reward_earned']) + rewards
            cursor.execute('UPDATE farming_positions SET reward_earned = ?, last_reward_calc = ? WHERE id = ?', 
                          (new_reward_earned, datetime.now().isoformat(), position_id))
            
            conn.commit()
            conn.close()
            
            return jsonify({
                'success': True,
                'rewards_harvested': rewards,
                'total_rewards_earned': new_reward_earned,
                'message': f'Harvested {rewards} Zeontrust tokens'
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    # ==================== GET USER FARMING POSITIONS ====================
    
    @app.route('/api/farming/my-positions', methods=['GET'])
    @jwt_required()
    def get_my_farming_positions():
        try:
            user_id = get_jwt_identity()
            
            conn = get_db()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT p.*, f.name, f.apr, f.reward_token
                FROM farming_positions p
                JOIN farms f ON p.farm_id = f.id
                WHERE p.user_id = ? AND p.status = 'active'
            ''', (user_id,))
            rows = cursor.fetchall()
            conn.close()
            
            positions = []
            for row in rows:
                # Calculate pending rewards
                pending = calculate_pending_rewards(row['id'], row['farm_id'], row['amount'])
                
                positions.append({
                    'id': row['id'],
                    'farm_name': row['name'],
                    'amount': row['amount'],
                    'apr': row['apr'],
                    'reward_token': row['reward_token'],
                    'reward_earned': row['reward_earned'],
                    'pending_rewards': pending,
                    'staked_at': row['staked_at']
                })
            
            return jsonify({'success': True, 'positions': positions})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    # ==================== GET FARM STATS ====================
    
    @app.route('/api/farming/stats', methods=['GET'])
    @jwt_required()
    def get_farming_stats():
        try:
            conn = get_db()
            cursor = conn.cursor()
            
            cursor.execute('SELECT SUM(CAST(amount AS REAL)) FROM farming_positions WHERE status = "active"')
            total_staked = cursor.fetchone()[0] or 0
            
            cursor.execute('SELECT COUNT(*) FROM farming_positions WHERE status = "active"')
            total_stakers = cursor.fetchone()[0] or 0
            
            conn.close()
            
            return jsonify({
                'success': True,
                'stats': {
                    'total_staked': total_staked,
                    'total_stakers': total_stakers,
                    'total_rewards_distributed': 125000,
                    'apr_average': 30.5
                }
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    return app


# ==================== HELPER FUNCTIONS ====================

def calculate_pending_rewards(position_id, farm_id, staked_amount):
    """Calculate pending rewards for a farming position"""
    # Mock calculation - in production, use proper reward calculation
    farms = {
        1: {'apr': 45.5, 'reward_per_second': 0.0001},
        2: {'apr': 35.2, 'reward_per_second': 0.00008},
        3: {'apr': 28.7, 'reward_per_second': 0.00006},
        4: {'apr': 12.5, 'reward_per_second': 0.00003}
    }
    
    farm = farms.get(farm_id, {'reward_per_second': 0.00005})
    seconds_staked = 86400  # Mock: 1 day
    rewards = float(staked_amount) * farm['reward_per_second'] * seconds_staked
    
    return round(rewards, 4)
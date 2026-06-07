from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.dapp_models import DAppFavoriteModel

def register_dapp_routes(app):
    
    @app.route('/api/dapps/list', methods=['GET'])
    @jwt_required()
    def get_dapps():
        try:
            network = request.args.get('network', 'tron')
            category = request.args.get('category', 'all')
            
            dapps = [
                {'name': 'Uniswap', 'url': 'https://app.uniswap.org', 'network': 'ethereum', 'icon': '🦄', 'category': 'DeFi'},
                {'name': 'PancakeSwap', 'url': 'https://pancakeswap.finance', 'network': 'bsc', 'icon': '🥞', 'category': 'DeFi'},
                {'name': 'SUN.io', 'url': 'https://sun.io', 'network': 'tron', 'icon': '☀️', 'category': 'DeFi'},
                {'name': 'OpenSea', 'url': 'https://opensea.io', 'network': 'ethereum', 'icon': '🖼️', 'category': 'NFT'},
                {'name': 'Aave', 'url': 'https://aave.com', 'network': 'ethereum', 'icon': '💧', 'category': 'Lending'},
                {'name': 'QuickSwap', 'url': 'https://quickswap.exchange', 'network': 'polygon', 'icon': '⚡', 'category': 'DeFi'}
            ]
            
            filtered = [d for d in dapps if d['network'] == network]
            if category != 'all':
                filtered = [d for d in filtered if d['category'] == category]
            
            return jsonify({'success': True, 'dapps': filtered})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/dapps/favorites', methods=['GET'])
    @jwt_required()
    def get_favorites():
        try:
            user_id = get_jwt_identity()
            favorites = DAppFavoriteModel.find_by_user(user_id)
            return jsonify({'success': True, 'favorites': favorites})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/dapps/favorites', methods=['POST'])
    @jwt_required()
    def add_favorite():
        try:
            user_id = get_jwt_identity()
            data = request.get_json()
            name = data.get('name')
            url = data.get('url')
            network = data.get('network', 'tron')
            icon = data.get('icon', '🌐')
            
            existing = DAppFavoriteModel.find_by_url(user_id, url)
            if existing:
                return jsonify({'error': 'DApp already in favorites'}), 400
            
            favorite_id = DAppFavoriteModel.create(user_id, name, url, network, icon)
            return jsonify({'success': True, 'favorite_id': favorite_id})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/dapps/favorites/<int:favorite_id>', methods=['DELETE'])
    @jwt_required()
    def remove_favorite(favorite_id):
        try:
            user_id = get_jwt_identity()
            success = DAppFavoriteModel.delete(favorite_id, user_id)
            if success:
                return jsonify({'success': True, 'message': 'Removed from favorites'})
            return jsonify({'error': 'Favorite not found'}), 404
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/dapps/categories', methods=['GET'])
    @jwt_required()
    def get_categories():
        categories = ['DeFi', 'NFT', 'Gaming', 'Lending', 'Bridge', 'Tool']
        return jsonify({'success': True, 'categories': categories})
    
    return app
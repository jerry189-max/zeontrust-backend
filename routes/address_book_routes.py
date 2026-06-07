from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.address_models import AddressBookModel

def register_address_book_routes(app):
    
    @app.route('/api/address-book/list', methods=['GET'])
    @jwt_required()
    def get_addresses():
        try:
            user_id = get_jwt_identity()
            network = request.args.get('network')
            addresses = AddressBookModel.find_by_user(user_id, network)
            return jsonify({'success': True, 'addresses': addresses})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/address-book/favorites', methods=['GET'])
    @jwt_required()
    def get_favorites():
        try:
            user_id = get_jwt_identity()
            favorites = AddressBookModel.find_favorites(user_id)
            return jsonify({'success': True, 'favorites': favorites})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/address-book/add', methods=['POST'])
    @jwt_required()
    def add_address():
        try:
            user_id = get_jwt_identity()
            data = request.get_json()
            name = data.get('name')
            address = data.get('address')
            network = data.get('network', 'tron')
            notes = data.get('notes')
            favorite = data.get('favorite', False)
            
            address_id = AddressBookModel.create(user_id, name, address, network, notes, favorite)
            return jsonify({'success': True, 'address_id': address_id})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/address-book/<int:address_id>', methods=['PUT'])
    @jwt_required()
    def update_address(address_id):
        try:
            user_id = get_jwt_identity()
            data = request.get_json()
            
            AddressBookModel.update(address_id, user_id, **data)
            return jsonify({'success': True, 'message': 'Address updated'})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/address-book/<int:address_id>', methods=['DELETE'])
    @jwt_required()
    def delete_address(address_id):
        try:
            user_id = get_jwt_identity()
            success = AddressBookModel.delete(address_id, user_id)
            if success:
                return jsonify({'success': True, 'message': 'Address deleted'})
            return jsonify({'error': 'Address not found'}), 404
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/address-book/<int:address_id>/favorite', methods=['POST'])
    @jwt_required()
    def toggle_favorite(address_id):
        try:
            user_id = get_jwt_identity()
            AddressBookModel.toggle_favorite(address_id, user_id)
            return jsonify({'success': True, 'message': 'Favorite toggled'})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    return app
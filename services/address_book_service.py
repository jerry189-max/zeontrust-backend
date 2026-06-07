from models.address_models import AddressBookModel

class AddressBookService:
    
    @staticmethod
    def add_address(user_id: int, name: str, address: str, network: str, notes: str = None, favorite: bool = False) -> dict:
        address_id = AddressBookModel.create(user_id, name, address, network, notes, favorite)
        return {'address_id': address_id, 'name': name, 'address': address, 'network': network}
    
    @staticmethod
    def get_addresses(user_id: int, network: str = None) -> list:
        return AddressBookModel.find_by_user(user_id, network)
    
    @staticmethod
    def get_favorites(user_id: int) -> list:
        return AddressBookModel.find_favorites(user_id)
    
    @staticmethod
    def update_address(address_id: int, user_id: int, **kwargs) -> bool:
        return AddressBookModel.update(address_id, user_id, **kwargs)
    
    @staticmethod
    def delete_address(address_id: int, user_id: int) -> bool:
        return AddressBookModel.delete(address_id, user_id)
    
    @staticmethod
    def toggle_favorite(address_id: int, user_id: int) -> bool:
        return AddressBookModel.toggle_favorite(address_id, user_id)
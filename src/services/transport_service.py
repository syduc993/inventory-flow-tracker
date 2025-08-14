# src/services/transport_service.py
from src.utils.transport_provider import get_transport_providers_from_file, update_transport_providers_json_file

class TransportProviderService:
    def __init__(self, app_token):
        self.app_token = app_token
    
    def get_transport_providers(self):
        """Lấy danh sách nhà cung cấp"""
        return get_transport_providers_from_file()
    
    def refresh_transport_providers(self, table_id="tblDefault"):
        """Làm mới danh sách nhà cung cấp"""
        return update_transport_providers_json_file(self.app_token, table_id)

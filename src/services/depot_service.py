# src/services/depot_service.py
from src.utils.depot import get_depots_from_file, update_depot_json_file

class DepotService:
    def get_depots(self):
        """Lấy danh sách depot"""
        return get_depots_from_file()
    
    def refresh_depots(self):
        """Làm mới danh sách depot"""
        return update_depot_json_file()
    
    def validate_depot(self, depot_id):
        """Kiểm tra depot_id có hợp lệ không"""
        if not depot_id:
            return False, "ID depot trống"
        
        depots = self.get_depots()
        for depot in depots:
            if depot.get('id') == str(depot_id):
                return True, depot.get('name', '')
        
        return False, "Depot không tồn tại"

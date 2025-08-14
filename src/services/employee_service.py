# src/services/employee_service.py
from src.utils.cache import get_employee_list_from_file, update_employee_json_file

class EmployeeService:
    def get_employees(self):
        """Lấy danh sách nhân viên"""
        return get_employee_list_from_file()
    
    def refresh_employees(self):
        """Làm mới danh sách nhân viên"""
        return update_employee_json_file()

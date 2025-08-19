# src/services/record_service.py
from src.utils.api import fetch_imex_details
from src.utils.larkbase import (
    larkbase_find_by_field, larkbase_write_data, 
    larkbase_update_data, larkbase_delete_record
)
import time
import datetime
import logging

class RecordService:
    def __init__(self, app_token, table_id):
        self.app_token = app_token
        self.table_id = table_id

    def search_record(self, bill_id):
        """Tìm kiếm record theo Bill ID"""
        return larkbase_find_by_field(self.app_token, self.table_id, "ID", bill_id)

    def create_record(self, form_data):
        """Tạo record mới với tách riêng ID và tên từ dropdown"""
        new_record = {}
        
        # Danh sách các trường cần chuyển đổi thành số
        numeric_fields = ["Số lượng", "Số lượng bao/tải giao", "Số lượng bao tải nhận"]
        
        for key, value in form_data.items():
            if key in numeric_fields and value:
                try:
                    new_record[key] = int(value) if value else 0
                except (ValueError, TypeError):
                    new_record[key] = 0
            elif key == "Người bàn giao":
                # Đây là giá trị từ hidden input (chỉ chứa ID)
                if value:
                    # Lưu ID vào cột riêng
                    new_record["ID người bàn giao"] = value
                    
                    # Tìm tên tương ứng với ID từ danh sách nhân viên
                    from src.services.employee_service import EmployeeService
                    employee_service = EmployeeService()
                    employees = employee_service.get_employees()
                    
                    employee_name = ""
                    for emp in employees:
                        if emp.get('id') == value:
                            employee_name = emp.get('name', '')
                            break
                    
                    if employee_name:
                        new_record["Người bàn giao"] = employee_name
                    else:
                        new_record["Người bàn giao"] = value  # Fallback về ID nếu không tìm thấy tên
                continue
            elif value and key not in ["Người bàn giao_hidden"]:  
                new_record[key] = value
        
        new_record["Ngày bàn giao"] = int(time.time() * 1000)
        
        # Debug: In ra dữ liệu trước khi gửi
        logging.info(f"Data to send: {new_record}")
        
        return larkbase_write_data(self.app_token, self.table_id, new_record)

    def update_record(self, record_id, form_data):
        """Cập nhật record với tách riêng ID và tên từ dropdown"""
        from src.utils.config import UPDATABLE_FIELDS
        
        update_data = {}
        for field in UPDATABLE_FIELDS:
            if field in form_data and form_data[field]:
                value = form_data[field]
                
                if field == "Người bàn giao":
                    # Lưu ID
                    update_data["ID người bàn giao"] = value
                    
                    # Tìm tên từ danh sách nhân viên
                    from src.services.employee_service import EmployeeService
                    employee_service = EmployeeService()
                    employees = employee_service.get_employees()
                    
                    employee_name = ""
                    for emp in employees:
                        if emp.get('id') == value:
                            employee_name = emp.get('name', '')
                            break
                    
                    if employee_name:
                        update_data["Người bàn giao"] = employee_name
                    else:
                        update_data["Người bàn giao"] = value
                elif field == "Ngày nhận hàng" and value:
                    dt_obj = datetime.datetime.strptime(value, '%Y-%m-%d')
                    update_data[field] = int(dt_obj.timestamp() * 1000)
                else:
                    update_data[field] = value
        
        if not update_data:
            return False, "Không có thông tin nào được thay đổi."
        
        return larkbase_update_data(self.app_token, self.table_id, record_id, update_data)

    def delete_record(self, record_id):
        """Xóa record"""
        return larkbase_delete_record(self.app_token, self.table_id, record_id)

    def get_api_data(self, bill_id):
        """Lấy dữ liệu từ API"""
        return fetch_imex_details(bill_id)

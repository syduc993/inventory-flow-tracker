# src/core/dependencies.py - Dependency Injection
from fastapi import Request
from fastapi.templating import Jinja2Templates

from src.services.record_service import RecordService
from src.services.employee_service import EmployeeService
from src.services.transport_service import TransportProviderService
from src.services.depot_service import DepotService
from src.utils.config import API_TOKENS, TABLE_IDS

# Setup templates
templates = Jinja2Templates(directory="templates")

# Services
def get_record_service() -> RecordService:
    return RecordService(API_TOKENS['MAIN_APP_TOKEN'], TABLE_IDS['MAIN_TABLE_ID'])

def get_employee_service() -> EmployeeService:
    return EmployeeService()

def get_transport_service() -> TransportProviderService:
    return TransportProviderService(API_TOKENS['MAIN_APP_TOKEN'])

def get_depot_service() -> DepotService:
    return DepotService()

# Helper function
def get_current_user(request: Request) -> dict:
    """Lấy thông tin user hiện tại từ request state"""
    return getattr(request.state, 'user', None)

# Template filters
def get_employee_display(employee_id, employees):
    """Tìm và trả về chuỗi 'Tên (ID)' từ danh sách nhân viên."""
    if not employee_id or not employees:
        return ""
    for emp in employees:
        if emp.get('id') == employee_id:
            return f"{emp.get('name', '')} ({emp.get('id', '')})"
    return employee_id

def get_transport_provider_display(provider_id, transport_providers):
    """Tìm và trả về tên nhà cung cấp từ ID."""
    if not provider_id or not transport_providers:
        return provider_id
    for provider in transport_providers:
        if provider.get('id') == provider_id:
            return provider.get('name', provider_id)
    return provider_id


# Thêm vào src/core/dependencies.py

def get_report_service():
    from src.services.report_service import ReportService
    return ReportService(API_TOKENS['MAIN_APP_TOKEN'], TABLE_IDS['MAIN_TABLE_ID'])


# Register template filters
templates.env.filters['get_employee_display'] = get_employee_display
templates.env.filters['get_transport_provider_display'] = get_transport_provider_display

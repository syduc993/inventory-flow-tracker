from fastapi import Request
from fastapi.templating import Jinja2Templates

from src.services.record_service import RecordService
from src.services.employee_service import EmployeeService
from src.services.transport_service import TransportProviderService
from src.services.depot_service import DepotService
from src.services.report_service import ReportService 
from src.utils.config import API_TOKENS, TABLE_IDS

_record_service_instance = RecordService(API_TOKENS['MAIN_APP_TOKEN'], TABLE_IDS['MAIN_TABLE_ID'])
_employee_service_instance = EmployeeService()
_transport_service_instance = TransportProviderService(API_TOKENS['MAIN_APP_TOKEN'])
_depot_service_instance = DepotService()
_report_service_instance = ReportService(API_TOKENS['MAIN_APP_TOKEN'], TABLE_IDS['MAIN_TABLE_ID'])


# Setup templates
templates = Jinja2Templates(directory="templates")

# Services (các hàm get_* giờ chỉ trả về instance đã được tạo sẵn)
def get_record_service() -> RecordService:
    return _record_service_instance

def get_employee_service() -> EmployeeService:
    return _employee_service_instance

def get_transport_service() -> TransportProviderService:
    return _transport_service_instance

def get_depot_service() -> DepotService:
    return _depot_service_instance

def get_report_service() -> ReportService:
    return _report_service_instance


# Helper function
def get_current_user(request: Request) -> dict:
    """Lấy thông tin user hiện tại từ request state"""
    return getattr(request.state, 'user', None)

# Template filters
def get_employee_display(employee_id, employees):
    if not employee_id or not employees:
        return ""
    for emp in employees:
        if emp.get('id') == employee_id:
            return f"{emp.get('name', '')} ({emp.get('id', '')})"
    return employee_id

def get_transport_provider_display(provider_id, transport_providers):
    if not provider_id or not transport_providers:
        return provider_id
    for provider in transport_providers:
        if provider.get('id') == provider_id:
            return provider.get('name', provider_id)
    return provider_id

# Register template filters
templates.env.filters['get_employee_display'] = get_employee_display
templates.env.filters['get_transport_provider_display'] = get_transport_provider_display
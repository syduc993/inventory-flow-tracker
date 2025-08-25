# FILE: src/routes/refresh_routes.py (FINAL & CORRECT PARTIAL UPDATE VERSION)
from fastapi import APIRouter, Request, Depends
# ✅ SỬA: Dùng lại Response và thêm templates để render HTML
from fastapi.responses import Response 
from src.core.dependencies import templates # Thêm templates
import time
import logging
import json

from src.services.employee_service import EmployeeService
from src.services.transport_service import TransportProviderService
from src.services.depot_service import DepotService
from src.core.dependencies import get_current_user, get_employee_service, get_transport_service, get_depot_service
from src.utils.config import TABLE_IDS

router = APIRouter(prefix="/refresh", tags=["refresh"])
logger = logging.getLogger(__name__)

# =================================================================================
# === HÀM REFRESH NHÂN VIÊN (TRẢ VỀ PARTIAL HTML) =================================
# =================================================================================
@router.post("/employees")
async def refresh_employees_endpoint(
    request: Request,
    employee_service: EmployeeService = Depends(get_employee_service)
):
    try:
        success, message = employee_service.refresh_employees()
        event_data = {"message": message, "type": "success" if success else "error"}
    except Exception as e:
        event_data = {"message": f"Lỗi hệ thống: {str(e)}", "type": "error"}

    headers = {"HX-Trigger": json.dumps({"show-refresh-notification": event_data})}
    
    # ✅ SỬA: Render lại component dropdown với dữ liệu mới và trả về HTML
    new_employees = employee_service.get_employees()
    context = {
        "request": request, 
        "employees": new_employees, 
        "field_name": "handover_person", 
        "placeholder": "Tìm nhân viên..."
    }
    # Dùng lại TemplateResponse để render và gửi header
    return templates.TemplateResponse(
        "components/dropdowns/employee.html",
        context,
        headers=headers
    )

# =================================================================================
# === HÀM REFRESH ĐƠN VỊ VẬN CHUYỂN (TRẢ VỀ PARTIAL HTML) ==========================
# =================================================================================
@router.post("/transport-providers")
async def refresh_transport_providers_endpoint(
    request: Request,
    transport_service: TransportProviderService = Depends(get_transport_service)
):
    try:
        time.sleep(0.5)
        table_id = TABLE_IDS.get('TRANSPORT_PROVIDERS_TABLE_ID', 'tblyiELQIi6M1j1r')
        success, message = transport_service.refresh_transport_providers(table_id)
        event_data = {"message": message, "type": "success" if success else "error"}
    except Exception as e:
        event_data = {"message": f"Lỗi hệ thống: {str(e)}", "type": "error"}
            
    headers = {"HX-Trigger": json.dumps({"show-refresh-notification": event_data})}
    
    # ✅ SỬA: Render lại component dropdown với dữ liệu mới và trả về HTML
    new_providers = transport_service.get_transport_providers()
    context = {
        "request": request,
        "transport_providers": new_providers,
        "field_name": "transport_provider",
        "placeholder": "Tìm đơn vị vận chuyển..."
    }
    return templates.TemplateResponse(
        "components/dropdowns/transport.html",
        context,
        headers=headers
    )

# =================================================================================
# === HÀM REFRESH KHO (TRẢ VỀ PARTIAL HTML) ========================================
# =================================================================================
@router.post("/depots")
async def refresh_depots_endpoint(
    request: Request,
    depot_service: DepotService = Depends(get_depot_service)
):
    try:
        time.sleep(0.5)
        success, message = depot_service.refresh_depots()
        event_data = {"message": message, "type": "success" if success else "error"}
    except Exception as e:
        event_data = {"message": f"Lỗi hệ thống: {str(e)}", "type": "error"}

    headers = {"HX-Trigger": json.dumps({"show-refresh-notification": event_data})}

    # ✅ SỬA: Render lại component dropdown với dữ liệu mới và trả về HTML
    new_depots = depot_service.get_depots()
    # Chú ý: cần truyền cả field_name và placeholder, ta có thể tạm hardcode
    # hoặc tìm cách truyền từ frontend, nhưng hardcode là đơn giản nhất.
    # Ta sẽ giả định field_name và placeholder dựa trên context.
    context = {
        "request": request,
        "depots": new_depots,
        "field_name": "depot", # Tên chung, không ảnh hưởng nhiều
        "placeholder": "Chọn kho..."
    }
    return templates.TemplateResponse(
        "components/dropdowns/depot.html",
        context,
        headers=headers
    )
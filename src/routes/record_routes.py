# src/routes/record_routes.py - Record CRUD Routes
from fastapi import APIRouter, Request, Form, Response, Depends
from fastapi.responses import HTMLResponse
import logging

from src.services.record_service import RecordService
from src.services.employee_service import EmployeeService
from src.services.transport_service import TransportProviderService
from src.core.dependencies import get_current_user, templates, get_record_service, get_employee_service, get_transport_service
from src.utils.config import CREATABLE_FIELDS

router = APIRouter(prefix="/records", tags=["records"])
logger = logging.getLogger(__name__)

def format_timestamp_ms_to_dt_string(ts_ms):
    if not ts_ms: return ""
    try:
        import datetime
        return datetime.datetime.fromtimestamp(int(ts_ms) / 1000).strftime('%Y-%m-%d %H:%M:%S')
    except (ValueError, TypeError):
        return str(ts_ms)

@router.post("/search", response_class=HTMLResponse)
async def search_bill(
    request: Request, 
    bill_id: str = Form(...),
    record_service: RecordService = Depends(get_record_service),
    employee_service: EmployeeService = Depends(get_employee_service),
    transport_service: TransportProviderService = Depends(get_transport_service)
):
    user = get_current_user(request)
    
    if not bill_id:
        return HTMLResponse("<div class='error'>Vui lòng nhập Bill ID.</div>")

    found, record = record_service.search_record(bill_id)
    context = {
        "request": request,
        "user": user,
        "employees": employee_service.get_employees(),
        "transport_providers": transport_service.get_transport_providers()
    }

    if found and record:
        context.update({
            "record": record,
            "format_ts": format_timestamp_ms_to_dt_string
        })
        return templates.TemplateResponse("pages/view_only.html", context)
    else:
        imex_items = record_service.get_api_data(bill_id)
        if not imex_items:
            return HTMLResponse("<div class='error'>❌ Không lấy được dữ liệu, kiểm tra lại Bill ID.</div>")

        example_item = imex_items[0]
        context["api_data"] = {
            "ID": bill_id,
            "ID kho đi": example_item.get("fromDepotId", ""),
            "Kho đi": example_item.get("fromDepotName", ""),
            "ID kho đến": example_item.get("toDepotId", ""),
            "Kho đến": example_item.get("toDepotName", ""),
            "Số lượng": int(example_item.get("realQuantity") or 0),
        }
        context["creatable_fields"] = CREATABLE_FIELDS
        return templates.TemplateResponse("components/forms/create.html", context)

@router.post("/", response_class=HTMLResponse)
async def create_record(
    request: Request,
    record_service: RecordService = Depends(get_record_service)
):
    user = get_current_user(request)
    form_data = await request.form()
    bill_id = form_data.get("ID", "Không rõ")
    
    logger.info(f"User {user.get('name')} creating record for Bill ID: {bill_id}")
    
    success, message = record_service.create_record(form_data)

    if success:
        return HTMLResponse(f"<div class='success'>✅ Đã thêm thành công Bill ID: {bill_id}</div>")
    else:
        return HTMLResponse(f"<div class='error'>❌ Lỗi khi thêm mới: {message}</div>")

@router.put("/{record_id}", response_class=HTMLResponse)
async def update_record(
    record_id: str, 
    request: Request,
    record_service: RecordService = Depends(get_record_service)
):
    user = get_current_user(request)
    form_data = await request.form()
    
    logger.info(f"User {user.get('name')} updating record: {record_id}")
    
    success, message = record_service.update_record(record_id, form_data)
    
    if success:
        return HTMLResponse("<div class='success'>📝 Cập nhật thành công. Form đã được reset.</div>")
    else:
        return HTMLResponse(f"<div class='error'>❌ Lỗi khi cập nhật: {message}</div>")

@router.delete("/{record_id}", response_class=Response)
async def delete_record_endpoint(
    record_id: str, 
    request: Request,
    record_service: RecordService = Depends(get_record_service)
):
    user = get_current_user(request)
    
    logger.info(f"User {user.get('name')} deleting record: {record_id}")
    
    success, message = record_service.delete_record(record_id)
    if success:
        return Response(status_code=200, content="<div class='success'>🗑️ Đã xóa thành công.</div>")
    else:
        return HTMLResponse(f"<div class='error'>❌ Lỗi khi xóa: {message}</div>", status_code=400)

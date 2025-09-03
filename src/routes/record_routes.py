# src/routes/record_routes.py - Record CRUD Routes
from fastapi import APIRouter, Request, Form, Response, Depends
from fastapi.responses import HTMLResponse
import logging
import datetime
from datetime import timedelta

from src.services.record_service import RecordService
from src.services.employee_service import EmployeeService
from src.services.transport_service import TransportProviderService
from src.core.dependencies import get_current_user, templates, get_record_service, get_employee_service, get_transport_service
from src.utils.config import CREATABLE_FIELDS

router = APIRouter(prefix="/records", tags=["records"])
logger = logging.getLogger(__name__)

# def format_timestamp_ms_to_dt_string(ts_ms):
#     if not ts_ms: return ""
#     try:
#         import datetime
#         return datetime.datetime.fromtimestamp(int(ts_ms) / 1000).strftime('%Y-%m-%d %H:%M:%S')
#     except (ValueError, TypeError):
#         return str(ts_ms)

def format_timestamp_ms_to_dt_string(ts_ms):
    """
    Chuyển đổi Unix timestamp (mili giây) sang chuỗi ngày giờ theo múi giờ GMT+7.
    """
    if not ts_ms: 
        return ""
    try:
        # Chuyển đổi timestamp từ mili giây sang giây
        timestamp_sec = int(ts_ms) / 1000
        
        # Tạo đối tượng datetime từ timestamp (thường là múi giờ UTC của server)
        utc_time = datetime.datetime.fromtimestamp(timestamp_sec)
        
        # ⭐ SỬA ĐỔI: Cộng thêm 7 giờ để chuyển sang múi giờ Việt Nam (GMT+7)
        #gmt7_time = utc_time + timedelta(hours=7)
        gmt7_time = utc_time  # Nguyên nhân là do dưới larkbase đã lưu Ngày bàn giao theo GMT + 7
        # Định dạng lại chuỗi ngày giờ theo format mong muốn
        return gmt7_time.strftime('%Y-%m-%d %H:%M:%S')
    except (ValueError, TypeError):
        # Nếu có lỗi, trả về giá trị gốc
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

        # Chỉ hiển thị thông báo "ID mới" thay vì form tạo mới
        return HTMLResponse("<div class='info'>📋 ID mới - chưa có bản ghi trong hệ thống.</div>")

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

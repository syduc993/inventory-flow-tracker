from fastapi import FastAPI, Request, Form, Response
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from services import RecordService, EmployeeService, TransportProviderService

app = FastAPI(title="IMEX Distribution API")

# Static files
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Services
APP_TOKEN = "Rm9PbvKLeaFFZcsSQpElnRjIgXg"
TABLE_ID = "tblJJPUEFhsXHaxY"
record_service = RecordService(APP_TOKEN, TABLE_ID)
employee_service = EmployeeService()
transport_provider_service = TransportProviderService(APP_TOKEN)

def format_timestamp_ms_to_dt_string(ts_ms):
    if not ts_ms: return ""
    try:
        import datetime
        return datetime.datetime.fromtimestamp(int(ts_ms) / 1000).strftime('%Y-%m-%d %H:%M:%S')
    except (ValueError, TypeError):
        return str(ts_ms)

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# @app.post("/search", response_class=HTMLResponse)
# async def search_bill(request: Request, bill_id: str = Form(...)):
#     if not bill_id:
#         return HTMLResponse("<div class='error'>Vui lòng nhập Bill ID.</div>")

#     found, record = record_service.search_record(bill_id)
#     context = {
#         "request": request,
#         "employees": employee_service.get_employees(),
#         "transport_providers": transport_provider_service.get_transport_providers()  # ← THÊM MỚI
#     }

#     if found and record:
#         from src.utils.config import LOCK_FIELDS
#         has_lock_values = any(record.get("fields", {}).get(f) for f in LOCK_FIELDS)
#         context.update({
#             "record": record,
#             "can_delete": not has_lock_values,
#             "lock_fields": ', '.join(LOCK_FIELDS),
#             "format_ts": format_timestamp_ms_to_dt_string
#         })
#         return templates.TemplateResponse("_update_form.html", context)
#     else:
#         imex_items = record_service.get_api_data(bill_id)
#         if not imex_items:
#             return HTMLResponse("<div class='error'>❌ Không lấy được dữ liệu, kiểm tra lại Bill ID.</div>")

#         example_item = imex_items[0]
#         context["api_data"] = {
#             "ID": bill_id,
#             "ID kho đi": example_item.get("fromDepotId", ""),
#             "Kho đi": example_item.get("fromDepotName", ""),
#             "ID kho đến": example_item.get("toDepotId", ""),
#             "Kho đến": example_item.get("toDepotName", ""),
#             "Số lượng": int(example_item.get("realQuantity") or 0),
#         }
#         from src.utils.config import CREATABLE_FIELDS
#         context["creatable_fields"] = CREATABLE_FIELDS
#         return templates.TemplateResponse("_create_form.html", context)

@app.post("/search", response_class=HTMLResponse)
async def search_bill(request: Request, bill_id: str = Form(...)):
    if not bill_id:
        return HTMLResponse("<div class='error'>Vui lòng nhập Bill ID.</div>")

    found, record = record_service.search_record(bill_id)
    context = {
        "request": request,
        "employees": employee_service.get_employees(),
        "transport_providers": transport_provider_service.get_transport_providers()
    }

    if found and record:
        # ← SỬA: Chỉ hiển thị thông tin, không cho edit
        context.update({
            "record": record,
            "format_ts": format_timestamp_ms_to_dt_string
        })
        # ← SỬA: Tạo template mới hoặc sửa template để chỉ hiển thị
        return templates.TemplateResponse("_view_only.html", context)
    else:
        # Phần tạo mới vẫn giữ nguyên
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
        from src.utils.config import CREATABLE_FIELDS
        context["creatable_fields"] = CREATABLE_FIELDS
        return templates.TemplateResponse("_create_form.html", context)


@app.post("/records", response_class=HTMLResponse)
async def create_record(request: Request):
    form_data = await request.form()
    bill_id = form_data.get("ID", "Không rõ")
    success, message = record_service.create_record(form_data)

    if success:
        return HTMLResponse(f"<div class='success'>✅ Đã thêm thành công Bill ID: {bill_id}</div>")
    else:
        return HTMLResponse(f"<div class='error'>❌ Lỗi khi thêm mới: {message}</div>")

@app.put("/records/{record_id}", response_class=HTMLResponse)
async def update_record(record_id: str, request: Request):
    form_data = await request.form()
    success, message = record_service.update_record(record_id, form_data)
    
    if success:
        return HTMLResponse("<div class='success'>📝 Cập nhật thành công. Form đã được reset.</div>")
    else:
        return HTMLResponse(f"<div class='error'>❌ Lỗi khi cập nhật: {message}</div>")

@app.delete("/records/{record_id}", response_class=Response)
async def delete_record_endpoint(record_id: str):
    success, message = record_service.delete_record(record_id)
    if success:
        return Response(status_code=200, content="<div class='success'>🗑️ Đã xóa thành công.</div>")
    else:
        return HTMLResponse(f"<div class='error'>❌ Lỗi khi xóa: {message}</div>", status_code=400)

def get_employee_display(employee_id, employees):
    """Tìm và trả về chuỗi 'Tên (ID)' từ danh sách nhân viên."""
    if not employee_id or not employees:
        return ""
    for emp in employees:
        if emp.get('id') == employee_id:
            return f"{emp.get('name', '')} ({emp.get('id', '')})"
    return employee_id # Trả về ID nếu không tìm thấy

# ← THÊM MỚI: Filter cho hiển thị tên nhà cung cấp
def get_transport_provider_display(provider_id, transport_providers):
    """Tìm và trả về tên nhà cung cấp từ ID."""
    if not provider_id or not transport_providers:
        return provider_id
    for provider in transport_providers:
        if provider.get('id') == provider_id:
            return provider.get('name', provider_id)
    return provider_id # Trả về ID nếu không tìm thấy

templates.env.filters['get_employee_display'] = get_employee_display
templates.env.filters['get_transport_provider_display'] = get_transport_provider_display  # ← THÊM MỚI

@app.post("/refresh-employees", response_class=HTMLResponse)
async def refresh_employees_endpoint():
    """Endpoint để làm mới danh sách nhân viên"""
    try:
        import time
        time.sleep(0.5)  # Tạo cảm giác xử lý
        
        success, message = employee_service.refresh_employees()
        
        if success:
            return HTMLResponse(f"<div class='success'>✅ {message}</div>")
        else:
            return HTMLResponse(f"<div class='error'>❌ Lỗi: {message}</div>")
            
    except Exception as e:
        return HTMLResponse(f"<div class='error'>❌ Lỗi hệ thống: {str(e)}</div>")

# ← THÊM MỚI: Endpoint để refresh transport providers
@app.post("/refresh-transport-providers", response_class=HTMLResponse)
async def refresh_transport_providers_endpoint():
    """Endpoint để làm mới danh sách đơn vị vận chuyển"""
    try:
        import time
        time.sleep(0.5)  # Tạo cảm giác xử lý
        
        # Bạn cần thay "tblDefault" bằng table ID thực tế chứa nhà cung cấp
        # Ví dụ: "tblXXXXXXXXXXXXXXX"
        success, message = transport_provider_service.refresh_transport_providers("tblyiELQIi6M1j1r")
        
        if success:
            return HTMLResponse(f"<div class='success'>✅ {message}</div>")
        else:
            return HTMLResponse(f"<div class='error'>❌ Lỗi: {message}</div>")
            
    except Exception as e:
        return HTMLResponse(f"<div class='error'>❌ Lỗi hệ thống: {str(e)}</div>")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

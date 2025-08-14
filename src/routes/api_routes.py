# src/routes/api_routes.py - API Routes
from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, JSONResponse
import time
import logging

from src.services.record_service import RecordService
from src.services.employee_service import EmployeeService
from src.services.transport_service import TransportProviderService
from src.services.depot_service import DepotService
from src.core.dependencies import get_current_user, templates, get_record_service, get_employee_service, get_transport_service, get_depot_service

router = APIRouter(tags=["api"])
logger = logging.getLogger(__name__)

@router.get("/", response_class=HTMLResponse)
async def read_root(
    request: Request,
    record_service: RecordService = Depends(get_record_service),
    employee_service: EmployeeService = Depends(get_employee_service),
    transport_service: TransportProviderService = Depends(get_transport_service),
    depot_service: DepotService = Depends(get_depot_service)
):
    print("🔍 Loading template: pages/index.html")
    user = get_current_user(request)
    return templates.TemplateResponse("pages/index.html", {
        "request": request,
        "user": user,
        "employees": employee_service.get_employees(),
        "transport_providers": transport_service.get_transport_providers(),
        "depots": depot_service.get_depots()
    })

@router.post("/validate-bill-id")
async def validate_bill_id(
    request: Request, 
    bill_id: str = Form(...),
    record_service: RecordService = Depends(get_record_service)
):
    """Validate single bill ID - chỉ dùng cho bulk form"""
    try:
        imex_items = record_service.get_api_data(bill_id)
        if not imex_items:
            return JSONResponse({
                "valid": False,
                "message": "ID không hợp lệ"
            })
        
        example_item = imex_items[0]
        quantity = int(example_item.get("realQuantity") or 0)
        
        return JSONResponse({
            "valid": True,
            "message": "ID hợp lệ",
            "quantity": quantity,
            "from_depot": example_item.get("fromDepotName", ""),
            "to_depot": example_item.get("toDepotName", "")
        })
        
    except Exception as e:
        return JSONResponse({
            "valid": False,
            "message": f"Lỗi kiểm tra: {str(e)}"
        })

@router.post("/bulk-create-records", response_class=HTMLResponse)
async def bulk_create_records(
    request: Request,
    record_service: RecordService = Depends(get_record_service),
    depot_service: DepotService = Depends(get_depot_service)
):
    """Create multiple records at once"""
    user = get_current_user(request)
    
    try:
        body = await request.json()
        from_depot = body.get("from_depot")
        to_depot = body.get("to_depot") 
        handover_person = body.get("handover_person")
        transport_provider = body.get("transport_provider", "")
        bill_data = body.get("bill_data", [])
        
        if not all([from_depot, to_depot, handover_person]):
            return HTMLResponse('<div class="error">❌ Thiếu thông tin bắt buộc</div>')
        
        # Validate depots
        from_valid, from_name = depot_service.validate_depot(from_depot)
        to_valid, to_name = depot_service.validate_depot(to_depot)
        
        if not from_valid:
            return HTMLResponse(f'<div class="error">❌ Kho đi không hợp lệ: {from_name}</div>')
        if not to_valid:
            return HTMLResponse(f'<div class="error">❌ Kho đến không hợp lệ: {to_name}</div>')
        
        results = []
        success_count = 0
        
        for item in bill_data:
            bill_id = item.get("bill_id")
            quantity = item.get("quantity", 0)
            
            # Validate bill ID
            imex_items = record_service.get_api_data(bill_id)
            if not imex_items:
                results.append(f"❌ {bill_id}: ID không hợp lệ")
                continue
            
            # Create record
            example_item = imex_items[0]
            record_data = {
                "ID": bill_id,
                "ID kho đi": example_item.get("fromDepotId", ""),
                "Kho đi": example_item.get("fromDepotName", ""),
                "ID kho đến": example_item.get("toDepotId", ""),
                "Kho đến": example_item.get("toDepotName", ""),
                "Số lượng": int(example_item.get("realQuantity") or 0),
                "Số lượng bao/tải giao": int(quantity) if quantity else 0,
                "Người bàn giao": handover_person,
                "Đơn vị vận chuyển": transport_provider,
                "Ngày bàn giao": int(time.time() * 1000)
            }
            
            success, message = record_service.create_record(record_data)
            if success:
                results.append(f"✅ {bill_id}: Thành công")
                success_count += 1
            else:
                results.append(f"❌ {bill_id}: {message}")
        
        # Format results
        result_html = f'<div class="success">📊 Hoàn thành: {success_count}/{len(bill_data)} bản ghi thành công</div>'
        result_html += '<div class="info"><ul>'
        for result in results:
            result_html += f'<li>{result}</li>'
        result_html += '</ul></div>'
        
        logger.info(f"User {user.get('name')} bulk created {success_count} records")
        return HTMLResponse(result_html)
        
    except Exception as e:
        logger.error(f"Error in bulk create: {e}")
        return HTMLResponse(f'<div class="error">❌ Lỗi hệ thống: {str(e)}</div>')

@router.get("/health")
async def health_check():
    """Health check endpoint (public)"""
    return {"status": "ok", "service": "inventory-flow-tracker"}

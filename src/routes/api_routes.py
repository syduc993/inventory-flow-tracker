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
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)

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



# src/routes/api_routes.py

@router.post("/validate-bill-id")
async def validate_bill_id(
    request: Request, 
    bill_id: str = Form(...),
    # from_depot: str = Form(None), # ❌ BỎ DÒNG NÀY
    to_depot: str = Form(...),      # ✅ SỬA: Đánh dấu là trường bắt buộc
    record_service: RecordService = Depends(get_record_service)
):
    """Validate single bill ID - chỉ dùng cho bulk form"""
    try:
        # ✅ SỬA: Chỉ cần kiểm tra Kho đến là đủ
        if not to_depot:
            return JSONResponse({
                "valid": False,
                "message": "Cần chọn Kho đến trước"
            })
        
        imex_items = record_service.get_api_data(bill_id)
        if not imex_items:
            return JSONResponse({
                "valid": False,
                "message": "ID không hợp lệ"
            })
        
        # ... (Phần logic kiểm tra status giữ nguyên)
        try:
            all_statuses = {int(item.get("status", 0)) for item in imex_items}
        except (ValueError, TypeError):
            return JSONResponse(...)

        valid_statuses = {3, 4, 5, 6}
        is_valid_bill = any(status in valid_statuses for status in all_statuses)

        if not is_valid_bill:
            return JSONResponse({
                "valid": False,
                "message": "ID chưa được duyệt"
            })
        
        example_item = imex_items[0]
        
        # ❌ BỎ: Không cần kiểm tra kho đi nữa
        # if example_item.get("fromDepotId", "") != from_depot:
        #     return JSONResponse({
        #         "valid": False,
        #         "message": "Không đúng kho đi"
        #     })
        
        # ✅ GIỮ LẠI: Vẫn kiểm tra kho đến
        if example_item.get("toDepotId", "") != to_depot:
            return JSONResponse({
                "valid": False,
                "message": "Không đúng kho đến"
            })
        
        return JSONResponse({
            "valid": True,
            "message": "ID hợp lệ",
            "from_depot": example_item.get("fromDepotName", ""),
            "to_depot": example_item.get("toDepotName", "")
        })
        
    except Exception as e:
        return JSONResponse({
            "valid": False,
            "message": "Lỗi kiểm tra"
        })





# @router.post("/validate-bill-id")
# async def validate_bill_id(
#     request: Request, 
#     bill_id: str = Form(...),
#     from_depot: str = Form(None),
#     to_depot: str = Form(None),
#     record_service: RecordService = Depends(get_record_service)
# ):
#     """Validate single bill ID - chỉ dùng cho bulk form"""
#     try:
#         # ✅ THÊM: Kiểm tra bắt buộc có Kho đi/Kho đến
#         if not from_depot or not to_depot:
#             return JSONResponse({
#                 "valid": False,
#                 "message": "Cần chọn Kho đi và Kho đến trước"
#             })
        
#         imex_items = record_service.get_api_data(bill_id)
#         if not imex_items:
#             return JSONResponse({
#                 "valid": False,
#                 "message": "ID không hợp lệ"
#             })
        
        
#         # Lấy tất cả status từ các dòng sản phẩm
#         try:
#             all_statuses = {int(item.get("status", 0)) for item in imex_items}
#         except (ValueError, TypeError):
#             return JSONResponse({
#                 "valid": False,
#                 "message": "Lỗi dữ liệu status từ API"
#             })

#         # Kiểm tra xem có BẤT KỲ status nào hợp lệ không
#         valid_statuses = {3, 4, 5, 6}
#         is_valid_bill = any(status in valid_statuses for status in all_statuses)

#         if not is_valid_bill:
#             # Chỉ báo lỗi nếu TẤT CẢ các dòng đều không hợp lệ
#             return JSONResponse({
#                 "valid": False,
#                 "message": "ID chưa được duyệt"
#             })
        

#         # Vẫn dùng example_item để kiểm tra thông tin chung như kho
#         example_item = imex_items[0]
        
#         # Validate kho đi/kho đến với thông tin chung
#         if example_item.get("fromDepotId", "") != from_depot:
#             return JSONResponse({
#                 "valid": False,
#                 "message": "Không đúng kho đi"
#             })
        
#         if example_item.get("toDepotId", "") != to_depot:
#             return JSONResponse({
#                 "valid": False,
#                 "message": "Không đúng kho đến"
#             })
        
#         return JSONResponse({
#             "valid": True,
#             "message": "ID hợp lệ",
#             "from_depot": example_item.get("fromDepotName", ""),
#             "to_depot": example_item.get("toDepotName", "")
#         })
        
#     except Exception as e:
#         return JSONResponse({
#             "valid": False,
#             "message": "Lỗi kiểm tra"
#         })



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
        # ❌ BỎ: Không cần from_depot nữa
        # from_depot = body.get("from_depot")
        to_depot = body.get("to_depot") 
        handover_person = body.get("handover_person")
        transport_provider = body.get("transport_provider", "")
        bill_data = body.get("bill_data", [])
        
        # ✅ SỬA: Chỉ validate những thông tin cần thiết
        # ❌ BỎ: Không check from_depot nữa  
        # if not from_depot:
        #     return HTMLResponse('<div class="error">❌ Thiếu thông tin kho đi</div>')
        if not to_depot:
            return HTMLResponse('<div class="error">❌ Thiếu thông tin kho đến</div>')
        if not handover_person:
            return HTMLResponse('<div class="error">❌ Thiếu thông tin người bàn giao</div>')
        if not transport_provider:
            return HTMLResponse('<div class="error">❌ Thiếu thông tin đơn vị vận chuyển</div>')
        
        # ✅ SỬA: Validate số lượng bắt buộc cho tất cả Bill ID
        for item in bill_data:
            bill_id = item.get("bill_id")
            quantity = item.get("quantity", 0)
            if not quantity or quantity == 0:
                return HTMLResponse(f'<div class="error">❌ Bill ID "{bill_id}": Bắt buộc nhập số lượng bao/tải</div>')
        
        # ✅ SỬA: Chỉ validate kho đến
        to_valid, to_name = depot_service.validate_depot(to_depot)
        
        if not to_valid:
            return HTMLResponse(f'<div class="error">❌ Kho đến không hợp lệ: {to_name}</div>')
        
        # ✅ SỬA: Counters cho summary - không lưu từng thông báo nữa
        success_count = 0
        error_count = 0
        total_count = len(bill_data)
        error_samples = []  # Chỉ lưu mẫu lỗi để hiển thị
        
        # ✅ SỬA: Chuẩn bị data cho batch creation
        records_to_create = []
        valid_bill_ids = []
        
        for item in bill_data:
            bill_id = item.get("bill_id")
            quantity = item.get("quantity", 0)
            bag_quantity = item.get("bag_quantity", 0)
            group_id = item.get("group_id")
            
            imex_items = record_service.get_api_data(bill_id)
            if not imex_items:
                error_count += 1
                if len(error_samples) < 3:
                    error_samples.append(f"{bill_id}: ID không hợp lệ")
                continue
            
            try:
                all_statuses = {int(item.get("status", 0)) for item in imex_items}
            except (ValueError, TypeError):
                error_count += 1
                if len(error_samples) < 3:
                    error_samples.append(f"{bill_id}: Lỗi dữ liệu status")
                continue

            valid_statuses = {3, 4, 5, 6}
            is_valid_bill = any(status in valid_statuses for status in all_statuses)

            if not is_valid_bill:
                error_count += 1
                if len(error_samples) < 3:
                    error_samples.append(f"{bill_id}: ID chưa được duyệt")
                continue
            
            # Vẫn dùng example_item để kiểm tra thông tin chung
            example_item = imex_items[0]

            # ❌ BỎ: Không check kho đi nữa
            # if example_item.get("fromDepotId", "") != from_depot:
            #     error_count += 1
            #     if len(error_samples) < 3:
            #         error_samples.append(f"{bill_id}: Không đúng kho đi")
            #     continue
            
            # ✅ GIỮ: Vẫn check kho đến
            if example_item.get("toDepotId", "") != to_depot:
                error_count += 1
                if len(error_samples) < 3:
                    error_samples.append(f"{bill_id}: Không đúng kho đến")
                continue

            # ⭐ TÍNH TOÁN TỔNG SỐ LƯỢNG TỪ API
            total_required_quantity = 0
            total_damaged_quantity = 0
            total_approved_quantity = 0
            total_real_quantity = 0

            for detail_item in imex_items:
                try:
                    total_required_quantity += int(detail_item.get("requiredQuantity") or 0)
                    total_damaged_quantity += int(detail_item.get("damagedQuantity") or 0)
                    total_approved_quantity += int(detail_item.get("approvedQuantity") or 0)
                    total_real_quantity += int(detail_item.get("realQuantity") or 0)
                except (ValueError, TypeError):
                    continue

            # ⭐ CẬP NHẬT `record_data` - lấy kho đi từ API thay vì form
            record_data = {
                "ID": bill_id,
                "ID kho đi": example_item.get("fromDepotId", ""),  # ✅ Lấy từ API
                "Kho đi": example_item.get("fromDepotName", ""),   # ✅ Lấy từ API
                "ID kho đến": example_item.get("toDepotId", ""),
                "Kho đến": example_item.get("toDepotName", ""),
                "Số lượng": total_real_quantity,
                "Số lượng bao": int(quantity),
                "Người bàn giao": handover_person,
                "Đơn vị vận chuyển": transport_provider,
                "Ngày bàn giao": int(time.time() * 1000),

                # Thêm 4 trường mới từ API
                "Số lượng sản phẩm yêu cầu": total_required_quantity,
                "Số lượng sản phẩm hỏng": total_damaged_quantity,
                "Số lượng sản phẩm yêu cầu được duyệt": total_approved_quantity,
                "Số lượng sản phẩm yêu cầu được xác nhận": total_real_quantity
            }
            
            # ✅ THÊM: Thêm thông tin Group Bill nếu có
            if bag_quantity > 0:
                record_data["Số lượng túi"] = int(bag_quantity)
            
            if group_id:
                record_data["Group ID"] = group_id
            
            records_to_create.append(record_data)
            valid_bill_ids.append(bill_id)

        # ✅ SỬA: Sử dụng batch creation
        if records_to_create:
            batch_success, batch_message = record_service.batch_create_records(records_to_create)
            
            if batch_success:
                success_count = len(valid_bill_ids)
            else:
                logger.warning(f"Batch creation failed: {batch_message}")
                return HTMLResponse(f'<div class="error">❌ Lỗi khi tạo hàng loạt: {batch_message}</div>')

        # ✅ SỬA: Format kết quả ngắn gọn
        if success_count == total_count:
            result_html = f'<div class="success">📊 Hoàn thành: {success_count}/{total_count} bản ghi thành công</div>'
        elif success_count > 0 and error_count > 0:
            result_html = f'<div class="info">📊 Hoàn thành: {success_count}/{total_count} bản ghi thành công'
            result_html += f'<br>❌ {error_count} bản ghi thất bại'
            
            if error_samples:
                result_html += f'<br><small>Ví dụ lỗi: {"; ".join(error_samples)}'
                if error_count > len(error_samples):
                    result_html += f' và {error_count - len(error_samples)} lỗi khác'
                result_html += '</small>'
            
            result_html += '</div>'
        else:
            result_html = f'<div class="error">❌ Không thể tạo bản ghi nào ({error_count}/{total_count} thất bại)'
            
            if error_samples:
                result_html += f'<br>Lỗi: {"; ".join(error_samples)}'
                if error_count > len(error_samples):
                    result_html += f' và {error_count - len(error_samples)} lỗi khác'
            
            result_html += '</div>'
        
        logger.info(f"User {user.get('name')} bulk created {success_count}/{total_count} records")
        return HTMLResponse(result_html)
        
    except Exception as e:
        logger.error(f"Error in bulk create: {e}")
        return HTMLResponse(f'<div class="error">❌ Lỗi hệ thống: {str(e)}</div>')



# @router.post("/bulk-create-records", response_class=HTMLResponse)
# async def bulk_create_records(
#     request: Request,
#     record_service: RecordService = Depends(get_record_service),
#     depot_service: DepotService = Depends(get_depot_service)
# ):
#     """Create multiple records at once"""
#     user = get_current_user(request)
    
#     try:
#         body = await request.json()
#         from_depot = body.get("from_depot")
#         to_depot = body.get("to_depot") 
#         handover_person = body.get("handover_person")
#         transport_provider = body.get("transport_provider", "")
#         bill_data = body.get("bill_data", [])
        
#         # ✅ SỬA: Tất cả thông tin đều bắt buộc
#         if not from_depot:
#             return HTMLResponse('<div class="error">❌ Thiếu thông tin kho đi</div>')
#         if not to_depot:
#             return HTMLResponse('<div class="error">❌ Thiếu thông tin kho đến</div>')
#         if not handover_person:
#             return HTMLResponse('<div class="error">❌ Thiếu thông tin người bàn giao</div>')
#         if not transport_provider:
#             return HTMLResponse('<div class="error">❌ Thiếu thông tin đơn vị vận chuyển</div>')
        
#         # ✅ SỬA: Validate số lượng bắt buộc cho tất cả Bill ID
#         for item in bill_data:
#             bill_id = item.get("bill_id")
#             quantity = item.get("quantity", 0)
#             if not quantity or quantity == 0:
#                 return HTMLResponse(f'<div class="error">❌ Bill ID "{bill_id}": Bắt buộc nhập số lượng bao/tải</div>')
        
#         # Validate depots
#         from_valid, from_name = depot_service.validate_depot(from_depot)
#         to_valid, to_name = depot_service.validate_depot(to_depot)
        
#         if not from_valid:
#             return HTMLResponse(f'<div class="error">❌ Kho đi không hợp lệ: {from_name}</div>')
#         if not to_valid:
#             return HTMLResponse(f'<div class="error">❌ Kho đến không hợp lệ: {to_name}</div>')
        
#         # ✅ SỬA: Counters cho summary - không lưu từng thông báo nữa
#         success_count = 0
#         error_count = 0
#         total_count = len(bill_data)
#         error_samples = []  # Chỉ lưu mẫu lỗi để hiển thị
        
#         # ✅ SỬA: Chuẩn bị data cho batch creation
#         records_to_create = []
#         valid_bill_ids = []
        
#         for item in bill_data:
#             bill_id = item.get("bill_id")
#             quantity = item.get("quantity", 0)
#             # ✅ THÊM: Lấy thêm bag_quantity và group_id từ JavaScript
#             bag_quantity = item.get("bag_quantity", 0)
#             group_id = item.get("group_id")  # Group ID từ JavaScript (có thể là None cho single records)
            
#             imex_items = record_service.get_api_data(bill_id)
#             if not imex_items:
#                 error_count += 1
#                 if len(error_samples) < 3:  # Chỉ lưu 3 mẫu lỗi đầu tiên
#                     error_samples.append(f"{bill_id}: ID không hợp lệ")
#                 continue
            
#             try:
#                 all_statuses = {int(item.get("status", 0)) for item in imex_items}
#             except (ValueError, TypeError):
#                 error_count += 1
#                 if len(error_samples) < 3:
#                     error_samples.append(f"{bill_id}: Lỗi dữ liệu status")
#                 continue

#             valid_statuses = {3, 4, 5, 6}
#             is_valid_bill = any(status in valid_statuses for status in all_statuses)

#             if not is_valid_bill:
#                 error_count += 1
#                 if len(error_samples) < 3:
#                     error_samples.append(f"{bill_id}: ID chưa được duyệt")
#                 continue
            
            
#             # Vẫn dùng example_item để kiểm tra thông tin chung
#             example_item = imex_items[0]

#             if example_item.get("fromDepotId", "") != from_depot:
#                 error_count += 1
#                 if len(error_samples) < 3:
#                     error_samples.append(f"{bill_id}: Không đúng kho đi")
#                 continue
#             if example_item.get("toDepotId", "") != to_depot:
#                 error_count += 1
#                 if len(error_samples) < 3:
#                     error_samples.append(f"{bill_id}: Không đúng kho đến")
#                 continue

#             # Chuẩn bị record data cho batch creation với tên cột đã đồng bộ
#             record_data = {
#                 "ID": bill_id,
#                 "ID kho đi": example_item.get("fromDepotId", ""),
#                 "Kho đi": example_item.get("fromDepotName", ""),
#                 "ID kho đến": example_item.get("toDepotId", ""),
#                 "Kho đến": example_item.get("toDepotName", ""),
#                 "Số lượng": int(example_item.get("realQuantity") or 0),
#                 "Số lượng bao": int(quantity), # <<< ĐÃ SỬA TỪ "Số lượng tải"
#                 "Người bàn giao": handover_person,
#                 "Đơn vị vận chuyển": transport_provider,
#                 "Ngày bàn giao": int(time.time() * 1000)
#             }
            
#             # ✅ THÊM: Thêm thông tin Group Bill nếu có
#             if bag_quantity > 0:
#                 record_data["Số lượng túi"] = int(bag_quantity) # <<< ĐÃ SỬA TỪ "Số lượng bao"
            
#             if group_id:
#                 record_data["Group ID"] = group_id
            
#             records_to_create.append(record_data)
#             valid_bill_ids.append(bill_id)

#         # ✅ SỬA: Sử dụng batch creation thay vì tạo từng record
#         if records_to_create:
#             batch_success, batch_message = record_service.batch_create_records(records_to_create)
            
#             if batch_success:
#                 # Batch thành công - tất cả records hợp lệ đều được tạo
#                 success_count = len(valid_bill_ids)
#             else:
#                 # Batch thất bại - fallback về tạo từng record
#                 logger.warning(f"Batch creation failed: {batch_message}, falling back to individual creation")
#                 return HTMLResponse(f'<div class="error">❌ Lỗi batch create: {batch_message}</div>')

#         # ✅ SỬA: Format kết quả ngắn gọn - không liệt kê từng ID
#         if success_count == total_count:
#             # Tất cả thành công
#             result_html = f'<div class="success">📊 Hoàn thành: {success_count}/{total_count} bản ghi thành công</div>'
#         elif success_count > 0 and error_count > 0:
#             # Một phần thành công
#             result_html = f'<div class="info">📊 Hoàn thành: {success_count}/{total_count} bản ghi thành công'
#             result_html += f'<br>❌ {error_count} bản ghi thất bại'
            
#             # Chỉ hiển thị mẫu lỗi nếu có
#             if error_samples:
#                 result_html += f'<br><small>Ví dụ lỗi: {"; ".join(error_samples)}'
#                 if error_count > len(error_samples):
#                     result_html += f' và {error_count - len(error_samples)} lỗi khác'
#                 result_html += '</small>'
            
#             result_html += '</div>'
#         else:
#             # Tất cả thất bại
#             result_html = f'<div class="error">❌ Không thể tạo bản ghi nào ({error_count}/{total_count} thất bại)'
            
#             # Hiển thị mẫu lỗi
#             if error_samples:
#                 result_html += f'<br>Lỗi: {"; ".join(error_samples)}'
#                 if error_count > len(error_samples):
#                     result_html += f' và {error_count - len(error_samples)} lỗi khác'
            
#             result_html += '</div>'
        
#         logger.info(f"User {user.get('name')} bulk created {success_count}/{total_count} records")
#         return HTMLResponse(result_html)
        
#     except Exception as e:
#         logger.error(f"Error in bulk create: {e}")
#         return HTMLResponse(f'<div class="error">❌ Lỗi hệ thống: {str(e)}</div>')



@router.get("/health")
async def health_check():
    """Health check endpoint (public)"""
    return {"status": "ok", "service": "inventory-flow-tracker"}
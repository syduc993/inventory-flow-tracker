# src/routes/report_routes.py
from fastapi import APIRouter, Request, Query, Depends, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse
from datetime import datetime, timedelta
import logging
import io
import re
import unicodedata

from src.services.report_service import ReportService
from src.core.dependencies import get_current_user, templates, get_report_service

router = APIRouter(prefix="/reports", tags=["reports"])
logger = logging.getLogger(__name__)

def create_safe_filename(from_depot, to_depot, date_str):
    """Tạo tên file an toàn, loại bỏ ký tự đặc biệt tiếng Việt"""
    def normalize_text(text):
        # Normalize Unicode và convert sang ASCII
        normalized = unicodedata.normalize('NFD', text)
        # Loại bỏ dấu và chỉ giữ ASCII
        ascii_text = ''.join(c for c in normalized if unicodedata.category(c) != 'Mn')
        # Thay thế khoảng trắng và ký tự đặc biệt bằng _
        safe_text = re.sub(r'[^A-Za-z0-9]+', '_', ascii_text)
        # Loại bỏ _ ở đầu và cuối
        return safe_text.strip('_')
    
    
    safe_from = normalize_text(from_depot)
    safe_to = normalize_text(to_depot)
    
    # Tạo tên file
    filename = f"tuyen_{safe_from}_to_{safe_to}_{date_str or 'tat_ca'}.xlsx"
    
    # Đảm bảo filename không quá dài
    if len(filename) > 100:
        filename = f"tuyen_route_{date_str or 'tat_ca'}.xlsx"
    
    return filename

@router.get("/daily", response_class=HTMLResponse)
async def daily_report_page(
    request: Request,
    start_date: str = Query(None, description="Ngày bắt đầu (YYYY-MM-DD)"),
    end_date: str = Query(None, description="Ngày kết thúc (YYYY-MM-DD)"),
    employee: str = Query(None, description="ID nhân viên"),
    from_depot: str = Query(None, description="ID kho đi"),
    to_depot: str = Query(None, description="ID kho đến"),
    transport_provider: str = Query(None, description="Đơn vị vận chuyển"),
    report_service: ReportService = Depends(get_report_service)
):
    """Trang báo cáo với bộ lọc khoảng ngày"""
    user = get_current_user(request)
    
    # Nếu không có start_date, sử dụng ngày hôm nay
    if not start_date:
        today = datetime.now()
        start_date = today.strftime('%Y-%m-%d')
        end_date = start_date  # Mặc định cùng ngày
    
    # Nếu chỉ có start_date mà không có end_date
    if start_date and not end_date:
        end_date = start_date
    
    try:
        # Validate date format
        start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
        end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')
        
        # Đảm bảo start_date <= end_date
        if start_date_obj > end_date_obj:
            start_date_obj, end_date_obj = end_date_obj, start_date_obj
            start_date, end_date = end_date, start_date
        
        # Lấy dữ liệu báo cáo với khoảng ngày
        report_data = report_service.get_daily_report(
            start_date_str=start_date,
            end_date_str=end_date,
            employee_filter=employee,
            from_depot_filter=from_depot,
            to_depot_filter=to_depot,
            transport_provider_filter=transport_provider
        )
        
        # Lấy danh sách để làm filter options
        all_employees = report_service.get_all_employees()
        all_depots = report_service.get_all_depots()
        all_transport_providers = report_service.get_all_transport_providers()
        
        # Tạo context cho template
        context = {
            "request": request,
            "user": user,
            "start_date": start_date_obj,
            "end_date": end_date_obj,
            "start_date_str": start_date,
            "end_date_str": end_date,
            "report_data": report_data,
            "today": datetime.now().strftime('%Y-%m-%d'),
            "all_employees": all_employees,
            "all_depots": all_depots,
            "all_transport_providers": all_transport_providers,
            "current_filters": {
                "employee": employee,
                "from_depot": from_depot,
                "to_depot": to_depot,
                "transport_provider": transport_provider
            }
        }
        
        return templates.TemplateResponse("pages/daily_report.html", context)
        
    except ValueError:
        logger.error(f"Invalid date format: start={start_date}, end={end_date}")
        context = {
            "request": request,
            "user": user,
            "error": "Định dạng ngày không hợp lệ. Vui lòng sử dụng định dạng YYYY-MM-DD",
            "today": datetime.now().strftime('%Y-%m-%d'),
            "all_employees": [],
            "all_depots": [],
            "all_transport_providers": [],
            "current_filters": {}
        }
        return templates.TemplateResponse("pages/daily_report.html", context)
        
    except Exception as e:
        logger.error(f"Error generating date range report: {e}")
        context = {
            "request": request,
            "user": user,
            "error": f"Lỗi khi tạo báo cáo: {str(e)}",
            "today": datetime.now().strftime('%Y-%m-%d'),
            "all_employees": [],
            "all_depots": [],
            "all_transport_providers": [],  # ✅ THÊM
            "current_filters": {}
        }
        return templates.TemplateResponse("pages/daily_report.html", context)




# @router.get("/daily", response_class=HTMLResponse)
# async def daily_report_page(
#     request: Request,
#     start_date: str = Query(None, description="Ngày bắt đầu (YYYY-MM-DD)"),
#     end_date: str = Query(None, description="Ngày kết thúc (YYYY-MM-DD)"),
#     employee: str = Query(None, description="ID nhân viên"),
#     from_depot: str = Query(None, description="ID kho đi"),
#     to_depot: str = Query(None, description="ID kho đến"),
#     report_service: ReportService = Depends(get_report_service)
# ):
#     """Trang báo cáo với bộ lọc khoảng ngày"""
#     user = get_current_user(request)
    
#     # Nếu không có start_date, sử dụng ngày hôm nay
#     if not start_date:
#         today = datetime.now()
#         start_date = today.strftime('%Y-%m-%d')
#         end_date = start_date  # Mặc định cùng ngày
    
#     # Nếu chỉ có start_date mà không có end_date
#     if start_date and not end_date:
#         end_date = start_date
    
#     try:
#         # Validate date format
#         start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
#         end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')
        
#         # Đảm bảo start_date <= end_date
#         if start_date_obj > end_date_obj:
#             start_date_obj, end_date_obj = end_date_obj, start_date_obj
#             start_date, end_date = end_date, start_date
        
#         # Lấy dữ liệu báo cáo với khoảng ngày
#         report_data = report_service.get_daily_report(
#             start_date_str=start_date,
#             end_date_str=end_date,
#             employee_filter=employee,
#             from_depot_filter=from_depot,
#             to_depot_filter=to_depot
#         )
        
#         # Lấy danh sách để làm filter options
#         all_employees = report_service.get_all_employees()
#         all_depots = report_service.get_all_depots()
        
#         # Tạo context cho template
#         context = {
#             "request": request,
#             "user": user,
#             "start_date": start_date_obj,
#             "end_date": end_date_obj,
#             "start_date_str": start_date,
#             "end_date_str": end_date,
#             "report_data": report_data,
#             "today": datetime.now().strftime('%Y-%m-%d'),
#             "all_employees": all_employees,
#             "all_depots": all_depots,
#             "current_filters": {
#                 "employee": employee,
#                 "from_depot": from_depot,
#                 "to_depot": to_depot
#             }
#         }
        
#         return templates.TemplateResponse("pages/daily_report.html", context)
        
#     except ValueError:
#         logger.error(f"Invalid date format: start={start_date}, end={end_date}")
#         context = {
#             "request": request,
#             "user": user,
#             "error": "Định dạng ngày không hợp lệ. Vui lòng sử dụng định dạng YYYY-MM-DD",
#             "today": datetime.now().strftime('%Y-%m-%d'),
#             "all_employees": [],
#             "all_depots": [],
#             "current_filters": {}
#         }
#         return templates.TemplateResponse("pages/daily_report.html", context)
        
#     except Exception as e:
#         logger.error(f"Error generating date range report: {e}")
#         context = {
#             "request": request,
#             "user": user,
#             "error": f"Lỗi khi tạo báo cáo: {str(e)}",
#             "today": datetime.now().strftime('%Y-%m-%d'),
#             "all_employees": [],
#             "all_depots": [],
#             "current_filters": {}
#         }
#         return templates.TemplateResponse("pages/daily_report.html", context)





@router.get("/daily/export-route")
async def export_route_report(
    request: Request,
    from_depot: str = Query(..., description="Tên kho đi"),
    to_depot: str = Query(..., description="Tên kho đến"),
    start_date: str = Query(None, description="Ngày bắt đầu (YYYY-MM-DD)"),
    end_date: str = Query(None, description="Ngày kết thúc (YYYY-MM-DD)"),
    employee: str = Query(None, description="ID nhân viên"),
    transport_provider: str = Query(None, description="Đơn vị vận chuyển"),  # ✅ THÊM
    report_service: ReportService = Depends(get_report_service)
):
    """Xuất báo cáo theo tuyến đường trong khoảng ngày ra Excel"""
    user = get_current_user(request)
    
    try:
        excel_buffer, record_count = report_service.export_route_records_to_excel(
            from_depot=from_depot,
            to_depot=to_depot,
            start_date_str=start_date,
            end_date_str=end_date,
            employee_filter=employee,
            transport_provider_filter=transport_provider
        )
        
        if not excel_buffer:
            raise HTTPException(status_code=404, detail="Không có dữ liệu cho tuyến đường này")
        
        # Tạo tên file với khoảng ngày
        date_range = f"{start_date}_to_{end_date}" if start_date and end_date else "tat_ca"
        filename = create_safe_filename(from_depot, to_depot, date_range)
        
        return StreamingResponse(
            io.BytesIO(excel_buffer.read()),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        logger.error(f"Error exporting route report: {e}")
        raise HTTPException(status_code=500, detail=f"Lỗi xuất báo cáo tuyến: {str(e)}")



# @router.get("/daily/export-route")
# async def export_route_report(
#     request: Request,
#     from_depot: str = Query(..., description="Tên kho đi"),
#     to_depot: str = Query(..., description="Tên kho đến"),
#     start_date: str = Query(None, description="Ngày bắt đầu (YYYY-MM-DD)"),
#     end_date: str = Query(None, description="Ngày kết thúc (YYYY-MM-DD)"),
#     employee: str = Query(None, description="ID nhân viên"),
#     report_service: ReportService = Depends(get_report_service)
# ):
#     """Xuất báo cáo theo tuyến đường trong khoảng ngày ra Excel"""
#     user = get_current_user(request)
    
#     try:
#         excel_buffer, record_count = report_service.export_route_records_to_excel(
#             from_depot=from_depot,
#             to_depot=to_depot,
#             start_date_str=start_date,
#             end_date_str=end_date,
#             employee_filter=employee
#         )
        
#         if not excel_buffer:
#             raise HTTPException(status_code=404, detail="Không có dữ liệu cho tuyến đường này")
        
#         # Tạo tên file với khoảng ngày
#         date_range = f"{start_date}_to_{end_date}" if start_date and end_date else "tat_ca"
#         filename = create_safe_filename(from_depot, to_depot, date_range)
        
#         return StreamingResponse(
#             io.BytesIO(excel_buffer.read()),
#             media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
#             headers={"Content-Disposition": f"attachment; filename={filename}"}
#         )
        
#     except Exception as e:
#         logger.error(f"Error exporting route report: {e}")
#         raise HTTPException(status_code=500, detail=f"Lỗi xuất báo cáo tuyến: {str(e)}")




# @router.get("/daily", response_class=HTMLResponse)
# async def daily_report_page(
#     request: Request,
#     date: str = Query(None, description="Ngày báo cáo (YYYY-MM-DD)"),
#     employee: str = Query(None, description="ID nhân viên"),
#     from_depot: str = Query(None, description="ID kho đi"),
#     to_depot: str = Query(None, description="ID kho đến"),
#     report_service: ReportService = Depends(get_report_service)
# ):
#     """Trang báo cáo hàng ngày với bộ lọc"""
#     user = get_current_user(request)
    
#     # Nếu không có date parameter, sử dụng ngày hôm nay
#     if not date:
#         date = datetime.now().strftime('%Y-%m-%d')
    
#     try:
#         # Validate date format
#         report_date = datetime.strptime(date, '%Y-%m-%d')
        
#         # Lấy dữ liệu báo cáo với filters
#         report_data = report_service.get_daily_report(
#             user_id=None,  # Không filter theo user nữa
#             date_str=date,
#             employee_filter=employee,
#             from_depot_filter=from_depot,
#             to_depot_filter=to_depot
#         )
        
#         # Lấy danh sách để làm filter options
#         all_employees = report_service.get_all_employees()
#         all_depots = report_service.get_all_depots()
        
#         # Tạo context cho template
#         context = {
#             "request": request,
#             "user": user,
#             "report_date": report_date,
#             "date_str": date,
#             "report_data": report_data,
#             "today": datetime.now().strftime('%Y-%m-%d'),
#             "all_employees": all_employees,
#             "all_depots": all_depots,
#             "current_filters": {
#                 "employee": employee,
#                 "from_depot": from_depot,
#                 "to_depot": to_depot
#             }
#         }
        
#         return templates.TemplateResponse("pages/daily_report.html", context)
        
#     except ValueError:
#         logger.error(f"Invalid date format: {date}")
#         context = {
#             "request": request,
#             "user": user,
#             "error": "Định dạng ngày không hợp lệ. Vui lòng sử dụng định dạng YYYY-MM-DD",
#             "today": datetime.now().strftime('%Y-%m-%d'),
#             "all_employees": [],
#             "all_depots": [],
#             "current_filters": {}
#         }
#         return templates.TemplateResponse("pages/daily_report.html", context)
        
#     except Exception as e:
#         logger.error(f"Error generating daily report: {e}")
#         context = {
#             "request": request,
#             "user": user,
#             "error": f"Lỗi khi tạo báo cáo: {str(e)}",
#             "today": datetime.now().strftime('%Y-%m-%d'),
#             "all_employees": [],
#             "all_depots": [],
#             "current_filters": {}
#         }
#         return templates.TemplateResponse("pages/daily_report.html", context)

# @router.get("/daily/export-route")
# async def export_route_report(
#     request: Request,
#     from_depot: str = Query(..., description="Tên kho đi"),
#     to_depot: str = Query(..., description="Tên kho đến"),
#     date: str = Query(None, description="Ngày báo cáo (YYYY-MM-DD)"),
#     employee: str = Query(None, description="ID nhân viên"),
#     report_service: ReportService = Depends(get_report_service)
# ):
#     """Xuất báo cáo theo tuyến đường cụ thể ra Excel"""
#     user = get_current_user(request)
    
#     try:
#         excel_buffer, record_count = report_service.export_route_records_to_excel(
#             from_depot=from_depot,
#             to_depot=to_depot,
#             user_id=None,
#             date_str=date,
#             employee_filter=employee
#         )
        
#         if not excel_buffer:
#             raise HTTPException(status_code=404, detail="Không có dữ liệu cho tuyến đường này")
        
#         # Sử dụng helper function để tạo tên file an toàn
#         filename = create_safe_filename(from_depot, to_depot, date)
        
#         return StreamingResponse(
#             io.BytesIO(excel_buffer.read()),
#             media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
#             headers={"Content-Disposition": f"attachment; filename={filename}"}
#         )
        
#     except Exception as e:
#         logger.error(f"Error exporting route report: {e}")
#         raise HTTPException(status_code=500, detail=f"Lỗi xuất báo cáo tuyến: {str(e)}")

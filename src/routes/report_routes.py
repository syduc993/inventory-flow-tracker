# # src/routes/report_routes.py - Report Routes
# from fastapi import APIRouter, Request, Query, Depends
# from fastapi.responses import HTMLResponse
# from datetime import datetime, timedelta
# import logging

# from src.services.report_service import ReportService
# from src.core.dependencies import get_current_user, templates, get_report_service

# router = APIRouter(prefix="/reports", tags=["reports"])
# logger = logging.getLogger(__name__)

# @router.get("/daily", response_class=HTMLResponse)
# async def daily_report_page(
#     request: Request,
#     date: str = Query(None, description="Ngày báo cáo (YYYY-MM-DD)"),
#     report_service: ReportService = Depends(get_report_service)
# ):
#     """Trang báo cáo hàng ngày của nhân viên"""
#     user = get_current_user(request)
    
#     # Nếu không có date parameter, sử dụng ngày hôm nay
#     if not date:
#         date = datetime.now().strftime('%Y-%m-%d')
    
#     try:
#         # Validate date format
#         report_date = datetime.strptime(date, '%Y-%m-%d')
        
#         # Lấy dữ liệu báo cáo
#         report_data = report_service.get_daily_report(user['user_id'], date)
        
#         # Tạo context cho template
#         context = {
#             "request": request,
#             "user": user,
#             "report_date": report_date,
#             "date_str": date,
#             "report_data": report_data,
#             "today": datetime.now().strftime('%Y-%m-%d')
#         }
        
#         return templates.TemplateResponse("pages/daily_report.html", context)
        
#     except ValueError:
#         logger.error(f"Invalid date format: {date}")
#         context = {
#             "request": request,
#             "user": user,
#             "error": "Định dạng ngày không hợp lệ. Vui lòng sử dụng định dạng YYYY-MM-DD",
#             "today": datetime.now().strftime('%Y-%m-%d')
#         }
#         return templates.TemplateResponse("pages/daily_report.html", context)
        
#     except Exception as e:
#         logger.error(f"Error generating daily report: {e}")
#         context = {
#             "request": request,
#             "user": user,
#             "error": f"Lỗi khi tạo báo cáo: {str(e)}",
#             "today": datetime.now().strftime('%Y-%m-%d')
#         }
#         return templates.TemplateResponse("pages/daily_report.html", context)

# @router.get("/weekly", response_class=HTMLResponse)
# async def weekly_report_page(
#     request: Request,
#     week_start: str = Query(None, description="Ngày bắt đầu tuần (YYYY-MM-DD)"),
#     report_service: ReportService = Depends(get_report_service)
# ):
#     """Trang báo cáo tuần của nhân viên"""
#     user = get_current_user(request)
    
#     # Nếu không có week_start, sử dụng tuần hiện tại
#     if not week_start:
#         today = datetime.now()
#         start_of_week = today - timedelta(days=today.weekday())
#         week_start = start_of_week.strftime('%Y-%m-%d')
    
#     try:
#         # Validate date format
#         start_date = datetime.strptime(week_start, '%Y-%m-%d')
#         end_date = start_date + timedelta(days=6)
        
#         # Lấy dữ liệu báo cáo tuần
#         report_data = report_service.get_weekly_report(user['user_id'], week_start)
        
#         context = {
#             "request": request,
#             "user": user,
#             "start_date": start_date,
#             "end_date": end_date,
#             "week_start": week_start,
#             "report_data": report_data
#         }
        
#         return templates.TemplateResponse("pages/weekly_report.html", context)
        
#     except Exception as e:
#         logger.error(f"Error generating weekly report: {e}")
#         context = {
#             "request": request,
#             "user": user,
#             "error": f"Lỗi khi tạo báo cáo tuần: {str(e)}"
#         }
#         return templates.TemplateResponse("pages/weekly_report.html", context)


# src/routes/report_routes.py
from fastapi import APIRouter, Request, Query, Depends
from fastapi.responses import HTMLResponse
from datetime import datetime, timedelta
import logging

from src.services.report_service import ReportService
from src.core.dependencies import get_current_user, templates, get_report_service

router = APIRouter(prefix="/reports", tags=["reports"])
logger = logging.getLogger(__name__)

@router.get("/daily", response_class=HTMLResponse)
async def daily_report_page(
    request: Request,
    date: str = Query(None, description="Ngày báo cáo (YYYY-MM-DD)"),
    employee: str = Query(None, description="ID nhân viên"),
    from_depot: str = Query(None, description="ID kho đi"),
    to_depot: str = Query(None, description="ID kho đến"),
    report_service: ReportService = Depends(get_report_service)
):
    """Trang báo cáo hàng ngày với bộ lọc"""
    user = get_current_user(request)
    
    # Nếu không có date parameter, sử dụng ngày hôm nay
    if not date:
        date = datetime.now().strftime('%Y-%m-%d')
    
    try:
        # Validate date format
        report_date = datetime.strptime(date, '%Y-%m-%d')
        
        # Lấy dữ liệu báo cáo với filters
        report_data = report_service.get_daily_report(
            user_id=None,  # Không filter theo user nữa
            date_str=date,
            employee_filter=employee,
            from_depot_filter=from_depot,
            to_depot_filter=to_depot
        )
        
        # Lấy danh sách để làm filter options
        all_employees = report_service.get_all_employees()
        all_depots = report_service.get_all_depots()
        
        # Tạo context cho template
        context = {
            "request": request,
            "user": user,
            "report_date": report_date,
            "date_str": date,
            "report_data": report_data,
            "today": datetime.now().strftime('%Y-%m-%d'),
            "all_employees": all_employees,
            "all_depots": all_depots,
            "current_filters": {
                "employee": employee,
                "from_depot": from_depot,
                "to_depot": to_depot
            }
        }
        
        return templates.TemplateResponse("pages/daily_report.html", context)
        
    except ValueError:
        logger.error(f"Invalid date format: {date}")
        context = {
            "request": request,
            "user": user,
            "error": "Định dạng ngày không hợp lệ. Vui lòng sử dụng định dạng YYYY-MM-DD",
            "today": datetime.now().strftime('%Y-%m-%d'),
            "all_employees": [],
            "all_depots": [],
            "current_filters": {}
        }
        return templates.TemplateResponse("pages/daily_report.html", context)
        
    except Exception as e:
        logger.error(f"Error generating daily report: {e}")
        context = {
            "request": request,
            "user": user,
            "error": f"Lỗi khi tạo báo cáo: {str(e)}",
            "today": datetime.now().strftime('%Y-%m-%d'),
            "all_employees": [],
            "all_depots": [],
            "current_filters": {}
        }
        return templates.TemplateResponse("pages/daily_report.html", context)

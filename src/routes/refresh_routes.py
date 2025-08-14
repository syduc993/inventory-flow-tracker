# src/routes/refresh_routes.py - Data Refresh Routes
from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
import time
import logging

from src.services.employee_service import EmployeeService
from src.services.transport_service import TransportProviderService
from src.services.depot_service import DepotService
from src.core.dependencies import get_current_user, get_employee_service, get_transport_service, get_depot_service

router = APIRouter(prefix="/refresh", tags=["refresh"])
logger = logging.getLogger(__name__)

@router.post("/employees", response_class=HTMLResponse)
async def refresh_employees_endpoint(
    request: Request,
    employee_service: EmployeeService = Depends(get_employee_service)
):
    """Endpoint để làm mới danh sách nhân viên"""
    user = get_current_user(request)
    logger.info(f"User {user.get('name')} refreshing employees")
    
    try:
        time.sleep(0.5)
        
        success, message = employee_service.refresh_employees()
        
        if success:
            return HTMLResponse(f"<div class='success'>✅ {message}</div>")
        else:
            return HTMLResponse(f"<div class='error'>❌ Lỗi: {message}</div>")
            
    except Exception as e:
        return HTMLResponse(f"<div class='error'>❌ Lỗi hệ thống: {str(e)}</div>")

@router.post("/transport-providers", response_class=HTMLResponse)
async def refresh_transport_providers_endpoint(
    request: Request,
    transport_service: TransportProviderService = Depends(get_transport_service)
):
    """Endpoint để làm mới danh sách đơn vị vận chuyển"""
    user = get_current_user(request)
    logger.info(f"User {user.get('name')} refreshing transport providers")
    
    try:
        time.sleep(0.5)
        
        success, message = transport_service.refresh_transport_providers("tblyiELQIi6M1j1r")
        
        if success:
            return HTMLResponse(f"<div class='success'>✅ {message}</div>")
        else:
            return HTMLResponse(f"<div class='error'>❌ Lỗi: {message}</div>")
            
    except Exception as e:
        return HTMLResponse(f"<div class='error'>❌ Lỗi hệ thống: {str(e)}</div>")

@router.post("/depots", response_class=HTMLResponse)
async def refresh_depots_endpoint(
    request: Request,
    depot_service: DepotService = Depends(get_depot_service)
):
    """Endpoint để làm mới danh sách depot"""
    user = get_current_user(request)
    logger.info(f"User {user.get('name')} refreshing depots")
    
    try:
        time.sleep(0.5)
        
        success, message = depot_service.refresh_depots()
        
        if success:
            return HTMLResponse(f"<div class='success'>✅ {message}</div>")
        else:
            return HTMLResponse(f"<div class='error'>❌ Lỗi: {message}</div>")
            
    except Exception as e:
        return HTMLResponse(f"<div class='error'>❌ Lỗi hệ thống: {str(e)}</div>")

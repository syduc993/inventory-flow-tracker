# src/routes/auth_routes.py - Authentication Routes
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
import secrets
import logging

from src.auth.lark_oauth import LarkOAuthService
from src.auth.session_manager import SessionManager
from src.utils.config import AUTH_CONFIG
from src.core.dependencies import templates

router = APIRouter(prefix="/auth", tags=["auth"])
logger = logging.getLogger(__name__)

# Initialize services
lark_oauth = LarkOAuthService(
    app_id=AUTH_CONFIG['LARK_APP_ID'],
    app_secret=AUTH_CONFIG['LARK_APP_SECRET'],
    base_url=AUTH_CONFIG['LARK_BASE_URL'],
    redirect_uri=AUTH_CONFIG['REDIRECT_URI']
)

session_manager = SessionManager(
    secret_key=AUTH_CONFIG['SECRET_KEY'],
    expire_hours=AUTH_CONFIG['SESSION_EXPIRE_HOURS']
)

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Trang đăng nhập"""
    return templates.TemplateResponse("auth/login.html", {"request": request})

@router.get("/lark")
async def login_with_lark():
    """Redirect đến Lark OAuth"""
    state = secrets.token_urlsafe(32)
    oauth_url = lark_oauth.generate_oauth_url(state)
    
    logger.info(f"🔗 Generated OAuth URL: {oauth_url}")
    
    response = RedirectResponse(url=oauth_url, status_code=302)
    response.set_cookie("oauth_state", state, httponly=True, max_age=600)
    return response

@router.get("/callback")
async def auth_callback(request: Request, code: str = None, state: str = None, error: str = None):
    """OAuth callback từ Lark"""
    if error:
        logger.error(f"OAuth error: {error}")
        return templates.TemplateResponse("auth/unauthorized.html", {
            "request": request,
            "error": "Đăng nhập thất bại từ Lark"
        })
    
    if not code:
        return templates.TemplateResponse("auth/unauthorized.html", {
            "request": request,
            "error": "Không nhận được mã xác thực"
        })
    
    try:
        # Step 1: Exchange code for token
        user_access_token = await lark_oauth.exchange_code_for_token(code)
        if not user_access_token:
            raise Exception("Không thể lấy access token")
        
        # Step 2: Get user info
        user_info = await lark_oauth.get_user_info(user_access_token)
        if not user_info:
            raise Exception("Không thể lấy thông tin user")
        
        # Step 3: Check permission
        open_id = user_info.get('open_id')
        has_permission, message = await lark_oauth.check_user_permission(
            open_id, 
            AUTH_CONFIG['AUTH_APP_TOKEN'], 
            AUTH_CONFIG['AUTH_TABLE_ID']
        )
        
        if not has_permission:
            return templates.TemplateResponse("auth/unauthorized.html", {
                "request": request,
                "error": message,
                "user_name": user_info.get('name', 'Unknown')
            })
        
        # Step 4: Create session
        session_token = session_manager.create_session_token(user_info)
        
        # Step 5: Redirect with session
        response = RedirectResponse(url="/", status_code=302)
        response.set_cookie(
            "session_token",
            session_token,
            httponly=True,
            secure=False,
            samesite="lax",
            max_age=AUTH_CONFIG['SESSION_EXPIRE_HOURS'] * 60 * 60
        )
        response.delete_cookie("oauth_state")
        
        logger.info(f"User {user_info.get('name')} đăng nhập thành công")
        return response
        
    except Exception as e:
        logger.error(f"Error during auth callback: {e}")
        return templates.TemplateResponse("auth/unauthorized.html", {
            "request": request,
            "error": f"Lỗi hệ thống: {str(e)}"
        })

@router.post("/logout")
async def logout():
    """Đăng xuất"""
    response = RedirectResponse(url="/login", status_code=302)
    response.delete_cookie("session_token")
    return response

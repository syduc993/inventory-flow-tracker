# src/core/app.py - Application Factory
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from src.auth.auth_middleware import AuthMiddleware
from src.auth.lark_oauth import LarkOAuthService
from src.auth.session_manager import SessionManager
from src.utils.config import AUTH_CONFIG

from src.routes import auth_routes, api_routes, record_routes, refresh_routes, report_routes

def create_app():
    """Create and configure FastAPI application"""
    app = FastAPI(title="IMEX Distribution API")
    
    # Static files
    app.mount("/static", StaticFiles(directory="static"), name="static")
    
    # ✅ THÊM: Templates setup
    templates = Jinja2Templates(directory="templates")
    
    # ✅ THÊM: Direct login route (không có prefix)
    @app.get("/login", response_class=HTMLResponse)
    async def login_page(request: Request):
        """Trang đăng nhập trực tiếp"""
        return templates.TemplateResponse("auth/login.html", {"request": request})
    
    # Setup authentication
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
    
    # Add authentication middleware
    app.add_middleware(
        AuthMiddleware,
        session_manager=session_manager,
        public_paths=["/login", "/auth/callback", "/auth/lark", "/health", "/static", "/favicon.ico"]
    )
    
    # Include routers
    app.include_router(auth_routes.router)
    app.include_router(api_routes.router)
    app.include_router(record_routes.router)
    app.include_router(refresh_routes.router)
    app.include_router(report_routes.router)
    
    return app

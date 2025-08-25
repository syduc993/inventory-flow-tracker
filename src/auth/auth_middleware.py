# # src/auth/auth_middleware.py
# import logging
# from typing import List
# from fastapi import Request, Response, HTTPException
# from fastapi.responses import RedirectResponse
# from starlette.middleware.base import BaseHTTPMiddleware
# from .session_manager import SessionManager

# logger = logging.getLogger(__name__)

# class AuthMiddleware(BaseHTTPMiddleware):
#     def __init__(self, app, session_manager: SessionManager, public_paths: List[str] = None):
#         super().__init__(app)
#         self.session_manager = session_manager
#         # ✅ SỬA: Sync public paths với main.py để tránh inconsistency
#         self.public_paths = public_paths or [
#             "/login",
#             "/auth/callback",
#             "/auth/lark",  # ← THÊM: Đảm bảo consistent với main.py
#             "/health",
#             "/static",
#             "/favicon.ico"
#         ]

#     def is_public_path(self, path: str) -> bool:
#         """Kiểm tra xem path có phải là public không"""
#         return any(path.startswith(public_path) for public_path in self.public_paths)

#     async def dispatch(self, request: Request, call_next):
#         # Skip auth cho public paths
#         if self.is_public_path(request.url.path):
#             return await call_next(request)

#         # Lấy session token từ cookie
#         session_token = request.cookies.get("session_token")
        
#         if not session_token:
#             logger.info(f"No session token, redirecting to login: {request.url.path}")
#             return RedirectResponse(url="/login", status_code=302)

#         # Verify token
#         user_info = self.session_manager.get_user_from_token(session_token)
#         if not user_info:
#             logger.info(f"Invalid session token, redirecting to login: {request.url.path}")
#             response = RedirectResponse(url="/login", status_code=302)
#             response.delete_cookie("session_token")
#             return response

#         # Thêm user info vào request state
#         request.state.user = user_info
        
#         # Try to refresh token if needed
#         refreshed_token = self.session_manager.refresh_token_if_needed(session_token)
        
#         response = await call_next(request)
        
#         # Set refreshed token if available
#         if refreshed_token and refreshed_token != session_token:
#             response.set_cookie(
#                 "session_token", 
#                 refreshed_token, 
#                 httponly=True,
#                 secure=False,  # Set True in production with HTTPS
#                 samesite="lax",
#                 max_age=24*60*60  # 24 hours
#             )
#             logger.info("Session token refreshed and set in cookie")

#         return response

# src/auth/auth_middleware.py


import logging
from typing import List
from fastapi import Request, Response, HTTPException
from fastapi.responses import RedirectResponse
from starlette.middleware.base import BaseHTTPMiddleware
from .session_manager import SessionManager

logger = logging.getLogger(__name__)


class AuthMiddleware(BaseHTTPMiddleware):
    """
    Middleware xử lý authentication cho toàn bộ ứng dụng FastAPI
    
    Chức năng chính:
    - Kiểm tra session token từ cookie cho tất cả requests
    - Redirect user đến trang login nếu chưa authenticate
    - Bỏ qua kiểm tra cho các public paths
    - Tự động refresh token khi cần thiết
    - Inject user info vào request state
    
    Flow xử lý:
    1. Kiểm tra xem path có phải public không
    2. Lấy session token từ cookie
    3. Verify token với SessionManager
    4. Thêm user info vào request state
    5. Refresh token nếu cần và set cookie mới
    """
    
    def __init__(self, app, session_manager: SessionManager, public_paths: List[str] = None):
        """
        Khởi tạo Authentication Middleware
        
        Args:
            app: FastAPI application instance
            session_manager: SessionManager instance để verify tokens
            public_paths: List các paths không cần authentication
        """
        super().__init__(app)
        self.session_manager = session_manager
        
        # ✅ STEP 1: Thiết lập danh sách public paths mặc định
        self.public_paths = public_paths or [
            "/login",           # Trang đăng nhập
            "/auth/callback",   # OAuth callback endpoint
            "/auth/lark",       # ← THÊM: Đảm bảo consistent với main.py
            "/health",          # Health check endpoint
            "/static",          # Static files (CSS, JS, images)
            "/favicon.ico"      # Favicon request
        ]

    def is_public_path(self, path: str) -> bool:
        """
        Kiểm tra xem path có phải là public path không cần authentication
        
        Args:
            path: Request path cần kiểm tra
            
        Returns:
            bool: True nếu là public path, False nếu cần authentication
            
        Logic:
        - Sử dụng startswith để match prefix paths (vd: /static/*)
        - Return True ngay khi tìm thấy match đầu tiên
        """
        # ✅ STEP 1: Duyệt qua từng public path để kiểm tra
        return any(path.startswith(public_path) for public_path in self.public_paths)

    async def dispatch(self, request: Request, call_next):
        """
        Main middleware function xử lý authentication cho mỗi request
        
        Args:
            request: FastAPI Request object
            call_next: Next middleware/route handler
            
        Returns:
            Response: HTTP response (có thể là redirect hoặc từ route handler)
            
        Flow xử lý:
        1. Kiểm tra public path → skip auth nếu đúng
        2. Lấy session token từ cookie
        3. Verify token với SessionManager
        4. Inject user info vào request state
        5. Process request và refresh token nếu cần
        6. Set refreshed token vào cookie response
        
        Error Handling:
        - No token → redirect to /login
        - Invalid token → redirect to /login + clear cookie
        - Token refresh fails → log warning nhưng vẫn proceed
        """
        
        # ✅ STEP 1: Bỏ qua authentication cho public paths
        if self.is_public_path(request.url.path):
            # Không cần auth cho public endpoints
            return await call_next(request)

        # ✅ STEP 2: Lấy session token từ HTTP cookie
        session_token = request.cookies.get("session_token")
        
        # ❌ ERROR CASE 1: Không có session token
        if not session_token:
            logger.info(f"🔍 No session token, redirecting to login: {request.url.path}")
            return RedirectResponse(url="/login", status_code=302)

        # ✅ STEP 3: Verify token với SessionManager
        user_info = self.session_manager.get_user_from_token(session_token)
        
        # ❌ ERROR CASE 2: Token không hợp lệ hoặc đã hết hạn
        if not user_info:
            logger.info(f"❌ Invalid session token, redirecting to login: {request.url.path}")
            # Tạo redirect response và xóa cookie không hợp lệ
            response = RedirectResponse(url="/login", status_code=302)
            response.delete_cookie("session_token")
            return response

        # ✅ STEP 4: Inject user info vào request state để routes có thể sử dụng
        request.state.user = user_info
        
        # ✅ STEP 5: Thử refresh token nếu sắp hết hạn
             # Check và refresh token proactively
        refreshed_token = self.session_manager.refresh_token_if_needed(session_token)
        
        # ✅ STEP 6: Tiếp tục xử lý request với middleware/route handler tiếp theo
        response = await call_next(request)
        
        # ✅ STEP 7: Set refreshed token vào cookie nếu có token mới
        if refreshed_token and refreshed_token != session_token:
            # Cập nhật cookie với token mới được refresh
            response.set_cookie(
                "session_token", 
                refreshed_token, 
                httponly=True,      # Bảo mật: chỉ server có thể đọc
                secure=False,       # Set True in production với HTTPS
                samesite="lax",     # CSRF protection
                max_age=24*60*60    # 24 giờ expiry
            )
            logger.info("✅ Session token refreshed and set in cookie")

        return response


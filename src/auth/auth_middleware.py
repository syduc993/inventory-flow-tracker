# src/auth/auth_middleware.py
import logging
from typing import List
from fastapi import Request, Response, HTTPException
from fastapi.responses import RedirectResponse
from starlette.middleware.base import BaseHTTPMiddleware
from .session_manager import SessionManager

logger = logging.getLogger(__name__)

class AuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, session_manager: SessionManager, public_paths: List[str] = None):
        super().__init__(app)
        self.session_manager = session_manager
        # ✅ SỬA: Sync public paths với main.py để tránh inconsistency
        self.public_paths = public_paths or [
            "/login",
            "/auth/callback",
            "/auth/lark",  # ← THÊM: Đảm bảo consistent với main.py
            "/health",
            "/static",
            "/favicon.ico"
        ]

    def is_public_path(self, path: str) -> bool:
        """Kiểm tra xem path có phải là public không"""
        return any(path.startswith(public_path) for public_path in self.public_paths)

    async def dispatch(self, request: Request, call_next):
        # Skip auth cho public paths
        if self.is_public_path(request.url.path):
            return await call_next(request)

        # Lấy session token từ cookie
        session_token = request.cookies.get("session_token")
        
        if not session_token:
            logger.info(f"No session token, redirecting to login: {request.url.path}")
            return RedirectResponse(url="/login", status_code=302)

        # Verify token
        user_info = self.session_manager.get_user_from_token(session_token)
        if not user_info:
            logger.info(f"Invalid session token, redirecting to login: {request.url.path}")
            response = RedirectResponse(url="/login", status_code=302)
            response.delete_cookie("session_token")
            return response

        # Thêm user info vào request state
        request.state.user = user_info
        
        # Try to refresh token if needed
        refreshed_token = self.session_manager.refresh_token_if_needed(session_token)
        
        response = await call_next(request)
        
        # Set refreshed token if available
        if refreshed_token and refreshed_token != session_token:
            response.set_cookie(
                "session_token", 
                refreshed_token, 
                httponly=True,
                secure=False,  # Set True in production with HTTPS
                samesite="lax",
                max_age=24*60*60  # 24 hours
            )
            logger.info("Session token refreshed and set in cookie")

        return response

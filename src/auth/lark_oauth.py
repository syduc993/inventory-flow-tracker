# src/auth/lark_oauth.py
import httpx
import json
import logging
from typing import Optional, Tuple, Dict, Any
from urllib.parse import urlencode
import time

logger = logging.getLogger(__name__)

class LarkOAuthService:
    def __init__(self, app_id: str, app_secret: str, base_url: str, redirect_uri: str):
        self.app_id = app_id
        self.app_secret = app_secret
        self.base_url = base_url
        self.redirect_uri = redirect_uri
        self._app_access_token = None
        self._token_expires_at = 0

    def generate_oauth_url(self, state: str = None) -> str:
        """Tạo URL OAuth để redirect user đến Lark"""
        params = {
            'app_id': self.app_id,
            'redirect_uri': self.redirect_uri,
            'response_type': 'code',
            'scope': 'contact:user.id:readonly'
        }
        if state:
            params['state'] = state
        
        oauth_url = f"{self.base_url}/authen/v1/authorize?" + urlencode(params)
        logger.info(f"Generated OAuth URL: {oauth_url}")
        return oauth_url

    async def get_app_access_token(self) -> Optional[str]:
        """Lấy app_access_token từ Lark"""
        # Check cache
        if self._app_access_token and time.time() < self._token_expires_at:
            return self._app_access_token

        url = f"{self.base_url}/auth/v3/app_access_token/internal"
        payload = {
            "app_id": self.app_id,
            "app_secret": self.app_secret
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload, timeout=10)
                response.raise_for_status()
                
                data = response.json()
                if data.get('code') == 0:
                    token = data.get('app_access_token')
                    expires_in = data.get('expire', 7200)  # Default 2 hours
                    
                    # Cache token
                    self._app_access_token = token
                    self._token_expires_at = time.time() + expires_in - 300  # 5 min buffer
                    
                    logger.info("Successfully obtained app_access_token")
                    return token
                else:
                    logger.error(f"Failed to get app_access_token: {data}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error getting app_access_token: {e}")
            return None

    async def exchange_code_for_token(self, code: str) -> Optional[str]:
        """Đổi authorization code thành user_access_token"""
        app_token = await self.get_app_access_token()
        if not app_token:
            return None

        url = f"{self.base_url}/authen/v1/oidc/access_token"
        headers = {
            "Authorization": f"Bearer {app_token}",
            "Content-Type": "application/json"
        }
        payload = {
            "grant_type": "authorization_code",
            "code": code
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, headers=headers, json=payload, timeout=10)
                response.raise_for_status()
                
                data = response.json()
                if data.get('code') == 0:
                    return data.get('data', {}).get('access_token')
                else:
                    logger.error(f"Failed to exchange code: {data}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error exchanging code: {e}")
            return None

    async def get_user_info(self, user_access_token: str) -> Optional[Dict[str, Any]]:
        """Lấy thông tin user từ user_access_token"""
        url = f"{self.base_url}/authen/v1/user_info"
        headers = {
            "Authorization": f"Bearer {user_access_token}"
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers, timeout=10)
                response.raise_for_status()
                
                data = response.json()
                if data.get('code') == 0:
                    return data.get('data')
                else:
                    logger.error(f"Failed to get user info: {data}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error getting user info: {e}")
            return None

    async def check_user_permission(self, open_id: str, app_token: str, table_id: str) -> Tuple[bool, str]:
        """Kiểm tra quyền user trong Larkbase table"""
        app_access_token = await self.get_app_access_token()
        if not app_access_token:
            return False, "Không thể xác thực với Lark"

        url = f"{self.base_url}/bitable/v1/apps/{app_token}/tables/{table_id}/records/search"
        headers = {
            "Authorization": f"Bearer {app_access_token}",
            "Content-Type": "application/json"
        }
        payload = {
            "filter": {
                "conjunction": "and",
                "conditions": [
                    {
                        "field_name": "Người",
                        "operator": "contains", 
                        "value": [open_id]
                    },
                    {
                        "field_name": "Trạng thái",
                        "operator": "is",
                        "value": ["Kích hoạt"]
                    }
                ]
            }
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, headers=headers, json=payload, timeout=10)
                response.raise_for_status()
                
                data = response.json()
                if data.get('code') == 0:
                    items = data.get('data', {}).get('items', [])
                    if items:
                        return True, "User có quyền truy cập"
                    else:
                        return False, "User không có quyền truy cập hoặc chưa được kích hoạt"
                else:
                    logger.error(f"Failed to check permissions: {data}")
                    return False, f"Lỗi kiểm tra quyền: {data.get('msg', 'Unknown error')}"
                    
        except Exception as e:
            logger.error(f"Error checking permissions: {e}")
            return False, f"Lỗi hệ thống: {str(e)}"

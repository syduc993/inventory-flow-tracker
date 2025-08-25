# # src/auth/lark_oauth.py
# import httpx
# import json
# import logging
# from typing import Optional, Tuple, Dict, Any
# from urllib.parse import urlencode
# import time

# logger = logging.getLogger(__name__)

# class LarkOAuthService:
#     def __init__(self, app_id: str, app_secret: str, base_url: str, redirect_uri: str):
#         self.app_id = app_id
#         self.app_secret = app_secret
#         self.base_url = base_url
#         self.redirect_uri = redirect_uri
#         self._app_access_token = None
#         self._token_expires_at = 0

#     def generate_oauth_url(self, state: str = None) -> str:
#         """Tạo URL OAuth để redirect user đến Lark"""
#         params = {
#             'app_id': self.app_id,
#             'redirect_uri': self.redirect_uri,
#             'response_type': 'code',
#             'scope': 'contact:user.id:readonly'
#         }
#         if state:
#             params['state'] = state
        
#         oauth_url = f"{self.base_url}/authen/v1/authorize?" + urlencode(params)
#         logger.info(f"Generated OAuth URL: {oauth_url}")
#         return oauth_url

#     async def get_app_access_token(self) -> Optional[str]:
#         """Lấy app_access_token từ Lark"""
#         # Check cache
#         if self._app_access_token and time.time() < self._token_expires_at:
#             return self._app_access_token

#         url = f"{self.base_url}/auth/v3/app_access_token/internal"
#         payload = {
#             "app_id": self.app_id,
#             "app_secret": self.app_secret
#         }
        
#         try:
#             async with httpx.AsyncClient() as client:
#                 response = await client.post(url, json=payload, timeout=10)
#                 response.raise_for_status()
                
#                 data = response.json()
#                 if data.get('code') == 0:
#                     token = data.get('app_access_token')
#                     expires_in = data.get('expire', 7200)  # Default 2 hours
                    
#                     # Cache token
#                     self._app_access_token = token
#                     self._token_expires_at = time.time() + expires_in - 300  # 5 min buffer
                    
#                     logger.info("Successfully obtained app_access_token")
#                     return token
#                 else:
#                     logger.error(f"Failed to get app_access_token: {data}")
#                     return None
                    
#         except Exception as e:
#             logger.error(f"Error getting app_access_token: {e}")
#             return None

#     async def exchange_code_for_token(self, code: str) -> Optional[str]:
#         """Đổi authorization code thành user_access_token"""
#         app_token = await self.get_app_access_token()
#         if not app_token:
#             return None

#         url = f"{self.base_url}/authen/v1/oidc/access_token"
#         headers = {
#             "Authorization": f"Bearer {app_token}",
#             "Content-Type": "application/json"
#         }
#         payload = {
#             "grant_type": "authorization_code",
#             "code": code
#         }
        
#         try:
#             async with httpx.AsyncClient() as client:
#                 response = await client.post(url, headers=headers, json=payload, timeout=10)
#                 response.raise_for_status()
                
#                 data = response.json()
#                 if data.get('code') == 0:
#                     return data.get('data', {}).get('access_token')
#                 else:
#                     logger.error(f"Failed to exchange code: {data}")
#                     return None
                    
#         except Exception as e:
#             logger.error(f"Error exchanging code: {e}")
#             return None

#     async def get_user_info(self, user_access_token: str) -> Optional[Dict[str, Any]]:
#         """Lấy thông tin user từ user_access_token"""
#         url = f"{self.base_url}/authen/v1/user_info"
#         headers = {
#             "Authorization": f"Bearer {user_access_token}"
#         }
        
#         try:
#             async with httpx.AsyncClient() as client:
#                 response = await client.get(url, headers=headers, timeout=10)
#                 response.raise_for_status()
                
#                 data = response.json()
#                 if data.get('code') == 0:
#                     return data.get('data')
#                 else:
#                     logger.error(f"Failed to get user info: {data}")
#                     return None
                    
#         except Exception as e:
#             logger.error(f"Error getting user info: {e}")
#             return None

#     async def check_user_permission(self, open_id: str, app_token: str, table_id: str) -> Tuple[bool, str]:
#         """Kiểm tra quyền user trong Larkbase table"""
#         app_access_token = await self.get_app_access_token()
#         if not app_access_token:
#             return False, "Không thể xác thực với Lark"

#         url = f"{self.base_url}/bitable/v1/apps/{app_token}/tables/{table_id}/records/search"
#         headers = {
#             "Authorization": f"Bearer {app_access_token}",
#             "Content-Type": "application/json"
#         }
#         payload = {
#             "filter": {
#                 "conjunction": "and",
#                 "conditions": [
#                     {
#                         "field_name": "Người",
#                         "operator": "contains", 
#                         "value": [open_id]
#                     },
#                     {
#                         "field_name": "Trạng thái",
#                         "operator": "is",
#                         "value": ["Kích hoạt"]
#                     }
#                 ]
#             }
#         }
        
#         try:
#             async with httpx.AsyncClient() as client:
#                 response = await client.post(url, headers=headers, json=payload, timeout=10)
#                 response.raise_for_status()
                
#                 data = response.json()
#                 if data.get('code') == 0:
#                     items = data.get('data', {}).get('items', [])
#                     if items:
#                         return True, "User có quyền truy cập"
#                     else:
#                         return False, "User không có quyền truy cập hoặc chưa được kích hoạt"
#                 else:
#                     logger.error(f"Failed to check permissions: {data}")
#                     return False, f"Lỗi kiểm tra quyền: {data.get('msg', 'Unknown error')}"
                    
#         except Exception as e:
#             logger.error(f"Error checking permissions: {e}")
#             return False, f"Lỗi hệ thống: {str(e)}"



# src/auth/lark_oauth.py


import httpx
import json
import logging
from typing import Optional, Tuple, Dict, Any
from urllib.parse import urlencode
import time

logger = logging.getLogger(__name__)


class LarkOAuthService:
    """
    Service xử lý OAuth authentication với Lark/Feishu platform
    
    Chức năng chính:
    - Tạo OAuth URL để redirect user đến Lark login
    - Lấy và cache app_access_token từ Lark API
    - Đổi authorization code thành user_access_token
    - Lấy thông tin user từ Lark API
    - Kiểm tra quyền user trong Larkbase table
    
    OAuth Flow:
    1. Generate OAuth URL → User login trên Lark
    2. Lark callback với code → Exchange code for token
    3. Use token để get user info
    4. Check user permission trong Larkbase
    
    Token Management:
    - Cache app_access_token với expiry time
    - Auto refresh khi token sắp hết hạn
    """
    
    def __init__(self, app_id: str, app_secret: str, base_url: str, redirect_uri: str):
        """
        Khởi tạo Lark OAuth Service
        
        Args:
            app_id: Lark app ID từ developer console
            app_secret: Lark app secret từ developer console  
            base_url: Base URL của Lark API (https://open.feishu.cn/open-apis)
            redirect_uri: Callback URL sau khi user login thành công
        """
        # ✅ STEP 1: Lưu thông tin app credentials
        self.app_id = app_id
        self.app_secret = app_secret
        self.base_url = base_url
        self.redirect_uri = redirect_uri
        
        # ✅ STEP 2: Khởi tạo token cache để tránh gọi API liên tục
        self._app_access_token = None  # Cache app token
        self._token_expires_at = 0     # Thời gian hết hạn token


    def generate_oauth_url(self, state: str = None) -> str:
        """
        Tạo OAuth URL để redirect user đến Lark login page
        
        Args:
            state: Optional state parameter để verify callback
            
        Returns:
            str: Complete OAuth URL cho Lark authorization
            
        OAuth Parameters:
        - app_id: ID của Lark app
        - redirect_uri: URL callback sau khi login
        - response_type: 'code' để nhận authorization code
        - scope: Quyền truy cập cần thiết (contact:user.id:readonly)
        - state: Tham số bảo mật để verify callback
        """
        # ✅ STEP 1: Chuẩn bị parameters cho OAuth URL
        params = {
            'app_id': self.app_id,
            'redirect_uri': self.redirect_uri,
            'response_type': 'code',  # Authorization Code Flow
            'scope': 'contact:user.id:readonly'  # Quyền đọc thông tin user cơ bản
        }
        
        # ✅ STEP 2: Thêm state parameter nếu có (để bảo mật)
        if state:
            params['state'] = state
        
        # ✅ STEP 3: Build complete OAuth URL với encoded parameters
        oauth_url = f"{self.base_url}/authen/v1/authorize?" + urlencode(params)
        logger.info(f"🔍 Generated OAuth URL: {oauth_url}")
        return oauth_url


    async def get_app_access_token(self) -> Optional[str]:
        """
        Lấy app_access_token từ Lark API với caching mechanism
        
        Returns:
            Optional[str]: App access token hoặc None nếu thất bại
            
        API Endpoint: /auth/v3/app_access_token/internal
        Method: POST
        
        Caching Strategy:
        - Cache token với expiry time
        - Return cached token nếu còn hạn
        - Refresh token khi sắp hết hạn (buffer 5 phút)
        
        Error Handling:
        - Network timeout (10s)
        - API error response
        - JSON parsing errors
        """
        # ✅ STEP 1: Kiểm tra cache - return nếu token còn hạn
        if self._app_access_token and time.time() < self._token_expires_at:
            # Token còn hạn, không cần gọi API
            return self._app_access_token

        # ✅ STEP 2: Chuẩn bị request để lấy token mới
        url = f"{self.base_url}/auth/v3/app_access_token/internal"
        payload = {
            "app_id": self.app_id,
            "app_secret": self.app_secret
        }
        
        try:
            # ✅ STEP 3: Gọi Lark API để lấy app access token
            async with httpx.AsyncClient() as client:
                # Đang request app access token từ Lark
                response = await client.post(url, json=payload, timeout=10)
                response.raise_for_status()  # Raise exception cho HTTP errors
                
                # ✅ STEP 4: Parse response và kiểm tra kết quả
                data = response.json()
                if data.get('code') == 0:  # Lark API success code
                    token = data.get('app_access_token')
                    expires_in = data.get('expire', 7200)  # Default 2 giờ
                    
                    # ✅ STEP 5: Cache token với expiry time (buffer 5 phút)
                    self._app_access_token = token
                    self._token_expires_at = time.time() + expires_in - 300  # 5 min buffer
                    
                    logger.info("✅ Successfully obtained app_access_token")
                    return token
                else:
                    # ❌ ERROR CASE 1: API trả về lỗi
                    logger.error(f"❌ Failed to get app_access_token: {data}")
                    return None
                    
        except Exception as e:
            # ❌ ERROR CASE 2: Network hoặc parsing error
            logger.error(f"❌ Error getting app_access_token: {e}")
            return None


    async def exchange_code_for_token(self, code: str) -> Optional[str]:
        """
        Đổi authorization code thành user_access_token
        
        Args:
            code: Authorization code từ Lark callback
            
        Returns:
            Optional[str]: User access token hoặc None nếu thất bại
            
        API Endpoint: /authen/v1/oidc/access_token
        Method: POST
        Headers: Authorization Bearer với app_access_token
        
        Flow:
        1. Lấy app_access_token trước
        2. Sử dụng app token để exchange code
        3. Return user access token
        
        Error Handling:
        - Không lấy được app token
        - Code không hợp lệ hoặc đã hết hạn
        - Network errors
        """
        # ✅ STEP 1: Lấy app access token trước (required để call API)
        app_token = await self.get_app_access_token()
        if not app_token:
            # ❌ ERROR CASE 1: Không lấy được app token
            logger.error("❌ Cannot get app_access_token, aborting code exchange")
            return None

        # ✅ STEP 2: Chuẩn bị request để exchange code
        url = f"{self.base_url}/authen/v1/oidc/access_token"
        headers = {
            "Authorization": f"Bearer {app_token}",  # Required app token auth
            "Content-Type": "application/json"
        }
        payload = {
            "grant_type": "authorization_code",  # OAuth standard grant type
            "code": code  # Code từ callback
        }
        
        try:
            # ✅ STEP 3: Gọi API để exchange code thành user token
            async with httpx.AsyncClient() as client:
                # Đang exchange authorization code
                response = await client.post(url, headers=headers, json=payload, timeout=10)
                response.raise_for_status()
                
                # ✅ STEP 4: Parse response và extract user token
                data = response.json()
                if data.get('code') == 0:  # Success
                    user_token = data.get('data', {}).get('access_token')
                    logger.info("✅ Successfully exchanged code for user token")
                    return user_token
                else:
                    # ❌ ERROR CASE 2: Code không hợp lệ hoặc đã hết hạn
                    logger.error(f"❌ Failed to exchange code: {data}")
                    return None
                    
        except Exception as e:
            # ❌ ERROR CASE 3: Network hoặc server error
            logger.error(f"❌ Error exchanging code: {e}")
            return None


    async def get_user_info(self, user_access_token: str) -> Optional[Dict[str, Any]]:
        """
        Lấy thông tin user từ user_access_token
        
        Args:
            user_access_token: Token của user sau khi exchange code
            
        Returns:
            Optional[Dict]: User info dictionary hoặc None nếu thất bại
            
        API Endpoint: /authen/v1/user_info
        Method: GET  
        Headers: Authorization Bearer với user_access_token
        
        Response Data:
        - open_id: Unique user ID trong Lark
        - name: Tên hiển thị của user
        - email: Email của user (nếu có)
        - avatar_url: URL ảnh đại diện
        
        Error Handling:
        - Token không hợp lệ hoặc hết hạn
        - User không tồn tại
        - Network errors
        """
        # ✅ STEP 1: Chuẩn bị request để lấy user info
        url = f"{self.base_url}/authen/v1/user_info"
        headers = {
            "Authorization": f"Bearer {user_access_token}"  # User token auth
        }
        
        try:
            # ✅ STEP 2: Gọi API để lấy thông tin user
            async with httpx.AsyncClient() as client:
                # Đang lấy thông tin user từ Lark
                response = await client.get(url, headers=headers, timeout=10)
                response.raise_for_status()
                
                # ✅ STEP 3: Parse response và extract user data
                data = response.json()
                if data.get('code') == 0:  # Success
                    user_info = data.get('data')
                    logger.info("✅ Successfully retrieved user info")
                    return user_info
                else:
                    # ❌ ERROR CASE 1: Token không hợp lệ hoặc user không tồn tại
                    logger.error(f"❌ Failed to get user info: {data}")
                    return None
                    
        except Exception as e:
            # ❌ ERROR CASE 2: Network hoặc server error
            logger.error(f"❌ Error getting user info: {e}")
            return None


    async def check_user_permission(self, open_id: str, app_token: str, table_id: str) -> Tuple[bool, str]:
        """
        Kiểm tra quyền user trong Larkbase table để authorize access
        
        Args:
            open_id: Unique user ID từ Lark
            app_token: App token của Larkbase (khác với app_access_token)
            table_id: ID của bảng permission trong Larkbase
            
        Returns:
            Tuple[bool, str]: (có_quyền, thông_báo)
            
        API Endpoint: /bitable/v1/apps/{app_token}/tables/{table_id}/records/search
        Method: POST
        Headers: Authorization Bearer với app_access_token
        
        Search Logic:
        - Tìm record có cột "Người" chứa open_id
        - Và cột "Trạng thái" = "Kích hoạt"
        - Return True nếu tìm thấy record phù hợp
        
        Permission Table Structure:
        - Người: Multi-select field chứa open_id của users
        - Trạng thái: Select field ("Kích hoạt"/"Vô hiệu hóa")
        
        Error Handling:
        - Không lấy được app access token
        - Table hoặc app_token không tồn tại
        - Network timeout
        - Permission denied
        """
        # ✅ STEP 1: Lấy app access token để authenticate với Larkbase API
        app_access_token = await self.get_app_access_token()
        if not app_access_token:
            # ❌ ERROR CASE 1: Không thể authenticate với Lark
            return False, "Không thể xác thực với Lark"

        # ✅ STEP 2: Chuẩn bị request để search permission records
        url = f"{self.base_url}/bitable/v1/apps/{app_token}/tables/{table_id}/records/search"
        headers = {
            "Authorization": f"Bearer {app_access_token}",
            "Content-Type": "application/json"
        }
        
        # ✅ STEP 3: Build search filter để tìm user permission
        payload = {
            "filter": {
                "conjunction": "and",  # Tất cả conditions phải đúng
                "conditions": [
                    {
                        "field_name": "Người",        # Field chứa user list
                        "operator": "contains",       # User có trong list
                        "value": [open_id]           # Open ID cần check
                    },
                    {
                        "field_name": "Trạng thái",   # Field trạng thái permission
                        "operator": "is",             # Exact match
                        "value": ["Kích hoạt"]       # Chỉ user đang active
                    }
                ]
            }
        }
        
        try:
            # ✅ STEP 4: Gọi Larkbase API để search permission
            async with httpx.AsyncClient() as client:
                # Đang kiểm tra quyền user trong Larkbase
                response = await client.post(url, headers=headers, json=payload, timeout=10)
                response.raise_for_status()
                
                # ✅ STEP 5: Parse response và kiểm tra kết quả
                data = response.json()
                if data.get('code') == 0:  # API call success
                    items = data.get('data', {}).get('items', [])
                    
                    if items:
                        # ✅ SUCCESS: Tìm thấy permission record
                        logger.info(f"✅ User {open_id} has access permission")
                        return True, "User có quyền truy cập"
                    else:
                        # ❌ NO PERMISSION: Không tìm thấy record hoặc user chưa active
                        logger.warning(f"❌ User {open_id} denied access - not found or inactive")
                        return False, "User không có quyền truy cập hoặc chưa được kích hoạt"
                else:
                    # ❌ ERROR CASE 2: API error (table không tồn tại, permission denied, etc.)
                    logger.error(f"❌ Failed to check permissions: {data}")
                    return False, f"Lỗi kiểm tra quyền: {data.get('msg', 'Unknown error')}"
                    
        except Exception as e:
            # ❌ ERROR CASE 3: Network timeout hoặc server error
            logger.error(f"❌ Error checking permissions: {e}")
            return False, f"Lỗi hệ thống: {str(e)}"


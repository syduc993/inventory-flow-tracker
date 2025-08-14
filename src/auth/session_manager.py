# src/auth/session_manager.py
import jwt
import time
import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class SessionManager:
    def __init__(self, secret_key: str, expire_hours: int = 24):
        self.secret_key = secret_key
        self.expire_hours = expire_hours
        self.algorithm = "HS256"

    def create_session_token(self, user_info: Dict[str, Any]) -> str:
        """Tạo JWT session token"""
        now = datetime.utcnow()
        payload = {
            'user_id': user_info.get('open_id'),
            'name': user_info.get('name'),
            'email': user_info.get('email'),
            'avatar_url': user_info.get('avatar_url'),
            'iat': now,
            'exp': now + timedelta(hours=self.expire_hours),
            'iss': 'inventory-flow-tracker'
        }
        
        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        logger.info(f"Created session token for user: {user_info.get('name')}")
        return token

    def verify_session_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify và decode JWT session token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            # Check expiration manually for better error handling
            exp = payload.get('exp')
            if exp and datetime.utcfromtimestamp(exp) < datetime.utcnow():
                logger.warning("Session token expired")
                return None
                
            return payload
            
        except jwt.ExpiredSignatureError:
            logger.warning("Session token expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid session token: {e}")
            return None
        except Exception as e:
            logger.error(f"Error verifying token: {e}")
            return None

    def refresh_token_if_needed(self, token: str, refresh_threshold_hours: int = 2) -> Optional[str]:
        """Refresh token nếu sắp hết hạn"""
        try:
            payload = self.verify_session_token(token)
            if not payload:
                return None
                
            exp = payload.get('exp')
            if exp:
                exp_time = datetime.utcfromtimestamp(exp)
                time_left = exp_time - datetime.utcnow()
                
                # Nếu còn ít hơn threshold thì refresh
                if time_left.total_seconds() < (refresh_threshold_hours * 3600):
                    # Tạo token mới với thông tin cũ
                    user_info = {
                        'open_id': payload.get('user_id'),
                        'name': payload.get('name'),
                        'email': payload.get('email'),
                        'avatar_url': payload.get('avatar_url')
                    }
                    new_token = self.create_session_token(user_info)
                    logger.info("Refreshed session token")
                    return new_token
                    
            return token  # Token còn tốt, không cần refresh
            
        except Exception as e:
            logger.error(f"Error refreshing token: {e}")
            return None

    def get_user_from_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Lấy thông tin user từ token"""
        payload = self.verify_session_token(token)
        if payload:
            return {
                'user_id': payload.get('user_id'),
                'name': payload.get('name'),
                'email': payload.get('email'),
                'avatar_url': payload.get('avatar_url')
            }
        return None

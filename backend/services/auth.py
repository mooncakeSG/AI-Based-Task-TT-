import logging
import jwt
import time
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from fastapi import HTTPException, Request, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from supabase import create_client, Client
from config.settings import settings

logger = logging.getLogger(__name__)

class SupabaseAuthService:
    def __init__(self):
        self.supabase: Optional[Client] = None
        self.jwt_secret = None
        self.initialized = False
        
        # Initialize Supabase client
        if settings.supabase_url and settings.supabase_anon_key:
            try:
                self.supabase = create_client(
                    settings.supabase_url, 
                    settings.supabase_anon_key
                )
                self.jwt_secret = settings.supabase_anon_key  # Used for JWT verification
                self.initialized = True
                logger.info("Supabase authentication service initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Supabase auth service: {e}")
        else:
            logger.warning("Supabase authentication not configured - auth features disabled")
    
    async def sign_up(self, email: str, password: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Register a new user with Supabase Auth
        
        Args:
            email (str): User email
            password (str): User password
            metadata (dict): Additional user metadata
            
        Returns:
            Dict containing user data and session info
        """
        if not self.initialized:
            raise HTTPException(
                status_code=503,
                detail="Authentication service not available"
            )
        
        try:
            # Sign up user with Supabase
            response = self.supabase.auth.sign_up({
                "email": email,
                "password": password,
                "options": {
                    "data": metadata or {}
                }
            })
            
            if response.user:
                return {
                    "user": {
                        "id": response.user.id,
                        "email": response.user.email,
                        "email_confirmed_at": response.user.email_confirmed_at,
                        "created_at": response.user.created_at,
                        "user_metadata": response.user.user_metadata
                    },
                    "session": {
                        "access_token": response.session.access_token if response.session else None,
                        "refresh_token": response.session.refresh_token if response.session else None,
                        "expires_at": response.session.expires_at if response.session else None
                    } if response.session else None,
                    "message": "User registered successfully. Please check your email for verification."
                }
            else:
                raise HTTPException(
                    status_code=400,
                    detail="Failed to create user account"
                )
                
        except Exception as e:
            logger.error(f"Sign up error: {str(e)}")
            if "already registered" in str(e).lower():
                raise HTTPException(
                    status_code=409,
                    detail="User with this email already exists"
                )
            raise HTTPException(
                status_code=400,
                detail=f"Registration failed: {str(e)}"
            )
    
    async def sign_in(self, email: str, password: str) -> Dict[str, Any]:
        """
        Sign in user with email and password
        
        Args:
            email (str): User email
            password (str): User password
            
        Returns:
            Dict containing user data and session info
        """
        if not self.initialized:
            raise HTTPException(
                status_code=503,
                detail="Authentication service not available"
            )
        
        try:
            response = self.supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            if response.user and response.session:
                return {
                    "user": {
                        "id": response.user.id,
                        "email": response.user.email,
                        "email_confirmed_at": response.user.email_confirmed_at,
                        "last_sign_in_at": response.user.last_sign_in_at,
                        "user_metadata": response.user.user_metadata
                    },
                    "session": {
                        "access_token": response.session.access_token,
                        "refresh_token": response.session.refresh_token,
                        "expires_at": response.session.expires_at,
                        "token_type": response.session.token_type
                    },
                    "message": "Sign in successful"
                }
            else:
                raise HTTPException(
                    status_code=401,
                    detail="Invalid email or password"
                )
                
        except Exception as e:
            logger.error(f"Sign in error: {str(e)}")
            if "invalid" in str(e).lower() or "wrong" in str(e).lower():
                raise HTTPException(
                    status_code=401,
                    detail="Invalid email or password"
                )
            raise HTTPException(
                status_code=400,
                detail=f"Sign in failed: {str(e)}"
            )
    
    async def sign_out(self, access_token: str) -> Dict[str, Any]:
        """
        Sign out user and invalidate session
        
        Args:
            access_token (str): User's access token
            
        Returns:
            Dict with success message
        """
        if not self.initialized:
            raise HTTPException(
                status_code=503,
                detail="Authentication service not available"
            )
        
        try:
            # Set the session for the current request
            self.supabase.auth.set_session(access_token, "")
            
            # Sign out
            response = self.supabase.auth.sign_out()
            
            return {
                "message": "Sign out successful"
            }
            
        except Exception as e:
            logger.error(f"Sign out error: {str(e)}")
            # Even if sign out fails, we can consider it successful from client perspective
            return {
                "message": "Sign out completed"
            }
    
    async def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """
        Refresh user session using refresh token
        
        Args:
            refresh_token (str): User's refresh token
            
        Returns:
            Dict containing new session info
        """
        if not self.initialized:
            raise HTTPException(
                status_code=503,
                detail="Authentication service not available"
            )
        
        try:
            response = self.supabase.auth.refresh_session(refresh_token)
            
            if response.session:
                return {
                    "session": {
                        "access_token": response.session.access_token,
                        "refresh_token": response.session.refresh_token,
                        "expires_at": response.session.expires_at,
                        "token_type": response.session.token_type
                    },
                    "user": {
                        "id": response.user.id,
                        "email": response.user.email,
                        "user_metadata": response.user.user_metadata
                    } if response.user else None,
                    "message": "Token refreshed successfully"
                }
            else:
                raise HTTPException(
                    status_code=401,
                    detail="Failed to refresh token"
                )
                
        except Exception as e:
            logger.error(f"Token refresh error: {str(e)}")
            raise HTTPException(
                status_code=401,
                detail="Token refresh failed"
            )
    
    async def get_user_from_token(self, access_token: str) -> Dict[str, Any]:
        """
        Get user information from access token
        
        Args:
            access_token (str): User's access token
            
        Returns:
            Dict containing user information
        """
        if not self.initialized:
            raise HTTPException(
                status_code=503,
                detail="Authentication service not available"
            )
        
        try:
            # Verify and decode the JWT token
            payload = jwt.decode(
                access_token, 
                self.jwt_secret, 
                algorithms=["HS256"],
                audience="authenticated"
            )
            
            # Check if token is expired
            if payload.get('exp', 0) < time.time():
                raise HTTPException(
                    status_code=401,
                    detail="Token expired"
                )
            
            # Get user from Supabase
            response = self.supabase.auth.get_user(access_token)
            
            if response.user:
                return {
                    "id": response.user.id,
                    "email": response.user.email,
                    "email_confirmed_at": response.user.email_confirmed_at,
                    "user_metadata": response.user.user_metadata,
                    "app_metadata": response.user.app_metadata
                }
            else:
                raise HTTPException(
                    status_code=401,
                    detail="Invalid token"
                )
                
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=401,
                detail="Token expired"
            )
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=401,
                detail="Invalid token"
            )
        except Exception as e:
            logger.error(f"Token verification error: {str(e)}")
            raise HTTPException(
                status_code=401,
                detail="Token verification failed"
            )
    
    async def reset_password(self, email: str) -> Dict[str, Any]:
        """
        Send password reset email
        
        Args:
            email (str): User email
            
        Returns:
            Dict with success message
        """
        if not self.initialized:
            raise HTTPException(
                status_code=503,
                detail="Authentication service not available"
            )
        
        try:
            response = self.supabase.auth.reset_password_email(email)
            
            return {
                "message": "Password reset email sent successfully"
            }
            
        except Exception as e:
            logger.error(f"Password reset error: {str(e)}")
            # Don't reveal if email exists or not for security
            return {
                "message": "If the email exists, a password reset link has been sent"
            }
    
    async def update_user(self, access_token: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update user information
        
        Args:
            access_token (str): User's access token
            updates (dict): Fields to update
            
        Returns:
            Dict containing updated user info
        """
        if not self.initialized:
            raise HTTPException(
                status_code=503,
                detail="Authentication service not available"
            )
        
        try:
            # Set session for the request
            self.supabase.auth.set_session(access_token, "")
            
            # Update user
            response = self.supabase.auth.update_user(updates)
            
            if response.user:
                return {
                    "user": {
                        "id": response.user.id,
                        "email": response.user.email,
                        "user_metadata": response.user.user_metadata
                    },
                    "message": "User updated successfully"
                }
            else:
                raise HTTPException(
                    status_code=400,
                    detail="Failed to update user"
                )
                
        except Exception as e:
            logger.error(f"User update error: {str(e)}")
            raise HTTPException(
                status_code=400,
                detail=f"User update failed: {str(e)}"
            )

# Global auth service instance
auth_service = SupabaseAuthService()

# FastAPI security scheme
security = HTTPBearer(auto_error=False)

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Optional[Dict[str, Any]]:
    """
    FastAPI dependency to get current authenticated user
    
    Returns:
        User dict if authenticated, None if not authenticated
    """
    if not credentials:
        return None
    
    try:
        user = await auth_service.get_user_from_token(credentials.credentials)
        return user
    except HTTPException:
        return None

async def require_auth(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """
    FastAPI dependency that requires authentication
    
    Returns:
        User dict if authenticated
        
    Raises:
        HTTPException if not authenticated
    """
    if not credentials:
        raise HTTPException(
            status_code=401,
            detail="Authentication required"
        )
    
    try:
        user = await auth_service.get_user_from_token(credentials.credentials)
        return user
    except HTTPException as e:
        raise e

async def get_user_id_from_token(access_token: str) -> Optional[str]:
    """
    Extract user ID from access token
    
    Args:
        access_token (str): JWT access token
        
    Returns:
        User ID if valid token, None otherwise
    """
    try:
        user = await auth_service.get_user_from_token(access_token)
        return user.get("id")
    except:
        return None

def extract_user_id_from_request(request: Request) -> Optional[str]:
    """
    Extract user ID from request headers
    
    Args:
        request (Request): FastAPI request object
        
    Returns:
        User ID if authenticated, None otherwise
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None
    
    token = auth_header.split(" ")[1]
    try:
        # Quick JWT decode without verification for user ID extraction
        payload = jwt.decode(token, options={"verify_signature": False})
        return payload.get("sub")  # 'sub' contains user ID in Supabase JWT
    except:
        return None

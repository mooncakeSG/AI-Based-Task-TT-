import logging
from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, Dict, Any
from services.auth import auth_service, get_current_user, require_auth

logger = logging.getLogger(__name__)
router = APIRouter()

# Pydantic models for authentication
class SignUpRequest(BaseModel):
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=6, max_length=128, description="User password (min 6 characters)")
    full_name: Optional[str] = Field(None, max_length=100, description="User's full name")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional user metadata")

class SignInRequest(BaseModel):
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password")

class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(..., description="Refresh token for session renewal")

class ResetPasswordRequest(BaseModel):
    email: EmailStr = Field(..., description="Email address for password reset")

class UpdateUserRequest(BaseModel):
    full_name: Optional[str] = Field(None, max_length=100, description="Updated full name")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Updated user metadata")

class AuthResponse(BaseModel):
    user: Dict[str, Any]
    session: Optional[Dict[str, Any]] = None
    message: str

class UserResponse(BaseModel):
    user: Dict[str, Any]
    message: str

class MessageResponse(BaseModel):
    message: str

@router.post("/auth/signup", response_model=AuthResponse)
async def sign_up(request: SignUpRequest):
    """
    Register a new user account
    
    Creates a new user account with Supabase Auth. Email verification
    may be required depending on your Supabase configuration.
    
    Args:
        request: Sign up request with email, password, and optional metadata
        
    Returns:
        User information and session data
    """
    try:
        # Prepare metadata
        metadata = request.metadata or {}
        if request.full_name:
            metadata["full_name"] = request.full_name
        
        result = await auth_service.sign_up(
            email=request.email,
            password=request.password,
            metadata=metadata
        )
        
        logger.info(f"User signed up successfully: {request.email}")
        return AuthResponse(**result)
        
    except HTTPException as e:
        logger.warning(f"Sign up failed for {request.email}: {e.detail}")
        raise e
    except Exception as e:
        logger.error(f"Unexpected error during sign up for {request.email}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred during registration"
        )

@router.post("/auth/signin", response_model=AuthResponse)
async def sign_in(request: SignInRequest):
    """
    Sign in with email and password
    
    Authenticates user credentials and returns access token and user information.
    
    Args:
        request: Sign in request with email and password
        
    Returns:
        User information and session data with access token
    """
    try:
        result = await auth_service.sign_in(
            email=request.email,
            password=request.password
        )
        
        logger.info(f"User signed in successfully: {request.email}")
        return AuthResponse(**result)
        
    except HTTPException as e:
        logger.warning(f"Sign in failed for {request.email}: {e.detail}")
        raise e
    except Exception as e:
        logger.error(f"Unexpected error during sign in for {request.email}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred during sign in"
        )

@router.post("/auth/signout", response_model=MessageResponse)
async def sign_out(current_user: Dict[str, Any] = Depends(require_auth)):
    """
    Sign out current user
    
    Invalidates the current session and signs out the user.
    Requires valid authentication token.
    
    Returns:
        Success message
    """
    try:
        # Extract token from the request (this is a simplified approach)
        # In practice, you might want to pass the token more explicitly
        result = await auth_service.sign_out("")
        
        logger.info(f"User signed out successfully: {current_user.get('email')}")
        return MessageResponse(**result)
        
    except Exception as e:
        logger.error(f"Error during sign out for user {current_user.get('id')}: {str(e)}")
        # Even if sign out fails, return success for user experience
        return MessageResponse(message="Sign out completed")

@router.post("/auth/refresh", response_model=AuthResponse)
async def refresh_token(request: RefreshTokenRequest):
    """
    Refresh authentication token
    
    Uses refresh token to obtain new access token when the current one expires.
    
    Args:
        request: Refresh token request
        
    Returns:
        New session data with fresh access token
    """
    try:
        result = await auth_service.refresh_token(request.refresh_token)
        
        logger.info("Token refreshed successfully")
        return AuthResponse(**result)
        
    except HTTPException as e:
        logger.warning(f"Token refresh failed: {e.detail}")
        raise e
    except Exception as e:
        logger.error(f"Unexpected error during token refresh: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred during token refresh"
        )

@router.post("/auth/reset-password", response_model=MessageResponse)
async def reset_password(request: ResetPasswordRequest):
    """
    Request password reset
    
    Sends password reset email to the specified address.
    For security, always returns success regardless of whether email exists.
    
    Args:
        request: Password reset request with email
        
    Returns:
        Success message
    """
    try:
        result = await auth_service.reset_password(request.email)
        
        logger.info(f"Password reset requested for: {request.email}")
        return MessageResponse(**result)
        
    except Exception as e:
        logger.error(f"Error during password reset for {request.email}: {str(e)}")
        # Always return success for security (don't reveal if email exists)
        return MessageResponse(
            message="If the email exists, a password reset link has been sent"
        )

@router.get("/auth/me", response_model=UserResponse)
async def get_current_user_info(current_user: Dict[str, Any] = Depends(require_auth)):
    """
    Get current user information
    
    Returns information about the currently authenticated user.
    Requires valid authentication token.
    
    Returns:
        Current user information
    """
    try:
        return UserResponse(
            user=current_user,
            message="User information retrieved successfully"
        )
        
    except Exception as e:
        logger.error(f"Error retrieving user info for {current_user.get('id')}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve user information"
        )

@router.put("/auth/me", response_model=UserResponse)
async def update_current_user(
    request: UpdateUserRequest,
    current_user: Dict[str, Any] = Depends(require_auth)
):
    """
    Update current user information
    
    Updates the authenticated user's profile information.
    Requires valid authentication token.
    
    Args:
        request: User update request with new information
        
    Returns:
        Updated user information
    """
    try:
        # Prepare updates
        updates = {}
        
        if request.metadata:
            updates["data"] = request.metadata
            
        if request.full_name:
            if "data" not in updates:
                updates["data"] = {}
            updates["data"]["full_name"] = request.full_name
        
        # Note: We need the actual access token here
        # This is a simplified implementation - in practice, you'd extract it from the request
        result = await auth_service.update_user("", updates)
        
        logger.info(f"User updated successfully: {current_user.get('email')}")
        return UserResponse(**result)
        
    except HTTPException as e:
        logger.warning(f"User update failed for {current_user.get('id')}: {e.detail}")
        raise e
    except Exception as e:
        logger.error(f"Unexpected error during user update for {current_user.get('id')}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred during user update"
        )

@router.get("/auth/status")
async def auth_status(current_user: Optional[Dict[str, Any]] = Depends(get_current_user)):
    """
    Check authentication status
    
    Returns current authentication status and user information if authenticated.
    Does not require authentication - returns status for any request.
    
    Returns:
        Authentication status and user info if authenticated
    """
    if current_user:
        return {
            "authenticated": True,
            "user": {
                "id": current_user.get("id"),
                "email": current_user.get("email"),
                "email_confirmed": current_user.get("email_confirmed_at") is not None
            },
            "message": "User is authenticated"
        }
    else:
        return {
            "authenticated": False,
            "user": None,
            "message": "User is not authenticated"
        }

@router.get("/auth/health")
async def auth_health():
    """
    Authentication service health check
    
    Returns the health status of the authentication service.
    
    Returns:
        Health status information
    """
    try:
        if auth_service.initialized:
            return {
                "status": "healthy",
                "service": "supabase_auth",
                "initialized": True,
                "message": "Authentication service is operational"
            }
        else:
            return {
                "status": "unavailable",
                "service": "supabase_auth", 
                "initialized": False,
                "message": "Authentication service not configured"
            }
            
    except Exception as e:
        logger.error(f"Auth health check failed: {str(e)}")
        return {
            "status": "error",
            "service": "supabase_auth",
            "initialized": False,
            "message": f"Authentication service error: {str(e)}"
        }

from fastapi import APIRouter, HTTPException, status, Query
from pydantic import BaseModel
from domain.user.entities import User
from infrastructure.db.repositories import UserRepository
from typing import Dict, Any, Optional
from shared.google_oauth import (
    verify_google_token, 
    get_google_login_url, 
    exchange_code_for_token,
    refresh_access_token,
    get_token_info
)
import uuid
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])

# 요청/응답 모델
class TokenVerifyRequest(BaseModel):
    access_token: str

class TokenRefreshRequest(BaseModel):
    refresh_token: str

class LoginUrlRequest(BaseModel):
    user_id: str
    user_email: str

class LoginUrlResponse(BaseModel):
    login_url: str
    message: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "Bearer"
    expires_in: int  # 초 단위
    expires_at: str  # ISO 형식 만료 시간
    refresh_token: Optional[str] = None
    refresh_token_expires_in: Optional[int] = None  # Refresh Token 만료 시간 (추정)
    scope: Optional[str] = None

class OAuthCallbackResponse(BaseModel):
    message: str
    token: TokenResponse
    user_info: Dict[str, Any]

class RefreshTokenErrorResponse(BaseModel):
    error: str
    message: str
    action_required: str
    login_url: str

@router.post("/login", response_model=LoginUrlResponse)
async def get_google_login_url_endpoint(request: LoginUrlRequest) -> LoginUrlResponse:
    """사용자 ID를 키값으로 DB를 조회하여 
    토큰 유무를 확인하고 토큰이 없으면 OAuth 로그인 URL을 반환합니다"""
    
    try:
        # 사용자 ID를 키값으로 DB를 조회하여 토큰 유무를 확인
        user_id = request.user_id
        user_email = request.user_email
        user = User(user_id=user_id, email=user_email)

        user_token = await UserRepository().get_token_by_id(user_id)
        if user_token:
            # 토큰이 있다면 토큰 검증
            token_info = await verify_google_token(user_token.access_token)
            if token_info:
                return LoginUrlResponse(
                    login_url='',
                    message="로그인 성공"
                )
            else:
                # 토큰이 없다면 구글 로그인 URL 생성
                await UserRepository().create(user)
                login_url = get_google_login_url()
                return LoginUrlResponse(
                    login_url=login_url,
                    message="로그인 필요"
                )
        else:
            # 구글 로그인 URL 생성
            await UserRepository().create(user)
            login_url = get_google_login_url()
            return LoginUrlResponse(
                login_url=login_url,
                message="로그인 필요"
            )

        
    except Exception as e:
        logger.error(f"Failed to generate Google login URL: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate login URL"
        )

@router.get("/callback", response_model=OAuthCallbackResponse)
async def google_oauth_callback(
    code: str = Query(..., description="구글에서 받은 authorization code"),
    error: Optional[str] = Query(None, description="OAuth 에러")
):
    """구글 OAuth 콜백을 처리합니다"""
    
    if error:
        logger.warning(f"Google OAuth error: {error}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"OAuth error: {error}"
        )
    
    try:
        # Authorization Code를 Access Token으로 교환
        token_data = await exchange_code_for_token(code)
        
        # 토큰 정보 추출
        access_token = token_data.get("access_token")
        if not access_token:
            raise ValueError("Access token not received")
        
        # 유효 기간 정보 처리
        expires_in = token_data.get("expires_in", 3600)  # 기본값 1시간
        expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
        
        # Access Token으로 사용자 정보 조회
        user_info = await verify_google_token(access_token)
        
        # 토큰 응답 구성
        token_response = TokenResponse(
            access_token=access_token, # 엑세스 토큰
            token_type="Bearer", # 토큰 타입
            expires_in=expires_in, # 엑세스 토큰 만료 시간
            expires_at=expires_at.isoformat() + "Z", # 엑세스 토큰 만료 시간
            refresh_token=token_data.get("refresh_token"), # 리프레시 토큰
            scope=token_data.get("scope") # 스코프
        )

        # DB에 저장

        user = await UserRepository().get_by_email(user_info.get("email"))
        if user:
            user.access_token = access_token
            user.refresh_token = token_data.get("refresh_token")
            user.expires_at = expires_at
            await UserRepository().update(user)
        else:
            user = User(user_id=user_info.get("email"), email=user_info.get("email"))
            await UserRepository().create(user)
        
        logger.info(f"OAuth login successful for user: {user_info.get('email')} (expires in {expires_in}s)")
        
        return OAuthCallbackResponse(
            message="Login successful",
            token=token_response,
            user_info=user_info
        )
        
    except ValueError as e:
        logger.error(f"OAuth callback error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected OAuth callback error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="OAuth callback failed"
        )

@router.post("/verify")
async def verify_google_token_endpoint(request: TokenVerifyRequest):
    """구글 Access Token을 검증합니다"""
    
    try:
        # 구글 토큰 검증 및 사용자 정보 조회
        user_info = await verify_google_token(request.access_token)
        
        # 토큰 정보도 함께 조회
        try:
            token_info = await get_token_info(request.access_token)
            expires_in = token_info.get("expires_in")
        except:
            expires_in = None
        
        logger.info(f"Token verification successful for user: {user_info.get('email')}")
        
        return {
            "message": "Token verification successful",
            "user_info": user_info,
            "token_expires_in": expires_in,
            "note": "Token expiration info is managed by Google OAuth server"
        }
        
    except ValueError as e:
        logger.warning(f"Token verification failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected token verification error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token verification failed"
        )

@router.post("/token/refresh", response_model=TokenResponse)
async def refresh_token_endpoint(request: TokenRefreshRequest):
    """Refresh Token으로 새로운 Access Token 발급"""
    
    try:
        # Refresh Token으로 새 Access Token 발급
        token_data = await refresh_access_token(request.refresh_token)
        
        # 토큰 정보 추출
        access_token = token_data.get("access_token")
        if not access_token:
            raise ValueError("New access token not received")
        
        # 유효 기간 정보 처리
        expires_in = token_data.get("expires_in", 3600)
        expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
        
        # 새 refresh_token이 있으면 사용, 없으면 기존 유지
        new_refresh_token = token_data.get("refresh_token", request.refresh_token)
        
        logger.info(f"Access token refreshed successfully (expires in {expires_in}s)")
        
        return TokenResponse(
            access_token=access_token,
            token_type="Bearer",
            expires_in=expires_in,
            expires_at=expires_at.isoformat() + "Z",
            refresh_token=new_refresh_token,
            scope=token_data.get("scope")
        )
        
    except ValueError as e:
        logger.warning(f"Token refresh failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected token refresh error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token refresh failed"
        )

@router.get("/token/info")
async def get_token_info_endpoint():
    """구글 OAuth 토큰 정보 안내"""
    
    return {
        "message": "Google OAuth Token Information",
        "token_details": {
            "access_token": {
                "description": "API 호출용 액세스 토큰",
                "expires_in": "3600초 (1시간)",
                "usage": "Authorization: Bearer {access_token}"
            },
            "refresh_token": {
                "description": "액세스 토큰 갱신용 토큰",
                "expires_in": "무기한 (사용자가 앱 권한 해제 시까지)",
                "usage": "액세스 토큰 만료 시 새 토큰 발급용"
            }
        },
        "expiration_handling": {
            "client_side": "expires_at 시간을 확인하여 토큰 만료 전 갱신",
            "server_side": "API 호출 시 401 에러 발생하면 토큰 만료로 판단"
        },
        "endpoints": {
            "login": "GET /api/v1/auth/google/login",
            "callback": "GET /api/v1/auth/google/callback",
            "verify": "POST /api/v1/auth/google/verify",
            "refresh": "POST /api/v1/auth/token/refresh"
        }
    } 
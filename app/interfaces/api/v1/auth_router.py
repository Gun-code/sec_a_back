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
from shared.google_callendar import get_google_calendar_events, save_google_calendar_events
from application.user.dto import CalendarRequest, CalendarResponse
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Authentication"])

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
    refresh_token: Optional[str] = None
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
        user_id = request.user_id
        user_email = request.user_email
        logger.info(f"Login request - user_id: {user_id}, user_email: {user_email}")
        
        # 기존 사용자 확인
        user_repo = UserRepository()
        logger.info("Checking existing user token...")
        user_token = await user_repo.get_token_by_id(user_id)
        
        if user_token and user_token.access_token:
            # 토큰이 있다면 토큰 검증
            try:
                logger.info("Verifying existing token...")
                token_info = await verify_google_token(user_token.access_token)
                if token_info:
                    return LoginUrlResponse(
                        login_url='',
                        message="유효한 토큰"
                    )
            except:
                # 토큰이 만료되었으면 새로 로그인 진행
                logger.info("Token verification failed, proceeding with new login")
                pass
        
        # 사용자가 없으면 미리 생성 (토큰 없이)
        if not user_token:
            logger.info("Creating new user...")
            
            # 이메일로도 확인해서 기존 사용자가 있는지 체크
            existing_user = await user_repo.get_by_email(user_email)
            if existing_user:
                logger.info(f"User already exists with email: {user_email}")
                user_token = existing_user
            else:
                # 정말 새로운 사용자인 경우에만 생성
                new_user = User(
                    user_id=user_id,
                    username=None,  # OAuth에서 받을 예정
                    email=user_email,
                    created_at=datetime.now(),  # 필수 필드 추가
                    access_token=None,
                    refresh_token=None,
                    expires_at=None
                )
                await user_repo.create(new_user)
                logger.info("New user created successfully")
        
        # 구글 로그인 URL 생성 (기본 스코프만 사용)
        logger.info("Generating Google login URL...")
        login_url = get_google_login_url(include_calendar=False)
        logger.info(f"Google login URL generated successfully: {login_url[:50]}...")
        
        return LoginUrlResponse(
            login_url=login_url,
            refresh_token=user_token.refresh_token,
            message="유효하지 않은 토큰"
        )
        
    except Exception as e:
        logger.error(f"Failed to generate Google login URL: {e}")
        logger.error(f"Error type: {type(e).__name__}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
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
        google_email = user_info.get("email")
        
        if not google_email:
            return OAuthCallbackResponse(
                message="Google email not received"
            )
        
        # 사용자 정보 저장 및 업데이트
        user_repo = UserRepository()
        user = await user_repo.get_by_email(google_email)
        
        if not user:
            return OAuthCallbackResponse(
                message="User not found"
            )
        
        # 기존 사용자 정보 업데이트 (user_id는 기존 디스코드 ID 유지)
        update_user = User(
            user_id=user.user_id,
            email=google_email,
            created_at=user.created_at,  # 기존 사용자의 created_at 유지
            username=user_info.get("name"),
            access_token=access_token,
            refresh_token=token_data.get("refresh_token"),
            expires_at=expires_at,
            updated_at=datetime.now(),
            is_active=True
        )
        
        await user_repo.update(update_user)
        
        logger.info(f"OAuth login successful for user: {google_email} -> discord_id: {user.user_id} (expires in {expires_in}s)")

        # calendar 조회 및 저장 - 수정된 함수 호출
        try:
            count_update = await save_google_calendar_events(access_token, google_email)
            logger.info(f"Calendar data: {count_update} events updated")
        except Exception as e:
            logger.error(f"Failed to save calendar events: {e}")
            # 캘린더 저장 실패해도 로그인은 성공으로 처리
            count_update = 0

        return OAuthCallbackResponse(
            message=f"Login successful, {count_update} events updated"
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

# @router.post("/verify")
# async def verify_google_token_endpoint(request: TokenVerifyRequest):
#     """구글 Access Token을 검증합니다"""
    
#     try:
#         # 구글 토큰 검증 및 사용자 정보 조회
#         user_info = await verify_google_token(request.access_token)
        
#         # 토큰 정보도 함께 조회
#         try:
#             token_info = await get_token_info(request.access_token)
#             expires_in = token_info.get("expires_in")
#         except:
#             expires_in = None
        
#         logger.info(f"Token verification successful for user: {user_info.get('email')}")
        
#         return {
#             "message": "Token verification successful",
#             "user_info": user_info,
#             "token_expires_in": expires_in,
#             "note": "Token expiration info is managed by Google OAuth server"
#         }
        
#     except ValueError as e:
#         logger.warning(f"Token verification failed: {e}")
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail=str(e)
#         )
#     except Exception as e:
#         logger.error(f"Unexpected token verification error: {e}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail="Token verification failed"
#         )

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
            "login": "POST /api/v1/auth/login",
            "callback": "GET /api/v1/auth/callback", 
            "verify": "POST /api/v1/auth/verify",
            "refresh": "POST /api/v1/auth/token/refresh"
        }
    } 



# 구글 캘린더 정보 조회
@router.post("/calendar", response_model=CalendarResponse)
async def get_calendar_endpoint(request: CalendarRequest):
    """구글 Oauth2 액세스 토큰을 통해 캘린더 정보를 조회합니다."""
    try:
        user_repo = UserRepository()
        # 사용자 정보 조회
        user = await user_repo.get_by_id(request.id)
        # user email 존재 확인
        if not user.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="login first"
            )
        
        # oauth access token 존재 확인
        if not user.access_token:
            req = LoginUrlRequest(
                user_id=user.user_id,
                user_email=user.email
            )
            return await get_google_login_url_endpoint(req)
        
        # access token 검증
        token_info = await verify_google_token(user.access_token)
        if not token_info:
            req = LoginUrlRequest(
                user_id=user.user_id,
                user_email=user.email
            )
            return await get_google_login_url_endpoint(req)
        
        # 구글 캘린더 API 호출
        calendar_data = await get_google_calendar_events(user.access_token)

        # 캘린더 데이터 저장 - 수정된 함수 호출
        count_update = await save_google_calendar_events(user.access_token, user.email)
        
        return CalendarResponse(
               message=f"Success, {count_update} events updated",
        )
        
    except Exception as e:
        logger.error(f"Error retrieving calendar data: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve calendar data"
        )
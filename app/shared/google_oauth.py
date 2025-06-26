import httpx
from typing import Dict, Any
from config.settings import settings
import logging

logger = logging.getLogger(__name__)

async def verify_google_token(access_token: str) -> Dict[str, Any]:
    """구글 액세스 토큰을 검증하고 사용자 정보를 반환"""
    
    try:
        async with httpx.AsyncClient() as client:
            # 구글 사용자 정보 API 호출
            response = await client.get(
                "https://www.googleapis.com/oauth2/v2/userinfo",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            
            if response.status_code != 200:
                logger.warning(f"Google token verification failed: {response.status_code}")
                raise ValueError("Invalid Google access token")
            
            user_info = response.json()
            logger.info(f"Google token verified for user: {user_info.get('email')}")
            
            return user_info
            
    except httpx.RequestError as e:
        logger.error(f"Error verifying Google token: {e}")
        raise ValueError("Failed to verify Google token")

def get_google_login_url(state: str = None) -> str:
    """구글 OAuth 로그인 URL 생성"""
    
    base_url = "https://accounts.google.com/o/oauth2/auth"
    
    params = {
        "client_id": settings.google_client_id,
        "redirect_uri": settings.google_oauth_redirect_uri,
        "scope": "openid email profile",
        "response_type": "code",
        "access_type": "offline",
    }
    
    if state:
        params["state"] = state
    
    # URL 생성
    query_string = "&".join([f"{k}={v}" for k, v in params.items()])
    
    return f"{base_url}?{query_string}"

async def exchange_code_for_token(authorization_code: str) -> Dict[str, Any]:
    """Authorization Code를 Access Token으로 교환"""
    
    try:
        async with httpx.AsyncClient() as client:
            data = {
                "client_id": settings.google_client_id,
                "client_secret": settings.google_client_secret,
                "code": authorization_code,
                "grant_type": "authorization_code",
                "redirect_uri": settings.google_oauth_redirect_uri,
            }
            
            response = await client.post("https://oauth2.googleapis.com/token", data=data)
            
            if response.status_code != 200:
                logger.error(f"Token exchange failed: {response.status_code} - {response.text}")
                raise ValueError("Failed to exchange authorization code")
            
            token_data = response.json()
            logger.info("Successfully exchanged code for tokens")
            
            return token_data
            
    except httpx.RequestError as e:
        logger.error(f"Error exchanging code for token: {e}")
        raise ValueError("Token exchange failed")

async def refresh_access_token(refresh_token: str) -> Dict[str, Any]:
    """Refresh Token을 사용하여 새로운 Access Token 발급"""
    
    try:
        async with httpx.AsyncClient() as client:
            data = {
                "client_id": settings.google_client_id,
                "client_secret": settings.google_client_secret,
                "refresh_token": refresh_token,
                "grant_type": "refresh_token",
            }
            
            response = await client.post("https://oauth2.googleapis.com/token", data=data)
            
            if response.status_code != 200:
                logger.error(f"Token refresh failed: {response.status_code} - {response.text}")
                raise ValueError("Failed to refresh access token")
            
            token_data = response.json()
            logger.info("Successfully refreshed access token")
            
            return token_data
            
    except httpx.RequestError as e:
        logger.error(f"Error refreshing token: {e}")
        raise ValueError("Token refresh failed")

async def get_token_info(access_token: str) -> Dict[str, Any]:
    """구글 토큰 정보 조회 (만료 시간 포함)"""
    
    try:
        async with httpx.AsyncClient() as client:
            # 구글 토큰 정보 API 호출
            response = await client.get(
                "https://www.googleapis.com/oauth2/v1/tokeninfo",
                params={"access_token": access_token}
            )
            
            if response.status_code != 200:
                logger.warning(f"Token info request failed: {response.status_code}")
                raise ValueError("Invalid or expired access token")
            
            token_info = response.json()
            logger.info(f"Token info retrieved, expires in: {token_info.get('expires_in')} seconds")
            
            return token_info
            
    except httpx.RequestError as e:
        logger.error(f"Error getting token info: {e}")
        raise ValueError("Failed to get token information") 
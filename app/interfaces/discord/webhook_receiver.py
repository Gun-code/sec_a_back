from fastapi import APIRouter, Request, HTTPException, status
from typing import Dict, Any
import json
import logging
from config.settings import settings

logger = logging.getLogger(__name__)

router = APIRouter()

class DiscordWebhookReceiver:
    """디스코드 웹훅 수신 및 처리"""
    
    def __init__(self):
        self.webhook_handlers = {
            "message": self._handle_message,
            "interaction": self._handle_interaction,
            "member_join": self._handle_member_join,
            "member_leave": self._handle_member_leave,
        }
    
    async def process_webhook(self, payload: Dict[str, Any]) -> Dict[str, str]:
        """웹훅 페이로드 처리"""
        try:
            event_type = payload.get("type", "unknown")
            
            if event_type in self.webhook_handlers:
                handler = self.webhook_handlers[event_type]
                return await handler(payload)
            else:
                logger.warning(f"Unknown webhook event type: {event_type}")
                return {"status": "ignored", "reason": f"Unknown event type: {event_type}"}
                
        except Exception as e:
            logger.error(f"Error processing webhook: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Webhook processing failed: {str(e)}"
            )
    
    async def _handle_message(self, payload: Dict[str, Any]) -> Dict[str, str]:
        """메시지 이벤트 처리"""
        author = payload.get("author", {})
        content = payload.get("content", "")
        channel_id = payload.get("channel_id")
        
        logger.info(f"Received message from {author.get('username', 'Unknown')} in channel {channel_id}: {content}")
        
        # 여기에 메시지 처리 로직 구현
        # 예: 특정 명령어 파싱, 데이터베이스 저장 등
        
        return {"status": "processed", "type": "message"}
    
    async def _handle_interaction(self, payload: Dict[str, Any]) -> Dict[str, str]:
        """인터랙션 이벤트 처리 (슬래시 명령어, 버튼 클릭 등)"""
        interaction_type = payload.get("type")
        user = payload.get("user", {})
        
        logger.info(f"Received interaction type {interaction_type} from {user.get('username', 'Unknown')}")
        
        # 여기에 인터랙션 처리 로직 구현
        
        return {"status": "processed", "type": "interaction"}
    
    async def _handle_member_join(self, payload: Dict[str, Any]) -> Dict[str, str]:
        """멤버 가입 이벤트 처리"""
        member = payload.get("member", {})
        guild_id = payload.get("guild_id")
        
        logger.info(f"Member {member.get('user', {}).get('username', 'Unknown')} joined guild {guild_id}")
        
        # 여기에 멤버 가입 처리 로직 구현
        # 예: 환영 메시지, 역할 부여 등
        
        return {"status": "processed", "type": "member_join"}
    
    async def _handle_member_leave(self, payload: Dict[str, Any]) -> Dict[str, str]:
        """멤버 탈퇴 이벤트 처리"""
        user = payload.get("user", {})
        guild_id = payload.get("guild_id")
        
        logger.info(f"Member {user.get('username', 'Unknown')} left guild {guild_id}")
        
        # 여기에 멤버 탈퇴 처리 로직 구현
        
        return {"status": "processed", "type": "member_leave"}

webhook_receiver = DiscordWebhookReceiver()

@router.post("/discord/webhook")
async def receive_discord_webhook(request: Request):
    """디스코드 웹훅 엔드포인트"""
    try:
        payload = await request.json()
        result = await webhook_receiver.process_webhook(payload)
        return result
        
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid JSON payload"
        )

@router.get("/discord/webhook/health")
async def webhook_health_check():
    """웹훅 엔드포인트 상태 확인"""
    return {"status": "healthy", "service": "discord_webhook_receiver"}

# 디스코드 봇으로 메시지 전송하는 함수 (선택사항)
async def send_discord_message(content: str, channel_id: str = None):
    """디스코드 채널로 메시지 전송"""
    if not settings.discord_webhook_url:
        logger.warning("Discord webhook URL not configured")
        return False
    
    try:
        import aiohttp
        
        payload = {
            "content": content,
            "username": "Backend Bot"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(settings.discord_webhook_url, json=payload) as response:
                if response.status == 204:
                    logger.info("Message sent to Discord successfully")
                    return True
                else:
                    logger.error(f"Failed to send Discord message: {response.status}")
                    return False
                    
    except Exception as e:
        logger.error(f"Error sending Discord message: {str(e)}")
        return False 
from typing import Optional, List, Dict, Any
from datetime import datetime
import logging
from config.settings import settings

logger = logging.getLogger(__name__)

class GoogleCalendarService:
    """구글 캘린더 API 서비스"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.google_calendar_api_key
        self.base_url = "https://www.googleapis.com/calendar/v3"
    
    async def create_event(
        self,
        calendar_id: str,
        title: str,
        start_datetime: datetime,
        end_datetime: datetime,
        description: Optional[str] = None,
        location: Optional[str] = None,
        attendees: Optional[List[str]] = None
    ) -> Optional[Dict[str, Any]]:
        """이벤트 생성"""
        if not self.api_key:
            logger.warning("Google Calendar API key not configured")
            return None
        
        try:
            import aiohttp
            
            event_data = {
                "summary": title,
                "description": description or "",
                "location": location or "",
                "start": {
                    "dateTime": start_datetime.isoformat(),
                    "timeZone": "Asia/Seoul"
                },
                "end": {
                    "dateTime": end_datetime.isoformat(),
                    "timeZone": "Asia/Seoul"
                }
            }
            
            if attendees:
                event_data["attendees"] = [{"email": email} for email in attendees]
            
            url = f"{self.base_url}/calendars/{calendar_id}/events"
            params = {"key": self.api_key}
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=event_data, params=params) as response:
                    if response.status == 200:
                        result = await response.json()
                        logger.info(f"Event created successfully: {result.get('id')}")
                        return result
                    else:
                        logger.error(f"Failed to create event: {response.status}")
                        return None
                        
        except Exception as e:
            logger.error(f"Error creating Google Calendar event: {str(e)}")
            return None
    
    async def get_event(self, calendar_id: str, event_id: str) -> Optional[Dict[str, Any]]:
        """이벤트 조회"""
        if not self.api_key:
            logger.warning("Google Calendar API key not configured")
            return None
        
        try:
            import aiohttp
            
            url = f"{self.base_url}/calendars/{calendar_id}/events/{event_id}"
            params = {"key": self.api_key}
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result
                    else:
                        logger.error(f"Failed to get event: {response.status}")
                        return None
                        
        except Exception as e:
            logger.error(f"Error getting Google Calendar event: {str(e)}")
            return None
    
    async def update_event(
        self,
        calendar_id: str,
        event_id: str,
        title: Optional[str] = None,
        start_datetime: Optional[datetime] = None,
        end_datetime: Optional[datetime] = None,
        description: Optional[str] = None,
        location: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """이벤트 수정"""
        if not self.api_key:
            logger.warning("Google Calendar API key not configured")
            return None
        
        # 기존 이벤트 정보 조회
        existing_event = await self.get_event(calendar_id, event_id)
        if not existing_event:
            return None
        
        try:
            import aiohttp
            
            # 업데이트할 필드만 변경
            if title:
                existing_event["summary"] = title
            if description is not None:
                existing_event["description"] = description
            if location is not None:
                existing_event["location"] = location
            if start_datetime:
                existing_event["start"] = {
                    "dateTime": start_datetime.isoformat(),
                    "timeZone": "Asia/Seoul"
                }
            if end_datetime:
                existing_event["end"] = {
                    "dateTime": end_datetime.isoformat(),
                    "timeZone": "Asia/Seoul"
                }
            
            url = f"{self.base_url}/calendars/{calendar_id}/events/{event_id}"
            params = {"key": self.api_key}
            
            async with aiohttp.ClientSession() as session:
                async with session.put(url, json=existing_event, params=params) as response:
                    if response.status == 200:
                        result = await response.json()
                        logger.info(f"Event updated successfully: {event_id}")
                        return result
                    else:
                        logger.error(f"Failed to update event: {response.status}")
                        return None
                        
        except Exception as e:
            logger.error(f"Error updating Google Calendar event: {str(e)}")
            return None
    
    async def delete_event(self, calendar_id: str, event_id: str) -> bool:
        """이벤트 삭제"""
        if not self.api_key:
            logger.warning("Google Calendar API key not configured")
            return False
        
        try:
            import aiohttp
            
            url = f"{self.base_url}/calendars/{calendar_id}/events/{event_id}"
            params = {"key": self.api_key}
            
            async with aiohttp.ClientSession() as session:
                async with session.delete(url, params=params) as response:
                    if response.status == 204:
                        logger.info(f"Event deleted successfully: {event_id}")
                        return True
                    else:
                        logger.error(f"Failed to delete event: {response.status}")
                        return False
                        
        except Exception as e:
            logger.error(f"Error deleting Google Calendar event: {str(e)}")
            return False
    
    async def list_events(
        self,
        calendar_id: str,
        time_min: Optional[datetime] = None,
        time_max: Optional[datetime] = None,
        max_results: int = 250
    ) -> List[Dict[str, Any]]:
        """이벤트 목록 조회"""
        if not self.api_key:
            logger.warning("Google Calendar API key not configured")
            return []
        
        try:
            import aiohttp
            
            url = f"{self.base_url}/calendars/{calendar_id}/events"
            params = {
                "key": self.api_key,
                "maxResults": max_results,
                "orderBy": "startTime",
                "singleEvents": True
            }
            
            if time_min:
                params["timeMin"] = time_min.isoformat()
            if time_max:
                params["timeMax"] = time_max.isoformat()
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result.get("items", [])
                    else:
                        logger.error(f"Failed to list events: {response.status}")
                        return []
                        
        except Exception as e:
            logger.error(f"Error listing Google Calendar events: {str(e)}")
            return []

# 싱글톤 인스턴스
google_calendar_service = GoogleCalendarService() 
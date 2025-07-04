import httpx
from infrastructure.db.repositories import EventRepository
from fastapi import HTTPException, status
from datetime import datetime


# 구글 캘린더 데이터 응답 형식
# {
#   "kind": "calendar#events",
#   "etag": "\"p33b33i92opd20g0\"",
#   "summary": "사용자 이름",
#   "updated": "2025-07-01T05:00:00.000Z",
#   "timeZone": "Asia/Seoul",
#   "accessRole": "owner",
#   "items": [
#     {
#       "kind": "calendar#event",
#       "id": "abcd1234efgh5678",
#       "status": "confirmed",
#       "htmlLink": "https://www.google.com/calendar/event?eid=...",
#       "summary": "회의",
#       "description": "프로젝트 진행 회의",
#       "location": "Zoom",
#       "start": {
#         "dateTime": "2025-07-01T10:00:00+09:00",
#         "timeZone": "Asia/Seoul"
#       },
#       "end": {
#         "dateTime": "2025-07-01T11:00:00+09:00",
#         "timeZone": "Asia/Seoul"
#       },
#       "creator": {
#         "email": "user@gmail.com"
#       },
#       "organizer": {
#         "email": "user@gmail.com",
#         "self": true
#       },
#       "created": "2025-06-30T08:00:00.000Z",
#       "updated": "2025-06-30T08:30:00.000Z"
#     },
#     ...
#   ]
# }

async def get_google_calendar_events(access_token: str):
    url = "https://www.googleapis.com/calendar/v3/calendars/primary/events"

    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        return response.json()
    
async def save_google_calendar_events(access_token: str, user_email: str):
    """캘린더 데이터를 MongoDB에 저장"""
    try:
        # 캘린더 데이터 조회
        calendar_items = await get_google_calendar_events(access_token)
        
        if not calendar_items or "items" not in calendar_items:
            return 0
        
        # 이벤트 데이터 저장
        event_repo = EventRepository()
        return await event_repo.update_many(calendar_items["items"], user_email)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save calendar events: {str(e)}"
        )

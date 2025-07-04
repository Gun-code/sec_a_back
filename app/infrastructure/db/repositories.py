from typing import Optional, List
from bson import ObjectId
from pymongo.errors import DuplicateKeyError
from domain.user.entities import User
from domain.user.repository import UserRepositoryInterface
from .models import UserDocument, EventDocument, EventDateTime, EventCreator, EventOrganizer, EventReminder
import logging
from datetime import datetime
from dateutil.parser import parse as parse_datetime

logger = logging.getLogger(__name__)

class UserRepository(UserRepositoryInterface):
    """MongoDB를 사용한 사용자 레포지토리 구현체"""
    
    async def create(self, user: User) -> User:
        """사용자 생성 - OAuth에서 사용"""
        try:
            user_doc = UserDocument(
                user_id=user.user_id,
                username=user.username,
                email=user.email,
                access_token=user.access_token,
                refresh_token=user.refresh_token,
                expires_at=user.expires_at,
                created_at=user.created_at,
                updated_at=user.updated_at,
                is_active=user.is_active
            )
            
            await user_doc.insert()
            return self._to_entity(user_doc)
            
        except DuplicateKeyError:
            raise ValueError("User with this username or email already exists")
    
    async def get_by_id(self, user_id: str) -> Optional[User]:
        """ID로 사용자 조회 - OAuth에서 사용"""
        try:
            user_doc = await UserDocument.find_one(UserDocument.user_id == user_id)
            return self._to_entity(user_doc) if user_doc else None
        except Exception:
            return None
    
    async def get_by_username(self, username: str) -> Optional[User]:
        """사용자명으로 사용자 조회"""
        # TODO: 사용자명 검색 기능 구현 예정
        user_doc = await UserDocument.find_one(UserDocument.username == username)
        return self._to_entity(user_doc) if user_doc else None
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """이메일로 사용자 조회 - OAuth에서 사용"""
        user_doc = await UserDocument.find_one(UserDocument.email == email)
        return self._to_entity(user_doc) if user_doc else None
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[User]:
        """모든 사용자 조회 (페이징 포함)"""
        # TODO: 사용자 목록 조회 기능 구현 예정 (관리자 기능)
        return []
    
    async def get_token_by_id(self, user_id: str) -> Optional[User]:
        """사용자 ID로 토큰 조회 - OAuth에서 사용"""
        user_doc = await UserDocument.find_one(UserDocument.user_id == user_id)
        return self._to_entity(user_doc) if user_doc else None
    
    async def update(self, user: User) -> User:
        """사용자 정보 업데이트 - OAuth에서 사용"""
        try:
            user_doc = await UserDocument.find_one(UserDocument.user_id == user.user_id)
            if not user_doc:
                raise ValueError("User not found")
            
            user_doc.username = user.username
            user_doc.email = user.email
            user_doc.access_token = user.access_token
            user_doc.refresh_token = user.refresh_token
            user_doc.expires_at = user.expires_at
            user_doc.is_active = user.is_active
            user_doc.updated_at = user.updated_at
            
            await user_doc.save()
            return self._to_entity(user_doc)
            
        except DuplicateKeyError:
            raise ValueError("Email already exists")
    
    async def delete(self, user_id: str) -> bool:
        """사용자 삭제"""
        # TODO: 사용자 삭제 기능 구현 예정 (관리자 기능)
        return False
    
    async def exists_by_username(self, username: str) -> bool:
        """사용자명 존재 여부 확인"""
        # TODO: 사용자명 중복 체크 기능 구현 예정
        return False
    
    async def exists_by_email(self, email: str) -> bool:
        """이메일 존재 여부 확인"""
        # TODO: 이메일 중복 체크 기능 구현 예정
        return False
    
    def _to_entity(self, user_doc: UserDocument) -> User:
        """MongoDB 문서를 도메인 엔티티로 변환"""
        
        return User(
            user_id=user_doc.user_id,
            username=user_doc.username,
            email=user_doc.email,
            access_token=user_doc.access_token,
            refresh_token=user_doc.refresh_token,
            expires_at=user_doc.expires_at,
            created_at=user_doc.created_at,
            updated_at=user_doc.updated_at,
            is_active=user_doc.is_active
        )



class EventRepository:
    """이벤트 레포지토리 (구글 캘린더 연동용)"""

    async def create(self, item: dict, created_by_user_email: str) -> None:
        """구글 캘린더 이벤트 1개 저장"""
        try:
            # 시작/종료 날짜 파싱
            is_all_day = "date" in item.get("start", {})
            start_dt = EventDateTime(
                date=item["start"].get("date"),
                dateTime=parse_datetime(item["start"]["dateTime"]) if "dateTime" in item["start"] else None,
                timeZone=item["start"].get("timeZone")
            )
            end_dt = EventDateTime(
                date=item["end"].get("date"),
                dateTime=parse_datetime(item["end"]["dateTime"]) if "dateTime" in item["end"] else None,
                timeZone=item["end"].get("timeZone")
            )

            # 문서 생성
            event_doc = EventDocument(
                google_event_id=item["id"],
                status=item.get("status", "confirmed"),
                title=item.get("summary"),
                description=item.get("description"),
                location=item.get("location"),
                html_link=item.get("htmlLink"),
                start=start_dt,
                end=end_dt,
                is_all_day=is_all_day,
                recurrence=item.get("recurrence"),
                reminders=EventReminder(**item["reminders"]) if "reminders" in item else None,
                creator=EventCreator(**item["creator"]) if "creator" in item else None,
                organizer=EventOrganizer(**item["organizer"]) if "organizer" in item else None,
                created_by_user_email=created_by_user_email,
                created_at=parse_datetime(item.get("created", datetime.utcnow().isoformat())),
                updated_at=parse_datetime(item.get("updated", datetime.utcnow().isoformat()))
            )

            await event_doc.insert()
            return None

        except DuplicateKeyError:
            raise ValueError("Event with this google_event_id already exists")

    async def create_many(self, items: List[dict], user_email: str):
        """구글 캘린더 이벤트 여러 개 저장"""
        results = 0
        for item in items:
            try:
                await self.create(item, created_by_user_email=user_email)
                results += 1
            except ValueError:
                continue  # 중복은 건너뜀
        return results

    async def update(self, item: dict, user_email: str):
        """구글 캘린더 이벤트 1개 수정"""
        try:
            event_doc = await EventDocument.find_one(EventDocument.google_event_id == item["id"])
            is_update = False
            if not event_doc:
                await self.create(item, user_email)
                is_update = True
            else:
                if item["updated"] != event_doc.updated_at:
                    is_update = True

            if is_update:
                update_event_doc = EventDocument(
                    google_event_id=item["id"],
                    status=item.get("status", "confirmed"),
                    title=item.get("summary"),
                    description=item.get("description"),
                    location=item.get("location"),
                    html_link=item.get("htmlLink"),
                    start=EventDateTime(
                        date=item["start"].get("date"),
                        dateTime=parse_datetime(item["start"]["dateTime"]) if "dateTime" in item["start"] else None,
                        timeZone=item["start"].get("timeZone")
                    ),
                    end=EventDateTime(
                        date=item["end"].get("date"),
                        dateTime=parse_datetime(item["end"]["dateTime"]) if "dateTime" in item["end"] else None,
                        timeZone=item["end"].get("timeZone")
                    ),
                    is_all_day="date" in item.get("start", {}),
                    recurrence=item.get("recurrence"),
                    reminders=EventReminder(**item["reminders"]) if "reminders" in item else None,
                    creator=EventCreator(**item["creator"]) if "creator" in item else None,
                    organizer=EventOrganizer(**item["organizer"]) if "organizer" in item else None,
                    created_by_user_email=user_email,
                    created_at=parse_datetime(item.get("created", datetime.utcnow().isoformat())),
                    updated_at=parse_datetime(item.get("updated", datetime.utcnow().isoformat()))
                )
                await update_event_doc.update()

            return is_update
        except Exception as e:
            raise ValueError(f"Error updating event: {e}")

    async def update_many(self, items: List[dict], user_email: str):
        """구글 캘린더 이벤트 여러 개 수정"""
        update_count = 0
        for item in items:
            is_update = await self.update(item, user_email)
            if is_update:
                update_count += 1
        return update_count

    async def get_by_email(self, event_email: str) -> Optional[List[dict]]:
        """이벤트 이메일로 이벤트 조회"""
        event_docs = await EventDocument.find(EventDocument.created_by_user_email == event_email).to_list()
        return [self._to_dict(event_doc) for event_doc in event_docs] if event_docs else None
        
    def _to_dict(self, event_doc: EventDocument) -> dict:
        """EventDocument를 딕셔너리로 변환"""
        return {
            "google_event_id": event_doc.google_event_id,
            "title": event_doc.title,
            "description": event_doc.description,
            "location": event_doc.location,
            "start": {
                "date": event_doc.start.date,
                "dateTime": event_doc.start.dateTime.isoformat() if event_doc.start.dateTime else None,
                "timeZone": event_doc.start.timeZone
            } if event_doc.start else None,
            "end": {
                "date": event_doc.end.date,
                "dateTime": event_doc.end.dateTime.isoformat() if event_doc.end.dateTime else None,
                "timeZone": event_doc.end.timeZone
            } if event_doc.end else None,
            "is_all_day": event_doc.is_all_day,
            "status": event_doc.status,
            "html_link": event_doc.html_link,
            "created_by_user_email": event_doc.created_by_user_email,
            "created_at": event_doc.created_at.isoformat() if event_doc.created_at else None,
            "updated_at": event_doc.updated_at.isoformat() if event_doc.updated_at else None
        }
      
    def __init__(self):
        pass
    
    # TODO: 구글 캘린더 API 연동
    # - 이벤트 생성
    # - 이벤트 조회
    # - 이벤트 수정
    # - 이벤트 삭제

# TODO: 디스코드 메시지 저장/조회 기능 구현 예정
class DiscordMessageRepository:
    """디스코드 메시지 레포지토리"""
    
    def __init__(self):
        pass
    
    # TODO: 디스코드 메시지 관련 기능
    # - 메시지 저장
    # - 메시지 조회
    # - 메시지 분석 
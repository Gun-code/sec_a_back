from beanie import Document
from pydantic import Field, EmailStr, BaseModel
from typing import Optional, List, Literal
from datetime import datetime
from pymongo import IndexModel

class UserDocument(Document):
    """사용자 MongoDB 문서 모델"""
    user_id: str  # 디스코드 사용자 ID (기본 키)
    username: Optional[str] = None  # 사용자명 (Google OAuth에서 받음)
    email: EmailStr  # 이메일 (유니크)
    full_name: Optional[str] = None
    is_active: bool = True
    
    # OAuth 관련 필드들
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    expires_at: Optional[datetime] = None
    
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    class Settings:
        name = "users"  # MongoDB 컬렉션 이름
        indexes = [
            IndexModel([("user_id", 1)], unique=True),  # user_id가 기본 키
            IndexModel([("username", 1)], unique=True, sparse=True),  # sparse로 null 중복 허용
            IndexModel([("email", 1)], unique=True),
            IndexModel([("created_at", -1)]),
        ]

class EventDateTime(BaseModel):
    date: Optional[str] = None         # 종일 이벤트 (YYYY-MM-DD)
    dateTime: Optional[datetime] = None  # 시간 포함 이벤트
    timeZone: Optional[str] = None

class EventCreator(BaseModel):
    email: Optional[str]
    displayName: Optional[str] = None
    self: Optional[bool] = None

class EventOrganizer(BaseModel):
    email: Optional[str]
    displayName: Optional[str] = None
    self: Optional[bool] = None

class EventReminder(BaseModel):
    useDefault: Optional[bool]
    overrides: Optional[List[dict]] = None

class EventDocument(Document):
    """Google Calendar 이벤트 문서 모델"""
    google_event_id: Optional[str] = None
    status: Optional[Literal["confirmed", "tentative", "cancelled"]] = "confirmed"
    title: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    html_link: Optional[str] = None

    start: EventDateTime
    end: EventDateTime
    is_all_day: bool = False

    recurrence: Optional[List[str]] = None
    reminders: Optional[EventReminder] = None

    creator: Optional[EventCreator] = None
    organizer: Optional[EventOrganizer] = None

    created_by_user_email: Optional[str] = None  # 내부 유저 ID
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "events"
        indexes = [
            {"key": [("google_event_id", 1)], "unique": True, "sparse": True},
            {"key": [("created_by_user_email", 1)]},
            {"key": [("start.dateTime", 1)]},  # 시간 기반 쿼리용 인덱스
        ]

class DiscordMessageDocument(Document):
    """디스코드 메시지 로그 MongoDB 문서 모델"""
    discord_message_id: str
    discord_channel_id: str
    discord_guild_id: Optional[str] = None
    discord_user_id: str
    discord_username: str
    content: Optional[str] = None
    message_type: str = "text"  # text, interaction, etc.
    created_at: datetime = Field(default_factory=datetime.now)
    
    class Settings:
        name = "discord_messages"
        indexes = [
            IndexModel([("discord_message_id", 1)], unique=True),
            IndexModel([("discord_channel_id", 1)]),
            IndexModel([("discord_user_id", 1)]),
            IndexModel([("created_at", -1)]),
        ]

class VectorDocument(Document):
    """ChromaDB와 동기화를 위한 벡터 문서 메타데이터"""
    content: str  # 원본 텍스트
    content_type: str  # "user_profile", "event_description", "discord_message" 등
    source_id: str  # 원본 문서의 ID
    vector_id: str  # ChromaDB에서의 벡터 ID
    metadata: dict = Field(default_factory=dict)  # 추가 메타데이터
    created_at: datetime = Field(default_factory=datetime.now)
    
    class Settings:
        name = "vectors"
        indexes = [
            IndexModel([("vector_id", 1)], unique=True),
            IndexModel([("source_id", 1)]),
            IndexModel([("content_type", 1)]),
        ]

# Beanie에서 사용할 문서 모델들
DOCUMENT_MODELS = [
    UserDocument,
    EventDocument,
    DiscordMessageDocument,
    VectorDocument,
] 
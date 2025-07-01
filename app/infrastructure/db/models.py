from beanie import Document, Indexed
from pydantic import Field, EmailStr
from typing import Optional, List
from datetime import datetime
from pymongo import IndexModel

class UserDocument(Document):
    """사용자 MongoDB 문서 모델"""
    user_id: Indexed(str, unique=True)  # 디스코드 사용자 ID (기본 키)
    username: Optional[str] = None  # 사용자명 (Google OAuth에서 받음)
    email: Indexed(EmailStr, unique=True)  # 이메일 (유니크)
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

class EventDocument(Document):
    """이벤트 MongoDB 문서 모델 (구글 캘린더 연동용)"""
    title: str
    description: Optional[str] = None
    start_datetime: datetime
    end_datetime: datetime
    location: Optional[str] = None
    is_all_day: bool = False
    google_event_id: Optional[Indexed(str, unique=True)] = None
    created_by_user_id: Optional[str] = None  # UserDocument의 ID 참조
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    class Settings:
        name = "events"
        indexes = [
            IndexModel([("start_datetime", 1)]),
            IndexModel([("google_event_id", 1)], unique=True, sparse=True),
            IndexModel([("created_by_user_id", 1)]),
        ]

class DiscordMessageDocument(Document):
    """디스코드 메시지 로그 MongoDB 문서 모델"""
    discord_message_id: Indexed(str, unique=True)
    discord_channel_id: Indexed(str)
    discord_guild_id: Optional[Indexed(str)] = None
    discord_user_id: Indexed(str)
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
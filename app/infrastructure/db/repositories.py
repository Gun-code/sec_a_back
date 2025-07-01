from typing import Optional, List
from bson import ObjectId
from pymongo.errors import DuplicateKeyError
from domain.user.entities import User
from domain.user.repository import UserRepositoryInterface
from .models import UserDocument
import logging

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

        
        # 양식 : {
        # user_id: str
        # username: Optional[str] = None
        # email: str
        # created_at: datetime
        # access_token: Optional[str] = None
        # refresh_token: Optional[str] = None
        # expires_at: Optional[datetime] = None
        # updated_at: Optional[datetime] = None
        # is_active: bool = True
        # }

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


# TODO: 구글 캘린더 연동 기능 구현 예정
class EventRepository:
    """이벤트 레포지토리 (구글 캘린더 연동용)"""
    
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
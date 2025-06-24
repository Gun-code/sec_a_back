from abc import ABC, abstractmethod
from typing import Optional, List
from .entities import User

class UserRepositoryInterface(ABC):
    """사용자 레포지토리 추상 인터페이스"""
    
    @abstractmethod
    async def create(self, user: User) -> User:
        """사용자 생성"""
        pass
    
    @abstractmethod
    async def get_by_id(self, user_id: str) -> Optional[User]:
        """ID로 사용자 조회"""
        pass
    
    @abstractmethod
    async def get_by_username(self, username: str) -> Optional[User]:
        """사용자명으로 사용자 조회"""
        pass
    
    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[User]:
        """이메일로 사용자 조회"""
        pass
    
    @abstractmethod
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[User]:
        """모든 사용자 조회 (페이징 포함)"""
        pass
    
    @abstractmethod
    async def update(self, user: User) -> User:
        """사용자 정보 업데이트"""
        pass
    
    @abstractmethod
    async def delete(self, user_id: str) -> bool:
        """사용자 삭제"""
        pass
    
    @abstractmethod
    async def exists_by_username(self, username: str) -> bool:
        """사용자명 존재 여부 확인"""
        pass
    
    @abstractmethod
    async def exists_by_email(self, email: str) -> bool:
        """이메일 존재 여부 확인"""
        pass 
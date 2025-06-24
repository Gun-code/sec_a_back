from typing import Optional, List
from domain.user.entities import User
from domain.user.repository import UserRepositoryInterface
from domain.user.value_objects import Email, Username, FullName
from .dto import CreateUserRequest, UpdateUserRequest, UserResponse
from shared.exceptions import UserAlreadyExistsError, UserNotFoundError

class UserUseCase:
    """사용자 관련 유스케이스"""
    
    def __init__(self, user_repository: UserRepositoryInterface):
        self.user_repository = user_repository
    
    async def create_user(self, request: CreateUserRequest) -> UserResponse:
        """사용자 생성"""
        # 밸류 오브젝트 검증
        username = Username(request.username)
        email = Email(request.email)
        full_name = FullName(request.full_name) if request.full_name else None
        
        # 중복 검사
        if await self.user_repository.exists_by_username(username.value):
            raise UserAlreadyExistsError(f"Username '{username.value}' already exists")
        
        if await self.user_repository.exists_by_email(email.value):
            raise UserAlreadyExistsError(f"Email '{email.value}' already exists")
        
        # 사용자 엔티티 생성
        user = User(
            username=username.value,
            email=email.value,
            full_name=full_name.value if full_name else None
        )
        
        # 저장
        created_user = await self.user_repository.create(user)
        
        return UserResponse.from_entity(created_user)
    
    async def get_user_by_id(self, user_id: str) -> UserResponse:
        """ID로 사용자 조회"""
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise UserNotFoundError(f"User with id {user_id} not found")
        
        return UserResponse.from_entity(user)
    
    async def get_user_by_username(self, username: str) -> UserResponse:
        """사용자명으로 사용자 조회"""
        user = await self.user_repository.get_by_username(username)
        if not user:
            raise UserNotFoundError(f"User with username '{username}' not found")
        
        return UserResponse.from_entity(user)
    
    async def get_all_users(self, skip: int = 0, limit: int = 100) -> List[UserResponse]:
        """모든 사용자 조회"""
        users = await self.user_repository.get_all(skip=skip, limit=limit)
        return [UserResponse.from_entity(user) for user in users]
    
    async def update_user(self, user_id: str, request: UpdateUserRequest) -> UserResponse:
        """사용자 정보 업데이트"""
        # 기존 사용자 조회
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise UserNotFoundError(f"User with id {user_id} not found")
        
        # 업데이트할 필드 검증 및 적용
        if request.email:
            email = Email(request.email)
            # 이메일 중복 검사 (자신 제외)
            existing_user = await self.user_repository.get_by_email(email.value)
            if existing_user and existing_user.id != user_id:
                raise UserAlreadyExistsError(f"Email '{email.value}' already exists")
            user.email = email.value
        
        if request.full_name is not None:
            if request.full_name:
                full_name = FullName(request.full_name)
                user.full_name = full_name.value
            else:
                user.full_name = None
        
        # 저장
        updated_user = await self.user_repository.update(user)
        
        return UserResponse.from_entity(updated_user)
    
    async def delete_user(self, user_id: str) -> bool:
        """사용자 삭제"""
        # 사용자 존재 확인
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise UserNotFoundError(f"User with id {user_id} not found")
        
        return await self.user_repository.delete(user_id)
    
    async def deactivate_user(self, user_id: str) -> UserResponse:
        """사용자 비활성화"""
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise UserNotFoundError(f"User with id {user_id} not found")
        
        user.deactivate()
        updated_user = await self.user_repository.update(user)
        
        return UserResponse.from_entity(updated_user)
    
    async def activate_user(self, user_id: str) -> UserResponse:
        """사용자 활성화"""
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise UserNotFoundError(f"User with id {user_id} not found")
        
        user.activate()
        updated_user = await self.user_repository.update(user)
        
        return UserResponse.from_entity(updated_user) 
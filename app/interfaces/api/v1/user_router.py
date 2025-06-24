from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List
from application.user.use_cases import UserUseCase
from application.user.dto import (
    CreateUserRequest, 
    UpdateUserRequest, 
    UserResponse, 
    UserListResponse,
    MessageResponse
)
from infrastructure.db.repositories import UserRepository
from shared.exceptions import UserAlreadyExistsError, UserNotFoundError

router = APIRouter()

async def get_user_use_case() -> UserUseCase:
    """사용자 유스케이스 의존성 주입"""
    user_repository = UserRepository()
    return UserUseCase(user_repository)

@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    request: CreateUserRequest,
    use_case: UserUseCase = Depends(get_user_use_case)
):
    """사용자 생성"""
    try:
        return await use_case.create_user(request)
    except UserAlreadyExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,  # MongoDB ObjectId는 문자열
    use_case: UserUseCase = Depends(get_user_use_case)
):
    """사용자 조회"""
    try:
        return await use_case.get_user_by_id(user_id)
    except UserNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

@router.get("/users", response_model=UserListResponse)
async def get_users(
    skip: int = Query(0, ge=0, description="건너뛸 항목 수"),
    limit: int = Query(100, ge=1, le=1000, description="조회할 최대 항목 수"),
    use_case: UserUseCase = Depends(get_user_use_case)
):
    """사용자 목록 조회"""
    users = await use_case.get_all_users(skip=skip, limit=limit)
    return UserListResponse(
        users=users,
        total=len(users),
        skip=skip,
        limit=limit
    )

@router.get("/users/username/{username}", response_model=UserResponse)
async def get_user_by_username(
    username: str,
    use_case: UserUseCase = Depends(get_user_use_case)
):
    """사용자명으로 사용자 조회"""
    try:
        return await use_case.get_user_by_username(username)
    except UserNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,  # MongoDB ObjectId는 문자열
    request: UpdateUserRequest,
    use_case: UserUseCase = Depends(get_user_use_case)
):
    """사용자 정보 수정"""
    try:
        return await use_case.update_user(user_id, request)
    except UserNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except UserAlreadyExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.delete("/users/{user_id}", response_model=MessageResponse)
async def delete_user(
    user_id: str,  # MongoDB ObjectId는 문자열
    use_case: UserUseCase = Depends(get_user_use_case)
):
    """사용자 삭제"""
    try:
        await use_case.delete_user(user_id)
        return MessageResponse(message="User deleted successfully")
    except UserNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

@router.patch("/users/{user_id}/deactivate", response_model=UserResponse)
async def deactivate_user(
    user_id: str,  # MongoDB ObjectId는 문자열
    use_case: UserUseCase = Depends(get_user_use_case)
):
    """사용자 비활성화"""
    try:
        return await use_case.deactivate_user(user_id)
    except UserNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

@router.patch("/users/{user_id}/activate", response_model=UserResponse)
async def activate_user(
    user_id: str,  # MongoDB ObjectId는 문자열
    use_case: UserUseCase = Depends(get_user_use_case)
):
    """사용자 활성화"""
    try:
        return await use_case.activate_user(user_id)
    except UserNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        ) 
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List

# TODO: 사용자 관리 기능 구현 예정
# from application.user.use_cases import UserUseCase
# from application.user.dto import (
#     CreateUserRequest, 
#     UpdateUserRequest, 
#     UserResponse, 
#     UserListResponse,
#     MessageResponse
# )
# from infrastructure.db.repositories import UserRepository
# from shared.exceptions import UserAlreadyExistsError, UserNotFoundError

router = APIRouter()

# TODO: 사용자 관리 API 구현 예정
# 현재는 OAuth 로그인만 구현되어 있음
# 추후 구현할 기능들:
# - 사용자 생성 (관리자용)
# - 사용자 조회
# - 사용자 목록 조회
# - 사용자 정보 수정
# - 사용자 삭제
# - 사용자 활성화/비활성화

# async def get_user_use_case() -> UserUseCase:
#     """사용자 유스케이스 의존성 주입"""
#     user_repository = UserRepository()
#     return UserUseCase(user_repository)

# @router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
# async def create_user(
#     request: CreateUserRequest,
#     use_case: UserUseCase = Depends(get_user_use_case)
# ):
#     """사용자 생성"""
#     pass

# @router.get("/users/{user_id}", response_model=UserResponse)
# async def get_user(
#     user_id: str,
#     use_case: UserUseCase = Depends(get_user_use_case)
# ):
#     """사용자 조회"""
#     pass

# @router.get("/users", response_model=UserListResponse)
# async def get_users(
#     skip: int = Query(0, ge=0, description="건너뛸 항목 수"),
#     limit: int = Query(100, ge=1, le=1000, description="조회할 최대 항목 수"),
#     use_case: UserUseCase = Depends(get_user_use_case)
# ):
#     """사용자 목록 조회"""
#     pass

# @router.put("/users/{user_id}", response_model=UserResponse)
# async def update_user(
#     user_id: str,
#     request: UpdateUserRequest,
#     use_case: UserUseCase = Depends(get_user_use_case)
# ):
#     """사용자 정보 수정"""
#     pass

# @router.delete("/users/{user_id}", response_model=MessageResponse)
# async def delete_user(
#     user_id: str,
#     use_case: UserUseCase = Depends(get_user_use_case)
# ):
#     """사용자 삭제"""
#     pass

@router.get("/info")
async def get_user_info():
    """사용자 관리 API 정보"""
    return {
        "message": "User Management API",
        "status": "TODO - Implementation pending",
        "available_features": [
            "OAuth 로그인 (구현 완료)"
        ],
        "planned_features": [
            "사용자 생성 (관리자용)",
            "사용자 조회",
            "사용자 목록 조회",
            "사용자 정보 수정",
            "사용자 삭제",
            "사용자 활성화/비활성화"
        ]
    } 
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from domain.user.entities import User

class CreateUserRequest(BaseModel):
    """사용자 생성 요청 DTO"""
    username: str = Field(..., min_length=3, max_length=20, description="사용자명")
    email: EmailStr = Field(..., description="이메일 주소")
    full_name: Optional[str] = Field(None, max_length=100, description="전체 이름")
    
    class Config:
        json_schema_extra = {
            "example": {
                "username": "johndoe",
                "email": "john@example.com",
                "full_name": "John Doe"
            }
        }

class UpdateUserRequest(BaseModel):
    """사용자 정보 수정 요청 DTO"""
    email: Optional[EmailStr] = Field(None, description="이메일 주소")
    full_name: Optional[str] = Field(None, max_length=100, description="전체 이름")
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "newemail@example.com",
                "full_name": "New Full Name"
            }
        }

class UserResponse(BaseModel):
    """사용자 응답 DTO"""
    id: str  # MongoDB ObjectId는 문자열
    username: str
    email: str
    full_name: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "507f1f77bcf86cd799439011",
                "username": "johndoe",
                "email": "john@example.com",
                "full_name": "John Doe",
                "is_active": True,
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00"
            }
        }
    
    @classmethod
    def from_entity(cls, user: User) -> "UserResponse":
        """User 엔티티로부터 응답 DTO 생성"""
        return cls(
            id=user.id,
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at
        )

class UserListResponse(BaseModel):
    """사용자 목록 응답 DTO"""
    users: list[UserResponse]
    total: int
    skip: int
    limit: int
    
    class Config:
        json_schema_extra = {
            "example": {
                "users": [
                    {
                        "id": "507f1f77bcf86cd799439011",
                        "username": "johndoe",
                        "email": "john@example.com",
                        "full_name": "John Doe",
                        "is_active": True,
                        "created_at": "2024-01-01T00:00:00",
                        "updated_at": "2024-01-01T00:00:00"
                    }
                ],
                "total": 1,
                "skip": 0,
                "limit": 100
            }
        }

class MessageResponse(BaseModel):
    """일반적인 메시지 응답 DTO"""
    message: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "User deleted successfully"
            }
        } 

class CalendarRequest(BaseModel):
    """구글 캘린더 정보 조회 요청 DTO"""
    id: str

    class Config:
        json_schema_extra = {
            "example": {
                "id": "1234567890"
            }
        }

class CalendarResponse(BaseModel):
    """구글 캘린더 정보 조회 응답 DTO"""
    message: str
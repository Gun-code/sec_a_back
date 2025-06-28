from datetime import datetime
from typing import Optional
from dataclasses import dataclass

@dataclass
class User:
    """사용자 도메인 엔티티"""
    user_id: str
    username: Optional[str] = None
    email: str
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    expires_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    is_active: bool = True
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        self.updated_at = datetime.now()
    
    def update_profile(self, full_name: Optional[str] = None, email: Optional[str] = None):
        """프로필 정보 업데이트"""
        if full_name is not None:
            self.full_name = full_name
        if email is not None:
            self.email = email
        self.updated_at = datetime.now()
    
    def deactivate(self):
        """사용자 비활성화"""
        self.is_active = False
        self.updated_at = datetime.now()
    
    def activate(self):
        """사용자 활성화"""
        self.is_active = True
        self.updated_at = datetime.now() 
from dataclasses import dataclass
from typing import ClassVar
import re

@dataclass(frozen=True)
class Email:
    """이메일 밸류 오브젝트"""
    value: str
    
    EMAIL_PATTERN: ClassVar[str] = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    def __post_init__(self):
        if not self.is_valid():
            raise ValueError(f"Invalid email format: {self.value}")
    
    def is_valid(self) -> bool:
        """이메일 형식 검증"""
        return bool(re.match(self.EMAIL_PATTERN, self.value))
    
    def domain(self) -> str:
        """이메일 도메인 반환"""
        return self.value.split('@')[1]

@dataclass(frozen=True)
class Username:
    """사용자명 밸류 오브젝트"""
    value: str
    
    MIN_LENGTH: ClassVar[int] = 3
    MAX_LENGTH: ClassVar[int] = 20
    VALID_PATTERN: ClassVar[str] = r'^[a-zA-Z0-9_]+$'
    
    def __post_init__(self):
        if not self.is_valid():
            raise ValueError(f"Invalid username: {self.value}")
    
    def is_valid(self) -> bool:
        """사용자명 검증"""
        if not (self.MIN_LENGTH <= len(self.value) <= self.MAX_LENGTH):
            return False
        return bool(re.match(self.VALID_PATTERN, self.value))

@dataclass(frozen=True)
class FullName:
    """전체 이름 밸류 오브젝트"""
    value: str
    
    MAX_LENGTH: ClassVar[int] = 100
    
    def __post_init__(self):
        if not self.is_valid():
            raise ValueError(f"Invalid full name: {self.value}")
    
    def is_valid(self) -> bool:
        """이름 검증"""
        return len(self.value.strip()) > 0 and len(self.value) <= self.MAX_LENGTH
    
    def first_name(self) -> str:
        """첫 번째 이름 반환"""
        return self.value.split()[0] if self.value.split() else ""
    
    def last_name(self) -> str:
        """마지막 이름 반환"""
        parts = self.value.split()
        return parts[-1] if len(parts) > 1 else "" 
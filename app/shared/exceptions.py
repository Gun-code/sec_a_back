"""공통 예외 클래스 정의"""

class BaseAppError(Exception):
    """애플리케이션 기본 예외"""
    
    def __init__(self, message: str, error_code: str = None):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)

class ValidationError(BaseAppError):
    """데이터 검증 오류"""
    
    def __init__(self, message: str, field: str = None):
        self.field = field
        super().__init__(message, "VALIDATION_ERROR")

class NotFoundError(BaseAppError):
    """리소스를 찾을 수 없음"""
    
    def __init__(self, resource: str, identifier: str = None):
        message = f"{resource} not found"
        if identifier:
            message += f": {identifier}"
        super().__init__(message, "NOT_FOUND")

class AlreadyExistsError(BaseAppError):
    """리소스가 이미 존재함"""
    
    def __init__(self, resource: str, identifier: str = None):
        message = f"{resource} already exists"
        if identifier:
            message += f": {identifier}"
        super().__init__(message, "ALREADY_EXISTS")

class AuthenticationError(BaseAppError):
    """인증 오류"""
    
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, "AUTHENTICATION_ERROR")

class AuthorizationError(BaseAppError):
    """권한 부족 오류"""
    
    def __init__(self, message: str = "Insufficient permissions"):
        super().__init__(message, "AUTHORIZATION_ERROR")

class ExternalServiceError(BaseAppError):
    """외부 서비스 연동 오류"""
    
    def __init__(self, service: str, message: str = None):
        error_message = f"External service error: {service}"
        if message:
            error_message += f" - {message}"
        super().__init__(error_message, "EXTERNAL_SERVICE_ERROR")

class DatabaseError(BaseAppError):
    """데이터베이스 오류"""
    
    def __init__(self, message: str = "Database operation failed"):
        super().__init__(message, "DATABASE_ERROR")

class ConfigurationError(BaseAppError):
    """설정 오류"""
    
    def __init__(self, setting: str, message: str = None):
        error_message = f"Configuration error: {setting}"
        if message:
            error_message += f" - {message}"
        super().__init__(error_message, "CONFIGURATION_ERROR")

# 사용자 관련 예외
class UserNotFoundError(NotFoundError):
    """사용자를 찾을 수 없음"""
    
    def __init__(self, identifier: str = None):
        super().__init__("User", identifier)

class UserAlreadyExistsError(AlreadyExistsError):
    """사용자가 이미 존재함"""
    
    def __init__(self, identifier: str = None):
        super().__init__("User", identifier)

class InvalidCredentialsError(AuthenticationError):
    """잘못된 인증 정보"""
    
    def __init__(self):
        super().__init__("Invalid username or password")

class InactiveUserError(AuthenticationError):
    """비활성화된 사용자"""
    
    def __init__(self):
        super().__init__("User account is inactive")

# 이벤트 관련 예외
class EventNotFoundError(NotFoundError):
    """이벤트를 찾을 수 없음"""
    
    def __init__(self, identifier: str = None):
        super().__init__("Event", identifier)

class EventConflictError(BaseAppError):
    """이벤트 시간 충돌"""
    
    def __init__(self, message: str = "Event time conflict"):
        super().__init__(message, "EVENT_CONFLICT")

# 외부 서비스 관련 예외
class GoogleCalendarError(ExternalServiceError):
    """구글 캘린더 API 오류"""
    
    def __init__(self, message: str = None):
        super().__init__("Google Calendar", message)

class DiscordWebhookError(ExternalServiceError):
    """디스코드 웹훅 오류"""
    
    def __init__(self, message: str = None):
        super().__init__("Discord Webhook", message)

# 파일 관련 예외
class FileNotFoundError(NotFoundError):
    """파일을 찾을 수 없음"""
    
    def __init__(self, filename: str = None):
        super().__init__("File", filename)

class FileSizeExceededError(ValidationError):
    """파일 크기 초과"""
    
    def __init__(self, max_size: str):
        super().__init__(f"File size exceeds maximum allowed size: {max_size}", "file_size")

class InvalidFileTypeError(ValidationError):
    """지원하지 않는 파일 형식"""
    
    def __init__(self, file_type: str):
        super().__init__(f"Invalid file type: {file_type}", "file_type")

# 비즈니스 로직 관련 예외
class BusinessRuleViolationError(BaseAppError):
    """비즈니스 규칙 위반"""
    
    def __init__(self, rule: str, message: str = None):
        error_message = f"Business rule violation: {rule}"
        if message:
            error_message += f" - {message}"
        super().__init__(error_message, "BUSINESS_RULE_VIOLATION")

class RateLimitExceededError(BaseAppError):
    """API 호출 한도 초과"""
    
    def __init__(self, limit: int, window: str):
        message = f"Rate limit exceeded: {limit} requests per {window}"
        super().__init__(message, "RATE_LIMIT_EXCEEDED") 
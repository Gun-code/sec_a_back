from typing import Optional, Any, Dict, List
from datetime import datetime, timezone
import re
import hashlib
import secrets
import json
import logging

logger = logging.getLogger(__name__)

def generate_random_string(length: int = 32) -> str:
    """랜덤 문자열 생성"""
    return secrets.token_urlsafe(length)

def hash_password(password: str) -> str:
    """비밀번호 해시화"""
    salt = secrets.token_hex(16)
    hashed = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
    return f"{salt}:{hashed.hex()}"

def verify_password(password: str, hashed: str) -> bool:
    """비밀번호 검증"""
    try:
        salt, password_hash = hashed.split(':')
        return hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000).hex() == password_hash
    except ValueError:
        return False

def validate_email(email: str) -> bool:
    """이메일 형식 검증"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_username(username: str) -> bool:
    """사용자명 검증"""
    pattern = r'^[a-zA-Z0-9_]{3,20}$'
    return bool(re.match(pattern, username))

def sanitize_filename(filename: str) -> str:
    """파일명 안전하게 변환"""
    # 특수문자 제거 및 공백을 언더스코어로 변환
    sanitized = re.sub(r'[^\w\s-]', '', filename)
    sanitized = re.sub(r'[-\s]+', '_', sanitized)
    return sanitized.strip('_')

def format_datetime(dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """날짜시간 포맷팅"""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.strftime(format_str)

def parse_datetime(date_str: str, format_str: str = "%Y-%m-%d %H:%M:%S") -> Optional[datetime]:
    """문자열을 datetime으로 파싱"""
    try:
        return datetime.strptime(date_str, format_str)
    except ValueError:
        logger.warning(f"Failed to parse datetime: {date_str}")
        return None

def safe_json_loads(json_str: str, default: Any = None) -> Any:
    """안전한 JSON 파싱"""
    try:
        return json.loads(json_str)
    except (json.JSONDecodeError, TypeError):
        logger.warning(f"Failed to parse JSON: {json_str}")
        return default

def safe_json_dumps(obj: Any, default: str = "{}") -> str:
    """안전한 JSON 직렬화"""
    try:
        return json.dumps(obj, ensure_ascii=False, default=str)
    except (TypeError, ValueError):
        logger.warning(f"Failed to serialize to JSON: {obj}")
        return default

def extract_numbers_from_string(text: str) -> List[int]:
    """문자열에서 숫자 추출"""
    return [int(match) for match in re.findall(r'\d+', text)]

def slugify(text: str) -> str:
    """텍스트를 URL 친화적인 슬러그로 변환"""
    # 소문자로 변환하고 특수문자를 하이픈으로 변환
    slug = re.sub(r'[^\w\s-]', '', text.lower())
    slug = re.sub(r'[-\s]+', '-', slug)
    return slug.strip('-')

def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """텍스트 자르기"""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix

def get_client_ip(request) -> str:
    """클라이언트 IP 주소 가져오기"""
    # FastAPI Request 객체에서 IP 추출
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    
    return request.client.host if request.client else "unknown"

def mask_sensitive_data(data: str, mask_char: str = "*", show_last: int = 4) -> str:
    """민감한 데이터 마스킹 (예: 이메일, 전화번호)"""
    if len(data) <= show_last:
        return mask_char * len(data)
    
    return mask_char * (len(data) - show_last) + data[-show_last:]

def calculate_pagination(page: int, page_size: int, total_count: int) -> Dict[str, Any]:
    """페이지네이션 정보 계산"""
    if page < 1:
        page = 1
    if page_size < 1:
        page_size = 10
    
    total_pages = (total_count + page_size - 1) // page_size
    offset = (page - 1) * page_size
    
    return {
        "page": page,
        "page_size": page_size,
        "total_count": total_count,
        "total_pages": total_pages,
        "offset": offset,
        "has_next": page < total_pages,
        "has_previous": page > 1
    }

def format_file_size(size_bytes: int) -> str:
    """파일 크기를 인간이 읽기 쉬운 형태로 변환"""
    if size_bytes == 0:
        return "0B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024.0 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f}{size_names[i]}"

def is_valid_url(url: str) -> bool:
    """URL 유효성 검사"""
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return bool(url_pattern.match(url))

class Timer:
    """실행 시간 측정용 컨텍스트 매니저"""
    
    def __init__(self, description: str = "Operation"):
        self.description = description
        self.start_time = None
        self.end_time = None
    
    def __enter__(self):
        self.start_time = datetime.now()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = datetime.now()
        duration = (self.end_time - self.start_time).total_seconds()
        logger.info(f"{self.description} completed in {duration:.3f} seconds")
    
    @property
    def elapsed(self) -> float:
        """경과 시간 반환 (초)"""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return 0.0 
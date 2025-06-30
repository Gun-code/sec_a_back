from pydantic_settings import BaseSettings
from typing import Optional
from dotenv import load_dotenv
import os
from pathlib import Path

# 프로젝트 루트 디렉터리 경로 찾기
current_dir = Path(__file__).parent  # config 디렉터리
app_dir = current_dir.parent  # app 디렉터리
root_dir = app_dir.parent  # 프로젝트 루트 디렉터리
env_file_path = root_dir / ".env"

# 루트 디렉터리의 .env 파일 로드
load_dotenv(env_file_path)

class Settings(BaseSettings):
    # 앱 설정
    app_name: str = "Backend API"
    debug: bool = True
    
    # MongoDB 설정
    mongodb_url: str = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    mongodb_db_name: str = os.getenv("MONGODB_DB_NAME", "backend_db")
    
    # ChromaDB 설정
    chromadb_path: str = "./chromadb_data"
    chromadb_collection_name: str = "documents"
    
    # 구글 OAuth 설정
    google_client_id: Optional[str] = os.getenv("GOOGLE_CLIENT_ID")
    google_client_secret: Optional[str] = os.getenv("GOOGLE_CLIENT_SECRET")
    google_oauth_redirect_uri: Optional[str] = os.getenv("GOOGLE_OAUTH_REDIRECT_URI")
    
    # 외부 API 설정
    google_calendar_api_key: Optional[str] = None
    discord_webhook_url: Optional[str] = None
    
    # CORS 설정
    allowed_origins: list = ["*"]
    
    # 임베딩 모델 설정
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    
    class Config:
        env_file = str(env_file_path)  # 루트 디렉터리의 .env 파일 경로
        env_file_encoding = "utf-8"

settings = Settings() 
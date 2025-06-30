from pydantic_settings import BaseSettings
from pydantic import Field
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
    mongodb_url: str = Field(default="mongodb://localhost:27017", env="MONGODB_URL")
    database_name: str = Field(default="backend_db", env="DATABASE_NAME")
    
    # ChromaDB 설정
    chromadb_path: str = Field(default="./chromadb_data", env="CHROMADB_PATH")
    chromadb_collection_name: str = Field(default="documents", env="CHROMADB_COLLECTION_NAME")
    
    # 구글 OAuth 설정
    google_client_id: Optional[str] = Field(default=None, env="GOOGLE_CLIENT_ID")
    google_client_secret: Optional[str] = Field(default=None, env="GOOGLE_CLIENT_SECRET")
    google_oauth_redirect_uri: Optional[str] = Field(default=None, env="GOOGLE_OAUTH_REDIRECT_URI")
    
    # 외부 API 설정
    google_calendar_api_key: Optional[str] = Field(default=None, env="GOOGLE_CALENDAR_API_KEY")
    discord_webhook_url: Optional[str] = Field(default=None, env="DISCORD_WEBHOOK_URL")
    
    # CORS 설정
    allowed_origins: list = ["*"]
    
    # 임베딩 모델 설정
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    
    class Config:
        env_file = str(env_file_path)  # 루트 디렉터리의 .env 파일 경로
        env_file_encoding = "utf-8"

settings = Settings() 
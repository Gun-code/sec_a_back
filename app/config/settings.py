from pydantic_settings import BaseSettings
from typing import Optional
from dotenv import load_dotenv
import os
load_dotenv()   

class Settings(BaseSettings):
    # 앱 설정
    app_name: str = "Backend API"
    debug: bool = True
    
    # MongoDB 설정
    mongodb_url: str = "mongodb://localhost:27017"
    mongodb_db_name: str = "backend_db"
    
    # ChromaDB 설정
    chromadb_path: str = "./chromadb_data"
    chromadb_collection_name: str = "documents"
    
    # 구글 OAuth 설정
    google_client_id: str = os.getenv("GOOGLE_CLIENT_ID")
    google_client_secret: str = os.getenv("GOOGLE_CLIENT_SECRET")
    google_oauth_redirect_uri: str = os.getenv("GOOGLE_OAUTH_REDIRECT_URI")
    
    # 외부 API 설정
    google_calendar_api_key: Optional[str] = None
    discord_webhook_url: Optional[str] = None
    
    # CORS 설정
    allowed_origins: list = ["*"]
    
    # 임베딩 모델 설정
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings() 
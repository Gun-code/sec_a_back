import motor.motor_asyncio
import chromadb
from chromadb.config import Settings as ChromaSettings
from beanie import init_beanie
from config.settings import settings
from .models import DOCUMENT_MODELS
import logging

logger = logging.getLogger(__name__)

# MongoDB 클라이언트
mongodb_client = None
database = None

# ChromaDB 클라이언트
chroma_client = None
chroma_collection = None

async def init_mongodb():
    """MongoDB 연결 초기화"""
    global mongodb_client, database
    
    try:
        # MongoDB 클라이언트 생성
        mongodb_client = motor.motor_asyncio.AsyncIOMotorClient(
            settings.mongodb_url,
            serverSelectionTimeoutMS=5000
        )
        
        # 데이터베이스 선택
        database = mongodb_client[settings.database_name]
        
        # Beanie 초기화 (ODM)
        await init_beanie(
            database=database,
            document_models=DOCUMENT_MODELS
        )
        
        logger.info(f"MongoDB connected successfully to {settings.mongodb_url}")
        
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        raise

def init_chromadb():
    """ChromaDB 연결 초기화"""
    global chroma_client, chroma_collection
    
    try:
        # ChromaDB 클라이언트 생성 (로컬 파일 시스템 사용)
        chroma_client = chromadb.PersistentClient(
            path=settings.chromadb_path,
            settings=ChromaSettings(anonymized_telemetry=False)
        )
        
        # 컬렉션 생성 또는 가져오기
        chroma_collection = chroma_client.get_or_create_collection(
            name=settings.chromadb_collection_name,
            metadata={"description": "Document embeddings for semantic search"}
        )
        
        logger.info(f"ChromaDB initialized at {settings.chromadb_path}")
        
    except Exception as e:
        logger.error(f"Failed to initialize ChromaDB: {e}")
        raise

async def get_database():
    """MongoDB 데이터베이스 인스턴스 반환"""
    if database is None:
        await init_mongodb()
    return database

def get_chroma_collection():
    """ChromaDB 컬렉션 인스턴스 반환"""
    if chroma_collection is None:
        init_chromadb()
    return chroma_collection

async def init_db():
    """모든 데이터베이스 초기화"""
    try:
        await init_mongodb()
        init_chromadb()
        logger.info("All databases initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise

async def close_db():
    """데이터베이스 연결 종료"""
    global mongodb_client
    
    if mongodb_client:
        mongodb_client.close()
        logger.info("MongoDB connection closed")

# 의존성 주입용 함수들
async def get_mongodb_database():
    """FastAPI 의존성 주입용 MongoDB 데이터베이스"""
    return await get_database()

def get_chromadb_collection():
    """FastAPI 의존성 주입용 ChromaDB 컬렉션"""
    return get_chroma_collection() 
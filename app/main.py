from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from interfaces.api.v1.user_router import router as user_router
from config.settings import settings
from infrastructure.db.session import init_db, close_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    """애플리케이션 시작/종료 시 실행되는 코드"""
    # 시작 시 데이터베이스 초기화
    await init_db()
    yield
    # 종료 시 데이터베이스 연결 해제
    await close_db()

app = FastAPI(
    title="Backend API",
    description="클린 아키텍처를 따른 FastAPI 백엔드 (MongoDB + ChromaDB)",
    version="1.0.0",
    lifespan=lifespan
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 실제 운영에서는 구체적인 도메인 지정
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(user_router, prefix="/api/v1", tags=["users"])

@app.get("/")
async def root():
    return {
        "message": "Backend API is running",
        "database": "MongoDB + ChromaDB",
        "architecture": "Clean Architecture"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "databases": {
            "mongodb": "connected",
            "chromadb": "connected"
        }
    }

# 벡터 검색 API 추가
@app.post("/api/v1/search")
async def search_documents(query: str, limit: int = 10):
    """벡터 기반 문서 검색"""
    from infrastructure.db.repositories import VectorRepository
    
    vector_repo = VectorRepository()
    results = vector_repo.search_similar(query, limit)
    
    return {
        "query": query,
        "results": results,
        "total": len(results)
    }

@app.get("/api/v1/vector/info")
async def get_vector_info():
    """벡터 데이터베이스 정보 조회"""
    from infrastructure.db.repositories import VectorRepository
    
    vector_repo = VectorRepository()
    info = vector_repo.get_collection_info()
    
    return info

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 
from typing import Optional, List
from bson import ObjectId
from pymongo.errors import DuplicateKeyError
from domain.user.entities import User
from domain.user.repository import UserRepositoryInterface
from .models import UserDocument, VectorDocument
from .session import get_chroma_collection
import chromadb
import logging

logger = logging.getLogger(__name__)

class UserRepository(UserRepositoryInterface):
    """MongoDB를 사용한 사용자 레포지토리 구현체"""
    
    async def create(self, user: User) -> User:
        """사용자 생성"""
        try:
            user_doc = UserDocument(
                username=user.username,
                email=user.email,
                full_name=user.full_name,
                is_active=user.is_active
            )
            
            await user_doc.insert()
            return self._to_entity(user_doc)
            
        except DuplicateKeyError:
            raise ValueError("User with this username or email already exists")
    
    async def get_by_id(self, user_id: str) -> Optional[User]:
        """ID로 사용자 조회"""
        try:
            user_doc = await UserDocument.get(ObjectId(user_id))
            return self._to_entity(user_doc) if user_doc else None
        except Exception:
            return None
    
    async def get_by_username(self, username: str) -> Optional[User]:
        """사용자명으로 사용자 조회"""
        user_doc = await UserDocument.find_one(UserDocument.username == username)
        return self._to_entity(user_doc) if user_doc else None
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """이메일로 사용자 조회"""
        user_doc = await UserDocument.find_one(UserDocument.email == email)
        return self._to_entity(user_doc) if user_doc else None
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[User]:
        """모든 사용자 조회 (페이징 포함)"""
        user_docs = await UserDocument.find_all().skip(skip).limit(limit).sort("-created_at").to_list()
        return [self._to_entity(user_doc) for user_doc in user_docs]
    
    async def update(self, user: User) -> User:
        """사용자 정보 업데이트"""
        try:
            user_doc = await UserDocument.get(ObjectId(user.id))
            if not user_doc:
                raise ValueError("User not found")
            
            user_doc.email = user.email
            user_doc.full_name = user.full_name
            user_doc.is_active = user.is_active
            user_doc.updated_at = user.updated_at
            
            await user_doc.save()
            return self._to_entity(user_doc)
            
        except DuplicateKeyError:
            raise ValueError("Email already exists")
    
    async def delete(self, user_id: str) -> bool:
        """사용자 삭제"""
        try:
            user_doc = await UserDocument.get(ObjectId(user_id))
            if user_doc:
                await user_doc.delete()
                return True
            return False
        except Exception:
            return False
    
    async def exists_by_username(self, username: str) -> bool:
        """사용자명 존재 여부 확인"""
        user_doc = await UserDocument.find_one(UserDocument.username == username)
        return user_doc is not None
    
    async def exists_by_email(self, email: str) -> bool:
        """이메일 존재 여부 확인"""
        user_doc = await UserDocument.find_one(UserDocument.email == email)
        return user_doc is not None
    
    def _to_entity(self, user_doc: UserDocument) -> User:
        """MongoDB 문서를 도메인 엔티티로 변환"""
        return User(
            id=str(user_doc.id),
            username=user_doc.username,
            email=user_doc.email,
            full_name=user_doc.full_name,
            is_active=user_doc.is_active,
            created_at=user_doc.created_at,
            updated_at=user_doc.updated_at
        )

class VectorRepository:
    """ChromaDB를 사용한 벡터 검색 레포지토리"""
    
    def __init__(self):
        self.collection = get_chroma_collection()
    
    async def add_document(
        self, 
        document_id: str, 
        content: str, 
        metadata: dict = None,
        embedding: List[float] = None
    ) -> bool:
        """문서를 벡터 데이터베이스에 추가"""
        try:
            # ChromaDB에 문서 추가
            self.collection.add(
                documents=[content],
                metadatas=[metadata or {}],
                ids=[document_id],
                embeddings=[embedding] if embedding else None
            )
            
            # MongoDB에 메타데이터 저장
            vector_doc = VectorDocument(
                content=content,
                content_type=metadata.get("type", "unknown") if metadata else "unknown",
                source_id=metadata.get("source_id", "") if metadata else "",
                vector_id=document_id,
                metadata=metadata or {}
            )
            await vector_doc.insert()
            
            return True
            
        except Exception as e:
            logger.error(f"Error adding document to vector store: {e}")
            return False
    
    def search_similar(
        self, 
        query: str, 
        limit: int = 10,
        where: dict = None
    ) -> List[dict]:
        """유사한 문서 검색"""
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=limit,
                where=where
            )
            
            return [
                {
                    "id": results["ids"][0][i],
                    "document": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i],
                    "distance": results["distances"][0][i] if "distances" in results else None
                }
                for i in range(len(results["ids"][0]))
            ]
            
        except Exception as e:
            logger.error(f"Error searching similar documents: {e}")
            return []
    
    async def delete_document(self, document_id: str) -> bool:
        """문서 삭제"""
        try:
            # ChromaDB에서 삭제
            self.collection.delete(ids=[document_id])
            
            # MongoDB에서 메타데이터 삭제
            vector_doc = await VectorDocument.find_one(VectorDocument.vector_id == document_id)
            if vector_doc:
                await vector_doc.delete()
            
            return True
            
        except Exception as e:
            logger.error(f"Error deleting document: {e}")
            return False
    
    def get_collection_info(self) -> dict:
        """컬렉션 정보 조회"""
        try:
            return {
                "name": self.collection.name,
                "count": self.collection.count(),
                "metadata": self.collection.metadata
            }
        except Exception as e:
            logger.error(f"Error getting collection info: {e}")
            return {}

class EventRepository:
    """이벤트 레포지토리 (구글 캘린더 연동용)"""
    
    def __init__(self):
        pass
    
    # 이벤트 관련 메서드들을 필요에 따라 구현
    # MongoDB의 EventDocument 사용

class DiscordMessageRepository:
    """디스코드 메시지 레포지토리"""
    
    def __init__(self):
        pass
    
    # 디스코드 메시지 관련 메서드들을 필요에 따라 구현
    # MongoDB의 DiscordMessageDocument 사용 
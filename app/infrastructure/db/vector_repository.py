from typing import List
from .models import VectorDocument
from .session import get_chroma_collection
import logging

logger = logging.getLogger(__name__)

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
"""
Vektör veritabanı yönetim modülü - FAISS kullanarak vektör araması

NOT: Bu modül geriye dönük uyumluluk için tutulmuştur.
Yeni kodlar src.repositories.vector_store_repository.VectorStoreRepository kullanmalıdır.
"""
from typing import List, Dict, Optional

from src.embeddings import EmbeddingGenerator
from src.repositories.vector_store_repository import VectorStoreRepository

class VectorStore(VectorStoreRepository):
    """
    FAISS tabanlı vektör veritabanı yönetimi
    
    NOT: Bu sınıf geriye dönük uyumluluk için tutulmuştur.
    Yeni kodlar VectorStoreRepository kullanmalıdır.
    """
    
    def __init__(self, embeddingGenerator: Optional[EmbeddingGenerator] = None):
        super().__init__(embeddingGenerator)
    
    def addDocuments(self, chunks: List[Dict], embeddings: List[List[float]]):
        """
        Doküman parçalarını ve embedding'lerini ekler
        
        NOT: Geriye dönük uyumluluk için. Yeni kodlar DocumentChunk kullanmalı.
        """
        from src.models.document import DocumentChunk
        
        # Dict'leri DocumentChunk'a çevir
        documentChunks = [DocumentChunk.fromDict(chunk) for chunk in chunks]
        super().addDocuments(documentChunks, embeddings)
    
    # search, save, load, clear, getStats metodları parent sınıftan geliyor

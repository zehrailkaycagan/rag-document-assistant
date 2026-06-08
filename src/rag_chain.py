"""
RAG Pipeline modülü - Retrieval-Augmented Generation zinciri
"""
from typing import List, Dict, Optional
import logging

from src.config import Config
from src.repositories.vector_store_repository import VectorStoreRepository
from src.services.rag_service import RAGService

# Geriye dönük uyumluluk için wrapper

logger = logging.getLogger(__name__)

class RAGChain:
    """
    RAG pipeline sınıfı
    
    NOT: Bu sınıf geriye dönük uyumluluk için tutulmuştur.
    Yeni kodlar RAGService kullanmalıdır.
    """
    
    def __init__(self, vectorStore: VectorStoreRepository, useOpenAI: bool = False):
        self.ragService = RAGService(vectorStore, useOpenAI)
    
    def query(self, question: str, topK: int = None) -> Dict:
        """Sorguya cevap üretir (geriye dönük uyumluluk için)"""
        result = self.ragService.query(question, topK)
        return result.toDict()

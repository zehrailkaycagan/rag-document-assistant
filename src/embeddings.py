"""
Embedding üretim modülü - Metinleri vektörlere çevirir
"""
from typing import List, Optional
import logging

from src.factories.embedding_factory import EmbeddingFactory
from src.config import Config

logger = logging.getLogger(__name__)

class EmbeddingGenerator:
    """Embedding üretimi için sınıf"""
    
    def __init__(self, modelType: Optional[str] = None):
        self.modelType = modelType or Config.EMBEDDING_MODEL
        self.embeddings = EmbeddingFactory.create(self.modelType)
    
    def generateEmbeddings(self, texts: List[str]) -> List[List[float]]:
        """Metin listesini embedding'lere çevirir"""
        try:
            embeddings = self.embeddings.embed_documents(texts)
            return embeddings
        except Exception as e:
            logger.error(f"Embedding üretim hatası: {e}")
            raise ValueError(f"Embedding üretilemedi: {str(e)}")
    
    def generateQueryEmbedding(self, query: str) -> List[float]:
        """Tek bir sorgu için embedding üretir"""
        try:
            embedding = self.embeddings.embed_query(query)
            return embedding
        except Exception as e:
            logger.error(f"Sorgu embedding hatası: {e}")
            raise ValueError(f"Sorgu embedding'i üretilemedi: {str(e)}")

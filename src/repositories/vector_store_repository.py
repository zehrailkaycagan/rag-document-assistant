"""
Vector Store Repository - Vektör veritabanı erişim katmanı
"""
import os
import pickle
from typing import List, Dict, Optional
import logging

import numpy as np
import faiss

from src.config import Config
from src.embeddings import EmbeddingGenerator
from src.models.document import DocumentChunk
from src.exceptions.vector_store_exceptions import (
    VectorStoreError,
    VectorStoreNotFoundError,
    VectorStoreSaveError
)

logger = logging.getLogger(__name__)

class VectorStoreRepository:
    """FAISS tabanlı vektör veritabanı repository"""
    
    def __init__(self, embeddingGenerator: Optional[EmbeddingGenerator] = None):
        self.embeddingGenerator = embeddingGenerator or EmbeddingGenerator()
        self.index: Optional[faiss.Index] = None
        self.documents: List[Dict] = []
        self.dimension: Optional[int] = None
        self.indexPath = Config.VECTOR_STORE_PATH
    
    def _createIndex(self, dimension: int):
        """Yeni bir FAISS index oluşturur"""
        self.dimension = dimension
        self.index = faiss.IndexFlatL2(dimension)
        logger.info(f"FAISS index oluşturuldu, boyut: {dimension}")
    
    def addDocuments(
        self, 
        chunks: List[DocumentChunk], 
        embeddings: List[List[float]]
    ) -> None:
        """
        Doküman parçalarını ve embedding'lerini ekler
        
        Args:
            chunks: Doküman parçaları
            embeddings: Embedding'ler
        
        Raises:
            VectorStoreError: Ekleme hatası
        """
        if not chunks or not embeddings:
            raise VectorStoreError("Chunks ve embeddings boş olamaz")
        
        if len(chunks) != len(embeddings):
            raise VectorStoreError("Chunks ve embeddings sayısı eşleşmiyor")
        
        # İlk eklemede index oluştur
        if self.index is None:
            self._createIndex(len(embeddings[0]))
        
        # Embedding'leri numpy array'e çevir
        embeddingsArray = np.array(embeddings).astype("float32")
        
        # Index'e ekle
        self.index.add(embeddingsArray)
        
        # Doküman bilgilerini sakla
        chunkDicts = [chunk.toDict() for chunk in chunks]
        self.documents.extend(chunkDicts)
        
        logger.info(f"{len(chunks)} doküman parçası vektör veritabanına eklendi")
    
    def search(self, query: str, topK: int = None, scoreThreshold: float = None) -> List[Dict]:
        """
        Sorguya en yakın doküman parçalarını bulur
        
        Args:
            query: Sorgu metni
            topK: Döndürülecek sonuç sayısı
            scoreThreshold: Maksimum distance threshold (None ise config'den alır)
        
        Returns:
            Arama sonuçları listesi
        """
        if self.index is None or len(self.documents) == 0:
            return []
        
        topK = topK or Config.TOP_K_RESULTS
        scoreThreshold = scoreThreshold if scoreThreshold is not None else getattr(Config, 'SCORE_THRESHOLD', None)
        
        # Sorgu için embedding üret
        queryEmbedding = self.embeddingGenerator.generateQueryEmbedding(query)
        queryVector = np.array([queryEmbedding]).astype("float32")
        
        # Arama yap - daha fazla sonuç al (filtreleme için)
        searchK = min(topK * 2, len(self.documents))  # 2 katı al, sonra filtrele
        distances, indices = self.index.search(queryVector, searchK)
        
        # Sonuçları formatla ve filtrele
        results = []
        for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
            if idx < len(self.documents):
                # Score threshold kontrolü - sadece çok yüksek değerler için filtrele
                # FAISS L2 distance için tipik değerler: 0.5-5.0 arası normal, >10.0 çok uzak
                if scoreThreshold is not None and distance > scoreThreshold:
                    logger.debug(f"Sonuç filtrelendi: distance={distance:.3f} > threshold={scoreThreshold}")
                    continue
                
                result = {
                    "document": self.documents[idx],
                    "score": float(distance),
                    "rank": i + 1
                }
                results.append(result)
                
                # İstenen sayıda sonuç bulunduysa dur
                if len(results) >= topK:
                    break
        
        logger.info(f"Arama tamamlandı: {len(results)} sonuç bulundu (topK={topK}, threshold={scoreThreshold})")
        if results:
            logger.debug(f"En iyi sonuç: distance={results[0]['score']:.3f}, dosya={results[0]['document'].get('source', 'N/A')}")
        
        return results
    
    def save(self, filePath: Optional[str] = None) -> None:
        """
        Vektör veritabanını diske kaydeder
        
        Args:
            filePath: Kayıt yolu (None ise config'den alır)
        
        Raises:
            VectorStoreSaveError: Kaydetme hatası
        """
        savePath = filePath or self.indexPath
        
        try:
            # Dizin yoksa oluştur
            os.makedirs(os.path.dirname(savePath), exist_ok=True)
            
            # FAISS index'i kaydet
            faiss.write_index(self.index, savePath + ".index")
            
            # Doküman bilgilerini kaydet
            with open(savePath + ".pkl", "wb") as f:
                pickle.dump(self.documents, f)
            
            logger.info(f"Vektör veritabanı kaydedildi: {savePath}")
        except Exception as e:
            logger.error(f"Vektör veritabanı kaydetme hatası: {e}")
            raise VectorStoreSaveError(f"Kaydetme başarısız: {str(e)}")
    
    def load(self, filePath: Optional[str] = None) -> bool:
        """
        Vektör veritabanını diskten yükler
        
        Args:
            filePath: Yükleme yolu (None ise config'den alır)
        
        Returns:
            Yükleme başarılı mı?
        """
        loadPath = filePath or self.indexPath
        
        indexFile = loadPath + ".index"
        pklFile = loadPath + ".pkl"
        
        if not os.path.exists(indexFile) or not os.path.exists(pklFile):
            logger.warning(f"Vektör veritabanı bulunamadı: {loadPath}")
            return False
        
        try:
            # FAISS index'i yükle
            self.index = faiss.read_index(indexFile)
            self.dimension = self.index.d
            
            # Doküman bilgilerini yükle
            with open(pklFile, "rb") as f:
                self.documents = pickle.load(f)
            
            logger.info(f"Vektör veritabanı yüklendi: {loadPath}, {len(self.documents)} doküman")
            return True
        except Exception as e:
            logger.error(f"Vektör veritabanı yükleme hatası: {e}")
            return False
    
    def clear(self) -> None:
        """Vektör veritabanını temizler"""
        self.index = None
        self.documents = []
        self.dimension = None
        logger.info("Vektör veritabanı temizlendi")
    
    def getStats(self) -> Dict:
        """Vektör veritabanı istatistiklerini döndürür"""
        return {
            "totalDocuments": len(self.documents),
            "dimension": self.dimension,
            "isLoaded": self.index is not None
        }
    
    def isEmpty(self) -> bool:
        """Vektör veritabanı boş mu?"""
        return self.index is None or len(self.documents) == 0

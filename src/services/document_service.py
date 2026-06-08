"""
Doküman işleme servisi
"""
import os
import logging
from typing import List
from pathlib import Path

from src.document_loader import DocumentLoader
from src.text_splitter import TextSplitter
from src.embeddings import EmbeddingGenerator
from src.repositories.vector_store_repository import VectorStoreRepository
from src.models.document import Document, DocumentChunk
from src.exceptions.document_exceptions import (
    DocumentLoadError,
    UnsupportedFileFormatError
)
from src.utils import isSupportedFile

logger = logging.getLogger(__name__)

class DocumentService:
    """Doküman işleme servisi"""
    
    def __init__(
        self,
        textSplitter: TextSplitter = None,
        embeddingGenerator: EmbeddingGenerator = None,
        vectorStoreRepository: VectorStoreRepository = None
    ):
        self.textSplitter = textSplitter or TextSplitter()
        self.embeddingGenerator = embeddingGenerator or EmbeddingGenerator()
        self.vectorStoreRepository = vectorStoreRepository or VectorStoreRepository(
            self.embeddingGenerator
        )
    
    def processUploadedFiles(
        self,
        uploadedFiles: List,
        savePath: str = None
    ) -> dict:
        """
        Yüklenen dosyaları işler ve vektör veritabanına ekler
        
        Args:
            uploadedFiles: Streamlit UploadedFile listesi
            savePath: Vektör veritabanı kayıt yolu
        
        Returns:
            İşlem sonucu bilgisi
        
        Raises:
            DocumentLoadError: Doküman yükleme hatası
        """
        if not uploadedFiles:
            raise DocumentLoadError("Dosya bulunamadı")
        
        # Dosyaları geçici olarak kaydet
        filePaths = []
        from src.config import Config
        import uuid
        from pathlib import Path
        
        for uploadedFile in uploadedFiles:
            if not isSupportedFile(uploadedFile.name):
                logger.warning(f"Desteklenmeyen dosya formatı: {uploadedFile.name}")
                continue
            
            try:
                # Dosya adı çakışmasını önle
                originalName = Path(uploadedFile.name).stem
                extension = Path(uploadedFile.name).suffix
                basePath = os.path.join(Config.UPLOADS_DIR, f"{originalName}{extension}")
                
                # Aynı isimde dosya varsa benzersiz isim oluştur
                if os.path.exists(basePath):
                    uniqueId = str(uuid.uuid4())[:8]
                    filePath = os.path.join(Config.UPLOADS_DIR, f"{originalName}_{uniqueId}{extension}")
                else:
                    filePath = basePath
                
                # Dizin oluştur
                os.makedirs(os.path.dirname(filePath), exist_ok=True)
                
                # Dosyayı kaydet
                with open(filePath, "wb") as f:
                    f.write(uploadedFile.getbuffer())
                
                filePaths.append(filePath)
                logger.info(f"Dosya kaydedildi: {filePath}")
                
            except PermissionError as pe:
                logger.error(f"Dosya yazma izni hatası: {uploadedFile.name} - {pe}")
                raise DocumentLoadError(f"Dosya yazma izni hatası: {uploadedFile.name}")
            except OSError as ose:
                logger.error(f"Dosya sistemi hatası: {uploadedFile.name} - {ose}")
                raise DocumentLoadError(f"Dosya kaydedilemedi: {uploadedFile.name}")
            except Exception as e:
                logger.error(f"Dosya kaydetme hatası: {uploadedFile.name} - {e}")
                raise DocumentLoadError(f"Dosya işlenemedi: {uploadedFile.name} - {str(e)}")
        
        if not filePaths:
            raise DocumentLoadError("İşlenecek geçerli dosya bulunamadı")
        
        return self.processFiles(filePaths, savePath)
    
    def processFiles(
        self,
        filePaths: List[str],
        savePath: str = None
    ) -> dict:
        """
        Dosya yollarından dokümanları işler
        
        Args:
            filePaths: Dosya yolu listesi
            savePath: Vektör veritabanı kayıt yolu
        
        Returns:
            İşlem sonucu bilgisi
        """
        # Dokümanları yükle
        documentDicts = DocumentLoader.loadMultipleDocuments(filePaths)
        if not documentDicts:
            raise DocumentLoadError("Dokümanlar yüklenemedi")
        
        documents = [Document.fromDict(doc) for doc in documentDicts]
        
        # Metinleri parçalara ayır
        chunks = self._splitDocuments(documents)
        if not chunks:
            raise DocumentLoadError("Dokümanlar parçalara ayrılamadı")
        
        # Embedding'leri üret
        embeddings = self._generateEmbeddings(chunks)
        
        # Vektör veritabanını temizle ve ekle
        self.vectorStoreRepository.clear()
        self.vectorStoreRepository.addDocuments(chunks, embeddings)
        
        # Kaydet
        if savePath:
            self.vectorStoreRepository.save(savePath)
        else:
            self.vectorStoreRepository.save()
        
        return {
            "success": True,
            "totalDocuments": len(documents),
            "totalChunks": len(chunks)
        }
    
    def _splitDocuments(self, documents: List[Document]) -> List[DocumentChunk]:
        """Dokümanları parçalara ayırır"""
        documentDicts = [doc.toDict() for doc in documents]
        chunkDicts = self.textSplitter.splitDocuments(documentDicts)
        return [DocumentChunk.fromDict(chunk) for chunk in chunkDicts]
    
    def _generateEmbeddings(self, chunks: List[DocumentChunk]) -> List[List[float]]:
        """Embedding'leri üretir"""
        texts = [chunk.text for chunk in chunks]
        return self.embeddingGenerator.generateEmbeddings(texts)

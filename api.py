"""
FastAPI REST API - RAG Document Assistant
"""
import os
import logging
from typing import List, Optional
from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel

from src.config import Config
from src.services.document_service import DocumentService
from src.services.rag_service import RAGService
from src.repositories.vector_store_repository import VectorStoreRepository
from src.embeddings import EmbeddingGenerator
from src.exceptions.document_exceptions import DocumentLoadError
from src.exceptions.rag_exceptions import RAGQueryError

# Logging yapılandırması
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI uygulaması
app = FastAPI(
    title="RAG Document Assistant API",
    description="RAG tabanlı doküman asistanı REST API",
    version="1.0.0"
)

# Gerekli dizinleri oluştur
Config.ensureDirectories()

# Global servisler
documentService: Optional[DocumentService] = None
ragService: Optional[RAGService] = None
vectorStoreRepository: Optional[VectorStoreRepository] = None

def initializeServices():
    """Servisleri başlatır"""
    global documentService, ragService, vectorStoreRepository
    
    if vectorStoreRepository is None:
        embeddingGenerator = EmbeddingGenerator()
        vectorStoreRepository = VectorStoreRepository(embeddingGenerator)
        
        # Kaydedilmiş index varsa yükle
        vectorStoreRepository.load()
        
        documentService = DocumentService(
            vectorStoreRepository=vectorStoreRepository
        )
        ragService = RAGService(
            vectorStoreRepository,
            useOpenAI=bool(Config.OPENAI_API_KEY)
        )

# Uygulama başlangıcında başlat
initializeServices()

# Request/Response modelleri
class QueryRequest(BaseModel):
    question: str
    topK: Optional[int] = None

class QueryResponse(BaseModel):
    answer: str
    sources: List[dict]
    success: bool

class StatusResponse(BaseModel):
    documentsLoaded: bool
    totalDocuments: int
    dimension: Optional[int]

# API Endpoints
@app.get("/")
async def root():
    """API kök endpoint"""
    return {
        "message": "RAG Document Assistant API",
        "version": "1.0.0",
        "endpoints": {
            "POST /upload": "Doküman yükleme",
            "POST /query": "Soru sorma",
            "GET /status": "Durum bilgisi",
            "DELETE /clear": "Vektör veritabanını temizleme"
        }
    }

@app.post("/upload")
async def uploadDocuments(files: List[UploadFile] = File(...)):
    """Doküman yükleme endpoint'i"""
    global documentService, ragService, vectorStoreRepository
    
    if not files:
        raise HTTPException(status_code=400, detail="Dosya bulunamadı")
    
    try:
        result = documentService.processUploadedFiles(files)
        
        return {
            "success": True,
            "message": f"{result['totalDocuments']} doküman başarıyla işlendi",
            "totalChunks": result["totalChunks"]
        }
    
    except DocumentLoadError as e:
        logger.error(f"Doküman yükleme hatası: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Beklenmeyen hata: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query", response_model=QueryResponse)
async def queryDocuments(request: QueryRequest):
    """Soru sorma endpoint'i"""
    global ragService, vectorStoreRepository
    
    if not ragService or vectorStoreRepository.isEmpty():
        raise HTTPException(
            status_code=400, 
            detail="Önce doküman yüklemelisiniz. /upload endpoint'ini kullanın."
        )
    
    try:
        result = ragService.query(request.question, topK=request.topK)
        
        return QueryResponse(
            answer=result.answer,
            sources=[source.toDict() for source in result.sources],
            success=True
        )
    
    except RAGQueryError as e:
        logger.error(f"Sorgu hatası: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Beklenmeyen hata: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/status", response_model=StatusResponse)
async def getStatus():
    """Durum bilgisi endpoint'i"""
    global vectorStoreRepository
    
    if vectorStoreRepository is None or vectorStoreRepository.isEmpty():
        return StatusResponse(
            documentsLoaded=False,
            totalDocuments=0,
            dimension=None
        )
    
    stats = vectorStoreRepository.getStats()
    return StatusResponse(
        documentsLoaded=stats["isLoaded"],
        totalDocuments=stats["totalDocuments"],
        dimension=stats["dimension"]
    )

@app.delete("/clear")
async def clearVectorStore():
    """Vektör veritabanını temizleme endpoint'i"""
    global documentService, ragService, vectorStoreRepository
    
    try:
        if vectorStoreRepository:
            vectorStoreRepository.clear()
            # Dosyaları da sil
            indexFile = Config.VECTOR_STORE_PATH + ".index"
            pklFile = Config.VECTOR_STORE_PATH + ".pkl"
            if os.path.exists(indexFile):
                os.remove(indexFile)
            if os.path.exists(pklFile):
                os.remove(pklFile)
        
        # Yeniden başlat
        initializeServices()
        
        return {"success": True, "message": "Vektör veritabanı temizlendi"}
    
    except Exception as e:
        logger.error(f"Temizleme hatası: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

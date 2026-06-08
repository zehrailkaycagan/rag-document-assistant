"""
Yapılandırma ayarları ve sabitler
"""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Uygulama yapılandırma sınıfı"""
    
    # OpenAI Ayarları
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    
    # Embedding Model Seçimi
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers")
    
    # Sentence Transformers Model
    SENTENCE_TRANSFORMERS_MODEL = os.getenv(
        "SENTENCE_TRANSFORMERS_MODEL", 
        "paraphrase-multilingual-MiniLM-L12-v2"  # Türkçe destekli çok dilli model
    )
    
    # OpenAI Model Ayarları
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
    OPENAI_EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
    
    # Vektör Veritabanı Yolu
    VECTOR_STORE_PATH = os.getenv("VECTOR_STORE_PATH", "./vector_store/faiss_index")
    
    # Dizin Yolları
    UPLOADS_DIR = "./uploads"
    DATA_DIR = "./data"
    VECTOR_STORE_DIR = "./vector_store"
    
    # Metin Bölme Ayarları
    CHUNK_SIZE = 1500  # Teknik içerik için daha büyük chunk
    CHUNK_OVERLAP = 300  # Daha fazla overlap ile bağlam korunur
    
    # RAG Ayarları
    TOP_K_RESULTS = 6  # Her sorgu için döndürülecek en ilgili doküman sayısı
    SCORE_THRESHOLD = None  # Maksimum distance threshold (None = filtreleme yok, FAISS L2 için tipik değerler 0.5-5.0)
    
    @classmethod
    def ensureDirectories(cls):
        """Gerekli dizinlerin var olduğundan emin ol"""
        os.makedirs(cls.UPLOADS_DIR, exist_ok=True)
        os.makedirs(cls.DATA_DIR, exist_ok=True)
        os.makedirs(cls.VECTOR_STORE_DIR, exist_ok=True)

"""
Embedding factory - Embedding modeli oluşturma
"""
import logging
from typing import Optional, List
from sentence_transformers import SentenceTransformer
from openai import OpenAI

from src.config import Config

logger = logging.getLogger(__name__)

class EmbeddingWrapper:
    """Embedding model wrapper - LangChain uyumluluğu için"""
    
    def __init__(self, model):
        self.model = model
        self.isOpenAI = hasattr(model, 'embeddings')
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Doküman listesi için embedding üretir"""
        if self.isOpenAI:
            return [self.model.embeddings.create(
                model=Config.OPENAI_EMBEDDING_MODEL,
                input=text
            ).data[0].embedding for text in texts]
        else:
            return self.model.encode(texts, show_progress_bar=False).tolist()
    
    def embed_query(self, query: str) -> List[float]:
        """Sorgu için embedding üretir"""
        if self.isOpenAI:
            return self.model.embeddings.create(
                model=Config.OPENAI_EMBEDDING_MODEL,
                input=query
            ).data[0].embedding
        else:
            return self.model.encode(query, show_progress_bar=False).tolist()

class EmbeddingFactory:
    """Embedding modeli factory sınıfı"""
    
    @staticmethod
    def create(modelType: Optional[str] = None):
        """
        Embedding modeli oluşturur
        
        Args:
            modelType: "openai" veya "sentence-transformers" (None ise config'den alır)
        
        Returns:
            Embedding model instance
        """
        modelType = modelType or Config.EMBEDDING_MODEL
        
        if modelType == "openai":
            return EmbeddingFactory._createOpenAIEmbeddings()
        else:
            return EmbeddingFactory._createSentenceTransformersEmbeddings()
    
    @staticmethod
    def _createOpenAIEmbeddings():
        """OpenAI embedding modeli oluşturur"""
        if not Config.OPENAI_API_KEY:
            logger.warning("OpenAI API key bulunamadı, sentence-transformers kullanılıyor")
            return EmbeddingFactory._createSentenceTransformersEmbeddings()
        
        try:
            client = OpenAI(api_key=Config.OPENAI_API_KEY)
            return EmbeddingWrapper(client)
        except Exception as e:
            logger.warning(f"OpenAI embedding başlatılamadı: {e}, sentence-transformers kullanılıyor")
            return EmbeddingFactory._createSentenceTransformersEmbeddings()
    
    @staticmethod
    def _createSentenceTransformersEmbeddings():
        """Sentence Transformers embedding modeli oluşturur"""
        import torch
        import os
        
        # PyTorch uyarılarını bastır
        os.environ['TOKENIZERS_PARALLELISM'] = 'false'
        
        try:
            # Device belirleme - her zaman CPU kullan
            device = 'cpu'
            
            # Model yükleme - PyTorch 2.5+ uyumlu
            logger.info(f"Sentence Transformers modeli yükleniyor: {Config.SENTENCE_TRANSFORMERS_MODEL}")
            
            # Model yükleme parametreleri
            try:
                # İlk deneme: normal yükleme
                model = SentenceTransformer(
                    Config.SENTENCE_TRANSFORMERS_MODEL,
                    device=device
                )
                logger.info("Sentence Transformers modeli başarıyla yüklendi")
                return EmbeddingWrapper(model)
                
            except Exception as firstError:
                errorMsg = str(firstError)
                
                # Meta tensor hatası varsa alternatif yöntem dene
                if "meta tensor" in errorMsg.lower() or "to_empty" in errorMsg.lower():
                    logger.warning("PyTorch meta tensor hatası tespit edildi, alternatif yöntem deneniyor...")
                    
                    # Alternatif 1: Daha basit model
                    try:
                        alternativeModel = "all-MiniLM-L6-v2"
                        logger.info(f"Alternatif model deneniyor: {alternativeModel}")
                        model = SentenceTransformer(alternativeModel, device=device)
                        logger.info("Alternatif model başarıyla yüklendi")
                        return EmbeddingWrapper(model)
                    except Exception as altError:
                        logger.warning(f"Alternatif model yüklenemedi: {altError}")
                        
                        # Alternatif 2: Model cache'i temizle ve tekrar dene
                        try:
                            logger.info("Model cache temizleniyor ve tekrar deneniyor...")
                            import shutil
                            from pathlib import Path
                            
                            # HuggingFace cache'ini temizle (opsiyonel, yorum satırı)
                            # cache_dir = Path.home() / ".cache" / "huggingface"
                            # if cache_dir.exists():
                            #     shutil.rmtree(cache_dir / "transformers", ignore_errors=True)
                            
                            # Son deneme: En basit model
                            simpleModel = "sentence-transformers/all-MiniLM-L6-v2"
                            model = SentenceTransformer(simpleModel, device=device)
                            logger.info("Basit model başarıyla yüklendi")
                            return EmbeddingWrapper(model)
                        except Exception as finalError:
                            logger.error(f"Tüm model yükleme denemeleri başarısız: {finalError}")
                            raise ValueError(f"Embedding modeli yüklenemedi. Son hata: {str(finalError)}")
                else:
                    # Diğer hatalar için
                    raise ValueError(f"Embedding modeli yüklenemedi: {errorMsg}")
                    
        except ValueError:
            # Zaten işlenmiş hatalar
            raise
        except Exception as e:
            errorMsg = str(e)
            logger.error(f"Sentence Transformers model yüklenemedi: {errorMsg}")
            raise ValueError(f"Embedding modeli yüklenemedi: {errorMsg}")

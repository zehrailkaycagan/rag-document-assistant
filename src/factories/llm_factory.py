"""
LLM factory - Language model oluşturma
"""
import logging
from typing import Optional

from src.config import Config

logger = logging.getLogger(__name__)

class LLMFactory:
    """LLM modeli factory sınıfı"""
    
    @staticmethod
    def create(useOpenAI: bool = False):
        """
        LLM modeli oluşturur
        
        Args:
            useOpenAI: OpenAI kullanılsın mı?
        
        Returns:
            LLM instance veya None (fallback modu için)
        """
        if not useOpenAI or not Config.OPENAI_API_KEY:
            return None
        
        try:
            # Önce LangChain'i dene
            try:
                from langchain_openai import ChatOpenAI
                return ChatOpenAI(
                    model=Config.OPENAI_MODEL,
                    temperature=0.7,
                    openai_api_key=Config.OPENAI_API_KEY
                )
            except ImportError:
                # LangChain yoksa OpenAI client kullan
                from openai import OpenAI
                client = OpenAI(api_key=Config.OPENAI_API_KEY)
                return client
        except Exception as e:
            logger.warning(f"OpenAI LLM başlatılamadı: {e}, basit yanıt modu kullanılıyor")
            return None

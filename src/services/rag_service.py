"""
RAG servisi - Sorgu işleme
"""
import logging
from typing import Optional

from src.repositories.vector_store_repository import VectorStoreRepository
from src.models.query_result import QueryResult, SourceInfo
from src.factories.llm_factory import LLMFactory
from src.config import Config
from src.exceptions.rag_exceptions import RAGQueryError

logger = logging.getLogger(__name__)

class RAGService:
    """RAG sorgu servisi"""
    
    def __init__(
        self,
        vectorStoreRepository: VectorStoreRepository,
        useOpenAI: bool = False
    ):
        self.vectorStoreRepository = vectorStoreRepository
        self.llm = LLMFactory.create(useOpenAI)
    
    def query(self, question: str, topK: int = None) -> QueryResult:
        """
        Sorguya cevap üretir
        
        Args:
            question: Kullanıcı sorusu
            topK: Döndürülecek sonuç sayısı
        
        Returns:
            QueryResult
        
        Raises:
            RAGQueryError: Sorgu hatası
        """
        if not question or not question.strip():
            return QueryResult(
                answer="Lütfen geçerli bir soru girin.",
                sources=[],
                context=""
            )
        
        if self.vectorStoreRepository.isEmpty():
            return QueryResult(
                answer="Üzgünüm, henüz doküman yüklenmemiş. Lütfen önce doküman yükleyin.",
                sources=[],
                context=""
            )
        
        try:
            # Vektör veritabanında arama yap
            searchResults = self.vectorStoreRepository.search(question, topK=topK)
            
            # Debug: Arama sonuçlarını logla
            logger.info(f"Soru: '{question}' - {len(searchResults)} sonuç bulundu")
            if searchResults:
                for i, result in enumerate(searchResults[:3], 1):
                    logger.debug(f"  Sonuç {i}: score={result['score']:.3f}, dosya={result['document'].get('source', 'N/A')}")
            else:
                logger.warning(f"Hiç sonuç bulunamadı. Vektör veritabanında {len(self.vectorStoreRepository.documents)} doküman var.")
            
            if not searchResults:
                return QueryResult(
                    answer="Üzgünüm, sorunuzla ilgili bilgi verilen dokümanlarda bulunmamaktadır. Lütfen farklı kelimelerle tekrar deneyin.",
                    sources=[],
                    context=""
                )
            
            # En ilgili parçaları birleştir
            contextParts = []
            sources = []
            
            for result in searchResults:
                doc = result["document"]
                contextParts.append(doc["text"])
                sources.append(SourceInfo(
                    fileName=doc["source"],
                    chunkIndex=doc.get("chunkIndex", 0),
                    score=result["score"]
                ))
            
            context = "\n\n---\n\n".join(contextParts)
            
            # Cevap üret
            answer = self._generateAnswer(context, question)
            
            return QueryResult(
                answer=answer,
                sources=sources,
                context=context
            )
        
        except Exception as e:
            logger.error(f"Sorgu hatası: {e}")
            raise RAGQueryError(f"Sorgu işlenemedi: {str(e)}")
    
    def _generateAnswer(self, context: str, question: str) -> str:
        """Cevap üretir"""
        if self.llm:
            return self._generateResponseWithLLM(context, question)
        else:
            return self._generateSimpleResponse(context, question)
    
    def _generateResponseWithLLM(self, context: str, question: str) -> str:
        """LLM kullanarak cevap üretir"""
        try:
            prompt = self._createPrompt(context, question)
            
            # LangChain ChatOpenAI kullanılıyorsa
            if hasattr(self.llm, 'invoke'):
                try:
                    from langchain.schema import HumanMessage, SystemMessage
                    messages = [
                        SystemMessage(content="Sen bir doküman asistanısın. Verilen doküman içeriğine dayanarak cevap verirsin."),
                        HumanMessage(content=prompt)
                    ]
                    response = self.llm.invoke(messages)
                    return response.content if hasattr(response, 'content') else str(response)
                except ImportError:
                    # LangChain yoksa OpenAI client kullan
                    from openai import OpenAI
                    client = OpenAI(api_key=Config.OPENAI_API_KEY)
                    response = client.chat.completions.create(
                        model=Config.OPENAI_MODEL,
                        messages=[
                            {"role": "system", "content": "Sen bir doküman asistanısın. Verilen doküman içeriğine dayanarak cevap verirsin."},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.7
                    )
                    return response.choices[0].message.content
            else:
                # OpenAI client direkt kullanılıyorsa
                from openai import OpenAI
                client = OpenAI(api_key=Config.OPENAI_API_KEY)
                response = client.chat.completions.create(
                    model=Config.OPENAI_MODEL,
                    messages=[
                        {"role": "system", "content": "Sen bir doküman asistanısın. Verilen doküman içeriğine dayanarak cevap verirsin."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7
                )
                return response.choices[0].message.content
        except Exception as e:
            logger.error(f"LLM yanıt hatası: {e}")
            return self._generateSimpleResponse(context, question)
    
    def _generateSimpleResponse(self, context: str, question: str) -> str:
        """LLM olmadan akıllı cevap üretir (fallback)"""
        if not context or not context.strip():
            return "Üzgünüm, sorunuzla ilgili bilgi verilen dokümanlarda bulunmamaktadır."
        
        # Soruyu analiz et ve ilgili kısımları bul
        questionLower = question.lower()
        contextLines = context.split('\n')
        
        # Soruyla ilgili satırları bul
        relevantLines = []
        for line in contextLines:
            lineLower = line.lower()
            # Sorudaki anahtar kelimeleri kontrol et
            questionWords = set(questionLower.split())
            lineWords = set(lineLower.split())
            commonWords = questionWords.intersection(lineWords)
            
            # En az 2 ortak kelime varsa veya satır uzunsa ekle
            if len(commonWords) >= 2 or len(line.strip()) > 100:
                relevantLines.append(line)
        
        # İlgili satırları birleştir
        if relevantLines:
            relevantContext = '\n'.join(relevantLines[:20])  # En fazla 20 satır
        else:
            # İlgili satır yoksa baştan al
            relevantContext = context[:2000]
        
        # Cevabı formatla
        answer = f"""Doküman içeriğinden ilgili bilgiler:

{relevantContext}

---
Not: Bu cevap doküman içeriğinden otomatik olarak çıkarılmıştır. Daha detaylı ve yapılandırılmış cevaplar için OpenAI API key'inizi yapılandırmanız önerilir."""
        
        return answer
    
    def _createPrompt(self, context: str, question: str) -> str:
        """RAG için geliştirilmiş prompt oluşturur"""
        return f"""Sen uzman bir doküman analiz asistanısın. Kullanıcının sorusunu, VERİLEN DOKÜMAN İÇERİĞİNE DAYANARAK detaylı, net ve doğru bir şekilde cevapla.

DOKÜMAN İÇERİĞİ:
{context}

GÖREVİN:
1. Soruyu dikkatlice oku ve anla
2. Doküman içeriğinde soruyla BİREBİR İLGİLİ bilgileri bul
3. Bulduğun bilgileri kullanarak KESİN, NET ve DETAYLI bir cevap oluştur
4. Teknik terimleri, kavramları ve tanımları DOĞRU kullan
5. Eğer doküman içeriğinde yeterli bilgi yoksa, "Bu bilgi verilen dokümanlarda bulunmamaktadır" de

ÖNEMLİ KURALLAR:
- SADECE doküman içeriğindeki bilgileri kullan
- Tahmin yapma, varsayımda bulunma veya genel bilgi ekleme
- Teknik terimleri olduğu gibi kullan (ör: "mum formasyonu", "doji", "engulfing", "support", "resistance" gibi)
- Cevabını Türkçe olarak ver
- Mümkünse doküman içeriğinden DOĞRUDAN ALINTILAR yap
- Cevabını yapılandırılmış ve okunabilir bir şekilde sun
- Birden fazla ilgili bilgi varsa, hepsini mantıklı bir sırayla sun

KULLANICI SORUSU: {question}

CEVAP (Detaylı, net ve doküman içeriğine dayalı olmalı):"""

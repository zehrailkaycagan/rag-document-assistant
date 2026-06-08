"""
Sorgu sonuç modelleri
"""
from dataclasses import dataclass
from typing import List

@dataclass
class SourceInfo:
    """Kaynak bilgisi modeli"""
    fileName: str
    chunkIndex: int
    score: float
    
    def toDict(self) -> dict:
        """SourceInfo'yu dictionary'ye çevirir"""
        return {
            "fileName": self.fileName,
            "chunkIndex": self.chunkIndex,
            "score": self.score
        }

@dataclass
class QueryResult:
    """Sorgu sonucu modeli"""
    answer: str
    sources: List[SourceInfo]
    context: str
    
    def toDict(self) -> dict:
        """QueryResult'ı dictionary'ye çevirir"""
        return {
            "answer": self.answer,
            "sources": [source.toDict() for source in self.sources],
            "context": self.context
        }

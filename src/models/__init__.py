"""
Veri modelleri ve entity sınıfları
"""
from .document import Document, DocumentChunk
from .query_result import QueryResult, SourceInfo

__all__ = [
    "Document",
    "DocumentChunk",
    "QueryResult",
    "SourceInfo"
]

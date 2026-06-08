"""
RAG pipeline ile ilgili exception'lar
"""

class RAGError(Exception):
    """RAG genel hatası"""
    pass

class RAGQueryError(Exception):
    """RAG sorgu hatası"""
    pass

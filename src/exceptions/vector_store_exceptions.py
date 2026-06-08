"""
Vektör veritabanı ile ilgili exception'lar
"""

class VectorStoreError(Exception):
    """Vektör veritabanı genel hatası"""
    pass

class VectorStoreNotFoundError(Exception):
    """Vektör veritabanı bulunamadı hatası"""
    pass

class VectorStoreSaveError(Exception):
    """Vektör veritabanı kaydetme hatası"""
    pass

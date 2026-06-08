"""
Doküman işleme ile ilgili exception'lar
"""

class DocumentLoadError(Exception):
    """Doküman yükleme hatası"""
    pass

class UnsupportedFileFormatError(Exception):
    """Desteklenmeyen dosya formatı hatası"""
    pass

class DocumentNotFoundError(Exception):
    """Doküman bulunamadı hatası"""
    pass

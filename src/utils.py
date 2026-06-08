"""
Yardımcı fonksiyonlar
"""
import os
from pathlib import Path

def getFileExtension(fileName: str) -> str:
    """Dosya uzantısını döndürür"""
    return Path(fileName).suffix.lower()

def isSupportedFile(fileName: str) -> bool:
    """Dosyanın desteklenen formatta olup olmadığını kontrol eder"""
    supportedExtensions = [".pdf", ".docx", ".txt"]
    return getFileExtension(fileName) in supportedExtensions

def cleanText(text: str) -> str:
    """Metni temizler ve normalize eder"""
    if not text:
        return ""
    
    # Fazla boşlukları temizle
    lines = text.split("\n")
    cleanedLines = [line.strip() for line in lines if line.strip()]
    return "\n".join(cleanedLines)

def formatFileSize(sizeInBytes: int) -> str:
    """Dosya boyutunu okunabilir formata çevirir"""
    for unit in ["B", "KB", "MB", "GB"]:
        if sizeInBytes < 1024.0:
            return f"{sizeInBytes:.2f} {unit}"
        sizeInBytes /= 1024.0
    return f"{sizeInBytes:.2f} TB"

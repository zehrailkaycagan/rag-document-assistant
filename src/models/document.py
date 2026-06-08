"""
Doküman modelleri
"""
from dataclasses import dataclass
from typing import Optional
from pathlib import Path

@dataclass
class Document:
    """Doküman modeli"""
    filePath: str
    fileName: str
    text: str
    fileType: str
    
    @classmethod
    def fromDict(cls, data: dict) -> "Document":
        """Dictionary'den Document oluşturur"""
        return cls(
            filePath=data["filePath"],
            fileName=data["fileName"],
            text=data["text"],
            fileType=data["fileType"]
        )
    
    def toDict(self) -> dict:
        """Document'ı dictionary'ye çevirir"""
        return {
            "filePath": self.filePath,
            "fileName": self.fileName,
            "text": self.text,
            "fileType": self.fileType
        }

@dataclass
class DocumentChunk:
    """Doküman parçası modeli"""
    text: str
    source: str
    filePath: str
    fileType: str
    chunkIndex: int
    totalChunks: int
    
    @classmethod
    def fromDict(cls, data: dict) -> "DocumentChunk":
        """Dictionary'den DocumentChunk oluşturur"""
        return cls(
            text=data["text"],
            source=data["source"],
            filePath=data["filePath"],
            fileType=data["fileType"],
            chunkIndex=data.get("chunkIndex", 0),
            totalChunks=data.get("totalChunks", 0)
        )
    
    def toDict(self) -> dict:
        """DocumentChunk'ı dictionary'ye çevirir"""
        return {
            "text": self.text,
            "source": self.source,
            "filePath": self.filePath,
            "fileType": self.fileType,
            "chunkIndex": self.chunkIndex,
            "totalChunks": self.totalChunks
        }

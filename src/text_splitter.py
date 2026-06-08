"""
Metin bölme modülü - Dokümanları anlamlı parçalara ayırır
"""
from typing import List
import re

from src.config import Config

class TextSplitter:
    """Metinleri RAG için uygun parçalara böler"""
    
    def __init__(
        self, 
        chunkSize: int = None, 
        chunkOverlap: int = None
    ):
        self.chunkSize = chunkSize or Config.CHUNK_SIZE
        self.chunkOverlap = chunkOverlap or Config.CHUNK_OVERLAP
    
    def splitText(self, text: str) -> List[str]:
        """Metni parçalara ayırır"""
        if not text or not text.strip():
            return []
        
        chunks = []
        separators = ["\n\n", "\n", ". ", "! ", "? ", " ", ""]
        
        def splitRecursive(text: str, separators: List[str]) -> List[str]:
            """Recursive olarak metni böler"""
            if len(text) <= self.chunkSize:
                return [text] if text.strip() else []
            
            if not separators:
                # Son çare: karakter karakter böl
                return [text[i:i+self.chunkSize] for i in range(0, len(text), self.chunkSize - self.chunkOverlap)]
            
            separator = separators[0]
            remainingSeparators = separators[1:]
            
            if separator == "":
                # Boş separator = karakter karakter böl
                return [text[i:i+self.chunkSize] for i in range(0, len(text), self.chunkSize - self.chunkOverlap)]
            
            splits = text.split(separator)
            currentChunk = ""
            result = []
            
            for i, split in enumerate(splits):
                # Separator'ı geri ekle (son split hariç)
                if i < len(splits) - 1:
                    split += separator
                
                # Eğer mevcut chunk + yeni split chunk boyutunu aşıyorsa
                potentialChunk = currentChunk + split if currentChunk else split
                
                if len(potentialChunk) <= self.chunkSize:
                    currentChunk = potentialChunk
                else:
                    # Mevcut chunk'ı kaydet
                    if currentChunk:
                        result.append(currentChunk)
                    
                    # Yeni split'i işle
                    if len(split) > self.chunkSize:
                        # Split çok büyük, recursive olarak böl
                        subChunks = splitRecursive(split, remainingSeparators)
                        result.extend(subChunks[:-1])  # Son chunk hariç (overlap için)
                        currentChunk = subChunks[-1] if subChunks else ""
                    else:
                        # Overlap ekle
                        if self.chunkOverlap > 0 and result:
                            lastChunk = result[-1]
                            overlapText = lastChunk[-self.chunkOverlap:] if len(lastChunk) > self.chunkOverlap else lastChunk
                            currentChunk = overlapText + split
                        else:
                            currentChunk = split
            
            if currentChunk:
                result.append(currentChunk)
            
            return [chunk.strip() for chunk in result if chunk.strip()]
        
        chunks = splitRecursive(text, separators)
        return chunks
    
    def splitDocuments(self, documents: List[dict]) -> List[dict]:
        """Birden fazla dokümanı parçalara ayırır"""
        allChunks = []
        
        for doc in documents:
            chunks = self.splitText(doc["text"])
            
            for i, chunk in enumerate(chunks):
                allChunks.append({
                    "text": chunk,
                    "source": doc["fileName"],
                    "filePath": doc["filePath"],
                    "fileType": doc["fileType"],
                    "chunkIndex": i,
                    "totalChunks": len(chunks)
                })
        
        return allChunks

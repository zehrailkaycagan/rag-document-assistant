# Mimari Dokümantasyonu

## Genel Bakış

Bu proje, **Clean Architecture** prensiplerine uygun olarak katmanlı bir mimari kullanmaktadır.

## Klasör Yapısı

```
src/
├── models/              # Veri modelleri (Entity/DTO)
├── exceptions/          # Özel exception sınıfları
├── factories/           # Factory pattern implementasyonları
├── repositories/       # Veri erişim katmanı (Repository Pattern)
├── services/           # İş mantığı katmanı (Service Layer)
├── config.py           # Yapılandırma
├── utils.py            # Yardımcı fonksiyonlar
├── document_loader.py  # Doküman yükleme
├── text_splitter.py    # Metin bölme
├── embeddings.py       # Embedding üretimi (Factory kullanır)
├── vector_store.py     # Geriye dönük uyumluluk (Repository kullanır)
└── rag_chain.py        # Geriye dönük uyumluluk (Service kullanır)
```

## Mimari Katmanlar

### 1. Models (Veri Modelleri)

**Konum:** `src/models/`

Veri transfer objeleri (DTO) ve entity sınıfları:

- `Document`: Doküman modeli
- `DocumentChunk`: Doküman parçası modeli
- `QueryResult`: Sorgu sonucu modeli
- `SourceInfo`: Kaynak bilgisi modeli

**Özellikler:**
- Dataclass kullanımı
- `fromDict()` ve `toDict()` metodları
- Tip güvenliği

### 2. Exceptions (Hata Yönetimi)

**Konum:** `src/exceptions/`

Özel exception sınıfları:

- `DocumentLoadError`: Doküman yükleme hatası
- `UnsupportedFileFormatError`: Desteklenmeyen format
- `VectorStoreError`: Vektör veritabanı hatası
- `RAGQueryError`: RAG sorgu hatası

**Avantajlar:**
- Daha iyi hata yönetimi
- Anlamlı hata mesajları
- Hata türlerine göre işlem yapma

### 3. Factories (Factory Pattern)

**Konum:** `src/factories/`

Nesne oluşturma için factory pattern:

- `EmbeddingFactory`: Embedding modeli oluşturma
- `LLMFactory`: LLM modeli oluşturma

**Avantajlar:**
- Merkezi nesne oluşturma
- Kolay test edilebilirlik
- Esnek yapılandırma

### 4. Repositories (Veri Erişim Katmanı)

**Konum:** `src/repositories/`

Veri erişim işlemleri:

- `VectorStoreRepository`: FAISS vektör veritabanı erişimi

**Avantajlar:**
- Veri erişim mantığının soyutlanması
- Kolay test edilebilirlik
- Veri kaynağı değişikliğinde kolay adaptasyon

### 5. Services (İş Mantığı Katmanı)

**Konum:** `src/services/`

İş mantığı ve orkestrasyon:

- `DocumentService`: Doküman işleme servisi
- `RAGService`: RAG sorgu servisi

**Avantajlar:**
- İş mantığının merkezileştirilmesi
- Kod tekrarının azaltılması
- Kolay bakım ve test

## Tasarım Desenleri

### 1. Factory Pattern
- Embedding ve LLM modeli oluşturma
- Merkezi yapılandırma yönetimi

### 2. Repository Pattern
- Vektör veritabanı erişiminin soyutlanması
- Veri kaynağı bağımsızlığı

### 3. Service Layer Pattern
- İş mantığının UI/API'dan ayrılması
- Yeniden kullanılabilir servisler

### 4. Dependency Injection
- Servisler ve repository'ler bağımlılık enjeksiyonu ile oluşturulur
- Test edilebilirlik artar

## Veri Akışı

### Doküman İşleme Akışı

```
┌─────────────────────────────────────────────────────────────┐
│                    Doküman İşleme Pipeline                   │
└─────────────────────────────────────────────────────────────┘

UI/API Layer (app.py / api.py)
    ↓
DocumentService
    ↓
DocumentLoader (PDF/DOCX/TXT parsing + tablo okuma)
    ↓
TextSplitter (Chunking: 1500 char, 300 overlap)
    ↓
EmbeddingGenerator (OpenAI veya SentenceTransformers)
    ↓
VectorStoreRepository
    ↓
FAISS Index (vektör + metadata saklama)
```

### Sorgu Akışı (RAG Pipeline)

```
┌─────────────────────────────────────────────────────────────┐
│                      RAG Query Pipeline                      │
└─────────────────────────────────────────────────────────────┘

UI/API Layer
    ↓
RAGService.query(question)
    ↓
1. EmbeddingGenerator.embedQuery(question)
    ↓
2. VectorStoreRepository.search(queryEmbedding, topK=6)
    ├─ FAISS similarity search
    ├─ Distance hesaplama (L2)
    └─ Top-K sonuç seçimi
    ↓
3. Context Oluşturma
    ├─ Seçilen chunk'ları birleştir
    ├─ SourceInfo oluştur (fileName, chunkIndex, score)
    └─ Prompt için hazırla
    ↓
4. Cevap Üretimi
    ├─ LLMFactory.create() → OpenAI GPT (opsiyonel)
    ├─ Prompt Engineering (hallucination azaltma)
    └─ Basit yanıt (LLM yoksa)
    ↓
5. QueryResult
    ├─ answer: str
    ├─ sources: List[SourceInfo]
    └─ context: str
    ↓
UI/API Response (source citation ile)
```

### Hallucination Azaltma Mekanizması

```
┌─────────────────────────────────────────────────────────────┐
│              Hallucination Azaltma Stratejileri              │
└─────────────────────────────────────────────────────────────┘

1. Prompt Engineering
   ├─ "SADECE doküman içeriğindeki bilgileri kullan"
   ├─ "Tahmin yapma veya genel bilgi ekleme"
   └─ "Doküman içeriğinde yeterli bilgi yoksa belirt"

2. Context Filtering
   ├─ Top-K sonuç seçimi (en ilgili parçalar)
   ├─ Score threshold (opsiyonel)
   └─ Düşük kaliteli sonuçların filtrelenmesi

3. Source Citation
   ├─ Her cevap için kaynak gösterimi
   ├─ Chunk index ve similarity score
   └─ Kullanıcı doğrulama yapabilir

4. Response Validation
   ├─ "Bu bilgi dokümanda yok" kontrolü
   └─ Doküman içeriği dışında cevap vermeme
```

## Geriye Dönük Uyumluluk

Eski kodların çalışmaya devam etmesi için:

- `VectorStore` → `VectorStoreRepository` wrapper
- `RAGChain` → `RAGService` wrapper
- `EmbeddingGenerator` → `EmbeddingFactory` kullanır

**Not:** Yeni kodlar doğrudan yeni sınıfları kullanmalıdır.

## Best Practices

1. **Separation of Concerns**: Her katman kendi sorumluluğuna odaklanır
2. **Single Responsibility**: Her sınıf tek bir işi yapar
3. **Dependency Inversion**: Üst katmanlar alt katmanlara bağımlı değil
4. **Open/Closed Principle**: Genişlemeye açık, değişikliğe kapalı
5. **DRY (Don't Repeat Yourself)**: Kod tekrarı minimum

## Test Edilebilirlik

Yeni mimari sayesinde:

- Mock repository'ler ile test
- Mock servisler ile test
- Factory'lerin test edilmesi kolay
- Unit test yazımı kolaylaştı

## RAG Pipeline Detayları

### Text Chunking Stratejisi
- **Chunk Size**: 1500 karakter (teknik içerik için optimize)
- **Chunk Overlap**: 300 karakter (bağlam korunması için)
- **Yöntem**: RecursiveCharacterTextSplitter mantığı
- **Avantaj**: Anlamlı parçalara bölme, bağlam kaybını minimize etme

### Embedding Stratejisi
- **OpenAI Embeddings**: 
  - Model: `text-embedding-3-small`
  - Boyut: 1536 boyutlu vektörler
  - Avantaj: Yüksek kalite, ücretli
  
- **SentenceTransformers**:
  - Model: `paraphrase-multilingual-MiniLM-L12-v2`
  - Boyut: 384 boyutlu vektörler
  - Avantaj: Ücretsiz, multilingual, lokal çalışır

### Vector DB (FAISS)
- **Index Type**: L2 (Euclidean distance)
- **Metadata**: Dosya adı, chunk index, timestamp
- **Arama**: Similarity search, Top-K retrieval
- **Performans**: Hızlı arama, lokal çalışır

### Prompt Engineering
- **Yapı**: Sistem mesajı + kullanıcı sorusu + doküman içeriği
- **Hallucination Azaltma**: 
  - Sadece doküman içeriğini kullanma talimatı
  - Tahmin yapmama zorunluluğu
  - Teknik terimleri doğru kullanma
- **Türkçe Optimizasyonu**: Türkçe cevap üretimi için özel talimatlar

### Source Citation Sistemi
- **SourceInfo Modeli**:
  - `fileName`: Kaynak dosya adı
  - `chunkIndex`: Hangi parçadan alındığı
  - `score`: Similarity score (düşük = daha benzer)
- **Gösterim**: UI'da kaynak listesi, API'de JSON formatında

## Gelecek İyileştirmeler

1. **Interface/Abstract Base Classes**: Daha iyi soyutlama
2. **Dependency Injection Container**: Otomatik DI
3. **Event Bus**: Event-driven mimari
4. **Caching Layer**: Performans iyileştirmesi
5. **Validation Layer**: Veri doğrulama
6. **Chroma DB Desteği**: Alternatif vektör veritabanı seçeneği
7. **Markdown Parsing**: Markdown dosya desteği
8. **Hybrid Search**: Keyword + semantic search kombinasyonu
9. **Re-ranking**: Sonuçları yeniden sıralama (cross-encoder)
10. **Multi-modal Support**: Görsel içerik desteği
# RAG Document Assistant

## Projenin Amacı

Bu projenin amacı, yüklenen dokümanları (PDF, DOCX, TXT) kullanarak çalışan,  
kullanıcı sorularına **yalnızca bu dokümanlara dayanarak** cevap veren  
**RAG (Retrieval-Augmented Generation) tabanlı bir akıllı doküman asistanı** geliştirmektir.

Bu asistan:
- Dokümanları gerçekten okur
- Dokümanda olmayan bilgiyi uydurmaz
- Gerekirse “bu bilgi dokümanda yok” diyebilir

---

## RAG Nedir? (Kısa)

RAG, yapay zekânın cevabı üretmeden önce:
1. İlgili doküman parçalarını bulmasını
2. Bu parçaları bağlam olarak kullanmasını
sağlayan bir yaklaşımdır.

Bu sayede sistem:
- Genel bilgiyle değil
- Verilen dokümanlarla konuşur

---

## Kullanılan Programlama Dili

- **Python 3.10+**

---

## Kullanılan Teknolojiler

### Yöntemler
- **Text Chunking** → Dokümanları anlamlı parçalara ayırma (RecursiveCharacterTextSplitter mantığı)
- **Embedding** → OpenAI veya SentenceTransformers ile vektör temsilleri
- **Vector DB** → FAISS ile lokal vektör veritabanı (Chroma DB desteği gelecekte eklenecek)
- **RAG (Retrieval-Augmented Generation)** → Doküman tabanlı cevap üretimi
- **Prompt Engineering** → Hallucination azaltma ve doğru cevap üretimi için optimize edilmiş prompt'lar

### Teknolojiler / Diller
- **Python 3.10+** → Ana programlama dili
- **FAISS** → Lokal vektör veritabanı (hızlı benzerlik araması)
- **OpenAI API** → Embedding ve LLM (opsiyonel, ücretli)
- **SentenceTransformers** → Ücretsiz embedding modelleri (multilingual destek)
- **Streamlit** → Kullanıcı arayüzü
- **FastAPI** → REST API katmanı
- **PyTorch** → SentenceTransformers backend
- **NumPy / Pandas** → Veri işleme

### Doküman İşleme
- **PDF Parsing** → pypdf ve pdfplumber (tablo okuma dahil)
- **DOCX Parsing** → python-docx (tablo okuma dahil)
- **TXT Parsing** → Standart metin dosyaları
- **Markdown Parsing** → Gelecekte eklenecek  

---

## Proje Dosya Yapısı

```
Rag Document Assistant/
├── src/                          # Kaynak kod modülleri
│   ├── __init__.py              # Paket başlatıcı
│   ├── config.py                # Yapılandırma ayarları
│   ├── utils.py                 # Yardımcı fonksiyonlar
│   ├── document_loader.py       # Doküman yükleme (PDF, DOCX, TXT)
│   ├── text_splitter.py         # Metin bölme modülü
│   ├── embeddings.py            # Embedding üretimi
│   ├── vector_store.py          # Geriye dönük uyumluluk
│   ├── rag_chain.py             # Geriye dönük uyumluluk
│   ├── models/                  # Veri modelleri
│   │   ├── document.py          # Doküman modelleri
│   │   └── query_result.py      # Sorgu sonuç modelleri
│   ├── exceptions/              # Özel exception sınıfları
│   │   ├── document_exceptions.py
│   │   ├── vector_store_exceptions.py
│   │   └── rag_exceptions.py
│   ├── factories/               # Factory pattern
│   │   ├── embedding_factory.py
│   │   └── llm_factory.py
│   ├── repositories/            # Veri erişim katmanı
│   │   └── vector_store_repository.py
│   └── services/               # İş mantığı katmanı
│       ├── document_service.py
│       └── rag_service.py
├── app.py                       # Streamlit kullanıcı arayüzü
├── api.py                       # FastAPI REST API
├── requirements.txt             # Python bağımlılıkları
├── .env.example                 # Ortam değişkenleri örneği
├── .gitignore                   # Git ignore dosyası
├── ARCHITECTURE.md              # Mimari dokümantasyonu
├── uploads/                     # Yüklenen dosyalar (geçici)
├── data/                        # İşlenmiş veriler
└── vector_store/                # FAISS index dosyaları
```

---

## Kurulum

### 1. Gereksinimler

- Python 3.10 veya üzeri
- pip (Python paket yöneticisi)

### 2. Projeyi Klonlayın veya İndirin

```bash
cd "Rag Document Assistant"
```

### 3. Sanal Ortam Oluşturun (Önerilir)

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 4. Bağımlılıkları Yükleyin

```bash
pip install -r requirements.txt
```

### 5. Ortam Değişkenlerini Yapılandırın (Opsiyonel)

`.env.example` dosyasını `.env` olarak kopyalayın ve gerekirse düzenleyin:

```bash
# Windows
copy .env.example .env

# Linux/Mac
cp .env.example .env
```

**Not:** OpenAI API key'i opsiyoneldir. Belirtmezseniz, sistem Sentence Transformers kullanacaktır (ücretsiz).

---

## Kullanım

### Streamlit Web Arayüzü (Önerilen)

```bash
streamlit run app.py
```

Tarayıcınızda `http://localhost:8501` adresine gidin.

**Kullanım Adımları:**
1. Sidebar'dan PDF, DOCX veya TXT dosyalarınızı yükleyin
2. "Dokümanları İşle" butonuna tıklayın
3. Ana ekranda sorunuzu yazın ve cevap alın

### FastAPI REST API

```bash
python api.py
```

veya

```bash
uvicorn api:app --reload
```

API dokümantasyonu: `http://localhost:8000/docs`

**API Endpoints:**
- `POST /upload` - Doküman yükleme
- `POST /query` - Soru sorma
- `GET /status` - Durum bilgisi
- `DELETE /clear` - Vektör veritabanını temizleme

**Örnek Kullanım:**

```python
import requests

# Doküman yükle
files = [('files', open('document.pdf', 'rb'))]
response = requests.post('http://localhost:8000/upload', files=files)
print(response.json())

# Soru sor
data = {"question": "Bu dokümanlarda ne anlatılıyor?"}
response = requests.post('http://localhost:8000/query', json=data)
print(response.json())
```

---

## Mimari

Proje, **Clean Architecture** prensiplerine uygun olarak katmanlı bir mimari kullanmaktadır:

- **Models**: Veri modelleri ve entity sınıfları
- **Exceptions**: Özel hata yönetimi
- **Factories**: Nesne oluşturma (Factory Pattern)
- **Repositories**: Veri erişim katmanı (Repository Pattern)
- **Services**: İş mantığı katmanı (Service Layer)

Detaylı mimari dokümantasyonu için [ARCHITECTURE.md](ARCHITECTURE.md) dosyasına bakın.

---

## Özellikler

### Doküman İşleme
✅ **Çoklu Format Desteği**: PDF, DOCX, TXT dosyalarını destekler  
✅ **Tablo Okuma**: PDF ve DOCX içindeki tabloları okuyup yorumlar  
✅ **Akıllı Metin Bölme**: Dokümanları anlamlı parçalara ayırır (chunk size: 1500, overlap: 300)

### Embedding ve Vektör Veritabanı
✅ **İki Embedding Seçeneği**: OpenAI (ücretli) veya Sentence Transformers (ücretsiz)  
✅ **Multilingual Destek**: Türkçe ve diğer diller için optimize edilmiş modeller  
✅ **Vektör Arama**: FAISS ile hızlı ve doğru benzerlik araması  
✅ **Metadata Saklama**: Dosya adı, chunk index ve similarity score bilgileri

### RAG ve Cevap Üretimi
✅ **RAG Pipeline**: Tam entegre Retrieval-Augmented Generation sistemi  
✅ **Prompt Engineering**: Hallucination azaltma için optimize edilmiş prompt'lar  
✅ **LLM Entegrasyonu**: OpenAI GPT modelleri ile cevap üretimi (opsiyonel)  
✅ **Hallucination Azaltma**: Sadece doküman içeriğine dayalı cevap üretimi  
✅ **Source Citation**: Her cevap için kaynak dosya ve chunk bilgisi gösterimi

### Kullanıcı Arayüzü
✅ **Web Arayüzü**: Kullanıcı dostu Streamlit arayüzü  
✅ **REST API**: FastAPI ile programatik erişim  
✅ **Gerçek Zamanlı İşlem**: Progress bar ve status göstergeleri  
✅ **Türkçe Destek**: Türkçe dokümanlar ve sorular için optimize edilmiş  

---

## Yapılandırma

`src/config.py` dosyasında veya `.env` dosyasında aşağıdaki ayarları yapabilirsiniz:

### Text Chunking Ayarları
- `CHUNK_SIZE`: Metin parça boyutu (varsayılan: 1500)
- `CHUNK_OVERLAP`: Parça örtüşme miktarı (varsayılan: 300)

### Embedding Ayarları
- `EMBEDDING_MODEL`: "openai" veya "sentence-transformers"
- `SENTENCE_TRANSFORMERS_MODEL`: Kullanılacak model adı (varsayılan: "paraphrase-multilingual-MiniLM-L12-v2")
- `OPENAI_API_KEY`: OpenAI API anahtarı (opsiyonel)
- `OPENAI_EMBEDDING_MODEL`: OpenAI embedding modeli (varsayılan: "text-embedding-3-small")

### Vector DB Ayarları
- `TOP_K_RESULTS`: Her sorgu için döndürülecek sonuç sayısı (varsayılan: 6)
- `SCORE_THRESHOLD`: Maksimum distance threshold (None = filtreleme yok)

### LLM Ayarları
- `OPENAI_MODEL`: OpenAI LLM modeli (varsayılan: "gpt-3.5-turbo")

---

## Nasıl Çalışır?

### RAG Pipeline Şeması

```
┌─────────────────────────────────────────────────────────────────┐
│                    RAG DOCUMENT ASSISTANT                        │
│                    Pipeline Akış Şeması                         │
└─────────────────────────────────────────────────────────────────┘

📄 DOKÜMAN YÜKLEME
    │
    ├─ PDF → pypdf + pdfplumber (tablo okuma)
    ├─ DOCX → python-docx (tablo okuma)
    └─ TXT → Standart metin okuma
    │
    ▼
✂️ METİN ÇIKARMA VE TEMİZLEME
    │
    ├─ Metin içeriği çıkarılır
    ├─ Tablolar formatlanır
    └─ Gereksiz karakterler temizlenir
    │
    ▼
📝 TEXT CHUNKING (Parçalama)
    │
    ├─ Chunk Size: 1500 karakter
    ├─ Chunk Overlap: 300 karakter
    └─ Anlamlı parçalara bölünür
    │
    ▼
🧮 EMBEDDING ÜRETİMİ
    │
    ├─ OpenAI Embeddings (opsiyonel, ücretli)
    └─ SentenceTransformers (ücretsiz, multilingual)
    │
    ▼
💾 VEKTÖR VERİTABANI (FAISS)
    │
    ├─ Embedding'ler vektörlere dönüştürülür
    ├─ FAISS index'e kaydedilir
    └─ Metadata (dosya adı, chunk index) saklanır
    │
    ▼
🔍 SORGU İŞLEME
    │
    ├─ Kullanıcı sorusu embedding'e çevrilir
    ├─ FAISS ile benzerlik araması yapılır
    ├─ Top-K sonuçlar alınır (varsayılan: 6)
    └─ En ilgili parçalar seçilir
    │
    ▼
📚 BAĞLAM OLUŞTURMA
    │
    ├─ Seçilen parçalar birleştirilir
    ├─ Source citation bilgileri eklenir
    └─ Prompt için hazırlanır
    │
    ▼
🤖 CEVAP ÜRETİMİ (RAG)
    │
    ├─ Prompt Engineering ile optimize edilmiş prompt
    ├─ OpenAI GPT (opsiyonel) veya basit yanıt
    ├─ Hallucination azaltma mekanizması
    └─ Sadece doküman içeriğine dayalı cevap
    │
    ▼
📎 SONUÇ VE KAYNAK GÖSTERİMİ
    │
    ├─ Cevap kullanıcıya gösterilir
    ├─ Kaynak dosyalar listelenir
    ├─ Chunk index ve similarity score gösterilir
    └─ Detaylı bağlam (expandable)
```

### Adım Adım İşlem

1. **Doküman Yükleme**: PDF, DOCX veya TXT dosyaları yüklenir
2. **Metin Çıkarma**: Dosyalardan metin içeriği çıkarılır (tablolar dahil)
3. **Parçalama (Text Chunking)**: Metinler anlamlı parçalara (chunks) bölünür
4. **Embedding**: Her parça vektörlere (embedding) dönüştürülür
5. **Vektör Veritabanı**: Embedding'ler FAISS veritabanına kaydedilir
6. **Sorgu İşleme**: Kullanıcı sorusu da embedding'e çevrilir
7. **Benzerlik Arama**: En benzer doküman parçaları bulunur
8. **Cevap Üretme**: Bulunan parçalar bağlam olarak kullanılarak cevap üretilir
9. **Source Citation**: Kullanılan kaynaklar gösterilir

---

## Hallucination Azaltma

Bu proje, LLM'lerin yanlış bilgi üretmesini (hallucination) azaltmak için çeşitli mekanizmalar kullanır:

### 1. Doküman Tabanlı Cevap Üretimi
- Sistem **sadece** yüklenen dokümanlardaki bilgileri kullanır
- Genel bilgi veya tahmin yapmaz
- Doküman içeriğinde bilgi yoksa açıkça belirtir

### 2. Prompt Engineering
- Optimize edilmiş prompt'lar ile LLM'e sadece doküman içeriğini kullanması söylenir
- Teknik terimlerin doğru kullanımı için özel talimatlar
- Alıntı yapma ve kaynak belirtme zorunluluğu

### 3. Source Citation
- Her cevap için kullanılan kaynak dosyalar gösterilir
- Chunk index ve similarity score bilgileri verilir
- Kullanıcı cevabın hangi dokümandan geldiğini görebilir

### 4. Context Filtering
- En ilgili parçalar seçilir (Top-K)
- Düşük benzerlik skorlu sonuçlar filtrelenebilir
- Sadece yüksek kaliteli bağlam kullanılır

## Source Citation (Kaynak Gösterimi)

Her sorgu sonucunda:
- **Kaynak Dosyalar**: Cevabın hangi dosyalardan alındığı gösterilir
- **Chunk Index**: Hangi parçadan alındığı belirtilir
- **Similarity Score**: Benzerlik skoru gösterilir (düşük = daha benzer)
- **Detaylı Bağlam**: Kullanılan metin parçaları expandable bölümde gösterilir

Örnek:
```
📎 Kaynaklar
1. crypto_candles.pdf (Parça: 5) - Score: 0.234
2. crypto_candles.pdf (Parça: 12) - Score: 0.456
```

## Sorun Giderme

### "ModuleNotFoundError" hatası
```bash
pip install -r requirements.txt
```

### FAISS yükleme hatası
```bash
pip install faiss-cpu
# veya GPU için
pip install faiss-gpu
```

### OpenAI API hatası
`.env` dosyasında `OPENAI_API_KEY` değerini kontrol edin veya Sentence Transformers kullanın.

### Embedding model yükleme hatası
- PyTorch meta tensor hatası alıyorsanız, model otomatik olarak alternatif modellere geçer
- İnternet bağlantınızı kontrol edin (model indirme için gerekli)
- Cache temizlemek için: `rm -rf ~/.cache/huggingface/`

---

## Lisans

Bu proje eğitim amaçlıdır.

---

## Katkıda Bulunma

1. Fork edin
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Commit edin (`git commit -m 'Add amazing feature'`)
4. Push edin (`git push origin feature/amazing-feature`)
5. Pull Request açın

---

## İletişim

Sorularınız için issue açabilirsiniz.
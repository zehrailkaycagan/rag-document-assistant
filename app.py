"""
Streamlit Kullanıcı Arayüzü - RAG Document Assistant
"""
import os
import logging
import streamlit as st

# TensorFlow uyarılarını bastır
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

from src.config import Config
from src.services.document_service import DocumentService
from src.services.rag_service import RAGService
from src.repositories.vector_store_repository import VectorStoreRepository
from src.embeddings import EmbeddingGenerator
from src.utils import formatFileSize
from src.exceptions.document_exceptions import DocumentLoadError

# Logging yapılandırması
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# TensorFlow ve diğer gereksiz uyarıları bastır
logging.getLogger('tensorflow').setLevel(logging.ERROR)
logging.getLogger('transformers').setLevel(logging.WARNING)
logging.getLogger('sentence_transformers').setLevel(logging.WARNING)

# Sayfa yapılandırması
st.set_page_config(
    page_title="RAG Document Assistant",
    page_icon="📚",
    layout="wide"
)

# Gerekli dizinleri oluştur
Config.ensureDirectories()

# Session state yönetimi
if "documentService" not in st.session_state:
    st.session_state.documentService = None
if "ragService" not in st.session_state:
    st.session_state.ragService = None
if "vectorStoreRepository" not in st.session_state:
    st.session_state.vectorStoreRepository = None
if "documentsLoaded" not in st.session_state:
    st.session_state.documentsLoaded = False

def initializeServices():
    """Servisleri başlatır"""
    try:
        if st.session_state.vectorStoreRepository is None:
            embeddingGenerator = EmbeddingGenerator()
            vectorStoreRepository = VectorStoreRepository(embeddingGenerator)
            
            # Kaydedilmiş index varsa yükle
            if vectorStoreRepository.load():
                st.session_state.documentsLoaded = True
            
            st.session_state.vectorStoreRepository = vectorStoreRepository
            st.session_state.documentService = DocumentService(
                vectorStoreRepository=vectorStoreRepository
            )
            st.session_state.ragService = RAGService(
                vectorStoreRepository,
                useOpenAI=bool(Config.OPENAI_API_KEY)
            )
    except Exception as e:
        logger.error(f"Servis başlatma hatası: {e}")
        # Hata durumunda None olarak bırak
        if st.session_state.vectorStoreRepository is None:
            st.session_state.documentService = None
            st.session_state.ragService = None
        raise

def processDocuments(uploadedFiles):
    """Yüklenen dokümanları işler"""
    if not uploadedFiles:
        return False
    
    # Servislerin başlatıldığından emin ol
    if st.session_state.documentService is None:
        try:
            initializeServices()
        except Exception as e:
            logger.error(f"Servis başlatma hatası: {e}")
            st.error(f"Servisler başlatılamadı: {str(e)}")
            return False
    
    # documentService hala None ise hata ver
    if st.session_state.documentService is None:
        st.error("Doküman servisi başlatılamadı. Lütfen sayfayı yenileyin.")
        return False
    
    try:
        with st.spinner("Dokümanlar işleniyor..."):
            result = st.session_state.documentService.processUploadedFiles(uploadedFiles)
            
            st.session_state.documentsLoaded = True
            st.success(
                f"✅ {result['totalDocuments']} doküman başarıyla işlendi "
                f"ve {result['totalChunks']} parçaya ayrıldı!"
            )
            return True
            
    except DocumentLoadError as e:
        logger.error(f"Doküman işleme hatası: {e}")
        st.error(f"Hata: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Beklenmeyen hata: {e}")
        st.error(f"Beklenmeyen hata: {str(e)}")
        return False

def main():
    """Ana uygulama fonksiyonu"""
    st.title("📚 RAG Document Assistant")
    st.markdown("---")
    
    # Sidebar - Doküman Yükleme
    with st.sidebar:
        st.header("📄 Doküman Yükleme")
        
        uploadedFiles = st.file_uploader(
            "PDF, DOCX veya TXT dosyaları yükleyin",
            type=["pdf", "docx", "txt"],
            accept_multiple_files=True
        )
        
        if uploadedFiles:
            totalSize = sum(f.size for f in uploadedFiles)
            st.info(f"Toplam: {len(uploadedFiles)} dosya ({formatFileSize(totalSize)})")
        
        if st.button("🔄 Dokümanları İşle", type="primary"):
            if uploadedFiles:
                processDocuments(uploadedFiles)
            else:
                st.warning("Lütfen önce dosya yükleyin")
        
        st.markdown("---")
        
        # Vektör veritabanı durumu
        st.header("📊 Durum")
        if st.session_state.documentsLoaded and st.session_state.vectorStoreRepository:
            stats = st.session_state.vectorStoreRepository.getStats()
            st.success(f"✅ {stats['totalDocuments']} doküman parçası yüklü")
        else:
            st.info("ℹ️ Henüz doküman yüklenmedi")
        
        st.markdown("---")
        
        if st.button("🗑️ Vektör Veritabanını Temizle"):
            if st.session_state.vectorStoreRepository:
                st.session_state.vectorStoreRepository.clear()
                # Dosyaları da sil
                indexFile = Config.VECTOR_STORE_PATH + ".index"
                pklFile = Config.VECTOR_STORE_PATH + ".pkl"
                if os.path.exists(indexFile):
                    os.remove(indexFile)
                if os.path.exists(pklFile):
                    os.remove(pklFile)
                st.session_state.documentsLoaded = False
                st.success("Vektör veritabanı temizlendi")
                st.rerun()
    
    # Ana içerik alanı
    try:
        initializeServices()
    except Exception as e:
        logger.error(f"Servis başlatma hatası: {e}")
        st.error(f"⚠️ Servisler başlatılamadı: {str(e)}")
        st.info("Lütfen sayfayı yenileyin veya konsol çıktısını kontrol edin.")
        return
    
    if not st.session_state.documentsLoaded:
        st.info("👈 Lütfen sidebar'dan doküman yükleyin ve işleyin")
        st.markdown("""
        ### Nasıl Kullanılır?
        1. **Doküman Yükle**: Sidebar'dan PDF, DOCX veya TXT dosyalarınızı yükleyin
        2. **İşle**: "Dokümanları İşle" butonuna tıklayın
        3. **Soru Sor**: Aşağıdaki alana sorunuzu yazın ve cevap alın
        """)
    else:
        st.header("💬 Soru Sor")
        
        question = st.text_input(
            "Dokümanlarınız hakkında bir soru sorun:",
            placeholder="Örn: Bu dokümanlarda ne anlatılıyor?"
        )
        
        if st.button("🔍 Ara", type="primary") or question:
            if question:
                with st.spinner("Cevap üretiliyor..."):
                    try:
                        result = st.session_state.ragService.query(question)
                        
                        # Cevabı göster
                        st.markdown("### 💡 Cevap")
                        st.write(result.answer)
                        
                        # Kaynakları göster
                        if result.sources:
                            st.markdown("### 📎 Kaynaklar")
                            for i, source in enumerate(result.sources, 1):
                                st.markdown(
                                    f"**{i}.** {source.fileName} "
                                    f"(Parça: {source.chunkIndex + 1})"
                                )
                        
                        # Detaylı bağlam (genişletilebilir)
                        with st.expander("🔍 Detaylı Bağlam"):
                            context = result.context
                            displayContext = (
                                context[:2000] + "..." 
                                if len(context) > 2000 
                                else context
                            )
                            st.text(displayContext)
                    
                    except Exception as e:
                        logger.error(f"Sorgu hatası: {e}")
                        st.error(f"Hata: {str(e)}")
            else:
                st.warning("Lütfen bir soru girin")

if __name__ == "__main__":
    main()

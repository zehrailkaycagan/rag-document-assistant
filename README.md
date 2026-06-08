# 📄 RAG Document Assistant

An end-to-end **Retrieval-Augmented Generation (RAG)** system that allows users to upload documents (PDF, DOCX, TXT) and query them using natural language. The system answers strictly based on provided documents, minimizing hallucinations and ensuring traceable, source-grounded responses.

---

# 🎯 Project Objective

The goal of this project is to build an intelligent document assistant that:

* Ingests and processes user-uploaded documents
* Retrieves relevant context using semantic search
* Generates answers strictly grounded in document content
* Avoids hallucination by design
* Can respond with “this information is not available in the document” when necessary

---

# 🧠 What is RAG?

Retrieval-Augmented Generation (RAG) is an architecture where:

1. Relevant document chunks are retrieved based on user queries
2. Retrieved context is passed to a language model
3. The model generates answers grounded only in that context

This ensures:

* Responses are **context-aware**
* Outputs are **document-specific**
* Hallucinations are significantly reduced

---

# 🛠️ Technology Stack

## Core Language

* **Python 3.10+**

---

## Machine Learning & NLP

* **SentenceTransformers** – Multilingual embeddings (free option)
* **OpenAI API** – Embeddings + LLM generation (optional)
* **PyTorch** – Backend for transformer models
* **NumPy / Pandas** – Data processing and transformation

---

## Vector Search & Retrieval

* **FAISS** – High-performance vector similarity search engine
* **Vector Store Layer** – Local persistent embedding index
* **Chunk Metadata Storage** – Source tracking and traceability

---

## Document Processing

* **PDF Parsing** – `pypdf`, `pdfplumber` (including table extraction)
* **DOCX Parsing** – `python-docx` (table support included)
* **TXT Parsing** – Native text processing
* **Markdown Support** – Planned extension

---

## Backend & API

* **FastAPI** – High-performance REST API framework
* **Streamlit** – Interactive web-based UI
* **Pydantic** – Data validation and schema enforcement

---

# 🏗️ System Architecture

```text
User Uploads Document
        ↓
Document Loader (PDF / DOCX / TXT)
        ↓
Text Extraction + Cleaning
        ↓
Text Chunking (1500 tokens, overlap 300)
        ↓
Embedding Generation (OpenAI / SentenceTransformers)
        ↓
FAISS Vector Database Indexing
        ↓
User Query Input
        ↓
Query Embedding
        ↓
Semantic Search (Top-K Similar Chunks)
        ↓
Context Construction
        ↓
LLM (RAG Prompt Engine)
        ↓
Final Answer + Source Citations
```

---

# 📁 Project Structure

```text
RAG Document Assistant/
│
├── src/
│   ├── __init__.py
│   ├── config.py
│   ├── utils.py
│   ├── document_loader.py
│   ├── text_splitter.py
│   ├── embeddings.py
│   ├── vector_store.py
│   ├── rag_chain.py
│   │
│   ├── models/
│   │   ├── document.py
│   │   └── query_result.py
│   │
│   ├── exceptions/
│   │   ├── document_exceptions.py
│   │   ├── vector_store_exceptions.py
│   │   └── rag_exceptions.py
│   │
│   ├── factories/
│   │   ├── embedding_factory.py
│   │   └── llm_factory.py
│   │
│   ├── repositories/
│   │   └── vector_store_repository.py
│   │
│   └── services/
│       ├── document_service.py
│       └── rag_service.py
│
├── app.py                  # Streamlit UI
├── api.py                  # FastAPI service
├── requirements.txt
├── .env.example
├── ARCHITECTURE.md
├── uploads/
├── data/
└── vector_store/
```

---

# 🚀 Installation

## 1. Requirements

* Python 3.10+
* pip package manager

---

## 2. Clone or Navigate

```bash
cd "Rag Document Assistant"
```

---

## 3. Create Virtual Environment

```bash
python -m venv venv
```

Activate:

**Windows**

```bash
venv\Scripts\activate
```

**Linux / macOS**

```bash
source venv/bin/activate
```

---

## 4. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 5. Environment Configuration (Optional)

```bash
cp .env.example .env
```

If OpenAI API key is not provided, the system automatically falls back to **SentenceTransformers (free mode)**.

---

# 💻 Usage

## 🖥️ Streamlit UI (Recommended)

```bash
streamlit run app.py
```

Open:

```
http://localhost:8501
```

### Workflow:

1. Upload PDF / DOCX / TXT files
2. Click **Process Documents**
3. Ask questions in the UI
4. Receive grounded answers with sources

---

## ⚙️ FastAPI Backend

Start API:

```bash
uvicorn api:app --reload
```

Or:

```bash
python api.py
```

API Docs:

```
http://localhost:8000/docs
```

---

## 📡 API Endpoints

| Method | Endpoint  | Description           |
| ------ | --------- | --------------------- |
| POST   | `/upload` | Upload documents      |
| POST   | `/query`  | Ask questions         |
| GET    | `/status` | System status         |
| DELETE | `/clear`  | Reset vector database |

---

## Example API Usage

```python
import requests

# Upload document
files = [('files', open('document.pdf', 'rb'))]
requests.post("http://localhost:8000/upload", files=files)

# Query document
response = requests.post(
    "http://localhost:8000/query",
    json={"question": "What is this document about?"}
)

print(response.json())
```

---

# 🧠 Core Architecture Principles

This system is designed using **Clean Architecture**:

## Layers

* **Models** → Data structures and entities
* **Exceptions** → Custom error handling
* **Factories** → Object creation logic
* **Repositories** → Data access layer (vector DB)
* **Services** → Business logic layer

This separation ensures:

* Maintainability
* Scalability
* Testability

---

# ✨ Key Features

## 📄 Document Processing

* Multi-format support: PDF, DOCX, TXT
* Table extraction from PDFs and DOCX files
* Intelligent text cleaning
* Chunking strategy (1500 size / 300 overlap)

---

## 🧮 Embeddings & Vector Search

* OpenAI embeddings (optional)
* SentenceTransformers (free, multilingual support)
* FAISS-based fast similarity search
* Metadata tracking (file, chunk index, score)

---

## 🤖 RAG Pipeline

* Full retrieval-augmented generation flow
* Context-aware prompt engineering
* LLM integration (OpenAI optional)
* Strict grounding in document content only

---

## 🧪 Hallucination Prevention

The system minimizes hallucinations via:

### 1. Strict Context Grounding

* Answers are generated ONLY from retrieved chunks
* No external knowledge injection

### 2. Prompt Constraints

* Model explicitly instructed to avoid assumptions
* Requires explicit “not found in document” responses

### 3. Source Attribution

* Every answer includes source document references
* Chunk-level traceability

### 4. Retrieval Filtering

* Top-K most relevant chunks only
* Low-similarity results filtered out

---

## 📎 Source Attribution

Each response includes:

* Source file name
* Chunk index
* Similarity score
* Extracted context preview

Example:

```
Sources:
1. report.pdf (chunk 5) – score: 0.234
2. report.pdf (chunk 12) – score: 0.456
```

---

# ⚙️ Configuration

## Chunking

* `CHUNK_SIZE`: 1500
* `CHUNK_OVERLAP`: 300

## Embeddings

* `EMBEDDING_MODEL`: openai / sentence-transformers
* Default model: `paraphrase-multilingual-MiniLM-L12-v2`

## Vector DB

* `TOP_K_RESULTS`: 6
* `SCORE_THRESHOLD`: optional filtering

## LLM

* Default OpenAI model: `gpt-3.5-turbo`

---

# 🔄 How It Works

1. User uploads document
2. Text is extracted and cleaned
3. Document is split into chunks
4. Each chunk is embedded into vectors
5. Vectors are stored in FAISS index
6. User submits a query
7. Query is embedded
8. Similar chunks are retrieved
9. Context is constructed
10. LLM generates grounded response
11. Sources are returned

---

# 🛡️ Hallucination Control Strategy

This system is explicitly designed to prevent hallucinations:

* No answer is generated without context retrieval
* LLM is constrained to provided documents only
* Missing information triggers explicit fallback responses
* Source traceability is mandatory for every output

---

# 🔧 Troubleshooting

## ModuleNotFoundError

```bash
pip install -r requirements.txt
```

---

## FAISS Installation Issues

```bash
pip install faiss-cpu
```

GPU version:

```bash
pip install faiss-gpu
```

---

## OpenAI API Issues

* Verify `.env` file configuration
* Ensure API key is valid
* Or switch to SentenceTransformers mode

---

## Model Loading Issues

* Check internet connection (for first-time downloads)
* Clear HuggingFace cache if needed:

```bash
rm -rf ~/.cache/huggingface/
```

---

# 📜 License

This project is intended for educational and research purposes.

---

# 🤝 Contribution Guidelines

1. Fork repository
2. Create feature branch
3. Commit changes
4. Push branch
5. Open Pull Request

---

# 📬 Contact

For issues or contributions, open a GitHub issue or discussion thread.

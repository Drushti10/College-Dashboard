# DocuMind AI — Intelligent Document Question-Answering & RAG Assistant

> A complete, production-grade Document Q&A application using Retrieval-Augmented Generation (RAG) powered by Streamlit, LangChain, FAISS CPU, Sentence Transformers, and Multi-Provider LLMs.

---

## 1. Project Title
**DocuMind AI: Verifiable Document Question-Answering and Retrieval-Augmented Generation (RAG) System**

---

## 2. Project Overview
DocuMind AI is a modern desktop web application that allows users to upload `.pdf` and `.docx` documents, process them into semantically searchable vector representations, ask natural language questions, and receive grounded answers backed by explicit source citations, exact page numbers, relevance metrics, and original text excerpts.

The system prevents AI hallucinations by constraining the language model to answer strictly from the retrieved document chunks, returning a polite fallback message if the query cannot be answered from the document.

---

## 3. Problem Statement
Standard Large Language Models (LLMs) suffer from two major limitations when applied to private or domain-specific documents:
1. **Knowledge Cutoffs & Hallucinations**: LLMs do not know about private enterprise or academic documents and will often invent plausible-sounding but incorrect information.
2. **Lack of Verifiability**: Traditional AI responses do not provide traceable citations or page numbers, making it impossible for researchers, students, and professionals to verify claims against the original document.

---

## 4. Objective
To design and build an intuitive, end-to-end RAG system that:
- Seamlessly extracts text and structural metadata from PDF and Word documents.
- Chunks content intelligently using recursive semantic boundaries.
- Indexes chunk embeddings in a FAISS vector database.
- Retrieves the top-$k$ most semantically relevant passages for any user query.
- Synthesizes an accurate answer with verifiable source citations and page numbers.
- Operates on student laptops with CPU support and provides an offline fallback mode requiring zero external API keys.

---

## 5. Features
- **Multi-Format Support**: Ingests `.pdf` (page-by-page preservation) and `.docx` (section/paragraph preservation).
- **Interactive RAG Controls**: Real-time sidebar sliders to adjust Chunk Size, Chunk Overlap, and Top-$K$ Retrieval.
- **Open-Source Embeddings**: Runs `sentence-transformers/all-MiniLM-L6-v2` locally on CPU.
- **Fast Similarity Search**: Employs FAISS CPU for sub-millisecond vector nearest-neighbor retrieval.
- **Multi-Provider LLM Integration**:
  - **Groq** (`llama-3.3-70b-versatile` / `llama-3.1-8b-instant`) — Free and ultra-fast.
  - **Google Gemini** (`gemini-1.5-flash`) — Free tier via Google AI Studio.
  - **OpenAI** (`gpt-4o-mini`).
  - **Offline Extractive Synthesizer** — Zero API keys required; 100% private and offline.
- **Grounded Responses & Citations**: Every answer references `[Source 1]`, `[Source 2]` with expandable cards displaying exact page numbers, similarity percentages, and quoted excerpts.
- **Anti-Hallucination Guardrails**: Responds strictly with *"I couldn't find this information in the uploaded document."* when questions fall outside document context.
- **Session Chat & Export**: Maintains multi-turn conversation during the session and provides 1-click `.txt` transcript download.
- **Real-Time Step Tracker**: 6-step progress indicator showing actual processing stages.

---

## 6. Technologies Used
| Component | Technology | Purpose |
|---|---|---|
| **Programming Language** | Python 3.10 - 3.14 | Core application language |
| **Web Interface** | Streamlit | Reactive dashboard with custom modern CSS |
| **Orchestration Framework** | LangChain Core & Community | Document schema and RAG abstraction |
| **Document Parsers** | `pypdf`, `python-docx` | Text & page metadata extraction |
| **Text Splitter** | `RecursiveCharacterTextSplitter` | Overlapping semantic chunking |
| **Embedding Model** | `all-MiniLM-L6-v2` (`sentence-transformers`) | 384-dimensional vector embeddings |
| **Vector Store** | FAISS CPU (`faiss-cpu`) | High-performance vector indexing & similarity search |
| **LLM Inference** | Groq / Google Gemini / OpenAI / Local Extractive | Grounded answer generation |
| **Configuration** | `python-dotenv` | Secure `.env` API key management |

---

## 7. System Workflow

```
┌─────────────────┐
│ PDF / DOCX File │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────┐
│ Text & Metadata Extraction      │  --> Preserves 1-indexed page numbers & section IDs
└────────┬────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│ Recursive Semantic Chunking     │  --> LangChain RecursiveCharacterTextSplitter
└────────┬────────────────────────┘      (Configurable chunk size & overlap)
         │
         ▼
┌─────────────────────────────────┐
│ Vector Embedding Generation     │  --> sentence-transformers/all-MiniLM-L6-v2
└────────┬────────────────────────┘      (Converts text chunks into 384-dim vectors)
         │
         ▼
┌─────────────────────────────────┐
│ FAISS Vector Store Indexing     │  --> Stores embeddings, texts, & page metadata
└────────┬────────────────────────┘
         │
         ▼
  [User Asks Question]
         │
         ▼
┌─────────────────────────────────┐
│ Vector Similarity Search        │  --> Encodes query and retrieves top-k chunks with scores
└────────┬────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│ Prompt Construction             │  --> Injects retrieved chunks + strict anti-hallucination rules
└────────┬────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│ LLM Generation / Synthesis      │  --> Groq / Gemini / OpenAI / Offline Local Mode
└────────┬────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│ UI Display with Source Cards    │  --> Answer + [Source #] + Page # + Similarity % + Excerpt
└─────────────────────────────────┘
```

---

## 8. Project Structure
```
document-qa-rag/
├── app.py                         # Streamlit interactive application entry point
├── requirements.txt               # Pinned Python package dependencies
├── README.md                      # Complete project documentation & viva guide
├── .env.example                   # Template for environment variables / API keys
├── .gitignore                     # Git exclusion rules for keys, cache, and venvs
├── create_sample_files.py         # Utility script to generate sample test documents
│
├── src/                           # Modular application package
│   ├── __init__.py                # Package initializer
│   ├── document_loader.py         # PDF (pypdf) & DOCX (python-docx) extraction
│   ├── text_splitter.py           # RecursiveCharacterTextSplitter logic
│   ├── embeddings.py              # SentenceTransformer vector embedding wrapper
│   ├── vector_store.py            # FAISS CPU vector database operations
│   ├── llm.py                     # Multi-provider LLM caller & offline synthesizer
│   └── utils.py                   # Custom CSS styling, metrics cards, export utils
│
├── data/
│   └── sample_document/           # Test documents
│       ├── sample_ai_overview.pdf # 4-page PDF document on AI, ML, Deep Learning & RAG
│       └── sample_ai_overview.docx# Word document covering AI & Transformers
│
└── tests/
    └── test_rag_pipeline.py       # Automated end-to-end unit and integration test suite
```

---

## 9. Installation Steps

### Prerequisites
- Python 3.10, 3.11, 3.12, 3.13, or 3.14 installed on your system.
- Git (optional).

### Step 1: Open Terminal & Navigate to Project Directory
```bash
cd document-qa-rag
```

### Step 2: Create a Virtual Environment
```bash
python -m venv .venv
```

### Step 3: Activate the Virtual Environment
- **Windows (PowerShell)**:
  ```powershell
  .\.venv\Scripts\Activate.ps1
  ```
- **Windows (Command Prompt)**:
  ```cmd
  .\.venv\Scripts\activate.bat
  ```
- **macOS / Linux**:
  ```bash
  source .venv/bin/activate
  ```

### Step 4: Install Dependencies
```bash
pip install -r requirements.txt
```

---

## 10. API Key Setup
DocuMind AI supports multiple providers. You only need **one** API key (or **zero** if using Offline Mode):

1. Duplicate `.env.example` and rename it to `.env`:
   ```bash
   cp .env.example .env
   ```
2. Open `.env` in any text editor and paste your key:
   - **Groq API Key (Recommended)**: Free key from [https://console.groq.com](https://console.groq.com)
     ```ini
     GROQ_API_KEY=gsk_your_key_here
     ```
   - **Google Gemini API Key**: Free key from [https://aistudio.google.com](https://aistudio.google.com)
     ```ini
     GEMINI_API_KEY=AIzaSy_your_key_here
     ```
   - **OpenAI API Key**: From [https://platform.openai.com](https://platform.openai.com)
     ```ini
     OPENAI_API_KEY=sk-proj-your_key_here
     ```

> **Note**: You can also enter or paste your API key directly in the Streamlit sidebar at runtime. If no key is entered, you can simply select **"Offline Extractive Mode (No API Key)"** in the dropdown!

---

## 11. How to Run the Application

Execute the following command in your activated terminal:
```bash
streamlit run app.py
```

Your browser will automatically open:
```
Local URL: http://localhost:8501
Network URL: http://192.168.x.x:8501
```

---

## 12. How the RAG Pipeline Works

RAG (Retrieval-Augmented Generation) combines two core mechanisms:
1. **Information Retrieval (IR)**: Locating the most relevant factual paragraphs from an external document repository based on vector similarity.
2. **Language Generation (NLG)**: Feeding those exact retrieved passages into an LLM as context with instructions to answer the query truthfully without hallucinating.

### Concept Explanations (Viva Concepts)

- **Streamlit**: An open-source Python framework that allows data scientists and developers to build reactive, interactive web dashboards in pure Python without writing boilerplate HTML/JavaScript.
- **Chunks**: Small, coherent segments of a larger document. Splitting text is essential because embedding models and LLMs have finite context windows, and smaller focused chunks yield sharper similarity matches.
- **RecursiveCharacterTextSplitter**: LangChain's intelligent text splitter that splits documents using a hierarchy of delimiters: paragraphs (`\n\n`), lines (`\n`), spaces (` `), and characters (`""`). It keeps paragraphs and sentences intact wherever possible.
- **Embeddings**: Mathematical representations of text in high-dimensional vector space (384 dimensions for `all-MiniLM-L6-v2`). Semantically related phrases have vectors located close to each other.
- **FAISS (Facebook AI Similarity Search)**: An open-source library created by Meta for dense vector indexing. It computes Euclidean ($L_2$) or Cosine distances between the user's query vector and millions of chunk vectors in milliseconds.
- **LLM (Large Language Model)**: A neural network trained on vast text data that synthesizes natural language answers based on the retrieved context chunks.
- **Retrieval**: The process of encoding a user query into a vector and querying the FAISS index to find the top-$k$ nearest chunk neighbors.
- **Citations**: Source attribution tags (e.g. `[Source 1]`, `Page 2`) that connect the LLM's statements back to the specific page and paragraph in the user's document.

---

## 13. Example Usage

1. Open `http://localhost:8501`.
2. In the sidebar, click **Browse files** and select `data/sample_document/sample_ai_overview.pdf`.
3. Watch the **6-Step Progress Tracker** process the document in under 3 seconds.
4. Inspect the 4 Metric Cards:
   - **4** Pages
   - **8** Chunks Created
   - **PDF** Document Type
   - **FAISS Ready ✓**
5. In the chat box, type:
   > *"What is supervised learning and what are its common algorithms?"*
6. Review the output:
   - **Answer**: *"Supervised learning algorithms are trained using labeled datasets where the desired output is known. Common algorithms include Linear Regression, Support Vector Machines, and Decision Trees [Source 1]."*
   - **Sources Area**: Expand the citation card to verify that this was retrieved from **Page 2** with **88% Relevance**.
7. Ask an out-of-context question:
   > *"How do you bake a chocolate cake?"*
8. Notice the anti-hallucination guardrail response:
   - *"I couldn't find this information in the uploaded document."*
9. Click **Export Q&A Transcript (.txt)** to save your session log.

---

## 14. Automated Testing

Run the included automated test suite to verify every component of the RAG pipeline:
```bash
python tests/test_rag_pipeline.py
```
This tests:
- PDF & DOCX text extraction
- Page metadata retention
- RecursiveCharacterTextSplitter chunking
- Embedding vector dimension (384)
- FAISS indexing & nearest-neighbor search
- Answer generation & source citations
- Negative out-of-context fallback handling
- Exception handling for invalid inputs

---

## 15. Common Errors and Troubleshooting

| Problem | Cause | Solution |
|---|---|---|
| `ModuleNotFoundError` | Virtual environment is not activated | Run `.\.venv\Scripts\Activate.ps1` before running `streamlit run app.py`. |
| "The document contains no extractable text" | Scanned image PDF without OCR text | Use a digital/searchable PDF or convert scanned files with an OCR tool first. |
| Groq/Gemini Authentication Error | Invalid or expired API key | Check your `.env` file or paste a fresh key into the sidebar text field. |
| FAISS installation issues | Old pip version | Upgrade pip: `python -m pip install --upgrade pip` and install `faiss-cpu`. |
| "Unsupported file format" | User uploaded `.txt`, `.jpg`, etc. | DocuMind AI natively processes `.pdf` and `.docx` formats. |

---

## 16. Future Enhancements
- Multi-document comparison and cross-document synthesis.
- Optical Character Recognition (OCR) integration (Tesseract/PaddleOCR) for scanned PDFs.
- Hybrid search combining BM25 keyword matching with FAISS dense vector search (Reciprocal Rank Fusion).
- Chat export to PDF and Markdown with formatted tables.
- Audio speech input (Whisper) for voice-driven document queries.

---

## 17. College Viva Guide & Interview Q&A

### Elevator Pitch (How to explain this project to your examiner in 60 seconds):
> *"DocuMind AI is a Retrieval-Augmented Generation application that solves the problem of AI hallucinations when querying private documents. When a user uploads a PDF or Word document, the system extracts its text while preserving exact page numbers. Using LangChain's RecursiveCharacterTextSplitter, the text is broken into overlapping chunks and converted into 384-dimensional vector embeddings via the open-source sentence-transformers model. These vectors are indexed in a FAISS vector database. When a query is asked, FAISS performs vector similarity search to retrieve the top matching chunks. These chunks are injected into a constrained LLM prompt that forces the model to answer strictly from the retrieved context and provide verifiable page citations. If the document does not contain the answer, it returns a polite fallback message rather than inventing facts."*

### Top 10 Viva Questions & Answers:

1. **What is RAG and why is it preferred over fine-tuning?**
   *Answer*: RAG (Retrieval-Augmented Generation) retrieves relevant external facts at inference time and injects them into the prompt. Fine-tuning modifies model weights, which is computationally expensive, prone to hallucinations, and difficult to update. RAG allows instant updates simply by updating the vector index.

2. **Why do we need chunking? Why not feed the entire document to the LLM?**
   *Answer*: Feeding entire documents exhausts token limits, increases API latency and costs, and dilutes the model's attention (known as the "lost in the middle" problem). Smaller, focused chunks allow FAISS to retrieve precisely the relevant paragraphs.

3. **What is chunk overlap and why is it important?**
   *Answer*: Chunk overlap ensures that consecutive chunks share a boundary of text (e.g. 200 characters). This prevents splitting a critical sentence or thought across chunk boundaries, ensuring semantic coherence is preserved.

4. **Why use `RecursiveCharacterTextSplitter` instead of splitting by character count?**
   *Answer*: It attempts to split on natural linguistic boundaries—first double line breaks (paragraphs), then single line breaks, then spaces between words. This ensures chunks contain complete sentences rather than words cut in half.

5. **What is an embedding?**
   *Answer*: An embedding is a dense vector of real numbers that represents the semantic meaning of text. Words and sentences with similar meanings are positioned closer to each other in this high-dimensional vector space.

6. **What embedding model did you choose and why?**
   *Answer*: We used `sentence-transformers/all-MiniLM-L6-v2`. It produces 384-dimensional vectors, runs quickly on a laptop CPU without needing a GPU, is completely open-source, and has strong semantic retrieval performance.

7. **How does FAISS work?**
   *Answer*: FAISS (Facebook AI Similarity Search) is an optimized C++ library with Python bindings for dense vector indexing. It calculates geometric distances (such as Euclidean distance or cosine similarity) between vectors to perform nearest-neighbor searches in sub-milliseconds.

8. **How does your project prevent hallucinations?**
   *Answer*: Through system prompt constraints and temperature control (0.1). The LLM is instructed to answer exclusively using the retrieved context passages and to output *"I couldn't find this information in the uploaded document."* if the information is absent.

9. **How are page numbers preserved for citations?**
   *Answer*: The document loader uses `pypdf` to iterate through pages sequentially. Each page's text is tagged with a `page` metadata key (`page: page_idx + 1`). When `RecursiveCharacterTextSplitter` splits the page, LangChain propagates this metadata to every child chunk.

10. **What is the difference between keyword search and semantic vector search?**
    *Answer*: Keyword search (like BM25 or SQL `LIKE`) matches exact words. If you search for "automobile", it misses documents containing "car". Semantic vector search matches the underlying meaning, so "automobile" and "car" yield nearly identical vectors and retrieve each other.

"""
DocuMind AI - Professional Document Question-Answering (RAG) Application
Built with Streamlit, LangChain, FAISS, Sentence Transformers, and Multi-Provider LLMs.
"""

import os
import sys
from pathlib import Path
import streamlit as st
from dotenv import load_dotenv

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.document_loader import load_document, DocumentProcessingError
from src.text_splitter import split_documents
from src.embeddings import get_embedding_model
from src.vector_store import create_vector_store, search_similar_chunks
from src.llm import generate_answer
from src.utils import get_custom_css, render_metric_cards, export_chat_history_to_text

# Load environment variables from .env
load_dotenv(PROJECT_ROOT / ".env")

# Streamlit Page Configuration
st.set_page_config(
    page_title="DocuMind AI - Document Q&A / RAG Assistant",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply Modern Custom CSS
st.markdown(get_custom_css(), unsafe_allow_html=True)


# ==========================================
# CACHED RESOURCES
# ==========================================
@st.cache_resource(show_spinner=False)
def load_cached_embeddings():
    """Caches sentence-transformers model so it loads only once into RAM."""
    return get_embedding_model("sentence-transformers/all-MiniLM-L6-v2")


# Initialize Session State
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "processed_doc" not in st.session_state:
    st.session_state.processed_doc = None
if "vector_store" not in st.session_state:
    st.session_state.vector_store = None
if "doc_summary" not in st.session_state:
    st.session_state.doc_summary = None
if "last_processed_filename" not in st.session_state:
    st.session_state.last_processed_filename = None


# ==========================================
# SIDEBAR
# ==========================================
with st.sidebar:
    st.markdown("## 📄 DocuMind AI")
    st.caption("Intelligent Document Q&A & Semantic RAG System")
    st.markdown("---")

    # Document Upload Section
    st.markdown("### 1. Upload Document")
    uploaded_file = st.file_uploader(
        "Select PDF or DOCX file",
        type=["pdf", "docx"],
        help="Upload a PDF or Word document to search and chat with."
    )

    # RAG Hyperparameters Section
    st.markdown("### 2. RAG Chunking Parameters")
    chunk_size = st.slider(
        "Chunk Size (characters)",
        min_value=300,
        max_value=2500,
        value=1000,
        step=100,
        help="Target length of each document segment."
    )
    chunk_overlap = st.slider(
        "Chunk Overlap (characters)",
        min_value=0,
        max_value=500,
        value=200,
        step=50,
        help="Character overlap between consecutive chunks to preserve contextual flow."
    )
    top_k = st.slider(
        "Top-K Chunks to Retrieve",
        min_value=1,
        max_value=8,
        value=4,
        step=1,
        help="Number of most semantically relevant chunks retrieved from FAISS for answering."
    )

    st.markdown("---")

    # LLM Settings Section
    st.markdown("### 3. Model & Generation Settings")
    provider_options = [
        "Groq (Recommended - Ultra Fast)",
        "Google Gemini",
        "OpenAI",
        "Offline Extractive Mode (No API Key)"
    ]
    selected_provider_label = st.selectbox(
        "LLM Provider",
        provider_options,
        index=0,
        help="Select the LLM provider for final answer generation."
    )

    # Map label to internal provider key
    if "Groq" in selected_provider_label:
        provider_key = "groq"
        default_model = "llama-3.3-70b-versatile"
        env_key = os.getenv("GROQ_API_KEY", "")
        key_help = "Get a free API key at https://console.groq.com"
    elif "Gemini" in selected_provider_label:
        provider_key = "gemini"
        default_model = "gemini-1.5-flash"
        env_key = os.getenv("GEMINI_API_KEY", "") or os.getenv("GOOGLE_API_KEY", "")
        key_help = "Get a free API key at https://aistudio.google.com"
    elif "OpenAI" in selected_provider_label:
        provider_key = "openai"
        default_model = "gpt-4o-mini"
        env_key = os.getenv("OPENAI_API_KEY", "")
        key_help = "API key from https://platform.openai.com"
    else:
        provider_key = "offline"
        default_model = "Extractive Synthesizer"
        env_key = ""
        key_help = "Local mode does not require any external API keys."

    user_api_key = ""
    if provider_key != "offline":
        user_api_key = st.text_input(
            f"{selected_provider_label.split(' ')[0]} API Key",
            type="password",
            value=env_key,
            help=key_help
        )
        if not user_api_key:
            st.info(f"💡 No key entered. Add your key above, or in `.env`, or switch to 'Offline Mode'.")

    st.markdown("---")

    # Session Management
    if st.button("🔄 Reset / Clear Session", use_container_width=True):
        st.session_state.chat_history = []
        st.session_state.processed_doc = None
        st.session_state.vector_store = None
        st.session_state.doc_summary = None
        st.session_state.last_processed_filename = None
        st.rerun()

    st.caption("DocuMind AI • Open-Source RAG Pipeline")


# ==========================================
# MAIN PAGE HEADER
# ==========================================
st.markdown("""
<div class="hero-container">
    <div class="hero-title">
        <span>DocuMind AI</span>
        <span class="hero-badge">RAG Assistant</span>
    </div>
    <p class="hero-subtitle">
        Ask questions from your documents with semantic vector search, strict factual grounding, and exact source citations.
    </p>
</div>
""", unsafe_allow_html=True)


# ==========================================
# DOCUMENT PROCESSING PIPELINE
# ==========================================
if uploaded_file is not None:
    current_file_id = f"{uploaded_file.name}_{chunk_size}_{chunk_overlap}"
    
    # Process document only when a new file is uploaded or parameters change
    if st.session_state.last_processed_filename != current_file_id:
        try:
            # 6-Step Processing Tracker
            progress_bar = st.progress(0)
            status_text = st.empty()

            status_text.markdown("⏳ **Step 1/6:** Reading uploaded file stream...")
            progress_bar.progress(15)

            status_text.markdown("📄 **Step 2/6:** Extracting text and metadata (pages/sections)...")
            raw_docs, summary = load_document(uploaded_file, uploaded_file.name)
            progress_bar.progress(35)

            status_text.markdown(f"✂️ **Step 3/6:** Splitting into chunks (size={chunk_size}, overlap={chunk_overlap})...")
            chunks = split_documents(raw_docs, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
            progress_bar.progress(60)

            status_text.markdown("🧠 **Step 4/6:** Loading sentence-transformers/all-MiniLM-L6-v2...")
            embed_model = load_cached_embeddings()
            progress_bar.progress(75)

            status_text.markdown("⚡ **Step 5/6:** Computing embeddings & building FAISS index...")
            vector_store = create_vector_store(chunks, embed_model)
            progress_bar.progress(95)

            status_text.markdown("✅ **Step 6/6:** Ready! Vector index successfully built.")
            progress_bar.progress(100)

            # Store in session state
            st.session_state.vector_store = vector_store
            st.session_state.doc_summary = summary
            st.session_state.doc_summary["total_chunks"] = len(chunks)
            st.session_state.last_processed_filename = current_file_id
            st.session_state.chat_history = []  # Clear previous document chat

            # Clear temporary progress indicators after brief moment
            status_text.empty()
            progress_bar.empty()
            st.success(f"Successfully processed **{uploaded_file.name}** into **{len(chunks)} chunks**!")

        except DocumentProcessingError as e:
            st.error(f"⚠️ Document Error: {str(e)}")
            st.stop()
        except Exception as e:
            st.error(f"⚠️ An unexpected error occurred while processing the document: {str(e)}")
            st.stop()

    # Display Metrics Cards
    if st.session_state.doc_summary:
        s = st.session_state.doc_summary
        st.markdown(
            render_metric_cards(
                pages=s.get("num_pages", 1),
                chunks=s.get("total_chunks", 0),
                file_type=s.get("file_type", "DOC"),
                status="FAISS Ready ✓"
            ),
            unsafe_allow_html=True
        )

else:
    # No file uploaded banner
    st.info("👆 Please upload a PDF or DOCX file using the sidebar to begin questioning your document.")
    st.markdown("""
    #### 🚀 How It Works:
    1. **Upload**: Select any PDF or Word document in the left sidebar.
    2. **Process**: DocuMind AI extracts text, preserves page numbers, chunks text, and computes 384-dimensional vector embeddings.
    3. **Search & Ask**: FAISS performs millisecond nearest-neighbor similarity search to pull exact matching contexts.
    4. **Verify**: Every answer is grounded strictly in the document text and accompanied by source cards showing exact page numbers and excerpts.
    """)
    st.stop()


# ==========================================
# CHAT / QUESTION & ANSWER INTERFACE
# ==========================================
st.markdown("### 💬 Ask Questions About Your Document")

# Render Existing Conversation History
for turn_idx, message in enumerate(st.session_state.chat_history):
    with st.chat_message("user"):
        st.write(message["question"])

    with st.chat_message("assistant"):
        st.markdown(f"**Answer:**\n\n{message['answer']}")
        
        # Display Sources / Citations
        sources = message.get("sources", [])
        if sources:
            with st.expander(f"📚 View Cited Sources ({len(sources)} Chunks Retreived)"):
                for src in sources:
                    st.markdown(f"""
                    <div class="source-box">
                        <div class="source-header">
                            <span>📌 <b>Source {src['source_id']}</b> &nbsp;|&nbsp; Page / Location: <b>{src['page']}</b></span>
                            <span style="color: #2563eb;">Relevance: <b>{src['relevance_pct']}%</b></span>
                        </div>
                        <div class="source-excerpt">
                            "{src['excerpt']}"
                        </div>
                        <div style="font-size: 0.75rem; color: #94a3b8; margin-top: 4px;">
                            ID: {src['chunk_str_id']} • File: {src['filename']} • Metric: L2 Distance {src['distance']}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)


# User Question Input
user_query = st.chat_input("Ask a question about your document...")

if user_query:
    if not user_query.strip():
        st.warning("Please type a valid question.")
    elif st.session_state.vector_store is None:
        st.error("Please process a document first before asking questions.")
    else:
        # Display user message
        with st.chat_message("user"):
            st.write(user_query)

        # Retrieve relevant chunks from FAISS
        with st.spinner("🔍 Searching vector store for relevant excerpts..."):
            retrieved_chunks = search_similar_chunks(
                vector_store=st.session_state.vector_store,
                query=user_query,
                top_k=top_k
            )

        # Generate answer via LLM
        with st.spinner("🤖 Generating grounded answer..."):
            active_key = user_api_key.strip() if user_api_key else None
            result = generate_answer(
                query=user_query,
                retrieved_chunks=retrieved_chunks,
                provider=provider_key,
                api_key=active_key,
                model_name=default_model
            )

        # Display assistant answer
        with st.chat_message("assistant"):
            st.markdown(f"**Answer:**\n\n{result['answer']}")

            # Render source citation cards
            sources = result.get("sources", [])
            if sources:
                with st.expander(f"📚 View Cited Sources ({len(sources)} Chunks Retrieved)", expanded=True):
                    for src in sources:
                        st.markdown(f"""
                        <div class="source-box">
                            <div class="source-header">
                                <span>📌 <b>Source {src['source_id']}</b> &nbsp;|&nbsp; Page / Location: <b>{src['page']}</b></span>
                                <span style="color: #2563eb;">Relevance: <b>{src['relevance_pct']}%</b></span>
                            </div>
                            <div class="source-excerpt">
                                "{src['excerpt']}"
                            </div>
                            <div style="font-size: 0.75rem; color: #94a3b8; margin-top: 4px;">
                                ID: {src['chunk_str_id']} • File: {src['filename']} • Metric: L2 Distance {src['distance']}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

        # Record in chat history
        st.session_state.chat_history.append({
            "question": user_query,
            "answer": result["answer"],
            "sources": result.get("sources", []),
            "provider": result.get("provider", "Unknown"),
            "model": result.get("model", "Unknown")
        })


# ==========================================
# FOOTER ACTIONS (CLEAR & EXPORT)
# ==========================================
if st.session_state.chat_history:
    st.markdown("---")
    col1, col2, _ = st.columns([1.5, 2, 4])
    
    with col1:
        if st.button("🗑️ Clear Conversation"):
            st.session_state.chat_history = []
            st.rerun()

    with col2:
        export_text = export_chat_history_to_text(
            st.session_state.chat_history,
            st.session_state.doc_summary.get("filename", "document") if st.session_state.doc_summary else "document"
        )
        st.download_button(
            label="📥 Export Q&A Transcript (.txt)",
            data=export_text,
            file_name=f"documind_qa_{st.session_state.doc_summary.get('filename', 'export')}.txt",
            mime="text/plain"
        )

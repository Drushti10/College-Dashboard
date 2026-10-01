"""
Vector Store Module for DocuMind AI
Manages FAISS (Facebook AI Similarity Search) index creation, embedding storage,
and semantic vector similarity retrieval with relevance scoring.

Educational Note for Viva / Concept Explanation:
FAISS is an open-source library developed by Meta AI for fast nearest-neighbor search
in high-dimensional vector spaces. Instead of comparing text strings with keywords,
FAISS calculates geometric distances (like Euclidean or Cosine distance) between vectors.
When a user asks a question, its vector is compared against all chunk vectors to find
the closest matches in milliseconds.
"""

import os
from typing import List, Tuple, Dict, Any, Optional
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from src.embeddings import SentenceTransformerEmbeddings


def create_vector_store(
    chunks: List[Document],
    embedding_model: SentenceTransformerEmbeddings
) -> FAISS:
    """
    Creates a FAISS vector store from document chunks and computes embeddings.
    
    Args:
        chunks: List of chunked Document objects
        embedding_model: SentenceTransformerEmbeddings instance
        
    Returns:
        FAISS vector store containing indexed chunk embeddings and metadata.
    """
    if not chunks:
        raise ValueError("Cannot create a vector store from an empty chunk list.")

    # FAISS.from_documents generates embeddings for every chunk and builds the index
    vector_store = FAISS.from_documents(
        documents=chunks,
        embedding=embedding_model
    )
    return vector_store


def search_similar_chunks(
    vector_store: FAISS,
    query: str,
    top_k: int = 4
) -> List[Tuple[Document, float, float]]:
    """
    Performs similarity search in the FAISS index to find the most relevant chunks.
    
    Args:
        vector_store: Instantiated FAISS vector store
        query: User question string
        top_k: Number of nearest chunks to retrieve (default: 4)
        
    Returns:
        List of tuples: (Document, raw_distance, relevance_percentage)
    """
    if not query.strip():
        return []

    # similarity_search_with_score returns (Document, L2 distance score)
    results_with_score = vector_store.similarity_search_with_score(query, k=top_k)

    scored_results: List[Tuple[Document, float, float]] = []

    for doc, distance in results_with_score:
        # Convert FAISS distance to an intuitive relevance percentage
        # For normalized embeddings, squared L2 distance ranges between 0 (identical) and 2 (orthogonal) or 4 (opposite)
        # Cosine Similarity = 1 - (L2_distance^2 / 2)
        try:
            cos_sim = 1.0 - (float(distance) ** 2) / 2.0
            relevance_pct = max(0.0, min(100.0, round(cos_sim * 100, 1)))
        except Exception:
            relevance_pct = max(0.0, min(100.0, round((1.0 / (1.0 + float(distance))) * 100, 1)))

        scored_results.append((doc, float(distance), relevance_pct))

    return scored_results


def save_vector_store(vector_store: FAISS, folder_path: str = "faiss_index") -> None:
    """Saves the FAISS index to disk for local persistence."""
    os.makedirs(folder_path, exist_ok=True)
    vector_store.save_local(folder_path)


def load_vector_store(
    folder_path: str,
    embedding_model: SentenceTransformerEmbeddings
) -> Optional[FAISS]:
    """Loads a previously saved FAISS index from disk."""
    if os.path.exists(folder_path):
        return FAISS.load_local(
            folder_path,
            embedding_model,
            allow_dangerous_deserialization=True
        )
    return None

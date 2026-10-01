"""
Embeddings Module for DocuMind AI
Uses sentence-transformers/all-MiniLM-L6-v2 to convert text chunks into numerical vectors.

Educational Note for Viva / Concept Explanation:
Embeddings convert text into numerical vectors (points in high-dimensional space)
so that semantically similar text can be searched mathematically.
Unlike keyword search (which only finds exact matching words), vector embeddings
capture the semantic meaning of sentences, allowing queries like
"What are the benefits?" to match text discussing "key advantages".
"""

from typing import List
from sentence_transformers import SentenceTransformer


class SentenceTransformerEmbeddings:
    """
    LangChain-compatible wrapper around SentenceTransformer.
    Implements embed_documents and embed_query required by FAISS.
    """
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.model_name = model_name
        # Load the sentence-transformer model onto CPU (lightweight & student laptop friendly)
        self.model = SentenceTransformer(model_name, device="cpu")

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Generates numerical embeddings for a list of document chunks.
        
        Args:
            texts: List of chunk text strings
            
        Returns:
            List of 384-dimensional vector embeddings as floating point lists.
        """
        if not texts:
            return []
        embeddings = self.model.encode(
            texts,
            show_progress_bar=False,
            convert_to_numpy=True,
            normalize_embeddings=True  # Normalizing enables exact cosine similarity via dot product
        )
        return embeddings.tolist()

    def embed_query(self, text: str) -> List[float]:
        """
        Generates a numerical embedding for a single user query.
        
        Args:
            text: User's question string
            
        Returns:
            384-dimensional vector embedding as a floating point list.
        """
        embedding = self.model.encode(
            text,
            show_progress_bar=False,
            convert_to_numpy=True,
            normalize_embeddings=True
        )
        return embedding.tolist()


def get_embedding_model(model_name: str = "sentence-transformers/all-MiniLM-L6-v2") -> SentenceTransformerEmbeddings:
    """
    Factory function to retrieve the embedding model instance.
    
    Args:
        model_name: Hugging Face model identifier (default: all-MiniLM-L6-v2)
        
    Returns:
        Configured SentenceTransformerEmbeddings instance.
    """
    return SentenceTransformerEmbeddings(model_name=model_name)

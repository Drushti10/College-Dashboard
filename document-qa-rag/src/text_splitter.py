"""
Text Splitter Module for DocuMind AI
Uses LangChain's RecursiveCharacterTextSplitter to divide document text
into overlapping chunks while preserving original page and document metadata.
"""

from typing import List
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


def split_documents(
    documents: List[Document],
    chunk_size: int = 1000,
    chunk_overlap: int = 200
) -> List[Document]:
    """
    Splits documents into overlapping chunks using RecursiveCharacterTextSplitter.
    
    Why chunking is needed:
    Large documents exceed the context limits of embedding models and LLMs.
    Breaking text into smaller chunks ensures each chunk retains coherent meaning
    and can be retrieved precisely based on semantic similarity.
    
    Why overlap is needed:
    Overlap ensures that context at the boundary between chunks is not lost.
    
    Args:
        documents: List of LangChain Document objects from document_loader
        chunk_size: Target maximum characters per chunk (default: 1000)
        chunk_overlap: Number of characters shared between adjacent chunks (default: 200)
        
    Returns:
        List of chunked Document objects enriched with chunk_id and preserved metadata.
    """
    if not documents:
        return []

    # Configure the recursive text splitter with intuitive separators
    # It tries to split on double newlines (paragraphs), then single newlines (lines),
    # then spaces (words), and finally individual characters.
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", " ", ""]
    )

    split_chunks = text_splitter.split_documents(documents)

    # Enrich metadata for each chunk
    for idx, chunk in enumerate(split_chunks):
        chunk.metadata["chunk_id"] = idx + 1
        chunk.metadata["chunk_str_id"] = f"chunk_{idx + 1}"
        chunk.metadata["chunk_char_count"] = len(chunk.page_content)

    return split_chunks

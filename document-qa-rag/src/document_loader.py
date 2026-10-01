"""
Document Loader Module for DocuMind AI
Extracts text and metadata from PDF and DOCX files.
Preserves page-level metadata for precise source citation.
"""

import io
import os
from typing import List, Tuple, Dict, Any
from langchain_core.documents import Document
from pypdf import PdfReader
import docx


class DocumentProcessingError(Exception):
    """Custom exception raised when document extraction fails."""
    pass


def load_document(file_source: Any, filename: str) -> Tuple[List[Document], Dict[str, Any]]:
    """
    Extracts text and page metadata from a PDF or DOCX file.
    
    Args:
        file_source: A file path (str), Path object, or file-like object (e.g. Streamlit UploadedFile)
        filename: Name of the uploaded file (e.g. 'document.pdf')
        
    Returns:
        Tuple containing:
        - List of LangChain Document objects with page_content and metadata
        - Summary dictionary with document statistics (filename, file_type, num_pages, total_chars)
    """
    ext = os.path.splitext(filename)[1].lower()
    
    if ext not in [".pdf", ".docx"]:
        raise DocumentProcessingError(
            f"Unsupported file format '{ext}'. Please upload a .pdf or .docx document."
        )

    # Convert file_source to BytesIO if it is bytes or already a file-like object
    if isinstance(file_source, bytes):
        file_stream = io.BytesIO(file_source)
    elif hasattr(file_source, "read"):
        # UploadedFile or BytesIO
        content = file_source.read()
        file_stream = io.BytesIO(content)
        # Reset pointer if needed
        if hasattr(file_source, "seek"):
            file_source.seek(0)
    elif isinstance(file_source, str) and os.path.exists(file_source):
        with open(file_source, "rb") as f:
            file_stream = io.BytesIO(f.read())
    else:
        raise DocumentProcessingError("Invalid file source provided.")

    documents: List[Document] = []

    if ext == ".pdf":
        documents = _load_pdf(file_stream, filename)
    elif ext == ".docx":
        documents = _load_docx(file_stream, filename)

    if not documents:
        raise DocumentProcessingError(
            "The document is empty or contains no extractable text. "
            "If this is a scanned image PDF, please use a searchable text document."
        )

    total_chars = sum(len(doc.page_content) for doc in documents)
    total_pages = len(set(doc.metadata.get("page", 1) for doc in documents))

    summary = {
        "filename": filename,
        "file_type": ext[1:].upper(),
        "num_pages": total_pages,
        "total_chars": total_chars,
        "raw_doc_count": len(documents)
    }

    return documents, summary


def _load_pdf(file_stream: io.BytesIO, filename: str) -> List[Document]:
    """Extracts text page-by-page from a PDF, preserving exact 1-indexed page numbers."""
    documents: List[Document] = []
    try:
        reader = PdfReader(file_stream)
        total_pages = len(reader.pages)
        
        if total_pages == 0:
            raise DocumentProcessingError("The PDF document has 0 pages.")

        for page_idx, page in enumerate(reader.pages):
            page_num = page_idx + 1  # 1-indexed for human readability
            extracted_text = page.extract_text() or ""
            cleaned_text = extracted_text.strip()
            
            # Only add if page contains non-empty readable text
            if cleaned_text:
                doc = Document(
                    page_content=cleaned_text,
                    metadata={
                        "source": filename,
                        "page": page_num,
                        "total_pages": total_pages,
                        "file_type": "PDF"
                    }
                )
                documents.append(doc)

    except Exception as e:
        if isinstance(e, DocumentProcessingError):
            raise e
        raise DocumentProcessingError(f"Failed to read PDF document: {str(e)}")

    return documents


def _load_docx(file_stream: io.BytesIO, filename: str) -> List[Document]:
    """Extracts text from a DOCX document preserving paragraph/section context."""
    documents: List[Document] = []
    try:
        doc_obj = docx.Document(file_stream)
        
        # Collect paragraphs
        full_paragraphs = []
        for p in doc_obj.paragraphs:
            text = p.text.strip()
            if text:
                full_paragraphs.append(text)
                
        # Also extract text from any tables in the docx
        for table in doc_obj.tables:
            for row in table.rows:
                row_text = " | ".join(cell.text.strip() for cell in row.cells if cell.text.strip())
                if row_text:
                    full_paragraphs.append(row_text)

        if not full_paragraphs:
            return []

        # Combine paragraphs into logical sections (e.g. 3-5 paragraphs per page unit)
        # so DOCX also gets meaningful section/pseudo-page divisions
        paragraphs_per_section = 5
        total_sections = (len(full_paragraphs) + paragraphs_per_section - 1) // paragraphs_per_section

        for sec_idx in range(total_sections):
            start = sec_idx * paragraphs_per_section
            end = start + paragraphs_per_section
            sec_text = "\n\n".join(full_paragraphs[start:end])
            
            doc = Document(
                page_content=sec_text,
                metadata={
                    "source": filename,
                    "page": f"Section {sec_idx + 1}",
                    "total_pages": total_sections,
                    "file_type": "DOCX"
                }
            )
            documents.append(doc)

    except Exception as e:
        raise DocumentProcessingError(f"Failed to read DOCX document: {str(e)}")

    return documents

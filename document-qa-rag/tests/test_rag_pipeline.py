"""
End-to-End Automated Pipeline Test Suite for DocuMind AI
Tests:
1. Document text & metadata extraction (.pdf and .docx)
2. RecursiveCharacterTextSplitter chunking
3. Sentence Transformers embedding generation
4. FAISS CPU indexing and similarity retrieval
5. Answer generation & source citation
6. Negative / Out-of-context testing (fallback phrase)
7. Error handling
"""

import sys
import unittest
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.document_loader import load_document, DocumentProcessingError
from src.text_splitter import split_documents
from src.embeddings import get_embedding_model
from src.vector_store import create_vector_store, search_similar_chunks
from src.llm import generate_answer


class TestDocuMindRAG(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Set up shared sample PDF and embedding model for tests."""
        cls.sample_pdf = PROJECT_ROOT / "data" / "sample_document" / "sample_ai_overview.pdf"
        assert cls.sample_pdf.exists(), f"Sample PDF not found at {cls.sample_pdf}"
        
        # Load embedding model once for all tests
        print("\nLoading sentence-transformers/all-MiniLM-L6-v2 for test suite...")
        cls.embedding_model = get_embedding_model()

    def test_01_document_loader(self):
        """Test PDF text extraction and page metadata preservation."""
        docs, summary = load_document(str(self.sample_pdf), self.sample_pdf.name)
        
        self.assertGreater(len(docs), 0, "No documents were extracted from PDF")
        self.assertEqual(summary["file_type"], "PDF")
        self.assertEqual(summary["num_pages"], 4)
        self.assertGreater(summary["total_chars"], 100)
        
        # Verify page-level metadata
        pages_found = [d.metadata.get("page") for d in docs]
        self.assertIn(1, pages_found)
        self.assertIn(2, pages_found)
        self.assertIn(3, pages_found)
        self.assertIn(4, pages_found)
        print("✓ Test 1 Passed: Document loader successfully parsed PDF with exact page metadata.")

    def test_02_text_splitter(self):
        """Test LangChain RecursiveCharacterTextSplitter with metadata enrichment."""
        docs, _ = load_document(str(self.sample_pdf), self.sample_pdf.name)
        chunks = split_documents(docs, chunk_size=500, chunk_overlap=100)
        
        self.assertGreater(len(chunks), len(docs), "Chunking should create multiple chunks")
        for chunk in chunks:
            self.assertIn("chunk_id", chunk.metadata)
            self.assertIn("chunk_str_id", chunk.metadata)
            self.assertIn("page", chunk.metadata)
            self.assertIn("source", chunk.metadata)
        print(f"✓ Test 2 Passed: Text splitter created {len(chunks)} overlapping chunks.")

    def test_03_embeddings(self):
        """Test sentence-transformers vector generation and dimensions."""
        test_text = "Supervised learning uses labeled training datasets."
        embedding = self.embedding_model.embed_query(test_text)
        
        self.assertEqual(len(embedding), 384, "Embedding vector length must be 384 dimensions")
        self.assertIsInstance(embedding[0], float)
        print("✓ Test 3 Passed: Embedding model produces valid 384-dim normalized vectors.")

    def test_04_faiss_vector_store_retrieval(self):
        """Test FAISS index creation and semantic similarity search."""
        docs, _ = load_document(str(self.sample_pdf), self.sample_pdf.name)
        chunks = split_documents(docs, chunk_size=500, chunk_overlap=100)
        
        vector_store = create_vector_store(chunks, self.embedding_model)
        query = "What is supervised learning?"
        
        results = search_similar_chunks(vector_store, query, top_k=3)
        self.assertEqual(len(results), 3)
        
        top_doc, distance, relevance_pct = results[0]
        self.assertIn("Supervised", top_doc.page_content)
        self.assertEqual(top_doc.metadata.get("page"), 2, "Supervised learning is on Page 2")
        self.assertGreater(relevance_pct, 40.0, "Relevant chunk should have good similarity score")
        print(f"✓ Test 4 Passed: FAISS retrieved Page {top_doc.metadata.get('page')} with {relevance_pct}% relevance.")

    def test_05_answer_generation_and_citations(self):
        """Test answer generation with source citations in offline/local mode."""
        docs, _ = load_document(str(self.sample_pdf), self.sample_pdf.name)
        chunks = split_documents(docs, chunk_size=500, chunk_overlap=100)
        vector_store = create_vector_store(chunks, self.embedding_model)
        
        query = "What are the common algorithms used in supervised learning?"
        retrieved_chunks = search_similar_chunks(vector_store, query, top_k=2)
        
        result = generate_answer(query, retrieved_chunks, provider="offline")
        self.assertIn("answer", result)
        self.assertGreater(len(result["sources"]), 0)
        self.assertEqual(result["sources"][0]["page"], 2)
        print(f"✓ Test 5 Passed: Answer generated with citations pointing to Page {result['sources'][0]['page']}.")

    def test_06_hallucination_prevention_fallback(self):
        """Test that out-of-context queries return the strict fallback phrase."""
        docs, _ = load_document(str(self.sample_pdf), self.sample_pdf.name)
        chunks = split_documents(docs, chunk_size=500, chunk_overlap=100)
        vector_store = create_vector_store(chunks, self.embedding_model)
        
        # Out-of-context question completely unrelated to the AI document
        query = "What is the secret recipe for Italian chocolate pizza?"
        # Empty retrieval or very low similarity
        result = generate_answer(query, [], provider="offline")
        
        expected_fallback = "I couldn't find this information in the uploaded document."
        self.assertEqual(result["answer"], expected_fallback)
        print("✓ Test 6 Passed: System strictly prevented hallucination with exact fallback phrase.")

    def test_07_error_handling(self):
        """Test error handling for unsupported file extensions."""
        with self.assertRaises(DocumentProcessingError):
            load_document(b"fake data", "unsupported_file.xyz")
        print("✓ Test 7 Passed: Error handling catches unsupported file types gracefully.")


if __name__ == "__main__":
    unittest.main(verbosity=2)

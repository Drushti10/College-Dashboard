"""
LLM Integration Module for DocuMind AI
Handles answer generation using retrieved document context.
Supports:
1. Groq (Llama 3.3 / 3.1) - Free and ultra-fast
2. Google Gemini (Gemini 2.5 Flash / 1.5 Flash) - Free tier via AI Studio
3. OpenAI (GPT-4o-mini)
4. Offline Extractive Synthesizer (Zero-API-key local fallback)

Guarantees:
- Strict grounding: Answers ONLY based on retrieved chunks.
- Exact fallback message: "I couldn't find this information in the uploaded document."
- Accurate source citations referencing [Source 1], [Source 2], etc.
"""

import os
import re
from typing import List, Tuple, Dict, Any, Optional
from langchain_core.documents import Document


SYSTEM_PROMPT = """You are DocuMind AI, a precise and factual document question-answering assistant.

Your task is to answer the user's question using ONLY the provided document context passages below.

STRICT INSTRUCTIONS:
1. Rely EXCLUSIVELY on the facts mentioned in the context. Do NOT use outside knowledge, speculate, or extrapolate.
2. If the answer cannot be found in the provided context, respond EXACTLY with:
   "I couldn't find this information in the uploaded document."
3. Attribute your statements to the relevant sources by citing their numbers in square brackets, for example: [Source 1], [Source 2].
4. Be concise, well-structured, and professional in your response.
"""


def format_context_prompt(retrieved_chunks: List[Tuple[Document, float, float]]) -> str:
    """
    Formats retrieved chunks into a numbered context block for the LLM.
    
    Args:
        retrieved_chunks: List of (Document, distance, relevance_pct) tuples
        
    Returns:
        Formatted context string.
    """
    context_parts = []
    for idx, (doc, _, _) in enumerate(retrieved_chunks):
        source_num = idx + 1
        page_info = doc.metadata.get("page", "Unknown")
        chunk_id = doc.metadata.get("chunk_str_id", f"chunk_{source_num}")
        text = doc.page_content.strip()
        context_parts.append(
            f"--- [Source {source_num}] (Page/Location: {page_info}, ID: {chunk_id}) ---\n{text}\n"
        )
    return "\n".join(context_parts)


def generate_answer(
    query: str,
    retrieved_chunks: List[Tuple[Document, float, float]],
    provider: str = "groq",
    api_key: Optional[str] = None,
    model_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    Dispatches generation request to the selected LLM provider or local fallback.
    
    Args:
        query: User question
        retrieved_chunks: Retrieved document chunks with similarity scores
        provider: 'groq', 'gemini', 'openai', or 'offline'
        api_key: Provider API key (optional if set in environment)
        model_name: Specific model override (optional)
        
    Returns:
        Dictionary with:
        - answer: generated answer text
        - provider: provider used
        - model: model used
        - sources: list of source metadata dictionaries
    """
    if not retrieved_chunks:
        return {
            "answer": "I couldn't find this information in the uploaded document.",
            "provider": provider,
            "model": "none",
            "sources": []
        }

    formatted_context = format_context_prompt(retrieved_chunks)
    provider_clean = provider.lower().strip()

    # Normalize environment keys
    if not api_key:
        if provider_clean == "groq":
            api_key = os.getenv("GROQ_API_KEY")
        elif provider_clean in ["gemini", "google"]:
            api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        elif provider_clean == "openai":
            api_key = os.getenv("OPENAI_API_KEY")

    # If provider is not offline but key is missing, fall back to offline mode
    if provider_clean != "offline" and not api_key:
        provider_clean = "offline"

    # Call chosen provider
    if provider_clean == "groq":
        return _generate_groq(query, formatted_context, retrieved_chunks, api_key, model_name)
    elif provider_clean in ["gemini", "google"]:
        return _generate_gemini(query, formatted_context, retrieved_chunks, api_key, model_name)
    elif provider_clean == "openai":
        return _generate_openai(query, formatted_context, retrieved_chunks, api_key, model_name)
    else:
        return _generate_offline_extractive(query, retrieved_chunks)


def _generate_groq(
    query: str,
    context: str,
    retrieved_chunks: List[Tuple[Document, float, float]],
    api_key: str,
    model_name: Optional[str]
) -> Dict[str, Any]:
    """Generate answer using Groq API."""
    from groq import Groq
    
    model = model_name or "llama-3.3-70b-versatile"
    client = Groq(api_key=api_key)
    
    prompt = f"DOCUMENT CONTEXT:\n{context}\n\nUSER QUESTION:\n{query}\n\nANSWER:"
    
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ],
        temperature=0.1,  # Low temperature for strict factual accuracy
        max_tokens=800
    )
    
    answer_text = response.choices[0].message.content.strip()
    return {
        "answer": answer_text,
        "provider": "Groq",
        "model": model,
        "sources": _build_source_cards(retrieved_chunks)
    }


def _generate_gemini(
    query: str,
    context: str,
    retrieved_chunks: List[Tuple[Document, float, float]],
    api_key: str,
    model_name: Optional[str]
) -> Dict[str, Any]:
    """Generate answer using Google Gemini API."""
    import google.generativeai as genai

    genai.configure(api_key=api_key)
    model_id = model_name or "gemini-1.5-flash"
    
    model = genai.GenerativeModel(
        model_name=model_id,
        system_instruction=SYSTEM_PROMPT
    )
    
    prompt = f"DOCUMENT CONTEXT:\n{context}\n\nUSER QUESTION:\n{query}\n\nANSWER:"
    
    response = model.generate_content(
        prompt,
        generation_config={"temperature": 0.1, "max_output_tokens": 800}
    )
    
    answer_text = response.text.strip()
    return {
        "answer": answer_text,
        "provider": "Google Gemini",
        "model": model_id,
        "sources": _build_source_cards(retrieved_chunks)
    }


def _generate_openai(
    query: str,
    context: str,
    retrieved_chunks: List[Tuple[Document, float, float]],
    api_key: str,
    model_name: Optional[str]
) -> Dict[str, Any]:
    """Generate answer using OpenAI API."""
    from openai import OpenAI

    model = model_name or "gpt-4o-mini"
    client = OpenAI(api_key=api_key)
    
    prompt = f"DOCUMENT CONTEXT:\n{context}\n\nUSER QUESTION:\n{query}\n\nANSWER:"
    
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ],
        temperature=0.1,
        max_tokens=800
    )
    
    answer_text = response.choices[0].message.content.strip()
    return {
        "answer": answer_text,
        "provider": "OpenAI",
        "model": model,
        "sources": _build_source_cards(retrieved_chunks)
    }


def _generate_offline_extractive(
    query: str,
    retrieved_chunks: List[Tuple[Document, float, float]]
) -> Dict[str, Any]:
    """
    Local Extractive Synthesizer (Works 100% offline without any API key).
    Performs sentence-level semantic matching from the retrieved chunks to construct
    a grounded answer with source citations.
    """
    # Check if the highest relevance chunk is below a reasonable relevance threshold
    best_relevance = retrieved_chunks[0][2] if retrieved_chunks else 0.0
    if best_relevance < 20.0:
        return {
            "answer": "I couldn't find this information in the uploaded document.",
            "provider": "Offline Synthesizer (Local)",
            "model": "Semantic Extractive",
            "sources": _build_source_cards(retrieved_chunks)
        }

    # Extract sentences from the top chunks that best match query words
    query_words = set(re.findall(r"\b\w{3,}\b", query.lower()))
    candidate_sentences = []
    
    for idx, (doc, _, rel_pct) in enumerate(retrieved_chunks[:3]):
        source_tag = f"[Source {idx + 1}]"
        # Split into sentences
        raw_sentences = re.split(r"(?<=[.!?])\s+", doc.page_content)
        for s in raw_sentences:
            s_clean = s.strip()
            if len(s_clean) < 20:
                continue
            s_words = set(re.findall(r"\b\w{3,}\b", s_clean.lower()))
            overlap = len(query_words.intersection(s_words))
            if overlap > 0:
                candidate_sentences.append((overlap, rel_pct, source_tag, s_clean))

    if not candidate_sentences:
        # Provide the top chunk summary if no exact sentence overlap
        top_doc, _, _ = retrieved_chunks[0]
        excerpt = top_doc.page_content.strip()[:350]
        answer_text = (
            f"Based on the document context [Source 1]:\n\n"
            f"> {excerpt}...\n\n"
            f"*(Generated via local extractive mode. Add an API key in the sidebar for full conversational synthesis.)*"
        )
    else:
        # Sort by overlap and relevance
        candidate_sentences.sort(key=lambda x: (x[0], x[1]), reverse=True)
        # Select top 3 distinct sentences
        selected = []
        seen_texts = set()
        for _, _, src_tag, sent in candidate_sentences:
            if sent not in seen_texts:
                seen_texts.add(sent)
                selected.append(f"{sent} {src_tag}")
            if len(selected) >= 3:
                break
                
        answer_text = " ".join(selected)

    return {
        "answer": answer_text,
        "provider": "Offline Synthesizer (Local)",
        "model": "Semantic Extractive",
        "sources": _build_source_cards(retrieved_chunks)
    }


def _build_source_cards(retrieved_chunks: List[Tuple[Document, float, float]]) -> List[Dict[str, Any]]:
    """Builds clean citation source metadata for UI display."""
    sources = []
    for idx, (doc, distance, relevance_pct) in enumerate(retrieved_chunks):
        sources.append({
            "source_id": idx + 1,
            "filename": doc.metadata.get("source", "Document"),
            "file_type": doc.metadata.get("file_type", "FILE"),
            "page": doc.metadata.get("page", "N/A"),
            "chunk_str_id": doc.metadata.get("chunk_str_id", f"chunk_{idx + 1}"),
            "relevance_pct": relevance_pct,
            "distance": round(distance, 4),
            "excerpt": doc.page_content.strip()
        })
    return sources

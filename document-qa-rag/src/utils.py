"""
Utility Functions and Styling for DocuMind AI
Provides custom CSS styling, citation formatters, metric renderers,
and session export tools.
"""

from typing import List, Dict, Any
from datetime import datetime


def get_custom_css() -> str:
    """
    Returns custom modern CSS to give Streamlit a sleek, professional UI
    with card elevation, clean typography, badge pills, and responsive layout.
    """
    return """
    <style>
    /* Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Main Container Padding */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 3rem !important;
        max-width: 1080px;
    }

    /* Hero Header */
    .hero-container {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border-radius: 16px;
        padding: 28px 32px;
        margin-bottom: 24px;
        color: #ffffff;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    .hero-title {
        font-size: 2rem;
        font-weight: 700;
        margin: 0;
        letter-spacing: -0.02em;
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .hero-badge {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
        color: white;
        font-size: 0.75rem;
        padding: 4px 10px;
        border-radius: 9999px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .hero-subtitle {
        font-size: 1rem;
        color: #94a3b8;
        margin-top: 8px;
        margin-bottom: 0;
    }

    /* Metric Grid */
    .metric-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 14px;
        margin: 20px 0 28px 0;
    }
    @media (max-width: 768px) {
        .metric-grid {
            grid-template-columns: repeat(2, 1fr);
        }
    }
    .metric-card {
        background: #ffffff;
        border-radius: 12px;
        padding: 16px 20px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05);
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px -2px rgba(0, 0, 0, 0.08);
    }
    .metric-val {
        font-size: 1.5rem;
        font-weight: 700;
        color: #0f172a;
        line-height: 1.2;
    }
    .metric-lbl {
        font-size: 0.8rem;
        font-weight: 500;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        margin-top: 4px;
    }

    /* Status Indicator Pills */
    .status-pill {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    .status-success {
        background: #ecfdf5;
        color: #059669;
        border: 1px solid #a7f3d0;
    }
    .status-info {
        background: #eff6ff;
        color: #2563eb;
        border: 1px solid #bfdbfe;
    }

    /* Source Citation Card */
    .source-box {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 14px 18px;
        margin-top: 10px;
        margin-bottom: 12px;
    }
    .source-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 8px;
        font-size: 0.85rem;
        font-weight: 600;
        color: #334155;
    }
    .source-excerpt {
        font-size: 0.9rem;
        color: #475569;
        line-height: 1.5;
        border-left: 3px solid #3b82f6;
        padding-left: 12px;
        margin: 6px 0;
        background: #ffffff;
        padding: 8px 12px;
        border-radius: 0 6px 6px 0;
        font-style: italic;
    }

    /* Answers */
    .answer-card {
        background: #ffffff;
        border-radius: 12px;
        padding: 20px 24px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        margin-bottom: 18px;
    }

    /* Sidebar tweaks */
    .css-1d391kg {
        padding-top: 2rem;
    }
    </style>
    """


def render_metric_cards(
    pages: int or str,
    chunks: int,
    file_type: str,
    status: str = "Ready ✓"
) -> str:
    """Generates HTML for 4 responsive metric summary cards."""
    return f"""
    <div class="metric-grid">
        <div class="metric-card">
            <div class="metric-val">{pages}</div>
            <div class="metric-lbl">Pages / Sections</div>
        </div>
        <div class="metric-card">
            <div class="metric-val">{chunks}</div>
            <div class="metric-lbl">Chunks Created</div>
        </div>
        <div class="metric-card">
            <div class="metric-val">{file_type}</div>
            <div class="metric-lbl">Document Type</div>
        </div>
        <div class="metric-card">
            <div class="metric-val" style="color: #059669;">{status}</div>
            <div class="metric-lbl">FAISS Vector Store</div>
        </div>
    </div>
    """


def export_chat_history_to_text(chat_history: List[Dict[str, Any]], filename: str) -> str:
    """
    Exports conversation history into a clean, readable text report.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines = [
        "=" * 70,
        f"DOCUMIND AI - DOCUMENT Q&A EXPORT",
        f"Document: {filename}",
        f"Generated At: {timestamp}",
        "=" * 70,
        ""
    ]

    for idx, turn in enumerate(chat_history):
        q_num = idx + 1
        lines.append(f"QUESTION {q_num}:")
        lines.append(f"{turn.get('question', '')}\n")
        lines.append(f"ANSWER {q_num}:")
        lines.append(f"{turn.get('answer', '')}\n")
        
        sources = turn.get("sources", [])
        if sources:
            lines.append("SOURCES CITED:")
            for s in sources:
                lines.append(
                    f"  [{s.get('source_id')}] Page: {s.get('page')} | ID: {s.get('chunk_str_id')} | Relevance: {s.get('relevance_pct')}%"
                )
                excerpt = s.get('excerpt', '').replace('\n', ' ')
                lines.append(f"      Excerpt: \"{excerpt[:200]}...\"")
        lines.append("-" * 70)
        lines.append("")

    return "\n".join(lines)

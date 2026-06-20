"""
app.py — ContribAgent
Run: streamlit run app.py
"""

import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
from dotenv import load_dotenv
load_dotenv()

DEBUG_MODE = os.getenv("DEBUG_MODE", "False").lower() in ("true", "1", "yes")

st.set_page_config(
    page_title="ContribAgent",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── suppress torchvision noise ──────────────────────────────────────────────
import logging
logging.getLogger("streamlit.watcher").setLevel(logging.CRITICAL)

# ─────────────────────────────────────────────────────────────────────────────
#  CSS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:ital,wght@0,300;0,400;0,500;0,600;0,700;0,800;1,400&display=swap');

/* ── reset ── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
html, body, [class*="css"], .stApp {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    background: #0a0a0f !important;
    color: #e8e8f0 !important;
}
#MainMenu, footer, header, .stDeployButton { display: none !important; }
.block-container { padding: 0 !important; max-width: 100% !important; }
section[data-testid="stSidebar"] { display: none !important; }

/* ── page shell ── */
.page {
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    background: #0a0a0f;
}

/* ── top nav ── */
.topnav {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 18px 48px;
    border-bottom: 1px solid rgba(255,255,255,0.06);
    background: rgba(10,10,15,0.95);
    backdrop-filter: blur(20px);
    position: sticky;
    top: 0;
    z-index: 100;
}
.nav-logo {
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 16px;
    font-weight: 700;
    color: #fff;
    letter-spacing: -0.02em;
}
.nav-logo-mark {
    width: 28px;
    height: 28px;
    background: linear-gradient(135deg, #6366f1, #8b5cf6);
    border-radius: 7px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 14px;
}
.nav-badge {
    font-size: 11px;
    font-weight: 600;
    color: #6366f1;
    background: rgba(99,102,241,0.12);
    border: 1px solid rgba(99,102,241,0.25);
    border-radius: 100px;
    padding: 3px 10px;
    letter-spacing: 0.04em;
}
.nav-pills {
    display: flex;
    gap: 6px;
}
.nav-pill {
    font-size: 12px;
    color: #6b7280;
    padding: 5px 12px;
    border-radius: 100px;
    font-weight: 500;
    border: 1px solid rgba(255,255,255,0.08);
}

/* ── hero ── */
.hero {
    padding: 80px 48px 64px;
    position: relative;
    overflow: hidden;
    text-align: center;
}
.hero-bg {
    position: absolute;
    inset: 0;
    background:
        radial-gradient(ellipse 60% 50% at 50% 0%, rgba(99,102,241,0.15) 0%, transparent 70%),
        radial-gradient(ellipse 40% 30% at 20% 60%, rgba(139,92,246,0.08) 0%, transparent 60%),
        radial-gradient(ellipse 40% 30% at 80% 60%, rgba(59,130,246,0.08) 0%, transparent 60%);
    pointer-events: none;
}
.hero-eyebrow {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #6366f1;
    background: rgba(99,102,241,0.1);
    border: 1px solid rgba(99,102,241,0.2);
    border-radius: 100px;
    padding: 5px 14px;
    margin-bottom: 28px;
}
.hero-title {
    font-size: clamp(36px, 5vw, 64px);
    font-weight: 800;
    color: #fff;
    line-height: 1.05;
    letter-spacing: -0.04em;
    margin-bottom: 20px;
}
.hero-title .g {
    background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #3b82f6 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.hero-sub {
    font-size: 17px;
    color: #9ca3af;
    max-width: 560px;
    line-height: 1.65;
    margin: 0 auto 40px;
    font-weight: 400;
}
.hero-stats {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 32px;
    margin-top: 8px;
}
.stat {
    text-align: center;
}
.stat-num {
    font-size: 22px;
    font-weight: 700;
    color: #fff;
    letter-spacing: -0.03em;
}
.stat-label {
    font-size: 11px;
    color: #6b7280;
    font-weight: 500;
    margin-top: 2px;
}
.stat-div {
    width: 1px;
    height: 32px;
    background: rgba(255,255,255,0.08);
}

/* ── main layout ── */
.workspace {
    display: grid;
    grid-template-columns: 380px 1fr;
    gap: 0;
    padding: 0 48px 48px;
    align-items: start;
    max-width: 1400px;
    margin: 0 auto;
    width: 100%;
}

/* ── sidebar panel ── */
.sidebar-panel {
    padding: 24px 24px 24px 0;
    position: sticky;
    top: 72px;
}
.panel-section {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 16px;
    overflow: hidden;
    margin-bottom: 12px;
}
.panel-header {
    padding: 14px 18px;
    border-bottom: 1px solid rgba(255,255,255,0.06);
    display: flex;
    align-items: center;
    gap: 8px;
}
.panel-header-icon {
    font-size: 14px;
}
.panel-header-label {
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #6b7280;
}
.panel-body {
    padding: 16px 18px;
}

/* ── textarea override ── */
.stTextArea > div > div {
    background: transparent !important;
}
.stTextArea textarea {
    background: rgba(255,255,255,0.04) !important;
    border: 1.5px solid rgba(255,255,255,0.1) !important;
    border-radius: 12px !important;
    color: #e8e8f0 !important;
    font-size: 14px !important;
    font-family: 'Inter', sans-serif !important;
    line-height: 1.6 !important;
    padding: 13px 15px !important;
    resize: none !important;
    transition: border-color 0.2s, box-shadow 0.2s !important;
    caret-color: #6366f1 !important;
}
.stTextArea textarea:focus {
    border-color: rgba(99,102,241,0.6) !important;
    box-shadow: 0 0 0 3px rgba(99,102,241,0.12) !important;
    outline: none !important;
}
.stTextArea textarea::placeholder { color: #4b5563 !important; }
.stTextArea label { display: none !important; }

/* ── buttons ── */
div[data-testid="stButton"] > button {
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    border-radius: 11px !important;
    transition: all 0.15s ease !important;
    width: 100% !important;
    cursor: pointer !important;
    font-size: 14px !important;
}

/* primary run button */
div[data-testid="stButton"]:first-of-type > button {
    background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%) !important;
    color: #fff !important;
    border: none !important;
    padding: 13px 20px !important;
    box-shadow: 0 4px 20px rgba(99,102,241,0.35), inset 0 1px 0 rgba(255,255,255,0.15) !important;
    letter-spacing: -0.01em !important;
}
div[data-testid="stButton"]:first-of-type > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 28px rgba(99,102,241,0.45), inset 0 1px 0 rgba(255,255,255,0.15) !important;
}
div[data-testid="stButton"]:first-of-type > button:active {
    transform: translateY(0) !important;
}

/* secondary clear button */
div[data-testid="stButton"]:nth-of-type(2) > button {
    background: transparent !important;
    color: #6b7280 !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    padding: 11px 20px !important;
}
div[data-testid="stButton"]:nth-of-type(2) > button:hover {
    border-color: rgba(255,255,255,0.2) !important;
    color: #9ca3af !important;
}

/* example buttons */
div[data-testid="stButton"]:nth-of-type(n+3) > button {
    background: rgba(255,255,255,0.03) !important;
    color: #9ca3af !important;
    border: 1px solid rgba(255,255,255,0.07) !important;
    padding: 9px 14px !important;
    font-size: 12px !important;
    font-weight: 500 !important;
    border-radius: 9px !important;
    text-align: left !important;
    justify-content: flex-start !important;
}
div[data-testid="stButton"]:nth-of-type(n+3) > button:hover {
    background: rgba(255,255,255,0.06) !important;
    border-color: rgba(99,102,241,0.3) !important;
    color: #e8e8f0 !important;
}

/* ── output panel ── */
.output-panel {
    padding: 24px 0 24px 24px;
}
.output-card {
    background: rgba(255,255,255,0.02);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 20px;
    overflow: hidden;
    min-height: 520px;
}
.output-topbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 14px 20px;
    border-bottom: 1px solid rgba(255,255,255,0.06);
    background: rgba(255,255,255,0.02);
}
.topbar-left {
    display: flex;
    align-items: center;
    gap: 10px;
}
.status-dot {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: #34d399;
    box-shadow: 0 0 6px rgba(52,211,153,0.6);
    animation: breathe 2.5s ease infinite;
}
.status-dot.idle {
    background: #374151;
    box-shadow: none;
    animation: none;
}
.status-dot.running {
    background: #f59e0b;
    box-shadow: 0 0 8px rgba(245,158,11,0.6);
    animation: breathe 1s ease infinite;
}
@keyframes breathe {
    0%,100% { opacity:1; transform: scale(1); }
    50%      { opacity:0.6; transform: scale(0.8); }
}
.topbar-label {
    font-size: 12px;
    font-weight: 600;
    color: #6b7280;
    letter-spacing: 0.05em;
    text-transform: uppercase;
}
.topbar-model {
    font-size: 11px;
    color: #374151;
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 100px;
    padding: 3px 10px;
    font-weight: 500;
}

/* ── empty state ── */
.empty-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 420px;
    text-align: center;
    padding: 40px;
}
.empty-glyph {
    font-size: 52px;
    margin-bottom: 20px;
    filter: grayscale(0.3);
}
.empty-h {
    font-size: 18px;
    font-weight: 700;
    color: #e8e8f0;
    margin-bottom: 8px;
    letter-spacing: -0.02em;
}
.empty-p {
    font-size: 13px;
    color: #4b5563;
    line-height: 1.6;
    max-width: 280px;
}
.empty-flow {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-top: 28px;
    flex-wrap: wrap;
    justify-content: center;
}
.flow-step {
    display: flex;
    align-items: center;
    gap: 5px;
    font-size: 11px;
    color: #4b5563;
    font-weight: 500;
}
.flow-icon {
    width: 22px;
    height: 22px;
    border-radius: 6px;
    background: rgba(255,255,255,0.05);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 11px;
}
.flow-arrow { color: #1f2937; font-size: 10px; }

/* ── running state ── */
.running-wrap {
    padding: 40px;
    min-height: 420px;
    display: flex;
    flex-direction: column;
    justify-content: center;
}
.running-header {
    display: flex;
    align-items: center;
    gap: 16px;
    margin-bottom: 32px;
}
.report-box {
    background: rgba(255,255,255,0.02);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 14px;
    padding: 24px;
    max-height: 700px;
    overflow-y: auto;
}
.spin-ring {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    border: 2.5px solid rgba(255,255,255,0.08);
    border-top-color: #6366f1;
    animation: spin 0.7s linear infinite;
    flex-shrink: 0;
}
[data-testid="stTextArea"] textarea {
    color: white !important;
    -webkit-text-fill-color: white !important;
    background: #111827 !important;
    opacity: 1 !important;
}
@keyframes spin { to { transform: rotate(360deg); } }
.running-title {
    font-size: 16px;
    font-weight: 600;
    color: #e8e8f0;
}
.running-sub {
    font-size: 13px;
    color: #4b5563;
    margin-top: 3px;
}
.step-list {
    display: flex;
    flex-direction: column;
    gap: 6px;
}
.step-item {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 10px 14px;
    border-radius: 10px;
    font-size: 13px;
    transition: all 0.3s ease;
}
.step-item.done {
    background: rgba(52,211,153,0.06);
    color: #34d399;
}
.step-item.active {
    background: rgba(99,102,241,0.1);
    color: #a5b4fc;
    border: 1px solid rgba(99,102,241,0.2);
}
.step-item.pending {
    color: #374151;
}
.step-check { font-size: 14px; }

/* ── result ── */
.result-wrap {
    padding: 28px 32px;
}

/* meta bar */
.meta-bar {
    display: grid;
    grid-template-columns: 1fr 1fr 1fr 1fr;
    gap: 1px;
    background: rgba(255,255,255,0.06);
    border-radius: 12px;
    overflow: hidden;
    margin-bottom: 28px;
}
.meta-cell {
    background: rgba(255,255,255,0.02);
    padding: 12px 16px;
}
.meta-icon { font-size: 16px; margin-bottom: 4px; }
.meta-label {
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #374151;
    margin-bottom: 3px;
}
.meta-value {
    font-size: 12px;
    font-weight: 600;
    color: #9ca3af;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}
.meta-value.accent { color: #818cf8; }

/* markdown styling */
.result-md { }
.result-md h1 {
    font-size: 22px; font-weight: 800; color: #f9fafb;
    letter-spacing: -0.03em; margin: 0 0 20px; line-height: 1.2;
}
.result-md h2 {
    font-size: 15px; font-weight: 700; color: #9ca3af;
    letter-spacing: 0.06em; text-transform: uppercase;
    margin: 32px 0 12px; padding-bottom: 8px;
    border-bottom: 1px solid rgba(255,255,255,0.06);
}
.result-md h3 {
    font-size: 14px; font-weight: 600; color: #e8e8f0;
    margin: 20px 0 8px;
}
.result-md p {
    font-size: 14px; color: #9ca3af; line-height: 1.75;
    margin: 0 0 14px;
}
.result-md ul, .result-md ol {
    padding-left: 18px; margin: 0 0 14px; color: #9ca3af;
}
.result-md li {
    font-size: 14px; line-height: 1.7; margin: 5px 0;
}
.result-md strong { color: #e8e8f0; font-weight: 600; }
.result-md code {
    background: rgba(99,102,241,0.12);
    border: 1px solid rgba(99,102,241,0.2);
    border-radius: 5px;
    padding: 2px 7px;
    font-size: 12.5px;
    font-family: 'JetBrains Mono', 'Fira Code', monospace;
    color: #a5b4fc;
}
.result-md pre {
    background: #0f0f17;
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 12px;
    padding: 18px 20px;
    overflow-x: auto;
    margin: 14px 0;
}
.result-md pre code {
    background: none; border: none; padding: 0;
    color: #c4b5fd; font-size: 13px;
}
.result-md blockquote {
    border-left: 3px solid #6366f1;
    margin: 14px 0;
    padding: 10px 16px;
    background: rgba(99,102,241,0.06);
    border-radius: 0 8px 8px 0;
    color: #9ca3af; font-style: italic;
}
.result-md a { color: #818cf8; text-decoration: none; }
.result-md a:hover { text-decoration: underline; }

/* ── streamlit markdown override ── */
.stMarkdown p    { font-size:14px!important; color:#9ca3af!important; line-height:1.75!important; }
.stMarkdown li   { font-size:14px!important; color:#9ca3af!important; line-height:1.7!important; }
.stMarkdown h1   { font-size:22px!important; font-weight:800!important; color:#f9fafb!important; letter-spacing:-0.03em!important; }
.stMarkdown h2   { font-size:13px!important; font-weight:700!important; color:#6b7280!important; letter-spacing:0.08em!important; text-transform:uppercase!important; }
.stMarkdown h3   { font-size:14px!important; font-weight:600!important; color:#e8e8f0!important; }
.stMarkdown strong { color:#e8e8f0!important; }
.stMarkdown code { background:rgba(99,102,241,0.12)!important; border:1px solid rgba(99,102,241,0.2)!important; border-radius:5px!important; padding:2px 7px!important; color:#a5b4fc!important; font-size:12.5px!important; }
.stMarkdown pre  { background:#0f0f17!important; border:1px solid rgba(255,255,255,0.07)!important; border-radius:12px!important; padding:18px 20px!important; }
.stMarkdown pre code { background:none!important; border:none!important; color:#c4b5fd!important; }
.stMarkdown a    { color:#818cf8!important; }

/* ── error ── */
.err-box {
    margin: 28px 32px;
    background: rgba(239,68,68,0.08);
    border: 1px solid rgba(239,68,68,0.2);
    border-radius: 12px;
    padding: 16px 20px;
    display: flex;
    gap: 12px;
    align-items: flex-start;
}
.err-icon { font-size: 18px; flex-shrink: 0; }
.err-title { font-size:14px; font-weight:600; color:#fca5a5; margin-bottom:4px; }
.err-body  { font-size:13px; color:#9ca3af; line-height:1.55; }

/* ── footer ── */
.app-footer {
    text-align: center;
    padding: 20px 48px;
    border-top: 1px solid rgba(255,255,255,0.04);
    font-size: 11px;
    color: #1f2937;
    letter-spacing: 0.04em;
}

/* ── scrollbar ── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.08); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: rgba(255,255,255,0.14); }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
#  Constants
# ─────────────────────────────────────────────────────────────────────────────
EXAMPLES = [
    "Find a beginner-friendly Python data-science repo and suggest a good first issue",
    "Help me contribute to a JavaScript testing library — find an open bug to fix",
    "Find a FastAPI repo with documentation issues and create a contribution plan",
    "Find an open-source ML repo needing help with dependency management",
]

STEPS = [
    ("🔍", "Searching GitHub repositories"),
    ("📦", "Fetching repository details"),
    ("🐛", "Reading open issues"),
    ("💾", "Cloning & indexing codebase into Qdrant"),
    ("🧠", "Running semantic retrieval"),
    ("🔗", "Mapping dependencies"),
    ("✅", "Verifying contribution plan"),
    ("📝", "Writing final recommendation"),
]

# ─────────────────────────────────────────────────────────────────────────────
#  Session state
# ─────────────────────────────────────────────────────────────────────────────
for k, v in [
    ("result", None),
    ("running", False),
    ("goal", ""),
    ("error", None),
    ("step", 0),
]:
    if k not in st.session_state:
        st.session_state[k] = v

# ─────────────────────────────────────────────────────────────────────────────
#  Helpers
# ─────────────────────────────────────────────────────────────────────────────
import json

def get_value(data, key, default="—"):
    if data is None:
        return default
    if isinstance(data, dict):
        return data.get(key, default)
    # Check if Pydantic model
    if hasattr(data, "model_dump"):
        return data.model_dump().get(key, default)
    return getattr(data, key, default)


from typing import Any

def to_display_text(value: Any) -> str:
    """
    Convert arbitrary agent output into safe displayable text.
    Never return Python dict/list object representations.
    """

    if value is None:
        return ""

    if isinstance(value, str):
        return value

    if hasattr(value, "model_dump"):
        value = value.model_dump()

    if isinstance(value, dict):
        for preferred_key in (
            "final_answer",
            "content",
            "answer",
            "report",
            "message",
            "text",
        ):
            candidate = value.get(preferred_key)
            if isinstance(candidate, str):
                return candidate

        return "```json\n" + json.dumps(
            value,
            indent=2,
            default=str
        ) + "\n```"

    if isinstance(value, list):
        if not value:
            return ""

        if all(isinstance(item, str) for item in value):
            return "\n\n".join(value)

        return "```json\n" + json.dumps(
            [
                item.model_dump()
                if hasattr(item, "model_dump")
                else item
                for item in value
            ],
            indent=2,
            default=str
        ) + "\n```"

    return str(value)


def render_final_answer(final_answer):
    return to_display_text(final_answer)


def ensure_blank_lines_around_tables(text: str) -> str:
    if not text:
        return text
    lines = text.split("\n")
    new_lines = []
    in_table = False
    for line in lines:
        stripped = line.strip()
        is_table_row = stripped.startswith("|") and stripped.endswith("|") and len(stripped) > 1
        if is_table_row:
            if not in_table:
                if new_lines and new_lines[-1].strip() != "":
                    new_lines.append("")
                in_table = True
            new_lines.append(line)
        else:
            if in_table:
                if stripped != "":
                    new_lines.append("")
                in_table = False
            new_lines.append(line)
    if in_table:
        new_lines.append("")
        new_lines.append("")
    return "\n".join(new_lines)


def format_evidence_table(evidence_items: list[dict]) -> str:
    if not evidence_items:
        return "\n\n_No verified evidence collected._\n\n"

    rows = [
        "| Badge | File | Verified fact |",
        "|---|---|---|",
    ]

    seen = set()

    for item in evidence_items:
        if hasattr(item, "model_dump"):
            item = item.model_dump()

        path = item.get("path", "") or item.get("source_path", "")
        if not path or path in seen:
            continue

        seen.add(path)

        badge = item.get("badge")
        if not badge:
            source_type = item.get("source_type", "")
            if source_type == "github_file":
                badge = "[CODE READ]"
            elif source_type == "github_repository":
                badge = "[REPO]"
            elif source_type == "github_issue":
                badge = "[ISSUE]"
            else:
                badge = "[FILE]"
        fact = item.get("verified_fact") or item.get("claim") or "Evidence retrieved"
        url = item.get("github_url") or item.get("source_url", "")

        file_display = f"[{path}]({url})" if url else f"`{path}`"

        rows.append(
            f"| {badge} | {file_display} | {fact} |"
        )

    return "\n\n" + "\n".join(rows) + "\n\n"


def format_dependency_edges(edges: list[dict]) -> str:
    if not edges:
        return (
            "_No verified dependency edges were found. "
            "Candidate files may exist, but no direct import or symbol "
            "relationship has been proven._"
        )

    lines = []

    for edge in edges:
        if hasattr(edge, "model_dump"):
            edge = edge.model_dump()

        source = edge.get("from_file", "Unknown")
        target = edge.get("to_file", "Unknown")
        symbol = edge.get("symbol")
        symbols = edge.get("symbols") or ([symbol] if symbol else [])
        relationship = edge.get("relationship", "reference")
        evidence = edge.get("evidence", "")

        symbols_str = ", ".join([f"`{s}`" for s in symbols if s]) if symbols else "`Unknown`"
        line = (
            f"- `{source}` → `{target}` "
            f"({relationship}: {symbols_str})"
        )

        if evidence:
            line += f"\n  - Evidence: `{evidence}`"

        lines.append(line)

    return "\n".join(lines)


def format_plan_steps(plan: Any) -> str:
    if not plan:
        return "_No implementation plan generated._"

    if hasattr(plan, "model_dump"):
        plan = plan.model_dump()

    if isinstance(plan, str):
        return plan

    if isinstance(plan, list):
        lines = []

        for index, step in enumerate(plan, start=1):
            if hasattr(step, "model_dump"):
                step = step.model_dump()

            if isinstance(step, dict):
                text = (
                    step.get("description")
                    or step.get("step")
                    or step.get("text")
                    or json.dumps(step, default=str)
                )
            else:
                text = str(step)

            lines.append(f"{index}. {text}")

        return "\n".join(lines)

    return to_display_text(plan)


def build_final_markdown(result: dict) -> str:
    final_answer = result.get("final_answer")

    # If final_answer is already a clean Markdown string, use it.
    if isinstance(final_answer, str) and final_answer.strip():
        return ensure_blank_lines_around_tables(final_answer)

    # Fall back if no final answer was generated at all
    if not final_answer or not str(final_answer).strip():
        thoughts = result.get("thoughts", [])
        obs = result.get("observations", [])
        if thoughts or obs:
            fallback = "**Agent completed — no final answer generated.**\n\n"
            if thoughts:
                fallback += f"**Last thought:** {to_display_text(thoughts[-1])}\n\n"
            if obs:
                fallback += f"**Last observation:** {to_display_text(obs[-1])}"
            return fallback

    evidence = format_evidence_table(
        result.get("evidence", [])
    )

    dependencies = format_dependency_edges(
        result.get("dependency_edges", [])
    )

    plan = format_plan_steps(
        result.get("contribution_plan", [])
    )

    confidence = result.get("confidence", 0.0)

    rendered = f"""
# Final Contribution Recommendation

## Evidence Collected

{evidence}

## Dependency Trace

{dependencies}

## Contribution Plan

{plan}

## Confidence

{confidence}
""".strip()
    return ensure_blank_lines_around_tables(rendered)


def run_agent(goal: str):
    """
    Creates one initial memory/state object and starts one autonomous agent.

    The SupervisorAgent itself decides:
    think → choose tool → execute tool → observe → collect evidence → think again.
    """

    from agents.supervisor import SupervisorAgent
    from models.initial_state import create_initial_state

    initial_state = create_initial_state(goal.strip())

    agent = SupervisorAgent()

    return agent.run(initial_state)


def meta_bar(repo, issue, lang, iters):
    repo_s  = (repo  or "—")[:28]
    issue_s = (issue or "—")[:28]
    lang_s  = (lang  or "—")[:14]
    return f"""
    <div class="meta-bar">
        <div class="meta-cell">
            <div class="meta-icon">📦</div>
            <div class="meta-label">Repository</div>
            <div class="meta-value accent" title="{repo}">{repo_s}</div>
        </div>
        <div class="meta-cell">
            <div class="meta-icon">🐛</div>
            <div class="meta-label">Issue</div>
            <div class="meta-value" title="{issue}">{issue_s}</div>
        </div>
        <div class="meta-cell">
            <div class="meta-icon">💻</div>
            <div class="meta-label">Language</div>
            <div class="meta-value">{lang_s}</div>
        </div>
        <div class="meta-cell">
            <div class="meta-icon">🔄</div>
            <div class="meta-label">Iterations</div>
            <div class="meta-value">{iters}</div>
        </div>
    </div>"""


def step_list_html(active_idx: int) -> str:
    rows = []
    for i, (icon, label) in enumerate(STEPS):
        if i < active_idx:
            cls = "done"; check = "✓"
        elif i == active_idx:
            cls = "active"; check = icon
        else:
            cls = "pending"; check = icon
        rows.append(f'<div class="step-item {cls}"><span class="step-check">{check}</span>{label}</div>')
    return "\n".join(rows)

# ─────────────────────────────────────────────────────────────────────────────
#  Layout
# ─────────────────────────────────────────────────────────────────────────────

# nav
st.markdown("""
<div class="topnav">
    <div class="nav-logo">
    <div class="nav-logo-mark">✦</div>
    ContribAgent
</div>
</div>
""", unsafe_allow_html=True)

# hero
st.markdown("""
<div class="hero">
    <div class="hero-bg"></div>
    <div class="hero-eyebrow">✦ AI-Powered Open Source Copilot</div>
    <div class="hero-title">
        Find your next<br><span class="g">contribution.</span>
    </div>
    <div class="hero-sub">
        Describe what you want to work on, the agent delivers a step-by-step plan.
    </div>
    <div class="hero-stats">
    </div>
</div>
""", unsafe_allow_html=True)

# two-column workspace
left, right = st.columns([38, 62], gap="large")

# ── LEFT — input ──────────────────────────────────────────────────────────────
# ── LEFT — input ──────────────────────────────────────────────────────────────
with left:
    st.markdown("""
    <div class="panel-section">
        <div class="panel-header">
            <span class="panel-header-label">Your Contribution Goal</span>
        </div>
        <div class="panel-body">
    """, unsafe_allow_html=True)

    goal = st.text_area(
        label="Your Contribution Goal",
        placeholder="e.g. Find a beginner-friendly Python repo and suggest a good first issue to fix…",
        height=150,
        label_visibility="collapsed",
        key="goal_text_area",
    )

    st.markdown("</div></div>", unsafe_allow_html=True)

    col1, col2 = st.columns([3, 1])

    with col1:
        run_clicked = st.button(
            "✦  Run Agent",
            use_container_width=True,
            type="primary",
            key="run_agent_button",
        )

    with col2:
        clear_clicked = st.button(
            "Clear",
            use_container_width=True,
            key="clear_agent_button",
        )

# ── RIGHT — output ────────────────────────────────────────────────────────────
with right:
    # Determine status dot class
    if st.session_state.running:
        dot_cls, dot_label = "running", "RUNNING"
    elif st.session_state.result:
        dot_cls, dot_label = "status-dot", "COMPLETE"
    else:
        dot_cls, dot_label = "idle", "IDLE"

    # ── handle run click ──
    if run_clicked and goal.strip():
        st.session_state.running = True
        st.session_state.result  = None
        st.session_state.error   = None
        st.session_state.goal    = goal

        step_slot = st.empty()
        for i in range(len(STEPS)):
            with step_slot.container():
                st.markdown(f"""
                <div class="running-wrap">
                    <div class="running-header">
                        <div class="spin-ring"></div>
                        <div>
                            <div class="running-title">{STEPS[i][1]}</div>
                            <div class="running-sub">Agent is reasoning — this may take 60–120 seconds</div>
                        </div>
                    </div>
                    <div class="step-list">{step_list_html(i)}</div>
                </div>
                """, unsafe_allow_html=True)
            time.sleep(0.08)

        try:
            final_state = run_agent(goal)
            st.session_state.result  = final_state
            st.session_state.running = False
        except Exception as e:
            st.session_state.error   = str(e)
            st.session_state.running = False

        step_slot.empty()
        st.rerun()

    elif run_clicked and not goal.strip():
        with st.container():
            st.markdown("""
            <div style="padding:28px 32px">
                <div class="err-box">
                    <span class="err-icon">⚠️</span>
                    <div>
                        <div class="err-title">No goal entered</div>
                        <div class="err-body">Please describe what you want to contribute before running the agent.</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    elif clear_clicked:
        st.session_state.pop("goal_text_area", None)
        st.session_state.goal = ""
        st.session_state.result = None
        st.session_state.error = None
        st.rerun()

    elif st.session_state.error:
        with st.container():
            err = st.session_state.error
            st.markdown(f"""
            <div style="padding:28px 32px">
                <div class="err-box">
                    <span class="err-icon">❌</span>
                    <div>
                        <div class="err-title">Agent error</div>
                        <div class="err-body">{err[:400]}</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    elif st.session_state.result:
        final_state = st.session_state.result
        
        # Build one final Markdown string
        final_markdown = build_final_markdown(final_state)
        
        # Defensive assertion
        assert isinstance(final_markdown, str), "final_markdown must be a string"

        sel_repo  = final_state.get("selected_repository")
        sel_issue = final_state.get("selected_issue")
        repo_name   = get_value(sel_repo, "full_name", "—")
        issue_title = get_value(sel_issue, "title", "—")
        lang        = (
            final_state.get("language")
            or (sel_repo.get("language") if isinstance(sel_repo, dict) else getattr(sel_repo, "language", None))
            or "Unknown"
        )
        iters       = final_state.get("iteration_count", 0)

        st.markdown(meta_bar(repo_name, issue_title, lang, iters), unsafe_allow_html=True)
        with st.container(border=True):
            st.markdown(final_markdown)

        if DEBUG_MODE:
            with st.expander("Developer Debug Trace"):
                st.write("final_answer type:", type(final_state.get("final_answer")))
                st.write("evidence type:", type(final_state.get("evidence")))
                st.write(
                    "dependency_edges type:",
                    type(final_state.get("dependency_edges"))
                )
                st.json(final_state)

    else:
        with st.container():
            st.markdown("""
            <div style="
                padding:40px;
                color:#6b7280;
                font-size:14px;
                line-height:1.7;
            ">
            </div>
            """, unsafe_allow_html=True)
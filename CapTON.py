"""
CapTON AI — SEO keywording & caption writing studio.
Redesigned UI — deployable as-is on Streamlit Community Cloud.
"""

import base64
import hashlib
import os

import streamlit as st
from st_copy_to_clipboard import st_copy_to_clipboard

from agents import fetch_seo_data, analysis_step, writing_step, agents


# ── CONSTANTS ───────────────────────────────────────────────────
LOGO_PATH = "logo.png"

LANGUAGE_OPTIONS = {
    "English": "English",
    "Hindi (Devanagari)": "Hindi written in Devanagari script",
    "Hinglish": "Hinglish: natural Hindi-English mix written in Roman script",
    "Spanish": "Spanish",
    "French": "French",
    "German": "German",
    "Portuguese": "Portuguese",
    "Arabic": "Arabic",
    "Bengali": "Bengali",
    "Tamil": "Tamil",
    "Telugu": "Telugu",
    "Marathi": "Marathi",
    "Gujarati": "Gujarati",
    "Punjabi": "Punjabi written in Gurmukhi script",
    "Urdu": "Urdu written in Urdu script",
}

SKELETON_HTML = """
<div class="skel-stack">
    <div class="skel" style="height:32px;width:46%;border-radius:999px;"></div>
    <div class="skel" style="height:130px;width:100%;"></div>
    <div class="skel" style="height:14px;width:82%;"></div>
    <div class="skel" style="height:14px;width:64%;"></div>
</div>
"""

EMPTY_STATE_HTML = """
<div class="empty-wrap">
    <div class="empty-icon">✦</div>
    <div class="empty-title">Awaiting your script</div>
    <div class="empty-body">
        Paste your video script on the left and hit <b>Generate</b> —
        your SEO-optimised assets will appear here.
    </div>
</div>
"""


# ── PAGE CONFIG ─────────────────────────────────────────────────
st.set_page_config(
    page_title="CapTON AI",
    page_icon=LOGO_PATH if os.path.exists(LOGO_PATH) else "✦",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ── HELPERS ─────────────────────────────────────────────────────
def getb64img(path: str):
    """Return base64 of the logo, or None so the UI can fall back gracefully."""
    try:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except (FileNotFoundError, OSError):
        return None


def inject_custom_css():
    st.markdown(
        """
        <style>
        /* ─── FONTS ─── */
        @import url('https://api.fontshare.com/v2/css?f[]=satoshi@400,500,600,700&f[]=cabinet-grotesk@700,800&display=swap');

        /* ─── DESIGN TOKENS ─── */
        :root {
            --bg:            #0a0a10;
            --surface:       #12121b;
            --surface-2:     #171724;
            --surface-3:     #1f1f2e;
            --border:        rgba(255,255,255,0.07);
            --border-strong: rgba(255,255,255,0.14);
            --text:          #eceaf6;
            --text-muted:    #9a98b2;
            --text-faint:    #565470;
            --primary:       #7c6af7;
            --primary-hover: #9080ff;
            --primary-soft:  rgba(124,106,247,0.12);
            --blue:          #63b3ed;
            --success:       #34d399;
            --error:         #f87171;
            --radius-sm:     8px;
            --radius-md:     12px;
            --radius-lg:     16px;
            --radius-xl:     22px;
            --font-display:  'Cabinet Grotesk', 'Satoshi', sans-serif;
            --font-body:     'Satoshi', -apple-system, BlinkMacSystemFont, sans-serif;
            --ease:          cubic-bezier(0.16, 1, 0.3, 1);
            --t:             200ms var(--ease);
        }

        /* ─── STRIP STREAMLIT CHROME ─── */
        #MainMenu, footer, header { visibility: hidden; }
        .stDeployButton { display: none !important; }
        [data-testid="stToolbar"], [data-testid="stDecoration"] { display: none !important; }

        /* ─── APP SHELL ─── */
        .stApp {
            background:
                radial-gradient(900px 520px at 12% -10%, rgba(124,106,247,0.13), transparent 60%),
                radial-gradient(820px 520px at 88% -6%,  rgba(99,179,237,0.09),  transparent 55%),
                radial-gradient(1000px 700px at 50% 115%, rgba(124,106,247,0.06), transparent 60%),
                var(--bg) !important;
            background-attachment: fixed !important;
            font-family: var(--font-body) !important;
            color: var(--text);
        }
        .stApp::after {
            content: '';
            position: fixed; top: 0; left: 0; right: 0;
            height: 2px; z-index: 9999; pointer-events: none;
            background: linear-gradient(90deg, transparent 5%, var(--primary) 35%, var(--blue) 65%, transparent 95%);
            opacity: 0.55;
        }
        .block-container {
            padding: 2.2rem 2.5rem 2.5rem !important;
            max-width: 1380px !important;
            margin: 0 auto !important;
        }
        ::selection { background: rgba(124,106,247,0.4); color: #fff; }

        /* ─── ENTRANCE MOTION ─── */
        @keyframes rise { from { opacity: 0; transform: translateY(12px); } to { opacity: 1; transform: none; } }
        @keyframes float { 0%,100% { transform: translateY(0); } 50% { transform: translateY(-5px); } }
        @keyframes shimmer { to { background-position: 200% center; } }
        @keyframes pulse { 0%,100% { opacity: 1; transform: scale(1); } 50% { opacity: 0.45; transform: scale(0.75); } }

        /* ─── HEADER ─── */
        .capton-header { text-align: center; padding: 2.4rem 1rem 1.4rem; animation: rise 0.6s var(--ease) both; }
        .capton-logo-row { display: inline-flex; align-items: center; gap: 1rem; margin-bottom: 0.7rem; }
        .capton-logo-img {
            width: 68px; height: 68px; border-radius: 18px; object-fit: contain;
            box-shadow: 0 0 0 1px rgba(124,106,247,0.4), 0 10px 36px rgba(124,106,247,0.35);
            animation: float 5s ease-in-out infinite;
        }
        .capton-logo-fallback {
            width: 68px; height: 68px; border-radius: 18px;
            display: flex; align-items: center; justify-content: center;
            font-family: var(--font-display); font-weight: 800; font-size: 2rem; color: #fff;
            background: linear-gradient(135deg, #7c6af7, #5a4fcf);
            box-shadow: 0 0 0 1px rgba(124,106,247,0.4), 0 10px 36px rgba(124,106,247,0.35);
        }
        .capton-wordmark {
            font-family: var(--font-display);
            font-size: clamp(2.4rem, 4.5vw, 3.4rem);
            font-weight: 800; letter-spacing: -0.045em; line-height: 1;
            background: linear-gradient(120deg, #d6c9ff 0%, #7c6af7 35%, #63b3ed 70%, #d6c9ff 100%);
            background-size: 200% auto;
            -webkit-background-clip: text; background-clip: text;
            -webkit-text-fill-color: transparent;
            animation: shimmer 8s linear infinite;
        }
        .capton-tagline { font-size: 1.02rem; color: var(--text-muted); margin-top: 0.55rem; letter-spacing: 0.01em; }

        /* ─── STATUS BADGE + CHIPS ─── */
        .capton-badge-wrap { text-align: center; margin-bottom: 0.9rem; }
        .capton-badge {
            display: inline-flex; align-items: center; gap: 0.45rem;
            font-size: 0.7rem; font-weight: 700; letter-spacing: 0.09em; text-transform: uppercase;
            padding: 0.32rem 0.85rem; border-radius: 999px;
            color: #b9b4e8; background: rgba(124,106,247,0.08);
            border: 1px solid rgba(124,106,247,0.25);
        }
        .capton-badge .dot {
            width: 6px; height: 6px; border-radius: 50%;
            background: var(--success); box-shadow: 0 0 8px var(--success);
            animation: pulse 2s ease-in-out infinite;
        }
        .capton-chips { display: flex; justify-content: center; gap: 0.5rem; flex-wrap: wrap; margin-bottom: 2.1rem; }
        .capton-chip {
            display: inline-flex; align-items: center; gap: 0.4rem;
            font-size: 0.76rem; font-weight: 500; color: var(--text-muted);
            background: rgba(255,255,255,0.03); border: 1px solid var(--border);
            padding: 0.38rem 0.85rem; border-radius: 999px; transition: var(--t);
        }
        .capton-chip:hover { color: var(--text); border-color: var(--border-strong); transform: translateY(-1px); }

        /* ─── GLASS CARDS (native bordered containers) ─── */
        [data-testid="stVerticalBlockBorderWrapper"] {
            background: linear-gradient(180deg, rgba(255,255,255,0.032), rgba(255,255,255,0.014)) !important;
            border: 1px solid var(--border) !important;
            border-radius: var(--radius-xl) !important;
            padding: 1.5rem 1.6rem 1.3rem !important;
            box-shadow: 0 1px 2px rgba(0,0,0,0.45), 0 16px 40px rgba(0,0,0,0.28);
            transition: border-color var(--t), box-shadow var(--t);
            animation: rise 0.5s var(--ease) both;
        }
        [data-testid="stVerticalBlockBorderWrapper"]:hover { border-color: var(--border-strong) !important; }

        /* ─── PANEL HEADERS ─── */
        .panel-label {
            display: flex; align-items: center; gap: 0.45rem;
            font-size: 0.66rem; font-weight: 700; letter-spacing: 0.12em; text-transform: uppercase;
            color: var(--primary); margin-bottom: 0.45rem;
        }
        .panel-label::before {
            content: ''; width: 14px; height: 2px; border-radius: 2px;
            background: linear-gradient(90deg, var(--primary), var(--blue));
        }
        .panel-title {
            font-family: var(--font-display); font-size: 1.25rem; font-weight: 700;
            color: var(--text); letter-spacing: -0.02em; margin-bottom: 0.25rem;
        }
        .panel-desc { font-size: 0.85rem; color: var(--text-muted); line-height: 1.55; margin-bottom: 1.1rem; }

        /* ─── WIDGET LABELS / CAPTIONS ─── */
        .stSelectbox label, .stTextArea label {
            font-size: 0.72rem !important; font-weight: 600 !important;
            letter-spacing: 0.08em !important; text-transform: uppercase !important;
            color: var(--text-faint) !important;
        }
        [data-testid="stCaptionContainer"] { color: var(--text-faint) !important; font-size: 0.74rem !important; text-align: right; }

        /* ─── TEXT AREAS ─── */
        /* Strip every Streamlit wrapper so only our skin shows */
        .stTextArea [data-testid="stTextAreaRootElement"],
        .stTextArea [data-testid="stTextAreaRootElement"] > div,
        .stTextArea [data-baseweb="base-input"],
        .stTextArea [data-baseweb="base-input"] > div {
            background: transparent !important;
            border: none !important;
            box-shadow: none !important;
        }

        /* The visible control: tinted glass with an inset shadow */
        .stTextArea [data-baseweb="textarea"] {
            background: rgba(255,255,255,0.028) !important;
            border: 1px solid var(--border) !important;
            border-radius: var(--radius-md) !important;
            box-shadow: inset 0 2px 10px rgba(0,0,0,0.28) !important;
            overflow: hidden;
            transition: border-color var(--t), box-shadow var(--t), background var(--t) !important;
        }
        .stTextArea [data-baseweb="textarea"]:hover {
            background: rgba(255,255,255,0.04) !important;
            border-color: var(--border-strong) !important;
        }
        .stTextArea [data-baseweb="textarea"]:focus-within {
            background: rgba(124,106,247,0.05) !important;
            border-color: rgba(124,106,247,0.55) !important;
            box-shadow: 0 0 0 3px rgba(124,106,247,0.14),
                        inset 0 2px 10px rgba(0,0,0,0.2) !important;
        }

        /* The textarea itself is now fully transparent */
        .stTextArea textarea {
            background: transparent !important;
            border: none !important;
            box-shadow: none !important;
            color: var(--text) !important;
            -webkit-text-fill-color: var(--text) !important;
            font-family: var(--font-body) !important;
            font-size: 0.92rem !important;
            line-height: 1.7 !important;
            padding: 0.95rem 1.05rem !important;
            caret-color: var(--primary) !important;
            resize: vertical !important;
        }
        .stTextArea textarea:focus { outline: none !important; }
        .stTextArea textarea::placeholder {
            color: var(--text-faint) !important;
            opacity: 1 !important;
        }

        /* "Press Ctrl+Enter…" hint text */
        .stTextArea [data-testid="stInputInstructions"],
        .stTextArea [data-testid="InputInstructions"] {
            color: var(--text-faint) !important;
            font-size: 0.7rem !important;
        }

        /* ─── SELECTBOX ─── */
        [data-baseweb="select"] > div {
            background: rgba(10,10,16,0.55) !important;
            border: 1px solid var(--border) !important;
            border-radius: var(--radius-md) !important;
            color: var(--text) !important;
            transition: border-color var(--t), box-shadow var(--t) !important;
        }
        [data-baseweb="select"] > div:hover { border-color: var(--border-strong) !important; }
        [data-baseweb="select"] > div:focus-within {
            border-color: rgba(124,106,247,0.6) !important;
            box-shadow: 0 0 0 3px rgba(124,106,247,0.15) !important;
        }
        [data-baseweb="select"] svg { fill: var(--text-muted) !important; }
        [data-baseweb="popover"], [data-baseweb="menu"] {
            background: var(--surface) !important;
            border: 1px solid var(--border) !important;
            border-radius: var(--radius-md) !important;
        }
        [role="listbox"] li { color: var(--text-muted) !important; font-size: 0.88rem !important; }
        [role="listbox"] li:hover, [role="option"][aria-selected="true"] {
            background: var(--primary-soft) !important; color: var(--text) !important;
        }

        /* ─── STEP LIST ─── */
        .step-list {
            display: flex; flex-direction: column; gap: 0.15rem;
            margin: 1.15rem 0 1.25rem; padding: 0.9rem 1rem;
            background: rgba(124,106,247,0.045);
            border: 1px solid rgba(124,106,247,0.14);
            border-radius: var(--radius-md);
        }
        .step-item { display: flex; align-items: center; gap: 0.65rem; font-size: 0.82rem; color: var(--text-muted); padding: 0.22rem 0; }
        .step-num {
            width: 20px; height: 20px; border-radius: 50%; flex-shrink: 0;
            display: flex; align-items: center; justify-content: center;
            font-size: 0.62rem; font-weight: 700; color: #c0b3ff;
            background: rgba(124,106,247,0.14); border: 1px solid rgba(124,106,247,0.32);
        }

        /* ─── PRIMARY BUTTON ─── */
        .stButton > button[kind="primary"] {
            position: relative; overflow: hidden;
            background: linear-gradient(135deg, #8b7bff 0%, #6d5cf0 45%, #5a4fcf 100%) !important;
            color: #fff !important; border: none !important;
            border-radius: var(--radius-md) !important;
            font-family: var(--font-body) !important;
            font-size: 0.95rem !important; font-weight: 700 !important;
            letter-spacing: 0.015em !important;
            padding: 0.85rem 1.5rem !important; height: auto !important;
            box-shadow: 0 1px 2px rgba(0,0,0,0.4), 0 6px 22px rgba(124,106,247,0.35) !important;
            transition: transform var(--t), box-shadow var(--t), filter var(--t) !important;
        }
        .stButton > button[kind="primary"]::before {
            content: ''; position: absolute; top: 0; left: -90%;
            width: 55%; height: 100%;
            background: linear-gradient(100deg, transparent, rgba(255,255,255,0.28), transparent);
            transform: skewX(-20deg); transition: left 0.55s var(--ease);
        }
        .stButton > button[kind="primary"]:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 2px 4px rgba(0,0,0,0.4), 0 10px 32px rgba(124,106,247,0.5) !important;
            filter: brightness(1.06);
        }
        .stButton > button[kind="primary"]:hover::before { left: 140%; }
        .stButton > button[kind="primary"]:active { transform: translateY(0) !important; }
        .stButton > button[kind="primary"]:focus-visible { outline: 2px solid var(--primary-hover) !important; outline-offset: 2px; }

        /* ─── SECONDARY BUTTONS ─── */
        .stButton > button:not([kind="primary"]) {
            background: var(--surface-3) !important;
            color: var(--text-muted) !important;
            border: 1px solid var(--border) !important;
            border-radius: var(--radius-sm) !important;
            font-size: 0.8rem !important; height: auto !important;
            transition: var(--t) !important;
        }
        .stButton > button:not([kind="primary"]):hover {
            background: var(--primary-soft) !important;
            border-color: rgba(124,106,247,0.35) !important;
            color: var(--primary-hover) !important;
        }

        /* ─── TABS (segmented control) ─── */
        .stTabs [data-baseweb="tab-list"] {
            background: rgba(10,10,16,0.5) !important;
            border: 1px solid var(--border) !important;
            border-radius: 999px !important;
            padding: 4px !important; gap: 3px !important; margin-bottom: 1.1rem !important;
        }
        .stTabs [data-baseweb="tab"] {
            background: transparent !important; border: none !important;
            border-radius: 999px !important;
            color: var(--text-muted) !important;
            font-family: var(--font-body) !important;
            font-size: 0.8rem !important; font-weight: 600 !important;
            padding: 0.45rem 0.9rem !important;
            transition: var(--t) !important;
        }
        .stTabs [data-baseweb="tab"]:hover { color: var(--text) !important; }
        .stTabs [aria-selected="true"] {
            background: linear-gradient(135deg, rgba(124,106,247,0.25), rgba(99,179,237,0.15)) !important;
            color: #fff !important;
            box-shadow: inset 0 0 0 1px rgba(124,106,247,0.35), 0 2px 8px rgba(0,0,0,0.3) !important;
        }
        .stTabs [data-baseweb="tab-panel"] { padding: 0.2rem 0 0 !important; }
        .stTabs [data-baseweb="tab-border"], .stTabs [data-baseweb="tab-highlight"] { display: none !important; }

        /* ─── PROGRESS ─── */
        .stProgress > div > div {
            background: rgba(255,255,255,0.06) !important;
            border-radius: 999px !important; height: 5px !important; overflow: hidden;
        }
        .stProgress > div > div > div { border-radius: 999px !important; }
        .stProgress > div > div > div > div {
            background: linear-gradient(90deg, var(--primary), var(--blue)) !important;
            transition: width 0.4s var(--ease) !important;
        }

        /* ─── STATUS / EXPANDER ─── */
        [data-testid="stExpander"] {
            background: rgba(18,18,27,0.7) !important;
            border: 1px solid var(--border) !important;
            border-radius: var(--radius-md) !important;
            overflow: hidden;
        }
        [data-testid="stExpander"] summary {
            font-family: var(--font-body) !important;
            font-size: 0.88rem !important; font-weight: 600 !important;
            color: var(--text) !important;
        }
        [data-testid="stExpander"] summary:hover { color: var(--primary-hover) !important; }
        [data-testid="stExpander"] svg { fill: var(--text-muted) !important; }

        /* ─── ALERTS ─── */
        .stAlert {
            background: rgba(18,18,27,0.8) !important;
            border: 1px solid var(--border) !important;
            border-radius: var(--radius-md) !important;
            font-size: 0.87rem !important;
        }

        /* ─── MARKDOWN ─── */
        .stMarkdown p { color: var(--text-muted); font-size: 0.875rem; }
        .output-title {
            font-family: var(--font-display); font-size: 1rem; font-weight: 700;
            color: var(--text); letter-spacing: -0.01em; padding-top: 0.15rem;
        }

        /* ─── COPY COMPONENT ALIGNMENT ─── */
        iframe[title*="copy"] { display: block; margin-left: auto; }

        /* ─── EMPTY STATE ─── */
        .empty-wrap {
            display: flex; flex-direction: column; align-items: center; justify-content: center;
            text-align: center; padding: 3.4rem 2rem; margin-top: 0.2rem;
            border: 1.5px dashed rgba(255,255,255,0.09);
            border-radius: var(--radius-lg);
            background: rgba(255,255,255,0.012);
        }
        .empty-icon {
            font-size: 2rem; margin-bottom: 0.9rem;
            background: linear-gradient(135deg, #c4b5fd, #63b3ed);
            -webkit-background-clip: text; background-clip: text;
            -webkit-text-fill-color: transparent;
            animation: float 4s ease-in-out infinite;
        }
        .empty-title { font-family: var(--font-display); font-size: 1rem; font-weight: 700; color: var(--text); margin-bottom: 0.35rem; }
        .empty-body { font-size: 0.82rem; color: var(--text-faint); line-height: 1.6; max-width: 32ch; }
        .empty-body b { color: var(--text-muted); }

        /* ─── SKELETON LOADER ─── */
        .skel-stack { display: flex; flex-direction: column; gap: 0.8rem; padding: 0.4rem 0 0.2rem; }
        .skel {
            border-radius: 10px;
            background: linear-gradient(90deg, rgba(255,255,255,0.035) 25%, rgba(255,255,255,0.08) 37%, rgba(255,255,255,0.035) 63%);
            background-size: 400% 100%;
            animation: skel 1.3s ease infinite;
        }
        @keyframes skel { 0% { background-position: 100% 0; } 100% { background-position: 0 0; } }

        /* ─── FOOTER ─── */
        .capton-footer {
            text-align: center; margin-top: 2.8rem; padding-top: 1.4rem;
            border-top: 1px solid var(--border);
            color: var(--text-faint); font-size: 0.75rem; letter-spacing: 0.02em;
        }
        .capton-footer b { color: var(--text-muted); font-weight: 600; }

        /* ─── SCROLLBAR / COLUMNS / RESPONSIVE ─── */
        ::-webkit-scrollbar { width: 6px; height: 6px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: var(--surface-3); border-radius: 999px; }
        ::-webkit-scrollbar-thumb:hover { background: var(--text-faint); }
        [data-testid="column"] { padding-inline: 0.5rem; }
        @media (max-width: 900px) {
            .block-container { padding: 1.4rem 1rem 2rem !important; }
            [data-testid="column"] { padding-inline: 0; }
        }
        @media (prefers-reduced-motion: reduce) {
            *, *::before, *::after { animation: none !important; transition: none !important; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def set_progress_color(color: str, placeholder_container):
    placeholder_container.markdown(
        f"""<style>
        .stProgress > div > div > div > div {{
            background: {color} !important;
            transition: background 0.3s ease;
        }}
        </style>""",
        unsafe_allow_html=True,
    )


def render_copyable_section(title: str, content: str, height: int = 280):
    safe_title = title.lower().replace(" ", "_").replace("-", "_")
    generation_id = st.session_state.get("generation_id", 0)
    text_key = f"output_{safe_title}_{generation_id}"

    header_col, button_col = st.columns([8, 1], vertical_alignment="center")
    with header_col:
        st.markdown(f'<div class="output-title">{title}</div>', unsafe_allow_html=True)

    edited_content = st.text_area(
        label=f"{title} content",
        value=content,
        height=height,
        label_visibility="collapsed",
        key=text_key,
    )
    content_hash = hashlib.sha256(edited_content.encode("utf-8")).hexdigest()[:16]

    with button_col:
        if edited_content.strip():
            st_copy_to_clipboard(
                edited_content,
                "📋 Copy",
                key=f"copy_{safe_title}_{generation_id}_{content_hash}",
            )


# ── MAIN ────────────────────────────────────────────────────────
def main():
    logo_b64 = getb64img(LOGO_PATH)
    inject_custom_css()

    st.session_state.setdefault("results", None)
    st.session_state.setdefault("generation_id", 0)

    # ── HEADER ──
    logo_html = (
        f'<img src="data:image/png;base64,{logo_b64}" class="capton-logo-img" alt="CapTON AI logo" />'
        if logo_b64
        else '<div class="capton-logo-fallback">C</div>'
    )
    st.markdown(
        f"""
        <div class="capton-header">
            <div class="capton-logo-row">{logo_html}<span class="capton-wordmark">CapTON&nbsp;AI</span></div>
            <div class="capton-tagline">SEO keywording &amp; caption writing, powered by a live agent pipeline</div>
        </div>
        <div class="capton-badge-wrap">
            <span class="capton-badge"><span class="dot"></span>AI agent pipeline active</span>
        </div>
        <div class="capton-chips">
            <span class="capton-chip">⚡ Live SEO signals</span>
            <span class="capton-chip">🧠 3-step agent workflow</span>
            <span class="capton-chip">🌍 15 output languages</span>
            <span class="capton-chip">📋 One-click copy</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col_input, col_output = st.columns([1, 1.15], gap="large")
    css_placeholder = st.empty()

    # ── LEFT: INPUT ──
    with col_input:
        with st.container(border=True):
            st.markdown(
                """
                <div class="panel-label">Input</div>
                <div class="panel-title">📝 Your video script</div>
                <div class="panel-desc">Paste your full script below. The pipeline analyses intent,
                fetches live SEO signals, and writes viral hooks &amp; captions automatically.</div>
                """,
                unsafe_allow_html=True,
            )

            with st.form("content_generator_form", clear_on_submit=False):
                script = st.text_area(
                    "Video script",
                    value="",
                    height=270,
                    placeholder=(
                        "Paste your video script here…\n\n"
                        "The AI agents will extract topic, audience signals, emotional hooks, "
                        "and SEO keywords automatically."
                    ),
                    label_visibility="collapsed",
                )

                st.caption(f"{len(script.split())} words · {len(script)} characters")

                selected_language_name = st.selectbox(
                    "Content language",
                    options=list(LANGUAGE_OPTIONS.keys()),
                    index=0,
                    help="Hooks, caption, and hashtags will be generated in this language.",
                )
                output_language = LANGUAGE_OPTIONS[selected_language_name]

                st.markdown(
                    """
                    <div class="step-list">
                        <div class="step-item"><div class="step-num">1</div>Live SEO context fetching</div>
                        <div class="step-item"><div class="step-num">2</div>Topic &amp; audience analysis</div>
                        <div class="step-item"><div class="step-num">3</div>Hook &amp; caption generation</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                generate = st.form_submit_button(
                    "✦ Generate Content",
                    type="primary",
                    use_container_width=True,
                )
            status_placeholder = st.empty()

    # ── RIGHT: OUTPUT ──
    with col_output:
        with st.container(border=True):
            st.markdown(
                """
                <div class="panel-label">Output</div>
                <div class="panel-title">🎯 Generated assets</div>
                <div class="panel-desc">SEO-optimised hooks, captions, and hashtags appear here —
                ready to copy &amp; publish across all platforms.</div>
                """,
                unsafe_allow_html=True,
            )

            skeleton = st.empty()
            busy = bool(generate and script.strip())

            if generate and not script.strip():
                status_placeholder.error("⚠️ Please paste a script before generating.")

            if busy:
                st.session_state.results = None
                set_progress_color("linear-gradient(90deg, #7c6af7, #63b3ed)", css_placeholder)
                skeleton.markdown(SKELETON_HTML, unsafe_allow_html=True)
                success = False

                with status_placeholder.container():
                    progress = st.progress(0)
                    with st.status("🧠 Processing your script…", expanded=True) as status:
                        try:
                            status.write("✅ Script received — initialising workflow…")
                            progress.progress(10)

                            status.write("⏳ Fetching live SEO context…")
                            seo_context = fetch_seo_data(script=script)
                            if not seo_context:
                                raise ValueError("SEO context could not be fetched.")
                            status.write("✅ SEO context fetched")
                            progress.progress(40)

                            analyzer, writer = agents()

                            status.write("⏳ Analysing topic, audience, and emotion…")
                            progress.progress(55)
                            analysis_result = analysis_step(
                                script=script, seo_context=seo_context, analyzer=analyzer,
                            )
                            if not isinstance(analysis_result, dict) or "error" in analysis_result:
                                err = analysis_result.get("error", "Unknown") if isinstance(analysis_result, dict) else type(analysis_result).__name__
                                raise ValueError(f"Analysis failed: {err}")
                            analysis = analysis_result.get("analysis", "")
                            if not analysis:
                                raise ValueError("Analysis completed but returned empty text.")
                            status.write("✅ Analysis complete")
                            progress.progress(75)

                            status.write(f"⏳ Crafting hooks and captions in {selected_language_name}…")
                            writing_result = writing_step(
                                script=script, seo_context=seo_context, analysis=analysis,
                                writer=writer, output_language=output_language,
                            )
                            if not isinstance(writing_result, dict) or "error" in writing_result:
                                err = writing_result.get("error", "Unknown") if isinstance(writing_result, dict) else "Invalid output."
                                raise ValueError(f"Writing failed: {err}")
                            hooks = writing_result.get("hooks", [])
                            caption = writing_result.get("caption", "")
                            hashtags = writing_result.get("hashtags", [])
                            if not hooks and not caption and not hashtags:
                                raise ValueError("Writer returned empty outputs.")

                            status.write("✅ Content generation finished")
                            progress.progress(100)
                            status.update(label="✨ Pipeline finished successfully", state="complete", expanded=False)

                            st.session_state.results = {
                                "hooks": "\n".join(f"{i}) {h}" for i, h in enumerate(hooks, start=1)),
                                "caption": caption,
                                "hashtags": " ".join(hashtags),
                                "final": f"{caption}\n\n{' '.join(hashtags)}".strip(),
                            }
                            st.session_state.generation_id += 1
                            success = True
                        except Exception as e:
                            set_progress_color("#f87171", css_placeholder)
                            progress.progress(100)
                            status.update(label="❌ Pipeline failed", state="error", expanded=True)
                            st.error(str(e))

                skeleton.empty()
                if success:
                    st.toast("Your content is ready to copy ✨", icon="✨")

            if st.session_state.results:
                tab1, tab2, tab3, tab4 = st.tabs(["🔥 Hooks", "✍️ Caption", "🏷️ Hashtags", "🚀 Ready-to-Paste"])
                with tab1:
                    render_copyable_section("Viral Hooks", st.session_state.results["hooks"])
                with tab2:
                    render_copyable_section("Cross-Platform Caption", st.session_state.results["caption"])
                with tab3:
                    render_copyable_section("SEO Hashtags", st.session_state.results["hashtags"])
                with tab4:
                    render_copyable_section("Full Description", st.session_state.results["final"], height=380)
            elif not busy:
                st.markdown(EMPTY_STATE_HTML, unsafe_allow_html=True)

    # ── FOOTER ──
    st.markdown(
        '<div class="capton-footer"><b>CapTON AI</b> · Multi-agent SEO content pipeline · Built with Streamlit</div>',
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
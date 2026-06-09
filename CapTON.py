import streamlit as st
from st_copy_to_clipboard import st_copy_to_clipboard
from agents import fetch_seo_data, analysis_step, writing_step, agents
import base64

def getb64img(path: str) -> str:
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()


st.set_page_config(
    page_title="CapTON AI",
    page_icon="logo.png",
    layout="wide",
    initial_sidebar_state="collapsed"
)


def inject_custom_css():
    st.markdown(
        """
        <style>
        /* ─── FONTS ─── */
        @import url('https://api.fontshare.com/v2/css?f[]=satoshi@400,500,600,700&f[]=cabinet-grotesk@700,800&display=swap');

        /* ─── DESIGN TOKENS ─── */
        :root {
            --bg:              #0d0d10;
            --surface:         #13131a;
            --surface-2:       #1a1a24;
            --surface-3:       #20202e;
            --border:          rgba(255,255,255,0.07);
            --border-hover:    rgba(255,255,255,0.14);
            --text:            #e8e8f0;
            --text-muted:      #8888a4;
            --text-faint:      #44445a;
            --primary:         #7c6af7;
            --primary-hover:   #9080ff;
            --primary-glow:    rgba(124,106,247,0.18);
            --primary-dim:     rgba(124,106,247,0.08);
            --success:         #34d399;
            --error:           #f87171;
            --radius-sm:       6px;
            --radius-md:       10px;
            --radius-lg:       14px;
            --radius-xl:       20px;
            --font-display:    'Cabinet Grotesk', sans-serif;
            --font-body:       'Satoshi', sans-serif;
            --transition:      180ms cubic-bezier(0.16, 1, 0.3, 1);
            --shadow-card:     0 1px 2px rgba(0,0,0,0.4), 0 8px 24px rgba(0,0,0,0.3);
            --shadow-glow:     0 0 0 1px rgba(124,106,247,0.25), 0 8px 32px rgba(124,106,247,0.12);
        }

        /* ─── STRIP STREAMLIT CHROME ─── */
        #MainMenu, footer, header { visibility: hidden; }
        .stDeployButton { display: none !important; }
        [data-testid="stToolbar"] { display: none !important; }

        /* ─── APP SHELL ─── */
        .stApp {
            background: var(--bg) !important;
            font-family: var(--font-body) !important;
        }
        .block-container {
            padding: 2.5rem 2.5rem 3rem !important;
            max-width: 100% !important;
        }

        /* ─── HEADER SECTION ─── */
        .capton-header {
            position: relative;
            text-align: center;
            padding: 3.5rem 1rem 2.5rem;
            margin-bottom: 0.5rem;
            overflow: hidden;
        }
        .capton-header::before {
            content: '';
            position: absolute;
            inset: -60% -40%;
            background:
                radial-gradient(ellipse at 40% 50%, rgba(124,106,247,0.14) 0%, transparent 65%),
                radial-gradient(ellipse at 70% 30%, rgba(99,179,237,0.08) 0%, transparent 55%);
            animation: headerPulse 8s ease-in-out infinite alternate;
            pointer-events: none;
        }
        @keyframes headerPulse {
            0%   { transform: scale(1) translate(0,0); opacity: 0.7; }
            100% { transform: scale(1.08) translate(2%,1%); opacity: 1; }
        }
        .capton-logo {
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            margin-bottom: 0.6rem;
        }
        .capton-wordmark {
            font-family: var(--font-display);
            font-size: clamp(2rem, 4vw, 3rem);
            font-weight: 800;
            letter-spacing: -0.04em;
            background: linear-gradient(135deg, #c4b5fd 0%, #7c6af7 40%, #63b3ed 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            line-height: 1.1;
        }
        .capton-tagline {
            font-family: var(--font-body);
            font-size: 1rem;
            color: var(--text-muted);
            letter-spacing: 0.01em;
            margin-top: 0.4rem;
        }

        /* ─── LIVE STATUS BADGE ─── */
        .capton-badge {
            display: inline-flex;
            align-items: center;
            gap: 0.3rem;
            font-size: 0.72rem;
            font-weight: 600;
            letter-spacing: 0.06em;
            text-transform: uppercase;
            padding: 0.25rem 0.7rem;
            border-radius: 999px;
            border: 1px solid var(--border);
            background: var(--surface-2);
            color: var(--text-muted);
            margin-bottom: 1.8rem;
        }
        .capton-badge .dot {
            width: 6px; height: 6px;
            background: var(--success);
            border-radius: 50%;
            animation: badgePulse 2s ease-in-out infinite;
        }
        @keyframes badgePulse {
            0%, 100% { opacity: 1; transform: scale(1); }
            50%       { opacity: 0.4; transform: scale(0.8); }
        }

        /* ─── PANEL CARDS ─── */
        .panel-card {
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: var(--radius-xl);
            padding: 1.6rem 1.75rem 1.2rem;
            box-shadow: var(--shadow-card);
            margin-bottom: 0.85rem;
        }
        .panel-label {
            font-size: 0.68rem;
            font-weight: 700;
            letter-spacing: 0.1em;
            text-transform: uppercase;
            color: var(--text-faint);
            margin-bottom: 0.3rem;
        }
        .panel-title {
            font-family: var(--font-display);
            font-size: 1.1rem;
            font-weight: 700;
            color: var(--text);
            margin-bottom: 0.3rem;
            letter-spacing: -0.02em;
        }
        .panel-desc {
            font-size: 0.84rem;
            color: var(--text-muted);
            line-height: 1.55;
        }

        /* ─── TEXT AREA ─── */
        .stTextArea > label { display: none !important; }
        .stTextArea textarea {
            background: var(--surface-2) !important;
            border: 1px solid var(--border) !important;
            border-radius: var(--radius-md) !important;
            color: var(--text) !important;
            font-family: var(--font-body) !important;
            font-size: 0.9rem !important;
            line-height: 1.65 !important;
            resize: vertical !important;
            padding: 0.85rem 1rem !important;
            transition: border-color var(--transition), box-shadow var(--transition) !important;
        }
        .stTextArea textarea:focus {
            border-color: var(--primary) !important;
            box-shadow: var(--shadow-glow) !important;
            outline: none !important;
        }
        .stTextArea textarea::placeholder { color: var(--text-faint) !important; }

        /* ─── PRIMARY GENERATE BUTTON ─── */
        .stButton > button[kind="primary"] {
            background: linear-gradient(135deg, #7c6af7 0%, #5a4fcf 100%) !important;
            color: #fff !important;
            border: none !important;
            border-radius: var(--radius-md) !important;
            font-family: var(--font-body) !important;
            font-size: 0.9rem !important;
            font-weight: 600 !important;
            letter-spacing: 0.01em !important;
            padding: 0.72rem 1.5rem !important;
            height: auto !important;
            box-shadow: 0 1px 2px rgba(0,0,0,0.3), 0 4px 12px rgba(124,106,247,0.3) !important;
            transition: all var(--transition) !important;
        }
        .stButton > button[kind="primary"]:hover {
            background: linear-gradient(135deg, #9080ff 0%, #7c6af7 100%) !important;
            box-shadow: 0 1px 2px rgba(0,0,0,0.3), 0 6px 20px rgba(124,106,247,0.45) !important;
            transform: translateY(-1px) !important;
        }
        .stButton > button[kind="primary"]:active { transform: translateY(0) !important; }

        /* ─── SECONDARY / COPY BUTTONS ─── */
        .stButton > button:not([kind="primary"]) {
            background: var(--surface-3) !important;
            color: var(--text-muted) !important;
            border: 1px solid var(--border) !important;
            border-radius: var(--radius-sm) !important;
            font-family: var(--font-body) !important;
            font-size: 0.8rem !important;
            padding: 0.3rem 0.65rem !important;
            height: auto !important;
            transition: all var(--transition) !important;
        }
        .stButton > button:not([kind="primary"]):hover {
            background: var(--primary-dim) !important;
            border-color: rgba(124,106,247,0.35) !important;
            color: var(--primary-hover) !important;
        }

        /* ─── MARKDOWN HEADINGS ─── */
        .stMarkdown h3 {
            font-family: var(--font-display) !important;
            font-size: 1.05rem !important;
            font-weight: 700 !important;
            color: var(--text) !important;
            letter-spacing: -0.02em !important;
            margin-bottom: 0.25rem !important;
        }
        .stMarkdown h4 {
            font-family: var(--font-display) !important;
            font-size: 0.92rem !important;
            font-weight: 700 !important;
            color: var(--text) !important;
        }
        .stMarkdown p { color: var(--text-muted) !important; font-size: 0.875rem !important; }

        /* ─── TABS ─── */
        .stTabs [data-baseweb="tab-list"] {
            background: var(--surface-2) !important;
            border-radius: var(--radius-md) !important;
            padding: 4px !important;
            gap: 2px !important;
            border: 1px solid var(--border) !important;
            margin-bottom: 1rem !important;
        }
        .stTabs [data-baseweb="tab"] {
            background: transparent !important;
            border-radius: var(--radius-sm) !important;
            color: var(--text-muted) !important;
            font-family: var(--font-body) !important;
            font-size: 0.8rem !important;
            font-weight: 600 !important;
            padding: 0.42rem 0.8rem !important;
            border: none !important;
            transition: all var(--transition) !important;
        }
        .stTabs [aria-selected="true"] {
            background: var(--surface-3) !important;
            color: var(--text) !important;
            box-shadow: 0 1px 3px rgba(0,0,0,0.35) !important;
        }
        .stTabs [data-baseweb="tab-panel"] { padding: 0 !important; }
        .stTabs [data-baseweb="tab-border"],
        .stTabs [data-baseweb="tab-highlight"] { display: none !important; }

        /* ─── PROGRESS BAR ─── */
        .stProgress > div > div {
            background: var(--surface-2) !important;
            border-radius: 999px !important;
            height: 3px !important;
            overflow: hidden;
        }
        .stProgress > div > div > div {
            border-radius: 999px !important;
            transition: background-color 0.3s ease !important;
        }

        /* ─── STATUS / EXPANDER ─── */
        [data-testid="stExpander"] {
            background: var(--surface-2) !important;
            border: 1px solid var(--border) !important;
            border-radius: var(--radius-md) !important;
        }

        /* ─── ALERTS ─── */
        .stAlert {
            background: var(--surface-2) !important;
            border: 1px solid var(--border) !important;
            border-radius: var(--radius-md) !important;
            font-family: var(--font-body) !important;
            font-size: 0.87rem !important;
        }
        .stInfo {
            background: rgba(124,106,247,0.06) !important;
            border-color: rgba(124,106,247,0.22) !important;
        }
        .stError {
            background: rgba(248,113,113,0.06) !important;
            border-color: rgba(248,113,113,0.22) !important;
        }

        /* ─── SCROLLBAR ─── */
        ::-webkit-scrollbar { width: 5px; height: 5px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: var(--surface-3); border-radius: 999px; }
        ::-webkit-scrollbar-thumb:hover { background: var(--text-faint); }

        /* ─── STEP LIST ─── */
        .step-list {
            display: flex;
            flex-direction: column;
            gap: 0.6rem;
            margin: 1rem 0 1.2rem;
        }
        .step-item {
            display: flex;
            align-items: center;
            gap: 0.6rem;
            font-size: 0.8rem;
            color: var(--text-muted);
            font-family: var(--font-body);
        }
        .step-num {
            width: 18px; height: 18px;
            border-radius: 50%;
            background: var(--surface-3);
            border: 1px solid var(--border);
            flex-shrink: 0;
            display: flex; align-items: center; justify-content: center;
            font-size: 0.6rem;
            color: var(--text-faint);
            font-weight: 700;
        }

        /* ─── EMPTY STATE ─── */
        .empty-wrap {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 4rem 2rem;
            text-align: center;
        }
        .empty-icon {
            font-size: 2.2rem;
            margin-bottom: 0.9rem;
            opacity: 0.35;
        }
        .empty-title {
            font-family: var(--font-display);
            font-size: 0.95rem;
            font-weight: 700;
            color: var(--text-muted);
            margin-bottom: 0.4rem;
            letter-spacing: -0.01em;
        }
        .empty-body {
            font-size: 0.8rem;
            color: var(--text-faint);
            line-height: 1.6;
            max-width: 30ch;
        }

        /* ─── COLUMN PADDING ─── */
        [data-testid="column"] { padding-inline: 0.4rem; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def set_progress_color(color: str, placeholder_container):
    placeholder_container.markdown(
        f"""<style>
        .stProgress > div > div > div > div {{
            background-color: {color} !important;
            transition: background-color 0.3s ease;
        }}
        </style>""",
        unsafe_allow_html=True,
    )


def render_copyable_section(title: str, content: str, height: int = 280):
    header_col, button_col = st.columns([9, 1])
    with header_col:
        st.markdown(f"#### {title}")
    with button_col:
        if content.strip():
            st_copy_to_clipboard(content, "📋", key=f"copy_{title}")
    st.text_area(
        label=f"{title} content",
        value=content,
        height=height,
        label_visibility="collapsed",
    )


# ─────────────────────────────────────────────────────────────────
def main():
    logo = getb64img("logo.png")
    inject_custom_css()

    # ── BRANDED HEADER ──────────────────────────────────────────
    st.markdown(f"""
<div class="capton-header">
    <div class="capton-logo">
        <img src="data:image/png;base64,{logo}"
             width="156" height="156"
             style="border-radius:11px; object-fit:contain;"
             alt="CapTON AI Logo" />
        <span class="capton-wordmark">CapTON AI</span>
    </div>
    <div class="capton-tagline">SEO Keywording &amp; Caption Writing — Powered by AI Agents</div>
</div>
""", unsafe_allow_html=True)

    st.markdown("""
    <div style="text-align:center;margin-bottom:2rem;">
        <span class="capton-badge">
            <span class="dot"></span>
            AI Agent Pipeline Active
        </span>
    </div>
    """, unsafe_allow_html=True)

    # ── TWO COLUMN LAYOUT ────────────────────────────────────────
    col_input, col_output = st.columns([1, 1.25], gap="large")
    css_placeholder = st.empty()

    # ── LEFT: INPUT ──────────────────────────────────────────────
    with col_input:
        st.markdown("""
        <div class="panel-card">
            <div class="panel-label">Input</div>
            <div class="panel-title">📝 Your Video Script</div>
            <div class="panel-desc">Paste your full script below. The agent pipeline will analyse intent,
            fetch live SEO signals, and generate viral hooks &amp; captions automatically.</div>
        </div>
        """, unsafe_allow_html=True)

        script = st.text_area(
            "Video Script",
            value="",
            height=295,
            placeholder="Paste your video script here…"

           "The AI agents will extract topic, audience signals, emotional hooks, and SEO keywords automatically.",
            label_visibility="collapsed"
        )

        st.markdown("""
        <div class="step-list">
            <div class="step-item"><div class="step-num">1</div>Live SEO context fetching</div>
            <div class="step-item"><div class="step-num">2</div>Topic &amp; audience analysis</div>
            <div class="step-item"><div class="step-num">3</div>Hook &amp; caption generation</div>
        </div>
        """, unsafe_allow_html=True)

        generate = st.button("🚀 Generate Content", type="primary", use_container_width=True)
        status_placeholder = st.empty()

    # ── RIGHT: OUTPUT ────────────────────────────────────────────
    with col_output:
        st.markdown("""
        <div class="panel-card">
            <div class="panel-label">Output</div>
            <div class="panel-title">🎯 Generated Assets</div>
            <div class="panel-desc">SEO-optimised hooks, captions, and hashtags will appear here —
            ready to copy and publish across all platforms.</div>
        </div>
        """, unsafe_allow_html=True)

        if "results" not in st.session_state:
            st.session_state.results = None

        if generate:
            if not script.strip():
                st.error("⚠️  Please paste a script before generating.")
                return

            st.session_state.results = None
            set_progress_color("#7c6af7", css_placeholder)

            with status_placeholder.container():
                progress = st.progress(0)
                with st.status("🧠 Processing your script…", expanded=True) as status:
                    try:
                        status.write("✅ Script received. Initialising workflow…")
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
                            err = analysis_result.get('error', 'Unknown') if isinstance(analysis_result, dict) else type(analysis_result).__name__
                            raise ValueError(f"Analysis failed: {err}")
                        analysis = analysis_result.get("analysis", "")
                        if not analysis:
                            raise ValueError("Analysis completed but returned empty text.")
                        status.write("✅ Analysis complete")
                        progress.progress(75)

                        status.write("⏳ Crafting hooks and captions…")
                        writing_result = writing_step(
                            script=script, seo_context=seo_context, analysis=analysis, writer=writer,
                        )
                        if not isinstance(writing_result, dict) or "error" in writing_result:
                            err = writing_result.get('error', 'Unknown') if isinstance(writing_result, dict) else "Invalid output."
                            raise ValueError(f"Writing failed: {err}")
                        hooks    = writing_result.get("hooks", [])
                        caption  = writing_result.get("caption", "")
                        hashtags = writing_result.get("hashtags", [])
                        if not hooks and not caption and not hashtags:
                            raise ValueError("Writer returned empty outputs.")

                        status.write("✅ Content generation finished!")
                        progress.progress(100)
                        status.update(label="✨ Pipeline finished successfully", state="complete", expanded=False)

                        st.session_state.results = {
                            "hooks":    "\n".join([f"{i}) {h}" for i, h in enumerate(hooks, start=1)]),
                            "caption":  caption,
                            "hashtags": " ".join(hashtags),
                            "final":    f"{caption}\n\n{' '.join(hashtags)}".strip()
                        }

                    except Exception as e:
                        set_progress_color("#f87171", css_placeholder)
                        progress.progress(100)
                        status.update(label="❌ Pipeline Failed", state="error", expanded=True)
                        st.error(str(e))
                        return

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
        else:
            st.markdown("""
            <div class="empty-wrap">
                <div class="empty-icon">✦</div>
                <div class="empty-title">Awaiting your script</div>
                <div class="empty-body">
                    Paste your video script on the left and hit Generate to see your SEO-optimised assets here.
                </div>
            </div>
            """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
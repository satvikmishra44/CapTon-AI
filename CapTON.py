import streamlit as st
from st_copy_to_clipboard import st_copy_to_clipboard
from agents import fetch_seo_data, analysis_step, writing_step, agents


def set_progress_colour(color: str):
    st.markdown(
        f"""
        <style>
        .stProgress > div > div > div > div {{
            background-color: {color};
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_copyable_section(title: str, content: str, height: int = 140):
    left, right = st.columns([8, 1])

    with left:
        st.subheader(title)

    with right:
        st.write("")
        if content.strip():
            st_copy_to_clipboard(content, "📋", key=f"copy_{title}")

    st.text_area(
        label=f"{title} content",
        value=content,
        height=height,
        label_visibility="collapsed",
    )


def main():
    st.set_page_config(
        page_title="CapTON AI",
        page_icon=":guardsman:",
        layout="wide",
    )

    st.title("CapTON AI: Your Personal AI Agent For SEO Keywording And Caption Writing")
    st.caption(
        "CapTON AI is an AI agent designed to assist you in generating SEO keywords and "
        "writing captions for your content. It uses advanced natural language processing "
        "techniques to understand your input and provide relevant suggestions."
    )

    st.markdown(
        """
Paste your full video script below and click **Generate**.

The system will:
- Analyze topic, audience, and emotion
- Pull SEO context from the web
- Generate 3 viral-style hooks
- Create a cross-platform caption
- Suggest 4 platform-agnostic hashtags
        """
    )

    script = st.text_area(
        "Enter Your Script Here",
        value="",
        height=260,
        placeholder="Enter Your Script Here",
    )

    col_left, col_right = st.columns([1, 2])

    with col_left:
        generate = st.button("Generate Hooks And Caption", type="primary")

    with col_right:
        st.write(" ")

    if generate:
        if not script.strip():
            st.error("Please paste a script before generating.")
            return

        set_progress_colour("#4CAF50")
        progress = st.progress(0)

        with st.status("Initializing pipeline...", expanded=True) as status:
            try:
                status.write("✅ Script received")
                progress.progress(8)

                status.write("✅ Workflow initialized")
                progress.progress(15)

                status.write("⏳ Fetching SEO context...")
                progress.progress(28)

                seo_context = fetch_seo_data(script=script)

                if not seo_context:
                    set_progress_colour("#FF4B4B")
                    progress.progress(100)
                    status.update(
                        label="❌ Pipeline failed during SEO fetching",
                        state="error",
                        expanded=True,
                    )
                    st.error("SEO context could not be fetched.")
                    return

                status.write("✅ SEO context fetched")
                progress.progress(40)

                analyzer, writer = agents()

                status.write("⏳ Analyzer agent is analyzing script...")
                progress.progress(55)

                analysis_result = analysis_step(
                    script=script,
                    seo_context=seo_context,
                    analyzer=analyzer,
                )

                if not isinstance(analysis_result, dict):
                    set_progress_colour("#FF4B4B")
                    progress.progress(100)
                    status.update(
                        label="❌ Pipeline failed during analysis",
                        state="error",
                        expanded=True,
                    )
                    st.error(f"Analysis returned unexpected type: {type(analysis_result).__name__}")
                    return

                if "error" in analysis_result:
                    set_progress_colour("#FF4B4B")
                    progress.progress(100)
                    status.update(
                        label="❌ Pipeline failed during analysis",
                        state="error",
                        expanded=True,
                    )
                    st.error(f"Analysis error: {analysis_result.get('error', 'Unknown analysis error')}")
                    return

                analysis = analysis_result.get("analysis", "")
                if not analysis:
                    set_progress_colour("#FF4B4B")
                    progress.progress(100)
                    status.update(
                        label="❌ Pipeline failed during analysis",
                        state="error",
                        expanded=True,
                    )
                    st.error("Analysis completed but no analysis text was returned.")
                    return

                status.write("✅ Analyzer finished")
                progress.progress(72)

                status.write("⏳ Writing caption now...")
                progress.progress(84)

                writing_result = writing_step(
                    script=script,
                    seo_context=seo_context,
                    analysis=analysis,
                    writer=writer,
                )

                if not isinstance(writing_result, dict):
                    set_progress_colour("#FF4B4B")
                    progress.progress(100)
                    status.update(
                        label="❌ Pipeline failed during writing",
                        state="error",
                        expanded=True,
                    )
                    st.error(
                        "Writing step returned unexpected output type. "
                        f"Expected dict, got {type(writing_result).__name__}. "
                        f"Raw output: {writing_result}"
                    )
                    return

                if "error" in writing_result:
                    set_progress_colour("#FF4B4B")
                    progress.progress(100)
                    status.update(
                        label="❌ Pipeline failed during writing",
                        state="error",
                        expanded=True,
                    )
                    st.error(f"Writing error: {writing_result.get('error', 'Unknown writing error')}")
                    return

                hooks = writing_result.get("hooks", [])
                caption = writing_result.get("caption", "")
                hashtags = writing_result.get("hashtags", [])

                if not hooks and not caption and not hashtags:
                    set_progress_colour("#FF4B4B")
                    progress.progress(100)
                    status.update(
                        label="❌ Pipeline failed during writing",
                        state="error",
                        expanded=True,
                    )
                    st.error("Writer completed but returned empty output.")
                    return

                status.write("✅ Writer finished")
                progress.progress(96)

                status.update(
                    label="✅ Pipeline finished successfully",
                    state="complete",
                    expanded=False,
                )
                progress.progress(100)

            except Exception as e:
                set_progress_colour("#FF4B4B")
                progress.progress(100)
                status.update(
                    label="❌ Pipeline failed unexpectedly",
                    state="error",
                    expanded=True,
                )
                st.error(f"Unexpected error: {e}")
                return

        hooks_text = "\n".join([f"{i}) {h}" for i, h in enumerate(hooks, start=1)])
        hashtags_text = " ".join(hashtags)
        final_description = f"{caption}\n\n{hashtags_text}".strip()

        col1, col2, col3 = st.columns(3)

        with col1:
            render_copyable_section("Hooks", hooks_text, height=220)

        with col2:
            render_copyable_section("Caption", caption, height=220)

        with col3:
            render_copyable_section("Hashtags", hashtags_text, height=220)

        st.markdown("---")
        render_copyable_section("Ready-to-paste Description", final_description, height=220)


if __name__ == "__main__":
    main()
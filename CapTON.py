import streamlit as st
from st_copy_to_clipboard import st_copy_to_clipboard
from main import run

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
    st.set_page_config(page_title="CapTON AI", page_icon=":guardsman:", layout="wide")

    st.title("CapTON AI: Your Personal AI Agent For SEO Keywording And Caption Writing")
    st.caption("CapTON AI is an AI agent designed to assist you in generating SEO keywords and writing captions for your content. It uses advanced natural language processing techniques to understand your input and provide relevant suggestions.")

    st.markdown(""" Paste your full video script below and click **Generate**.

The system will:
- Analyze topic, audience, and emotion
- Pull SEO context from the web
- Generate 3 viral-style hooks
- Create a cross-platform caption
- Suggest 4 platform-agnostic hashtags
        """
    )

    # Input Area
    script = st.text_area("Enter Your Script Here", value="", height=260, placeholder="Enter Your Script Here")

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
            status.write("✅ Script received")
            progress.progress(10)

            status.write("✅ Workflow initialized")
            progress.progress(18)

            status.write("⏳ Fetching SEO context...")
            progress.progress(30)

            try:
                with st.spinner("Running SEO search and multi-agent CrewAI workflow..."):
                    data = run(script)

                if not data:
                    set_progress_colour("#FF4B4B")
                    progress.progress(100)
                    status.update(
                        label="❌ Pipeline failed (no data returned)",
                        state="error",
                        expanded=True,
                    )
                    st.error("Workflow failed (no data returned). Check backend logs.")
                    return

                if "error" in data:
                    set_progress_colour("#FF4B4B")
                    progress.progress(100)
                    status.write("❌ SEO / workflow step failed")
                    status.update(
                        label="❌ Pipeline failed",
                        state="error",
                        expanded=True,
                    )
                    st.error(f"Workflow error: {data['error']}")
                    return

                status.write("✅ SEO context fetched")
                progress.progress(45)

                status.write("⏳ Analyzer agent is analyzing script...")
                progress.progress(60)

                status.write("✅ Analyzer finished")
                progress.progress(72)

                status.write("⏳ Writing caption now...")
                progress.progress(88)

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

        hooks = data.get("hooks", [])
        caption = data.get("caption", "")
        hashtags = data.get("hashtags", [])

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
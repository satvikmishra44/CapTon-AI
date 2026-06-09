import streamlit as st

from main import run

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
            st.error("Please Enter Your Script First!!!")
            return 
        
        progress = st.progress(0)
        # Status container for step-by-step messages
        with st.status("Initializing pipeline...", expanded=True) as status:
            status.write("✅ Script received")
            progress.progress(10)

            status.write("✅ Workflow initialized")
            progress.progress(20)

            with st.spinner("Running SEO search and multi-agent CrewAI workflow..."):
                status.write("⏳ Fetching SEO context (DuckDuckGo)...")
                progress.progress(40)

                # Single call runs: SEO + Analyzer + JSON Writer
                data = run(script)

            if data is None:
                status.update(
                    label="❌ Pipeline failed (see terminal logs)",
                    state="error",
                    expanded=True,
                )
                st.error("Workflow failed. Check the terminal logs for details.")
                return

            status.write("✅ SEO context ready")
            progress.progress(70)

            status.write("✅ Analyzer + Writer agents completed")
            progress.progress(90)

            status.update(
                label="✅ Pipeline finished successfully",
                state="complete",
                expanded=False,
            )
            progress.progress(100)

        hooks = data.get("hooks", [])
        caption = data.get("caption", "")
        hashtags = data.get("hashtags", [])

        # Displaying Hooks On Left And Caption + Hashtags On Right

        hooks_col, caption_col = st.columns([1, 2])

        with hooks_col:
            st.subheader("Hooks")
            if hooks:
                for i, h in enumerate(hooks, start=1):
                    st.markdown(f"**{i})** {h}")

            else:
                st.info("No Hooks Generated")

        with caption_col:
            st.subheader("Caption With Hashtags")
            if caption:
                st.write(caption)
            else:
                st.info("No Caption Generated")

            st.subheader("Hashtags")
            if(hashtags):
                st.code(" ".join(hashtags), language=None)
            else:
                st.info("No Hashtags Generated")

        st.markdown("----")

        st.subheader("Ready To Paste Description")
        if caption or hashtags:
            description = caption + "\n\n" + " ".join(hashtags)
            st.text_area("Description", value=description, height=200)

        else:
            st.info("No Description Generated")


if __name__ == "__main__":
    main()
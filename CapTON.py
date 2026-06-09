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
        
        with st.expander("Agent Status...", expanded=True):
            st.write("Script Recieved. Starting Agent....")
            status_placeholder = st.empty()

        with st.spinner("CapTON is getting SEO ready..."):
            status_placeholder.write("Analyzing Script For Topic And Fetching SEO Context...")
            data = run(script)

        if data is None:
            st.error("An Internal Error Occured. Please Try Again Later.")
            return 
        
        status_placeholder.write("Caption And Hooks Generated Succesfully! Displaying Results Below...")

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
import streamlit as st


def write():
    st.title('Alfred - Research')
    with st.spinner("Loading About ..."):
        st.markdown(
            """
            Research tabs
            """,
            unsafe_allow_html=True,
        )

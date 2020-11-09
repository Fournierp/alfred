import streamlit as st


def write():
    st.title('Alfred - Prediction')
    with st.spinner("Loading About ..."):
        st.markdown(
            """
            Prediction tabs
            """,
            unsafe_allow_html=True,
        )

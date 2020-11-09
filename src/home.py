import streamlit as st


def write():
    st.title('Alfred - Home')
    with st.spinner("Loading About ..."):
        st.markdown(
            """
            This Streamlit app is a Financial data dashbord that could be used
            for data visualization, exploration and predicting behavior of
            Financial quantities.
            """,
            unsafe_allow_html=True,
        )

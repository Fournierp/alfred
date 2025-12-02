import streamlit as st


def write() -> None:
    st.title('Alfred - Home')
    st.markdown(
        """
        This Streamlit app is a financial data dashbord. It is a proof of concept for data visualization &
         exploration and can be customized.
        """,
        unsafe_allow_html=True,
    )

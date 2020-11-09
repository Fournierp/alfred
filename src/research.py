import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime


@st.cache
def load_data():
    companies = pd.read_html('https://en.wikipedia.org/wiki/List_of_S'
                             '%26P_500_companies')[0]
    return companies.drop('SEC filings', axis=1).set_index('Symbol')


@st.cache()
def load_quotes(asset):
    return yf.download(asset)


def write():
    st.title('Alfred - Research')
    with st.spinner("Loading About ..."):
        st.markdown(
            """
            Research tabs
            """,
            unsafe_allow_html=True,
        )

        companies = load_data()

        # Show table of companies
        if st.checkbox('View companies list', value=True):
            option = st.selectbox(
                'Which sectors should be displayed',
                ('All',) + tuple(companies['GICS Sector'].unique()),
                index=0)

            if option != 'All':
                st.dataframe(companies[['Security',
                                        'GICS Sector',
                                        'Date first added',
                                        'Founded']][companies['GICS Sector'] == option])
            else:
                st.dataframe(companies[['Security',
                                        'GICS Sector',
                                        'Date first added',
                                        'Founded']])

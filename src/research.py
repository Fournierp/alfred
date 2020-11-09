import streamlit as st
import pandas as pd
import yfinance as yf
from geopy.geocoders import Nominatim
import requests
import urllib.parse
import requests
import json


@st.cache
def load_data():
    companies = pd.read_html('https://en.wikipedia.org/wiki/List_of_S'
                             '%26P_500_companies')[0]
    return companies.drop('SEC filings', axis=1).set_index('Symbol')


@st.cache(suppress_st_warning=True)
def load_quotes(asset):
    return yf.download(asset)


def write():
    st.title('Alfred - Research')
    geolocator = Nominatim(user_agent="paul.fournier")

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

        def label(symbol):
            ''' Fancy display of company names'''
            a = companies.loc[symbol]
            return symbol + ' - ' + a.Security

        # Select companies to display
        st.subheader('Select assets')
        assets = st.multiselect('Click below to select a new asset',
                                companies.index.sort_values(),
                                format_func=label)

        # Determine if display company info
        if st.checkbox('View company info', True):
            st.table(companies.loc[assets][['Security',
                                            'GICS Sector',
                                            'GICS Sub-Industry',
                                            'Headquarters Location',
                                            'Date first added',
                                            'Founded']])

        # When at least one company is selected
        if len(assets):
            if len(assets) > 1:
                df = pd.DataFrame()
                for asset in assets:
                    # Display multiple companies on a single graph
                    data = load_quotes(asset)
                    data.index.name = None
                    data = data.rename(columns={'Adj Close': asset})
                    df = pd.concat([df, data[:][asset]], axis=1)

            else:
                # Display company on a graph
                data = load_quotes(assets)
                data.index.name = None
                data = data.rename(columns={'Adj Close': assets[0]})
                df = data[:][assets[0]]

            st.line_chart(df)

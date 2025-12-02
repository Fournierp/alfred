import pandas as pd
import streamlit as st
import yfinance as yf


def rename_company(companies: pd.DataFrame, asset: str) -> str:
    a = companies.loc[asset]
    return asset + ' - ' + a.Security


@st.cache_data
def load_data() -> pd.DataFrame:
    url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
    headers = {'User-Agent': 'Mozilla/5.0'}
    companies = pd.read_html(url, storage_options=headers)[1]
    return companies.set_index('Symbol')


@st.cache_data
def load_quotes(asset: str) -> pd.DataFrame:
    data = yf.download(asset, period='max')
    data.index.name = None
    data = data[('Close', asset)]
    if isinstance(data, pd.Series):
        return data.rename(asset)
    return data.rename({('Close', asset): asset})

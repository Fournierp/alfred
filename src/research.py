import streamlit as st
import pandas as pd
import yfinance as yf
import numpy as np
import api


@st.cache
def load_data():
    companies = pd.read_html('https://en.wikipedia.org/wiki/List_of_S'
                             '%26P_500_companies')[0]
    return companies.drop('SEC filings', axis=1).set_index('Symbol')


@st.cache(suppress_st_warning=True)
def load_quotes(asset):
    return yf.download(asset)


def news_table(company):
    """
    Get the news headlines from the API and fill a table.
    """
    df = pd.DataFrame(columns=["Title", "About", "Source", "Links", "Published on"])

    # Make an API call
    res = api.get_articles(company)

    # Skip if no headline was found
    number_of_results = res["totalResults"]
    if int(number_of_results) != 0:
        # Take the 10 most relevant articles published in the range and display
        # the source, the company name, the title, the date and link
        for counter, result in enumerate(res["articles"]):
            if counter > 9:
                break
            df = df.append(pd.DataFrame([[result["title"], company, result["source"]["name"],
                                          result["url"], result["publishedAt"][:10]]],
                                        columns=["Title", "About", "Source", "Links", "Published on"]),
                           ignore_index=True)

    return df


def write():
    st.title('Alfred - Research')

    with st.spinner("Loading About ..."):
        st.markdown(
            """ Research tabs """,
            unsafe_allow_html=True,
        )
        # Get company names and info
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
            ''' Fancy display of company names '''
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

            # Slider for Moving Average window
            maw = st.slider("Select the Moving Average window \
            (Select 1 to execute no curve smoothing)", 1, 200, 50, 1)

            if len(assets) > 1:
                stocks = pd.DataFrame([])
                news = pd.DataFrame([])
                for asset in assets:
                    # Stocks Graph
                    # Get data for that company
                    data = load_quotes(asset)
                    data.index.name = None
                    data = data.rename(columns={'Adj Close': asset})
                    # Moving average
                    if maw != 1:
                        tmp = np.round(data[:][asset].rolling(maw).mean(), 2)
                    else:
                        tmp = data[:][asset]
                    stocks = pd.concat([stocks, tmp], axis=1)

                    # News articles
                    news = news.append(news_table(companies.loc[asset].Security), ignore_index=True)

            else:
                # Stocks Graph
                # Get data for that company
                data = load_quotes(assets)
                data.index.name = None
                data = data.rename(columns={'Adj Close': assets[0]})
                stocks = data[:][assets[0]]
                # Moving average
                if maw != 1:
                    ma = np.round(stocks.rolling(maw).mean(), 2)
                    # Checkbox for Bollinger Bands
                    if st.checkbox('View Bollinger Bands', value=True):
                        # Compute Bollinger Bands
                        std = np.round(stocks.rolling(maw).std(), 2)
                        ub = ma + std * 2
                        lb = ma - std * 2

                        stocks = pd.concat([stocks, ub, lb], axis=1, ignore_index=True)
                        stocks = stocks.rename(
                            columns={0: assets[0], 1: "Upper Bollinger Band", 2: "Lower Bollinger Band"})
                    else:
                        stocks = ma

                    # News articles
                    news = news_table(companies.loc[assets[0]].Security)

            st.line_chart(stocks)
            if news.empty:
                st.write('''No news articles about the companies.''')
            else:
                st.table(news)

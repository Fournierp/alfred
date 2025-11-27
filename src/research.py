import numpy as np
import pandas as pd
import streamlit as st
import yfinance as yf

import api


@st.cache_data
def load_data() -> pd.DataFrame:
    url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
    headers = {'User-Agent': 'Mozilla/5.0'}
    companies = pd.read_html(url, storage_options=headers)[1]
    return companies.set_index('Symbol')


@st.cache_data()
def load_quotes(asset: str) -> pd.DataFrame:
    return yf.download(asset, period='max')


def news_table(company: str) -> pd.DataFrame:
    df = pd.DataFrame(columns=['Title', 'About', 'Source', 'Links', 'Published on'])

    res = api.get_articles(company)

    articles_to_display = 10
    if int(res['totalResults']) != 0:
        # Take the 10 most relevant articles published in the range and display
        # the source, the company name, the title, the date and link
        for counter, result in enumerate(res['articles']):
            if counter >= articles_to_display:
                break
            new_row = pd.DataFrame(
                [
                    [
                        result['title'],
                        company,
                        result['source']['name'],
                        result['url'],
                        result['publishedAt'][:articles_to_display],
                    ]
                ],
                columns=['Title', 'About', 'Source', 'Links', 'Published on'],
            )
            df = pd.concat([df, new_row], ignore_index=True)

    return df


def display_companies_list(companies: pd.DataFrame) -> None:
    if st.checkbox('View companies list', value=True):
        option = st.selectbox(
            'Which sectors should be displayed', ('All', *tuple(companies['GICS Sector'].unique())), index=0
        )

        if option != 'All':
            st.dataframe(
                companies[['Security', 'GICS Sector', 'Date added', 'Founded']][companies['GICS Sector'] == option]
            )
        else:
            st.dataframe(companies[['Security', 'GICS Sector', 'Date added', 'Founded']])


def get_asset_selection(companies: pd.DataFrame) -> list[str]:
    def label(symbol: str) -> str:
        """Fancy display of company names"""
        a = companies.loc[symbol]
        return symbol + ' - ' + a.Security

    st.subheader('Select assets')
    return st.multiselect('Click below to select a new asset', companies.index.sort_values(), format_func=label)


def display_company_info(companies: pd.DataFrame, assets: list[str]) -> None:
    if st.checkbox('View company info', value=True):
        st.table(
            companies.loc[assets][
                [
                    'Security',
                    'GICS Sector',
                    'GICS Sub-Industry',
                    'Headquarters Location',
                    'Date added',
                    'Founded',
                ]
            ]
        )


def process_multiple_assets(
    assets: list[str], companies: pd.DataFrame, moving_average_window: int
) -> tuple[pd.DataFrame, pd.DataFrame]:
    stocks = pd.DataFrame([])
    news = pd.DataFrame([])

    for asset in assets:
        data = load_quotes(asset)
        data.index.name = None
        data = data[('Close', asset)]

        if moving_average_window != 1:
            tmp = pd.Series(np.round(data.rolling(moving_average_window).mean(), 2), name=asset)
        else:
            tmp = pd.Series(data[:], name=asset)
        stocks = pd.concat([stocks, tmp], axis=1)

        news = pd.concat([news, news_table(companies.loc[asset].Security)], ignore_index=True)

    return stocks, news


def process_single_asset(
    asset: str, companies: pd.DataFrame, moving_average_window: int
) -> tuple[pd.DataFrame, pd.DataFrame]:
    data = load_quotes([asset])
    data.index.name = None
    stocks = data.loc[:, ('Close', asset)]

    if moving_average_window != 1:
        moving_average = np.round(stocks.rolling(moving_average_window).mean(), 2)
        if st.checkbox('View Bollinger Bands', value=True):
            std = np.round(stocks.rolling(moving_average_window).std(), 2)
            upper_bound = moving_average + std * 2
            lower_bound = moving_average - std * 2

            stocks = pd.concat([stocks, upper_bound, lower_bound], axis=1, ignore_index=True)
            stocks = stocks.rename(columns={0: asset, 1: 'Upper Bollinger Band', 2: 'Lower Bollinger Band'})
        else:
            stocks = pd.DataFrame(moving_average.values, index=moving_average.index, columns=[asset])

    news = news_table(companies.loc[asset].Security)
    return stocks, news


def display_stock_data(stocks: pd.DataFrame, news: pd.DataFrame) -> None:
    st.line_chart(stocks)
    if news.empty:
        st.write("""No news articles about the companies.""")
    else:
        st.dataframe(news, width='stretch')


def write() -> None:
    st.title('Alfred - Research')

    with st.spinner('Loading About ...'):
        st.markdown(""" Research tabs """, unsafe_allow_html=True)
        companies = load_data()

        display_companies_list(companies)
        assets = get_asset_selection(companies)
        display_company_info(companies, assets)

        if len(assets):
            moving_average_window = st.slider(
                'Select the Moving Average window (Select 1 to execute no curve smoothing)',
                1,
                200,
                50,
                1,
            )

            if len(assets) > 1:
                stocks, news = process_multiple_assets(assets, companies, moving_average_window)
            else:
                stocks, news = process_single_asset(assets[0], companies, moving_average_window)

            display_stock_data(stocks, news)

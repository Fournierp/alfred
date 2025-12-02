import numpy as np
import pandas as pd
import streamlit as st

import api
from src.utils import load_data, load_quotes, rename_company


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
    st.subheader('Select asset(s)')
    return st.multiselect(
        'Click below to select a new asset',
        companies.index.sort_values(),
        format_func=lambda x: rename_company(companies, x),
    )


def display_company_info(companies: pd.DataFrame, assets: list[str]) -> None:
    if st.checkbox('View company info', value=True):
        st.table(
            companies.loc[assets][
                ['Security', 'GICS Sector', 'GICS Sub-Industry', 'Headquarters Location', 'Date added', 'Founded']
            ]
        )


def process_multiple_assets(assets: list[str], companies: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    stocks = pd.DataFrame([])
    news = pd.DataFrame([])

    for asset in assets:
        stocks = pd.concat([stocks, load_quotes(asset)], axis=1)

        news = pd.concat([news, news_table(companies.loc[asset].Security)], ignore_index=True)

    return stocks, news


def process_single_asset(asset: str, companies: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    moving_average_window = st.slider(
        'Select the Moving Average window (Select 1 to execute no curve smoothing)',
        1,
        200,
        50,
        1,
    )

    stocks = load_quotes(asset)

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


def display_data(stocks: pd.DataFrame, news: pd.DataFrame) -> None:
    st.header('Stock Prices')
    if stocks.empty:
        st.warning('No stock data available.')
    else:
        st.line_chart(stocks)

    st.header('News Articles')
    if news.empty:
        st.warning('No news articles about the companies.')
    else:
        st.dataframe(news, width='stretch')


def write() -> None:
    st.title('Alfred - Research')

    with st.spinner('Loading ...'):
        companies = load_data()

        display_companies_list(companies)
        assets = get_asset_selection(companies)
        display_company_info(companies, assets)

        if len(assets):
            load_data_button = st.button('📊 Load Data', type='primary')

            if load_data_button:
                with st.spinner('Fetching stock data...'):
                    if len(assets) > 1:
                        stocks, news = process_multiple_assets(assets, companies)
                    else:
                        stocks, news = process_single_asset(assets[0], companies)

                display_data(stocks, news)
            elif not load_data_button:
                st.info('👆 Click "Load Stock Data" to fetch and display stock information')

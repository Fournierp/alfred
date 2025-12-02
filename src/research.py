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

    if 'stock_cache' not in st.session_state:
        st.session_state.stock_cache = {}
    if 'news_cache' not in st.session_state:
        st.session_state.news_cache = {}

    for asset in assets:
        if asset not in st.session_state.stock_cache:
            st.session_state.stock_cache[asset] = load_quotes(asset)

        stocks = pd.concat([stocks, st.session_state.stock_cache[asset]], axis=1)

        company_name = companies.loc[asset].Security
        if company_name not in st.session_state.news_cache:
            st.session_state.news_cache[company_name] = news_table(company_name)
        news = pd.concat([news, st.session_state.news_cache[company_name]], ignore_index=True)

    return stocks, news


def process_single_asset(asset: str, companies: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    if 'stock_cache' not in st.session_state:
        st.session_state.stock_cache = {}
    if 'news_cache' not in st.session_state:
        st.session_state.news_cache = {}

    if asset not in st.session_state.stock_cache:
        st.session_state.stock_cache[asset] = load_quotes(asset)

    stocks = st.session_state.stock_cache[asset]

    company_name = companies.loc[asset].Security
    if company_name not in st.session_state.news_cache:
        st.session_state.news_cache[company_name] = news_table(company_name)

    return stocks, st.session_state.news_cache[company_name]


def display_data(stocks: pd.DataFrame, news: pd.DataFrame, time_range: str = 'All') -> None:
    st.header('Stock Prices')
    if stocks.empty:
        st.warning('No stock data available.')
    elif time_range != 'All' and not stocks.empty:
        filtered_stocks = filter_by_time_range(stocks, time_range)
        st.line_chart(filtered_stocks)
    else:
        st.line_chart(stocks)

    st.header('News Articles')
    if news.empty:
        st.warning('No news articles about the companies.')
    else:
        st.dataframe(news, width='stretch')


def filter_by_time_range(data: pd.DataFrame, time_range: str) -> pd.DataFrame:
    if data.empty:
        return data

    end_date = data.index[-1]

    if time_range == '1M':
        start_date = end_date - pd.DateOffset(months=1)
    elif time_range == '3M':
        start_date = end_date - pd.DateOffset(months=3)
    elif time_range == '6M':
        start_date = end_date - pd.DateOffset(months=6)
    elif time_range == '1Y':
        start_date = end_date - pd.DateOffset(years=1)
    elif time_range == '5Y':
        start_date = end_date - pd.DateOffset(years=5)
    else:
        return data

    return data[data.index >= start_date]


def write() -> None:
    st.title('Alfred - Research')

    if 'stock_cache' not in st.session_state:
        st.session_state.stock_cache = {}
    if 'news_cache' not in st.session_state:
        st.session_state.news_cache = {}

    with st.sidebar:
        st.subheader('Cache Management')
        if st.session_state.stock_cache:
            st.write(f'Cached stocks: {len(st.session_state.stock_cache)}')
            assets_list = list(st.session_state.stock_cache.keys())[:5]
            suffix = '...' if len(st.session_state.stock_cache) > 5 else ''  # noqa: PLR2004
            st.write(f'Assets: {", ".join(assets_list)}{suffix}')
        if st.button('🗑️ Clear Cache'):
            st.session_state.stock_cache = {}
            st.session_state.news_cache = {}
            st.rerun()

    with st.spinner('Loading ...'):
        companies = load_data()

        display_companies_list(companies)
        assets = get_asset_selection(companies)
        display_company_info(companies, assets)

        if len(assets):
            time_range = st.selectbox(
                'Select time range',
                ['All', '1M', '3M', '6M', '1Y', '5Y'],
                index=0,
                help='Filter the displayed stock data by time range',
            )

            load_data_button = st.button('📊 Load Data', type='primary')

            if load_data_button:
                with st.spinner('Fetching stock data...'):
                    if len(assets) > 1:
                        stocks, news = process_multiple_assets(assets, companies)
                    else:
                        stocks, news = process_single_asset(assets[0], companies)

                    display_data(stocks, news, time_range)
            else:
                st.info('👆 Click "Load Data" to fetch and display stock information')

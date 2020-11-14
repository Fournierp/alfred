import streamlit as st
import json

import pandas as pd
import numpy as np

import yfinance as yf

from tensorflow.keras.models import model_from_json
from tensorflow.keras import backend as K


@st.cache
def load_model():
    # Load model
    json_file = open('models/checkpoints/lstm_next_price_model.json', 'r')
    loaded_model_json = json_file.read()
    json_file.close()
    loaded_model = model_from_json(loaded_model_json)

    # Load weights into new model
    loaded_model.load_weights("models/checkpoints/lstm_next_prices.h5")
    return loaded_model


@st.cache
def load_data():
    companies = pd.read_html('https://en.wikipedia.org/wiki/List_of_S'
                             '%26P_500_companies')[0]
    return companies.drop('SEC filings', axis=1).set_index('Symbol')


@st.cache(suppress_st_warning=True)
def load_quotes(asset):
    return yf.download(asset)


def get_model_data():
    with open('models/data.txt') as f:
        data = json.load(f)
        total_max = data["total_max"]
        total_min = data["total_min"]
        input_len = data["input_len"]
        return total_max, total_min, input_len


def predict_next_stock(model, stocks, input_len):
    historical_prices = np.array(stocks[-input_len:].copy())
    # Run model
    prediction = model.predict(historical_prices)[0]
    return prediction


def write():
    st.title('Alfred - Prediction')
    with st.spinner("Loading About ..."):
        st.markdown(
            """ Prediction tabs """,
            unsafe_allow_html=True,
        )
        # Get company names and info
        companies = load_data()
        # Get model
        model = load_model()

        def label(symbol):
            ''' Fancy display of company names '''
            a = companies.loc[symbol]
            return symbol + ' - ' + a.Security

        # Select companies to display
        st.subheader('Select assets')
        asset = st.selectbox('Click below to select a new asset',
                             companies.index.sort_values(),
                             format_func=label)

        # Get data for that company
        st.write(asset)

        data = load_quotes(asset)
        data.index.name = None
        data = data.rename(columns={'Adj Close': asset})
        stocks = data[:][asset]
        st.line_chart(stocks)

        # Model prediction
        total_max, total_min, input_len = get_model_data()
        predicted = predict_next_stock(model, stocks, input_len)
        # Inverse transform
        predicted = predicted * (total_max - total_min) + total_min
        st.write(predicted)

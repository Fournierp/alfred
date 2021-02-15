import streamlit as st
import json

import pandas as pd
import numpy as np

import yfinance as yf

from tensorflow.keras.models import model_from_json


@st.cache
def load_model():
    # Load price window model
    json_file = open('models/checkpoints/lstm_long_term_model.json', 'r')
    lstm_model_json = json_file.read()
    json_file.close()
    lstm_model = model_from_json(lstm_model_json)

    # Load weights into new model
    lstm_model.load_weights("models/checkpoints/lstm_long_term.h5")

    return lstm_model


@st.cache
def load_data():
    companies = pd.read_html('https://en.wikipedia.org/wiki/List_of_S'
                             '%26P_500_companies')[0]
    return companies.drop('SEC filings', axis=1).set_index('Symbol')


@st.cache(suppress_st_warning=True)
def load_quotes(asset):
    return yf.download(asset)


def get_model_data():
    with open('models/checkpoints/data_long_term.txt') as f:
        data = json.load(f)
        total_max = data["total_max"]
        total_min = data["total_min"]
        input_len = data["input_len"]
        output_len = data["output_len"]
        return total_max, total_min, input_len, output_len


def predict_next_stock(model, stocks):
    # Get model information
    total_max, total_min, input_len, output_len = get_model_data()
    # Get last window of data
    historical_prices = np.array(stocks[-input_len:].copy())
    historical_prices = np.reshape(historical_prices, (1, historical_prices.shape[0], 1))
    # Normalise the data
    historical_prices = (historical_prices - total_min) / (total_max - total_min)
    # Run model
    prediction = model.predict(historical_prices)
    # Inverse transform
    return prediction * (total_max - total_min) + total_min


def write():
    st.title('Alfred - Prediction')
    with st.spinner("Loading About ..."):
        st.markdown(
            """ Prediction tabs """,
            unsafe_allow_html=True,
        )
        # Get company names and info
        companies = load_data()
        # Get models
        lstm_model = load_model()

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

        # Model prediction
        predicted_val = predict_next_stock(lstm_model, stocks)

        # visualization
        slope = (predicted_val[0][0] - stocks.values[-1]) / 5
        projection_line = [stocks.values[-1]+i*slope for i in range(1, 6)]
        project_index = [stocks.index[-1]+pd.Timedelta(i, unit='D') for i in range(1, 6)]
        projection = pd.Series(data=projection_line, index=project_index)
        data = pd.concat([stocks, projection], axis=1, ignore_index=True)
        data = data.rename(
            columns={0: asset[0], 1: "Predicted value", 2: "Lower Bollinger Band"})

        st.line_chart(data)

        st.write(f'Long Short Term Memory model predicts the stock to be valued at {predicted_val[0][0]:.2f} in 5 days.')

import json
from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st
from tensorflow.keras.models import Model, model_from_json

from src.utils import load_data, load_quotes, rename_company


@st.cache_resource
def load_model():  # noqa: ANN201
    with Path('models/checkpoints/lstm_model.json').open('r') as json_file:
        lstm_model_json = json_file.read()
    lstm_model = model_from_json(lstm_model_json)
    lstm_model.load_weights('models/checkpoints/lstm.weights.h5')

    return lstm_model


def get_model_data() -> tuple[float, float, int, int]:
    with Path('models/checkpoints/lstm_data.txt').open() as f:
        data = json.load(f)
        total_max = data['total_max']
        total_min = data['total_min']
        input_len = data['input_len']
        output_len = data['output_len']
        return total_max, total_min, input_len, output_len


def predict_next_stock(model: Model, stocks: pd.Series) -> float:
    total_max, total_min, input_len, _ = get_model_data()

    historical_prices = np.array(stocks[-input_len:].copy())

    # Normalization
    historical_prices = np.reshape(historical_prices, (historical_prices.shape[0], 1))
    first_price = historical_prices[0, 0]
    norm_historical_prices = (historical_prices / first_price) - 1
    norm_historical_prices = (norm_historical_prices - total_min) / (total_max - total_min)

    # Prediction
    prediction = model.predict(norm_historical_prices[np.newaxis, ...], verbose=0)

    # De-normalization
    prediction = prediction * (total_max - total_min) + total_min
    return (prediction + 1) * first_price


def write() -> None:
    st.title('Alfred - Prediction')

    with st.spinner('Loading ...'):
        companies = load_data()
        lstm_model = load_model()

        asset = st.selectbox(
            'Click below to select a new asset',
            companies.index.sort_values(),
            format_func=lambda x: rename_company(companies, x),
        )

        predict_button = st.button('🔮 Generate Prediction', type='primary')

        if predict_button:
            with st.spinner('Fetching data and generating prediction...'):
                stocks = load_quotes(asset)
                predicted_val = predict_next_stock(lstm_model, stocks)
                predicted_price = predicted_val[0][0]
                current_price = stocks.to_numpy()[-1]

                projection_index = stocks.index[-1] + pd.Timedelta(1, unit='D')
                projection = pd.Series(
                    data=[current_price, predicted_price], index=[stocks.index[-1], projection_index]
                )
                last_month_stocks = stocks.loc[stocks.index >= stocks.index[-1] - pd.Timedelta(days=30)]
                data = pd.concat([last_month_stocks, projection], axis=1, ignore_index=True)
                data = data.rename(columns={0: asset, 1: 'Predicted value'})

                predicted_price_change = ((predicted_price - current_price) / current_price) * 100

            if data is not None:
                st.line_chart(data)

                emoji = '🚀📈' if predicted_price_change > 0 else '💔📉'

                st.write(
                    f"""{emoji} LSTM model predicts the stock to be valued at {predicted_price:.2f} at the next closing
                     time. ({'+' if predicted_price_change > 0 else ''}{predicted_price_change:.2f}%)."""
                )
        elif not predict_button:
            st.info('👆 Click "Generate Prediction" to fetch data and predict future stock price')

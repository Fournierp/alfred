import json
from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st
from tensorflow.keras.models import Model, model_from_json

from src.research import load_data, load_quotes


@st.cache_data
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
    print(historical_prices)
    historical_prices = np.reshape(historical_prices, (historical_prices.shape[0], 1))
    norm_historical_prices = (historical_prices / historical_prices[0, 0]) - 1

    norm_historical_prices = (norm_historical_prices - total_min) / (total_max - total_min)

    prediction = model.predict(norm_historical_prices[np.newaxis, ...])

    return prediction * (total_max - total_min) + total_min


def write() -> None:
    st.title('Alfred - Prediction')

    with st.spinner('Loading About ...'):
        st.markdown(""" Prediction tabs """, unsafe_allow_html=True)
        companies = load_data()
        lstm_model = load_model()

        def label(symbol: str) -> str:
            a = companies.loc[symbol]
            return symbol + ' - ' + a.Security

        st.subheader('Select assets')
        asset = st.selectbox('Click below to select a new asset', companies.index.sort_values(), format_func=label)

        print(asset)

        data = load_quotes(asset)
        data.index.name = None
        print(data)
        stocks = data[('Close', asset)]

        predicted_val = predict_next_stock(lstm_model, stocks)

        slope = (predicted_val[0][0] - stocks.to_numpy()[-1]) / 5
        projection_line = [stocks.to_numpy()[-1] + i * slope for i in range(1, 6)]
        project_index = [stocks.index[-1] + pd.Timedelta(i, unit='D') for i in range(1, 6)]
        projection = pd.Series(data=projection_line, index=project_index)
        data = pd.concat([stocks, projection], axis=1, ignore_index=True)
        data = data.rename(columns={0: asset[0], 1: 'Predicted value'})

        st.line_chart(data)

        predicted_price = predicted_val[0][0]
        current_price = stocks.to_numpy()[-1]
        predicted_price_change = ((predicted_price - current_price) / current_price) * 100

        emoji = '🚀📈' if predicted_price_change > 0 else '💔📉'

        st.write(
            f"""{emoji} LSTM model predicts the stock to be valued at {predicted_price:.2f} in 5 days
             ({'+' if predicted_price_change > 0 else ''}{predicted_price_change:.2f}%)."""
        )

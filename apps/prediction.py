import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import sd_material_ui

from datetime import timedelta
from datetime import datetime

import plotly.plotly as py
import plotly.graph_objs as go

import api
from app import app, server
import json

import numpy as np
import pandas as pd

from tensorflow.keras.models import model_from_json
from tensorflow.keras import backend as K

layout = html.Div([
    # Hidden div inside the app that stores the intermediate value
    html.Div(id='intermediate-value', style={'display': 'none'}),

    dcc.Dropdown(
        id='company-dropdown',
        placeholder="Select company",
        multi=False,
        clearable=True,
        options=api.nasdaq_parse("https://www.nasdaq.com/quotes/nasdaq-100-stocks.aspx"),
    ),

    dcc.Graph(id='stock-graph-prediction'),

    html.Div(
        html.Div(
            id='rl-decision',
        ),
        # Use columns for different model prediction
        # className="two columns",
    )
    ])


@app.callback(
    Output('intermediate-value', 'children'),
    [Input('company-dropdown', 'value')])
def store_data(value):
    """
    Callback to get stock data from the API and store it in a hidden div.
    """
    if(value is None):
        return

    # Make the API call
    data = api.get_hidden_stocks_daily(value)

    # Store a JSON serialized version of the data
    json_data = json.loads(data)
    return json.dumps(json_data)


@app.callback(
    Output('stock-graph-prediction', 'figure'),
    [Input('intermediate-value', 'children')])
def graph_stocks_prediction_daily(json_data):
    """
    Callback to get stock data from the hidden div, draw a graph from it and make
    predictions for the next Stock Prices (and graph those).
    """
    # Parse
    json_res = json.loads(json_data)
    series = json_res["Time Series (Daily)"]
    days = [day for day in series]
    closing = [float(series[day]["4. close"]) for day in days]

    # Graph the current Stock Prices
    traces = []
    traces.append(go.Scatter(
        x=days,
        y=closing,
        name="Stock Prices",
        line = dict(color = '#1125ff'),
        opacity = 0.8
    ))

    # Get the last 25 days stock prices
    model_input = closing[:25]
    model_input = [float(numeric_string) for numeric_string in model_input]
    model_input = np.reshape(model_input, (1, 1, 25))

    # Load model
    json_file = open('models/lstm_variation_model.json', 'r')
    loaded_model_json = json_file.read()
    json_file.close()
    loaded_model = model_from_json(loaded_model_json)
    # Load weights into new model
    loaded_model.load_weights("models/lstm_variations.h5")

    # Run model
    prediction = loaded_model.predict(model_input)[0]
    # Reset for future model predictions
    K.clear_session()

    # Process predictions from stock variations to stock values
    variations = prediction + 1
    predicted = variations * closing[0]

    # Get the index
    start_day = days[0]
    start_day = datetime.strptime(start_day, '%Y-%m-%d')
    days = []
    next_day = start_day + timedelta(days=1)
    days.append(next_day.strftime('%Y-%m-%d'))
    next_day = next_day + timedelta(days=1)
    days.append(next_day.strftime('%Y-%m-%d'))
    next_day = next_day + timedelta(days=1)
    days.append(next_day.strftime('%Y-%m-%d'))
    next_day = next_day + timedelta(days=1)
    days.append(next_day.strftime('%Y-%m-%d'))
    next_day = next_day + timedelta(days=1)
    days.append(next_day.strftime('%Y-%m-%d'))

    # Graph predictions
    traces.append(go.Scatter(
        x=days,
        y=predicted,
        name="Predictions",
        mode = 'lines',
        line = dict(color = '#56fc0a'),
        opacity = 0.8
    ))

    return {
        'data': traces,
        'layout': go.Layout(
            title='Time Series of the Company stock',
            xaxis=dict(
                rangeselector=dict(
                    buttons=list([
                        dict(count=7,
                             label='1w',
                             step='day',
                             stepmode='backward'),
                        dict(count=1,
                             label='1m',
                             step='month',
                             stepmode='backward'),
                        dict(count=3,
                             label='3m',
                             step='month',
                             stepmode='backward'),
                        dict(step='all')
                    ])
                ),
                rangeslider=dict(
                    visible = True
                ),
                type='date'
            )
        )
    }


@app.callback(
    Output('rl-decision', 'children'),
    [Input('intermediate-value', 'children'),
     Input('stock-graph-prediction', 'figure')])
def predict_stocks_decision_daily(json_data, figure):
    """
    Callback to get stock data from the hidden div and perform RL to predict the optimal decision to make.
    """
    # Parse
    json_res = json.loads(json_data)
    series = json_res["Time Series (Daily)"]
    days = [day for day in series]
    closing = [float(series[day]["4. close"]) for day in days]

    # Get the last 100 days stock prices
    model_input = closing[:100]
    model_input = [float(numeric_string) for numeric_string in model_input]
    model_input = np.reshape(model_input, (1, 1, 100))

    # Load model
    json_file = open('models/dqn_model.json', 'r')
    loaded_model_json = json_file.read()
    json_file.close()
    loaded_model = model_from_json(loaded_model_json)
    # load weights into new model
    loaded_model.load_weights("models/dqn_weights.h5")
    # Run model
    decisions = loaded_model.predict(model_input)
    # Reset for future model predictions
    K.clear_session()

    # Render output
    if np.argmax(decisions) == 0:    # Stay
        return sd_material_ui.Paper(children=[sd_material_ui.FontIcon(className='material-icons',
                                                                      iconName='trending_flat',
                                                                      hoverColor="#1125ff"),
                                              html.P('The Deep Q Network advices to ignore this stock')],
                                    zDepth=2,
                                    rounded=True,
                                    style=dict(height=150,
                                               width=150,
                                               margin=20,
                                               textAlign='center',
                                               display='inline-block'
                                               ),
                                    ),

    elif(np.argmax(decisions) == 1): # Buy
        return sd_material_ui.Paper(children=[sd_material_ui.FontIcon(className='material-icons',
                                                                      iconName='trending_up',
                                                                      hoverColor="#56fc0a"),
                                              html.P('The Deep Q Network advices to invest in this stock')],
                                    zDepth=2,
                                    rounded=True,
                                    style=dict(height=150,
                                               width=150,
                                               margin=20,
                                               textAlign='center',
                                               display='inline-block'
                                               ),
                                    ),

    else:                            # Sell
        return sd_material_ui.Paper(children=[sd_material_ui.FontIcon(className='material-icons',
                                                                      iconName='trending_down',
                                                                      hoverColor="#fc000c"),
                                              html.P('The Deep Q Network advices to sell this stock')],
                                    zDepth=2,
                                    rounded=True,
                                    style=dict(height=150,
                                               width=150,
                                               margin=20,
                                               textAlign='center',
                                               display='inline-block'
                                               ),
                                    ),


# @app.callback(
#     Output('stock-graph-intraday', 'figure'),
#     [Input('company-dropdown', 'value')])
# def get_stocks_intraday(value):
#     """
#     Callback to get stock data from the API and draw a graph from it.
#     """
#     # Return an empty graph untill a company is selected
#     if(value is None):
#         return
#
#     # For each company selected, make the API call and update the graph
#     traces = []
#     for symbol in value:
#         days, closing = api.get_stocks_intraday(symbol)
#         traces.append(go.Scatter(
#             x=days,
#             y=closing,
#             name=symbol,
#             line = dict(color = '#17BECF'),
#             opacity = 0.8
#         ))
#
#     return {
#         'data': traces,
#         'layout': go.Layout(
#             title='Time Series of the Company stock',
#             xaxis=dict(
#                 rangeselector=dict(
#                     buttons=list([
#                         dict(count=1,
#                              label='1h',
#                              step='hour',
#                              stepmode='backward'),
#                         dict(count=3,
#                              label='3h',
#                              step='hour',
#                              stepmode='backward'),
#                         dict(count=9,
#                              label='9h',
#                              step='hour',
#                              stepmode='backward'),
#                         dict(step='all')
#                     ])
#                 ),
#                 rangeslider=dict(
#                     visible = True
#                 ),
#                 type='date'
#             )
#         )
#     }

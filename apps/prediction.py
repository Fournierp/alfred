import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from datetime import datetime as dt
import sd_material_ui

import pandas as pd
import plotly.plotly as py
import plotly.graph_objs as go

import api
from app import app, server

from tensorflow.keras.models import load_model

layout = html.Div([
    dcc.Dropdown(
        id='company-dropdown',
        placeholder="Select company",
        multi=False,
        clearable=True,
        options=api.nasdaq_parse("https://www.nasdaq.com/quotes/nasdaq-100-stocks.aspx"),
    ),

    dcc.Graph(id='stock-graph-prediction'),

    sd_material_ui.Snackbar(id='rl-stay', open=False, message='Stay', autoHideDuration=4000,
    bodyStyle={
        "background": "#119DFF",
        "border": "1px solid #1125ff",
        "color": "white",
    }),
    sd_material_ui.Snackbar(id='rl-buy', open=False, message='Buy this Stock', autoHideDuration=4000,
    bodyStyle={
        "background": "#56fc0a",
        "border": "1px solid #43cc04",
        "color": "white",
    }),
    sd_material_ui.Snackbar(id='rl-sell', open=False, message='Sell this Stock', autoHideDuration=4000,
    bodyStyle={
        "background": "#fc000c",
        "border": "1px solid #c9040d",
        "color": "white",
    }),
    ])


# @app.callback(
#     Output('stock-graph-prediction', 'figure'),
#     [Input('company-dropdown', 'value')])
# def graph_stocks_daily(value):
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
#         days, closing = api.get_stocks_daily(symbol)
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
#                         dict(count=7,
#                              label='1w',
#                              step='day',
#                              stepmode='backward'),
#                         dict(count=1,
#                              label='1m',
#                              step='month',
#                              stepmode='backward'),
#                         dict(count=3,
#                              label='3m',
#                              step='month',
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
#

@app.callback(
    Output('stock-graph-prediction', 'figure'),
    [Input('company-dropdown', 'value')])
def graph_stocks_prediction_daily(value):
    """
    Callback to get stock data from the API and draw a graph from it.
    """
    # Return an empty graph untill a company is selected
    if(value is None):
        return

    # Make the API call
    days, closing = api.get_stocks_daily(symbol)
    # Graph the current Stock prices
    traces.append(go.Scatter(
        x=days,
        y=closing,
        name=symbol,
        line = dict(color = '#17BECF'),
        opacity = 0.8
    ))

    # Load model
    model = load_model('models/dqn50.h5')
    # Get the last 100 days stock prices
    model_input = closing[-100:]
    # Run model
    predictions = model.predict(model_input)[0]

    # Get the index
    start_day = days[-1]
    days = []
    for i in range(3):
        next_day = start_day + datetime.timedelta(days=1)
        days.append(next_day)

    traces.append(go.Scatter(
        x=days,
        y=predictions,
        name=symbol,
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
    Output('rl-stay', 'open'),
    [Input('company-dropdown', 'value')])
def predict_stay_stocks_daily(value):
    """
    Callback to get stock data from the API, perform RL to predict the optimal decision to make.
    """
    # Return an empty graph untill a company is selected
    if(value is None):
        return

    # For the company selected, make the API call and update the graph
    days, closing = api.get_stocks_daily(value)
    # Get the last 100 days stock prices
    model_input = closing[-100:]
    # Load model
    model = load_model('models/dqn50.h5')
    # Run model
    decisions = model.predict(model_input)
    # Render output
    if decisions == 0:    # Stay
        return True
    else:
        return False


@app.callback(
    Output('rl-buy', 'open'),
    [Input('company-dropdown', 'value')])
def predict_buy_stocks_daily(value):
    """
    Callback to get stock data from the API, perform RL to predict the optimal decision to make.
    """
    # Return an empty graph untill a company is selected
    if(value is None):
        return

    # For the company selected, make the API call and update the graph
    days, closing = api.get_stocks_daily(value)
    # Get the last 100 days stock prices
    model_input = closing[-100:]
    # Load model
    model = load_model('models/dqn50')
    # Run model
    decisions = model.predict(model_input)
    # Render output
    if decisions == 1:    # Buy
        return True
    else:
        return False


@app.callback(
    Output('rl-sell', 'open'),
    [Input('company-dropdown', 'value')])
def predict_sell_stocks_daily(value):
    """
    Callback to get stock data from the API, perform RL to predict the optimal decision to make.
    """
    # Return an empty graph untill a company is selected
    if(value is None):
        return

    # For the company selected, make the API call and update the graph
    days, closing = api.get_stocks_daily(value)
    # Get the last 100 days stock prices
    model_input = closing[-100:]
    # Load model
    model = load_model('models/dqn50')
    # Run model
    decisions = model.predict(model_input)
    # Render output
    if decisions == 2:    # Sell
        return True
    else:
        return False


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

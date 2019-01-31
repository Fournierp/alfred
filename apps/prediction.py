import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from datetime import datetime as dt

import pandas as pd
import plotly.plotly as py
import plotly.graph_objs as go

import api
from app import app, server

layout = [
    dcc.Dropdown(
        id='company-dropdown',
        placeholder="Select companies",
        multi=True,
        clearable=True,
        options=api.nasdaq_parse("https://www.nasdaq.com/quotes/nasdaq-100-stocks.aspx"),
    ),

    dcc.Graph(id='stock-graph-intraday'),
    ]


@app.callback(
    Output('stock-graph-intraday', 'figure'),
    [Input('company-dropdown', 'value')])
def get_stocks_intraday(value):
    """
    Callback to get stock data from the API and draw a graph from it.
    """
    # Return an empty graph untill a company is selected
    if(value is None):
        return

    # For each company selected, make the API call and update the graph
    traces = []
    for symbol in value:
        days, closing = api.get_stocks_intraday(symbol)
        traces.append(go.Scatter(
            x=days,
            y=closing,
            name=symbol,
            line = dict(color = '#17BECF'),
            opacity = 0.8
        ))

    return {
        'data': traces,
        'layout': go.Layout(
            title='Time Series of the Company stock',
            xaxis=dict(
                rangeselector=dict(
                    buttons=list([
                        dict(count=1,
                             label='1h',
                             step='hour',
                             stepmode='backward'),
                        dict(count=3,
                             label='3h',
                             step='hour',
                             stepmode='backward'),
                        dict(count=9,
                             label='9h',
                             step='hour',
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

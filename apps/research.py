import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

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
        options= api.nasdaq_parse("https://www.nasdaq.com/quotes/nasdaq-100-stocks.aspx"),
    ),

    dcc.Graph(id='stock-graph'),
]


@app.callback(
    Output('stock-graph', 'figure'),
    [Input('company-dropdown', 'value')])
def get_stocks_daily(value):
    print(value)
    if(value is None):
        return

    traces = []
    for symbol in value:
        days, closing = api.stock(symbol, "TIME_SERIES_DAILY")
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
                             label='1d',
                             step='day',
                             stepmode='backward'),
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

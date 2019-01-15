import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

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

    dcc.Graph(id='stock-graph'),

    # table div
    html.Div(
        id="news_table",
        className="row",
        style={
            "maxHeight": "350px",
            "overflowY": "scroll",
            "padding": "8",
            "marginTop": "5",
            "backgroundColor":"white",
            "border": "1px solid #C8D4E3",
            "borderRadius": "3px"
        },
    ),
]


@app.callback(
    Output('stock-graph', 'figure'),
    [Input('company-dropdown', 'value')])
def get_stocks_daily(value):
    if(value is None):
        return

    traces = []
    for symbol in value:
        days, closing = api.get_stocks(symbol, "TIME_SERIES_DAILY")
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


@app.callback(
    Output('news_table', 'children'),
    [Input('company-dropdown', 'value')])
def news_table(companies):
    df = pd.DataFrame(columns=["Souce", "Title", "Published At", "Link"])

    if(companies is None):
        return

    nasdaq = api.nasdaq_parse("https://www.nasdaq.com/quotes/nasdaq-100-stocks.aspx")

    formatted_companies = ""
    for company in nasdaq:
        if(company['value'] == companies[0]):
            formatted_companies = company['label']

    res = api.get_articles(formatted_companies)

    number_of_results = res["totalResults"]

    if(int(number_of_results) == 0):
        return
        
    else:
        counter = 0
        for result in res["articles"]:
            if(counter > 9):
                break
            tmp = pd.DataFrame([[result["source"]["name"], result["title"],
                            result["publishedAt"], result["url"]]],
                            columns=["Souce", "Title", "Published At", "Link"])
            df = df.append(tmp, ignore_index=True)
            counter += 1

        return html.Table(
            # Header
            [html.Tr([html.Th(col) for col in df.columns])] +

            # Body
            [
                html.Tr(
                    [
                        html.Td(df.iloc[i][col])
                        for col in df.columns
                    ]
                )
                for i in range(len(df))
            ]
        )

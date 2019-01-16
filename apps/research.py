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

    dcc.Graph(id='stock-graph'),

    html.Div(
        [
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
        ],
        className="row tabs_div"
        )
    ]


@app.callback(
    Output('stock-graph', 'figure'),
    [Input('company-dropdown', 'value')])
def get_stocks_daily(value):
    """
    Callback to get stock data from the API and draw a graph from it.
    """
    # Return an empty graph untill a company is selected
    if(value is None):
        return

    # For each company selected, make the API call and update the graph
    traces = []
    for symbol in value:
        days, closing = api.get_stocks_daily(symbol)
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
    """
    Callback to get the news headlines from the API and fill a table.
    """
    df = pd.DataFrame(columns=["Souce", "Title", "Published on"])

    # Return an empty header untill dates and companies are selected
    if(companies is None or companies == []):
        return

    # API call
    res = api.get_articles(companies)

    # Return an empty table if no headline was found
    number_of_results = res["totalResults"]
    if(int(number_of_results) == 0):
        return html.Table(
            # Header
            [html.Tr([html.Th(col) for col in df.columns])]
        )

    else:
        # Take the 10 most relevant articles published in the range and display
        # the source, the title, the date and link
        counter = 0
        links = []
        for result in res["articles"]:
            if(counter > 9):
                break
            tmp = pd.DataFrame([[result["source"]["name"], result["title"],
                            result["publishedAt"][:10]]],
                            columns=["Souce", "Title", "Published on"])
            df = df.append(tmp, ignore_index=True)
            links.append(result["url"])
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
                    ] +
                    [
                        html.A(
                            children='Reference',
                            target= '_blank',
                            href=links[i]
                        ),
                    ]
                )
                for i in range(len(df))
            ]
        )

# -*- coding: utf-8 -*-
import flask
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from app import app, server
from apps import research, prediction


app.layout = html.Div([
    html.H1('Alfred Virtual Assistant'),

    html.Div('''
        Alfred: A web application to assist you with your stock investments.
    '''),

    html.Br(),

    html.Div([

        dcc.Tabs(
            id="tabs",
            style={"height":"20","verticalAlign":"middle"},
            children=[
                dcc.Tab(label="Live", value="one"),
                dcc.Tab(label="Research", value="two"),
                dcc.Tab(label="Predictions", value="three"),
            ],
            value="two",
        )

        ],
        className="row tabs_div"
    ),

    html.Div(id="tab_content", className="row", style={"margin": "2% 3%"}),

])


@app.callback(
    Output("tab_content", "children"),
    [Input("tabs", "value")])
def render_content(tab):
    """
    Callback to switch between tabs.
    """
    if tab == "one":
        return html.Div([
            html.H3('Tab content 1')
        ])
    elif tab == "two":
        return research.layout
    elif tab == "three":
        return prediction.layout
    else:
        return research.layout


if __name__ == "__main__":
    app.run_server(debug=True)

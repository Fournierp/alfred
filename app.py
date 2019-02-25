import flask
import dash
import dash_core_components as dcc
import dash_html_components as html

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css',
                        'https://fonts.googleapis.com/icon?family=Material+Icons']

server = flask.Flask("Alfred")
app = dash.Dash("Alfred", server=server, external_stylesheets=external_stylesheets)
app.config.suppress_callback_exceptions = True

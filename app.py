import os

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
from dash.dependencies import Input, Output, State

app = dash.Dash(__name__)
server = app.server

# Custom Script for Heroku
if 'DYNO' in os.environ:
    app.scripts.append_script({
        'external_url': 'https://cdn.rawgit.com/chriddyp/ca0d8f02a1659981a0ea7f013a378bbd/raw/e79f3f789517deec58f41251f7dbb6bee72c44ab/plotly_ga.js'
    })

app.layout = html.Div(children=[
    # .container class is fixed, .container.scalable is scalable
    html.Div(className="banner", children=[
        # Change App Name here
        html.H2('App Name'),

        html.Img(
            src="https://s3-us-west-1.amazonaws.com/plotly-tutorials/logo/new-branding/dash-logo-by-plotly-stripe-inverted.png"
        )
    ]),

    html.Div(id='body', className='container scalable', children=[
        # Add your code here

        html.Img(
            style={'width': '50%'},
            src="https://images.unsplash.com/photo-1530593697255-8f5822e1dcac?ixlib=rb-0.3.5&ixid=eyJhcHBfaWQiOjEyMDd9&s=93dcb4421a7d1550b1f2f83e4bf30ad0&auto=format&fit=crop&w=1950&q=80"
        ),

        html.Div(
            html.A("Click here for the source image", href='https://unsplash.com/photos/sTuW5DPo6AI')
        )
    ])
])

external_css = [
    # Normalize the CSS
    "https://cdnjs.cloudflare.com/ajax/libs/normalize/7.0.0/normalize.min.css",
    # Fonts
    "https://fonts.googleapis.com/css?family=Open+Sans|Roboto",
    "https://maxcdn.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css",
    # Base Stylesheet, replace this with your own base-styles.css using Rawgit
    "https://cdn.rawgit.com/xhlulu/9a6e89f418ee40d02b637a429a876aa9/raw/base-styles.css",
    # Custom Stylesheet, replace this with your own custom-styles.css using Rawgit
    "https://cdn.rawgit.com/xhlulu/638e683e245ea751bca62fd427e385ab/raw/custom-styles.css"
]

for css in external_css:
    app.css.append_css({"external_url": css})

# Running the server
if __name__ == '__main__':
    app.run_server(debug=True)

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go

from Data import *

app = dash.Dash(__name__)
server = app.server
app.scripts.config.serve_locally = True

df = pd.read_csv("data/wafer-production.csv").dropna()


def generate_metrics_table():
    table = html.Table(
        id='Metric summary table',
        children=[
            # Header
            html.Tr(
                id='table-header',
                children=[html.Th(col) for col in column]),

            # Body
            html.Tr(
                id='table-body',
                children=[]
            )
        ]
    )
    return table


def generate_section_banner(title):
    return html.Div(
        className="section-banner",
        children=title
    )


app.layout = html.Div(
    children=[
        # Banner
        html.Div(
            id='banner',
            className="banner", children=[
                html.H5('Manufacturing SPC Dashboard - Process Control and Exception Reporting'),
                html.Img(
                    src="https://s3-us-west-1.amazonaws.com/plotly-tutorials/logo/new-branding/dash-logo-by-plotly-stripe-inverted.png"
                )
            ]
        ),

        # Tabs
        html.Div(
            id='tab-bar',
            children=[
                dcc.Tabs(
                    id="tabs",
                    value="tab-2",
                    children=[
                        dcc.Tab(label='What is SPC?', value='tab-1'),
                        dcc.Tab(label='Control Chart Dashboard 1', value='tab-2'),
                        dcc.Tab(label='Control Chart Dashboard 2', value='tab-3'),
                    ]
                )
            ]
        ),
        # Main app
        html.Div(
            id='tabs-content',
            className='container scalable',
            children=[
                html.Div(
                    id='top-section-container',
                    className='row',
                    children=[
                        # Metrics summary
                        html.Div(
                            id='metric-summary-session',
                            className='six columns',
                            children=[
                                generate_section_banner('Process Control Metrics Summary'),
                                generate_metrics_table()
                            ]
                        ),
                        # Treemap
                        html.Div(
                            id='treemap-session',
                            className='six columns',
                            children=generate_section_banner('% OOC per Parameter')
                        )
                    ]
                ),
                # Control chart
                html.Div(
                    id='control-chart-container',
                    className='twelve columns',
                    children=[
                        generate_section_banner('Control Chart'),

                        dcc.Interval(
                            id='interval-component',
                            interval=1 * 1000,  # in milliseconds
                            n_intervals=0
                        ),

                        dcc.Graph(
                            id="control-chart-live",
                            figure=go.Figure({
                                'data': [{'x': [], 'y': []}]
                            })
                        )
                    ]
                )
            ]
        )
    ]
)


@app.callback(
    Output('control-chart-live', 'figure'),
    [Input('interval-component', 'n_intervals')],
    state=[State('control-chart-live', 'figure')]
)
def update_chart(interval, curr_fig):
    dff, stats, count, mean, ucl, lcl = get_graph_trendline(df, 'Length1')
    layout = {
        'shapes':
            [
                {
                    'type': 'line',
                    'x0': 1,
                    'y0': ucl,
                    'x1': count,
                    'y1': ucl,
                    'line': {
                        'color': 'rgb(50, 171, 96)',
                        'width': 2,
                        'dash': 'dashdot'
                    }
                },

                {
                    'type': 'line',
                    'x0': 1,
                    'y0': lcl,
                    'x1': count,
                    'y1': lcl,
                    'line': {
                        'color': 'rgb(50, 171, 96)',
                        'width': 2,
                        'dash': 'dashdot'
                    }
                }]
    }

    x_array = dff['Batch_Num'].tolist()
    y_array = dff['Length1'].tolist()

    curr_fig['data'][0]['x'].append(x_array[interval])
    curr_fig['data'][0]['y'].append(y_array[interval])

    curr_fig['layout'] = layout

    return curr_fig


# Running the server
if __name__ == '__main__':
    app.run_server(dev_tools_hot_reload=False, debug=True, host='0.0.0.0', port=8051)


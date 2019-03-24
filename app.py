import os
import sys
import time

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
import dash_daq as daq
import plotly.figure_factory as ff
import squarify

from Data import df, state_dict, populate_ooc

app = dash.Dash(__name__)
server = app.server
app.scripts.config.serve_locally = True
app.config['suppress_callback_exceptions'] = True

params = list(df)
max_length = len(df)


def generate_metric_row(id, style, col1, col2, col3, col4, col5, col6):
    if style is None:
        style = {
            'height': '100px',
            'width': '100%',
        }
    return html.Div(
        id=id,
        className='row metric-row',
        style=style,
        children=[
            html.Div(
                id=col1['id'],
                style={},
                className='one column',
                children=col1['children']
            ),
            html.Div(
                id=col2['id'],
                style={},
                className='one column',
                children=col2['children']
            ),
            html.Div(
                id=col3['id'],
                style={
                    'height': '100%',
                },
                className='four columns',
                children=col3['children']
            ),
            html.Div(
                id=col4['id'],
                style={},
                className='one column',
                children=col4['children']
            ),
            html.Div(
                id=col5['id'],
                style={
                    'height': '100%',

                },
                className='three columns',
                children=col5['children']
            ),
            html.Div(
                id=col6['id'],
                style={},
                className='one column',
                children=col6['children']
            )
        ]
    )


def create_callback(retfunc):
    """
    pass *input_value to retfunc

    creates a callback function
    """

    def callback(*input_values):
        if input_values is not None and input_values != 'None':
            try:
                ret_val = retfunc(*input_values)
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print('Callback Exception:', e, exc_type, fname, exc_tb.tb_lineno)
                print('parameters:', *input_values)
            return ret_val
        else:
            return []

    return callback


def generate_graph(interval, value, fig):
    col = fig['data'][0]['name']

    if col != value:  # click
        col = value
    # else is interval

    stats = state_dict[col]
    col_data = stats['data']
    count = stats['count']
    mean = stats['mean']
    ucl = stats['ucl']
    lcl = stats['lcl']
    usl = stats['usl']
    lsl = stats['lsl']
    # minimum = stats['min']
    # maximum = stats['max']

    x_array = state_dict['Batch']['data'].tolist()
    y_array = col_data.tolist()
    fig['data'][0]['name'] = col

    if interval > max_length:
        total_count = max_length - 1
    else:
        total_count = interval

    fig['data'][0]['y'] = y_array[:total_count]
    fig['data'][0]['x'] = x_array[:total_count]

    len_figure = len(fig['data'][0]['x'])

    fig['layout'] = dict(title='Individual measurements', showlegend=True, xaxis={
        'zeroline': False,
        'title': 'Batch_Num',
        'showline': False
    }, yaxis={
        'title': value,
        'autorange': True
    }, annotations=[
        {'x': len_figure + 2, 'y': lcl, 'xref': 'x', 'yref': 'y', 'text': 'LCL:' + str(round(lcl, 2)),
         'showarrow': True},
        {'x': len_figure + 2, 'y': ucl, 'xref': 'x', 'yref': 'y', 'text': 'UCL: ' + str(round(ucl, 2)),
         'showarrow': True},
        {'x': len_figure + 2, 'y': usl, 'xref': 'x', 'yref': 'y', 'text': 'USL: ' + str(round(usl, 2)),
         'showarrow': True},
        {'x': len_figure + 2, 'y': lsl, 'xref': 'x', 'yref': 'y', 'text': 'LSL: ' + str(round(lsl, 2)),
         'showarrow': True}
    ], shapes=[
        {
            'type': 'line',
            'xref': 'x',
            'yref': 'y',
            'x0': 1,
            'y0': usl,
            'x1': len_figure + 2,
            'y1': usl,
            'line': {
                'color': 'rgb(50, 171, 96)',
                'width': 1,
                'dash': 'dashdot'
            }
        },
        {
            'type': 'line',
            'xref': 'x',
            'yref': 'y',
            'x0': 1,
            'y0': lsl,
            'x1': len_figure + 2,
            'y1': lsl,
            'line': {
                'color': 'rgb(50, 171, 96)',
                'width': 1,
                'dash': 'dashdot'
            }
        },
        {
            'type': 'line',
            'xref': 'x',
            'yref': 'y',
            'x0': 1,
            'y0': ucl,
            'x1': len_figure + 2,
            'y1': ucl,
            'line': {
                'color': 'rgb(255,127,80)',
                'width': 1,
                'dash': 'dashdot'
            }
        },
        {
            'type': 'line',
            'xref': 'x',
            'yref': 'y',
            'x0': 1,
            'y0': mean,
            'x1': len_figure + 2,
            'y1': mean,
            'line': {
                'color': 'rgb(255,127,80)',
                'width': 2
            }
        },
        {
            'type': 'line',
            'xref': 'x',
            'yref': 'y',
            'x0': 1,
            'y0': lcl,
            'x1': len_figure + 2,
            'y1': lcl,
            'line': {
                'color': 'rgb(255,127,80)',
                'width': 1,
                'dash': 'dashdot'
            }
        }
    ])

    return fig


def generate_metric_list():
    # Build header
    metric_header_div = [
        generate_metric_row(
            'metric_header',
            {
                'height': '50px'
            },
            {
                'id': "m_header_1",
                'children': html.Div("Parameter")
            },
            {
                'id': "m_header_2",
                'children': html.Div("Count")
            },
            {
                'id': "m_header_3",
                'children': html.Div("Sparkline")
            },
            {
                'id': "m_header_4",
                'children': html.Div("OOC%")
            },
            {
                'id': "m_header_5",
                'children': html.Div("%OOC")
            },
            {
                'id': "m_header_6",
                'children': html.Div("P/F")
            }),
    ]

    input_list = []
    children = []
    for index in range(1, len(params)):
        item = params[index]
        # Add individual rows into input list

        button_id = item + '_param'
        input_list.append(Input(button_id, 'n_clicks'))

        sparkline_graph_id = item + '_sparkline_graph'
        count_id = item + '_count'
        ooc_percentage_id = item + '_OOC_number'
        ooc_graph_id = item + '_OOC_graph'
        indicator_id = item + '_indicator'

        children.append(
            generate_metric_row(
                item + "_row", None,
                {
                    'id': item,
                    'children': html.Button(
                        id=button_id,
                        children=item,
                        style={
                            'width': '100%',
                        }
                    )
                },
                {
                    'id': count_id,
                    'children': '0'
                },
                {
                    'id': item + '_sparkline',
                    'children': dcc.Graph(
                        id=sparkline_graph_id,
                        style={
                            'width': '100%',
                            'height': '95%',
                        },
                        config={
                            'staticPlot': False,
                            'editable': False,
                            'displayModeBar': False
                        },
                        figure=go.Figure({
                            'data': [{'x': [], 'y': [], 'mode': 'lines+markers', 'name': item, }],
                            'layout': {
                                'margin': dict(
                                    l=0, r=0, t=4, b=4, pad=0
                                )
                            }
                        }))
                },
                {
                    'id': ooc_percentage_id,
                    'children': '0.00%'
                },
                {
                    'id': ooc_graph_id + '_container',
                    'children': dcc.Graph(
                        id=ooc_graph_id,
                        style={
                            'width': '100%',
                            'height': '95%'
                        },
                        config={
                            'staticPlot': False,
                            'editable': False,
                            'displayModeBar': False
                        },
                        figure=ff.create_bullet(
                            data=[{
                                "label": "label",
                                "range": [4, 7, 10],
                                "performance": [0, 4]
                            }],
                            measures='performance',
                            ranges='range',
                            titles='label',
                            height=50,
                            width=150,
                            margin=dict(l=5, r=0, t=0, b=0, pad=0),
                        )
                    )
                },
                {
                    'id': item + '_pf',
                    'children': daq.Indicator(
                        id=indicator_id,
                        value=True,
                        color='#00cc96'
                    )
                },
            ))

        # Update total count, ooc_percentage in Metrics
        @app.callback(
            output=[
                Output(count_id, 'children'),
                Output(ooc_percentage_id, 'children'),
                Output(ooc_graph_id, 'figure'),
                Output(indicator_id, 'color')
            ],
            inputs=[
                Input('interval-component', 'n_intervals'),
            ],
            state=[
                State(button_id, 'children')
            ]
        )
        def update_count(interval, col):
            if interval >= max_length:
                total_count = max_length - 1
            else:
                total_count = interval
            ooc_percentage_f = state_dict[col]['ooc'][total_count] * 100
            ooc_percentage_str = "%.2f" % ooc_percentage_f + '%'

            if ooc_percentage_f > 10:
                ooc_percentage_f = 10

            ooc_fig = ff.create_bullet(
                data=[{
                    "label": "label",
                    "range": [4, 7, 10],
                    "performance": [0, ooc_percentage_f],
                }],
                measures='performance',
                ranges='range',
                titles='label',
                height=50,
                width=150,
                margin=dict(l=5, r=0, t=0, b=0, pad=0),
                font={'size': 1},
                measure_colors=['rgb(0,0,0)', 'rgb(0,0,0)'],
                range_colors=['rgb(152,251,152)', 'rgb(250,128,114)'],
            )
            color = '#00cc96'
            if ooc_percentage_f > 5:
                color = '#FF0000'

            return total_count, ooc_percentage_str, ooc_fig, color

        # Update sparkline plot in Metrics

        @app.callback(
            output=Output(sparkline_graph_id, 'figure'),
            inputs=[
                Input('interval-component', 'n_intervals')
            ],
            state=[
                State(button_id, 'children')
            ]
        )
        def generate_sparkline_graph(interval, col):

            if interval >= max_length:
                total_count = max_length - 1
            else:
                total_count = interval

            x_array = state_dict['Batch']['data'].tolist()
            y_array = state_dict[col]['data'].tolist()

            new_fig = go.Figure({
                'data': [{'x': x_array[:total_count], 'y': y_array[:total_count], 'mode': 'lines+markers',
                          'name': item}],
                'layout': {
                    'margin': dict(
                        l=0, r=0, t=4, b=4, pad=0
                    )
                }
            })

            return new_fig


    metric_header_div.append(
        html.Div(
            style={
                'height': '100%',
                'overflow': 'scroll'
            },
            children=children
        )
    )

    input_list.append(Input('interval-component', 'n_intervals'))
    # app referencing the dash app object
    app.callback(output=[Output('control-chart-live', 'figure'), Output('click_state', 'data')],
                 inputs=input_list,
                 state=[State('control-chart-live', 'figure'), State('click_state', 'data')]
                 )(create_callback(update_graph))

    return html.Div(
        id='metric_list',
        className='row',
        style={
            'height': '100%'
        },
        children=metric_header_div
    )


# Update live-SPC chart upon click on metric row
def update_graph(*inputs):
    click_state = inputs[-1]
    interval = inputs[-3]
    figure = inputs[-2]

    if len(click_state) == 0:
        return generate_graph(interval, params[3], figure), inputs[:-3]
    for j in range(len(inputs) - 3):
        if click_state[j] != inputs[j]:
            return generate_graph(interval, params[j + 1], figure), inputs[:-3]

    curr_fig = figure['data'][0]['name']
    return generate_graph(interval, curr_fig, figure), inputs[:-3]


# default_treemap
def generate_default_treemap(batch_num):

    x = 0.
    y = 0.
    width = 100.
    height = 100.

    values = []
    for param in params[1:]:
        size_of_rect = (state_dict[param]['ooc'][batch_num]*100) + 1
        values.append(size_of_rect)

    normed = squarify.normalize_sizes(values, width, height)
    rects = squarify.squarify(normed, x, y, width, height)

    color_brewer = ['rgb(75,103,144)', 'rgb(101,123,159)', 'rgb(127,143,175)', 'rgb(152,165,191)', 'rgb(177,187,206)',
                    'rgb(203,209,222)']

    #TODO: colormap for rect


    shapes = []
    annotations = []
    counter = 0


    for r in rects:
        shapes.append(
            dict(
                type='rect',
                x0=r['x'],
                y0=r['y'],
                x1=r['x'] + r['dx'],
                y1=r['y'] + r['dy'],
                line=dict(width=1),
                fillcolor=color_brewer[counter]
            )
        )
        annotations.append(
            dict(
                x=r['x'] + (r['dx'] / 2),
                y=r['y'] + (r['dy'] / 2),
                text=params[1:][counter],
                showarrow=False
            )
        )
        counter = counter + 1
        if counter >= len(color_brewer):
            counter = 0

    t = time.time()

    # For hover text
    trace0 = go.Scatter(
        x=[r['x'] + (r['dx'] / 2) for r in rects],
        y=[r['y'] + (r['dy'] / 2) for r in rects],
        text=[str(v) for v in params[1:]],
        mode='text',
    )

    layout = dict(
        height=400,
        width=500,
        margin=dict(l=0, r=0, t=10, b=0),
        xaxis=dict(showgrid=False, zeroline=False),
        yaxis=dict(showgrid=False, zeroline=False),
        shapes=shapes,
        annotations=annotations,
        hovermode='closest',
        config=dict(displayModeBar=False)
    )
    # print(time.time()-t)

    return trace0, layout



def generate_tree_map():
    return html.Div(
        id='treemap-container',
        style={'padding': '10px 0px'},
        children=dcc.Graph(
            id='treemap',
            figure=dict(data=[generate_default_treemap(0)[0]], layout=generate_default_treemap(0)[1])
        )
    )


@app.callback(
    output=Output('treemap', 'figure'),
    inputs=[
        Input('interval-component', 'n_intervals')]
)
def update_treemap(interval):
    if interval >= max_length:
        total_count = max_length - 1
    else:
        total_count = interval

    new_fig = dict(data=[generate_default_treemap(total_count)[0]], layout=generate_default_treemap(total_count)[1])
    return new_fig



def build_top_panel():
    return html.Div(
        id='top-section-container',
        className='row',
        style={
            'height': '45vh'
        },
        children=[
            # Metrics summary
            html.Div(
                id='metric-summary-session',
                className='eight columns',
                style={'height': '100%'},
                children=[
                    generate_section_banner('Process Control Metrics Summary'),
                    html.Div(
                        id='metric_div',
                        style={
                            'height': '100%',
                            'width': '100%',
                            'margin': '10px 5px'
                        },
                        children=generate_metric_list()
                    )
                ]
            ),
            # Tree Map
            html.Div(
                id='treemap-session',
                className='four columns',
                children=[
                    generate_section_banner('% OOC per Parameter'),
                    generate_tree_map()
                ]
            )
        ]
    )


def generate_section_banner(title):
    return html.Div(
        className="section-banner",
        children=title
    )


def build_chart_panel():
    return html.Div(
        id='control-chart-container',
        className='twelve columns',
        children=[
            generate_section_banner('Live SPC Chart'),

            dcc.Interval(
                id='interval-component',
                interval=1 * 1000,  # in milliseconds
                n_intervals=0
            ),

            dcc.Graph(
                id="control-chart-live",
                figure=go.Figure({
                    'data': [{'x': [], 'y': [], 'mode': 'lines+markers', 'name': params[3]}]
                }
                )
            )
        ]
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
                html.Div(id='test-update', children='test'),
                build_top_panel(),
                build_chart_panel(),
                # daq.LEDDisplay(
                #     id='operator-id',
                #     value='2701'
                # ),
                # daq.LEDDisplay(
                #     id='batch_num',
                #     value='620'
                # ),
                dcc.Store(
                    id='click_state',
                    data=[]
                )
            ]
        )
    ]
)

# Running the server
if __name__ == '__main__':
    app.run_server(dev_tools_hot_reload=False, debug=True, host='0.0.0.0', port=8051, use_reloader=False)

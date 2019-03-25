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

suffix_row = '_row'
suffix_button_id = '_button'
suffix_sparkline_graph = '_sparkline_graph'
suffix_count = '_count'
suffix_ooc_n = '_OOC_number'
suffix_ooc_g = '_OOC_graph'
suffix_indicator = '_indicator'


#  todo create a list of config


def root_layout():
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
                            dcc.Tab(label='Control Chart Dashboard 1', value='tab-2')
                        ]
                    )
                ]
            ),
            # Main app
            html.Div(
                id='tabs-content',
                className='container scalable',
                children=[
                    build_top_panel(),
                    build_chart_panel(),
                ]
            )
        ]
    )


def generate_section_banner(title):
    return html.Div(
        className="section-banner",
        children=title,
    )


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
                    generate_metric_list_header(),
                    html.Div(
                        # id='metric_div',
                        style={
                            'height': 'calc(100% - 90px)',
                            'width': '100%',
                            'overflow': 'scroll'
                        },
                        children=[
                            generate_para1_row(),
                            generate_para2_row(),
                            generate_para3_row(),
                            generate_para4_row(),
                            generate_para5_row()
                        ]
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


# Build header
def generate_metric_list_header():
    return generate_metric_row(
        'metric_header',
        {
            'height': '30px',
            'margin': '10px 0px',
            'textAlign': 'center'
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
            'children': html.Div("Pass/Fail")
        })


def generate_para1_row():
    return generate_metric_row_helper(1)


def generate_para2_row():
    return generate_metric_row_helper(2)


def generate_para3_row():
    return generate_metric_row_helper(3)


def generate_para4_row():
    return generate_metric_row_helper(4)


def generate_para5_row():
    return generate_metric_row_helper(5)


def generate_metric_row_helper(index):
    item = params[index]

    div_id = item + suffix_row
    button_id = item + suffix_button_id
    sparkline_graph_id = item + suffix_sparkline_graph
    count_id = item + suffix_count
    ooc_percentage_id = item + suffix_ooc_n
    ooc_graph_id = item + suffix_ooc_g
    indicator_id = item + suffix_indicator

    return generate_metric_row(
        div_id, None,
        {
            'id': item,
            'children': html.Button(
                id=button_id,
                children=item,
                n_clicks_timestamp=0
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
                    'data': [{'x': [], 'y': [], 'mode': 'lines+markers', 'name': item}],
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
                        "range": [3, 5, 10],
                        "performance": [0, 4]
                    }],
                    measures='performance',
                    ranges='range',
                    titles='label',
                    height=50,
                    width=200,
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
        }
    )


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
                style={'textAlign': 'center'},
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


def build_chart_panel():
    return html.Div(
        id='control-chart-container',
        className='twelve columns',
        children=[
            generate_section_banner('Live SPC Chart'),

            dcc.Interval(
                id='interval-component',
                interval=2 * 1000,  # in milliseconds
                n_intervals=0
            ),

            dcc.Store(
                id='control-chart-state',
                data=params[1]
            ),
            dcc.Graph(
                id="control-chart-live",
                figure=go.Figure({
                    'data': [{'x': [], 'y': [], 'mode': 'lines+markers'}]
                }
                )
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


def generate_graph(interval, col):
    # col = fig['data'][0]['name']

    # if col != value:  # click
    #     col = value
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

    if interval > max_length:
        total_count = max_length - 1
    else:
        total_count = interval

    ooc_trace = {'x': [],
                 'y': [],
                 'name': 'OOC',
                 'mode': 'markers',
                 'marker': dict(color='rgba(210, 77, 87, 1)', symbol="square", size=11)
                 }

    for index, data in enumerate(y_array[:total_count]):
        if data >= ucl or data <= lcl:
            ooc_trace['x'].append(index + 1)
            ooc_trace['y'].append(data)

    fig = {
        'data': [
            {
                'x': x_array[:total_count],
                'y': y_array[:total_count],
                'mode': 'lines+markers',
                'name': col},

            ooc_trace
        ]
    }

    len_figure = len(fig['data'][0]['x'])

    fig['layout'] = dict(title='Individual measurements', showlegend=True, xaxis={
        'zeroline': False,
        'title': 'Batch_Num',
        'showline': False
    }, yaxis={
        'title': col,
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


#  ======= update each row at interval =========
@app.callback(
    output=[
        Output('Para1' + suffix_count, 'children'),
        Output('Para1' + suffix_sparkline_graph, 'figure'),
        Output('Para1' + suffix_ooc_n, 'children'),
        Output('Para1' + suffix_ooc_g, 'figure'),
        Output('Para1' + suffix_indicator, 'color')
    ],
    inputs=[Input('interval-component', 'n_intervals')],
)
def update_param1_row(interval):
    count, ooc_n, ooc_g, indicator = update_count(interval, 'Para1')
    spark_line_graph = update_spark_line_graph(interval, 'Para1')
    return count, spark_line_graph, ooc_n, ooc_g, indicator


@app.callback(
    output=[
        Output('Para2' + suffix_count, 'children'),
        Output('Para2' + suffix_sparkline_graph, 'figure'),
        Output('Para2' + suffix_ooc_n, 'children'),
        Output('Para2' + suffix_ooc_g, 'figure'),
        Output('Para2' + suffix_indicator, 'color')
    ],
    inputs=[Input('interval-component', 'n_intervals')],
)
def update_param1_row(interval):
    count, ooc_n, ooc_g, indicator = update_count(interval, 'Para2')
    spark_line_graph = update_spark_line_graph(interval, 'Para2')
    return count, spark_line_graph, ooc_n, ooc_g, indicator


@app.callback(
    output=[
        Output('Para3' + suffix_count, 'children'),
        Output('Para3' + suffix_sparkline_graph, 'figure'),
        Output('Para3' + suffix_ooc_n, 'children'),
        Output('Para3' + suffix_ooc_g, 'figure'),
        Output('Para3' + suffix_indicator, 'color')
    ],
    inputs=[Input('interval-component', 'n_intervals')],
)
def update_param1_row(interval):
    count, ooc_n, ooc_g, indicator = update_count(interval, 'Para3')
    spark_line_graph = update_spark_line_graph(interval, 'Para3')
    return count, spark_line_graph, ooc_n, ooc_g, indicator


@app.callback(
    output=[
        Output('Para4' + suffix_count, 'children'),
        Output('Para4' + suffix_sparkline_graph, 'figure'),
        Output('Para4' + suffix_ooc_n, 'children'),
        Output('Para4' + suffix_ooc_g, 'figure'),
        Output('Para4' + suffix_indicator, 'color')
    ],
    inputs=[Input('interval-component', 'n_intervals')],
)
def update_param1_row(interval):
    count, ooc_n, ooc_g, indicator = update_count(interval, 'Para4')
    spark_line_graph = update_spark_line_graph(interval, 'Para4')
    return count, spark_line_graph, ooc_n, ooc_g, indicator


@app.callback(
    output=[
        Output('Para5' + suffix_count, 'children'),
        Output('Para5' + suffix_sparkline_graph, 'figure'),
        Output('Para5' + suffix_ooc_n, 'children'),
        Output('Para5' + suffix_ooc_g, 'figure'),
        Output('Para5' + suffix_indicator, 'color')
    ],
    inputs=[Input('interval-component', 'n_intervals')],
)
def update_param1_row(interval):
    count, ooc_n, ooc_g, indicator = update_count(interval, 'Para5')
    spark_line_graph = update_spark_line_graph(interval, 'Para5')
    return count, spark_line_graph, ooc_n, ooc_g, indicator


#  ======= button to choose figure ============
@app.callback(
    output=Output('control-chart-live', 'figure'),
    inputs=[
        Input('interval-component', 'n_intervals'),
        Input('Para1' + suffix_button_id, 'n_clicks_timestamp'),
        Input('Para2' + suffix_button_id, 'n_clicks_timestamp'),
        Input('Para3' + suffix_button_id, 'n_clicks_timestamp'),
        Input('Para4' + suffix_button_id, 'n_clicks_timestamp'),
        Input('Para5' + suffix_button_id, 'n_clicks_timestamp'),
    ])
def update_control_chart(interval, p1, p2, p3, p4, p5):
    if p1 == p2 == p3 == p4 == p5 == 0:
        p1 = time.time()

    # first find out who clicked last
    ts_list = {
        'Para1': p1,
        'Para2': p2,
        'Para3': p3,
        'Para4': p4,
        'Para5': p5
    }
    latest_clicked = '',
    latest = 0
    for key in ts_list:
        if ts_list[key] > latest:
            latest_clicked = key
            latest = ts_list[key]

    return generate_graph(interval, latest_clicked)


def update_spark_line_graph(interval, col):
    # update spark line graph
    if interval >= max_length:
        total_count = max_length - 1
    else:
        total_count = interval

    x_array = state_dict['Batch']['data'].tolist()
    y_array = state_dict[col]['data'].tolist()

    new_fig = go.Figure({
        'data': [{'x': x_array[:total_count], 'y': y_array[:total_count], 'mode': 'lines+markers',
                  'name': col}],
        'layout': {
            'margin': dict(
                l=0, r=0, t=4, b=4, pad=0
            )
        }
    })

    return new_fig


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
            "range": [3, 5, 10],
            "performance": [0, ooc_percentage_f],
        }],
        measures='performance',
        ranges='range',
        titles='label',
        height=50,
        width=200,
        margin=dict(l=5, r=0, t=0, b=0, pad=0),
        font={'size': 1},
        measure_colors=['rgb(0,0,0)', 'rgb(0,0,0)'],
        range_colors=['rgb(152,251,152)', 'rgb(250,128,114)'],
    )
    color = '#00cc96'
    if ooc_percentage_f > 5:
        color = '#FF0000'

    return total_count, ooc_percentage_str, ooc_fig, color


# default_treemap
def generate_default_treemap(batch_num):
    x = 0.
    y = 0.
    width = 100.
    height = 100.

    values = []
    for param in params[1:]:
        size_of_rect = (state_dict[param]['ooc'][batch_num] * 100) + 1
        values.append(size_of_rect)

    normed = squarify.normalize_sizes(values, width, height)
    rects = squarify.squarify(normed, x, y, width, height)

    color_brewer = ['rgb(75,103,144)', 'rgb(101,123,159)', 'rgb(127,143,175)', 'rgb(152,165,191)', 'rgb(177,187,206)',
                    'rgb(203,209,222)']

    # TODO: colormap for rect

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
        hovermode='closest'
    )
    # print(time.time()-t)

    return trace0, layout


def generate_tree_map():
    return html.Div(
        id='treemap-container',
        style={'padding': '10px 0px'},
        children=dcc.Graph(
            id='treemap',
            figure=dict(data=[generate_default_treemap(0)[0]], layout=generate_default_treemap(0)[1]),
            config={
                'staticPlot': False,
                'editable': False,
                'displayModeBar': False
            }
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


root_layout()

# Running the server
if __name__ == '__main__':
    app.run_server(dev_tools_hot_reload=False, debug=True, host='0.0.0.0', port=8051, use_reloader=False)

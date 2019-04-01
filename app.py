import time

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_table
import plotly.graph_objs as go
import dash_daq as daq
from textwrap import dedent

import pandas as pd

app = dash.Dash(__name__)
server = app.server
app.scripts.config.serve_locally = True
app.config['suppress_callback_exceptions'] = True

df = pd.read_csv("data/spc_data.csv")

params = list(df)
max_length = len(df)

suffix_row = '_row'
suffix_button_id = '_button'
suffix_sparkline_graph = '_sparkline_graph'
suffix_count = '_count'
suffix_ooc_n = '_OOC_number'
suffix_ooc_g = '_OOC_graph'
suffix_indicator = '_indicator'


def root_layout():
    app.layout = html.Div(
        children=[
            # Banner
            build_banner(),
            # Tabs
            build_tabs(),
            # Main app
            html.Div(
                id='app-content',
                className='container scalable'
            ),
            # html.Button('Proceed to measure', id='tab-trigger-btn', n_clicks=0, style={'display': 'inline'}),
            dcc.Store(
                id='value-setter-store',
                data=init_value_setter_store()
            ),
            generate_modal(),
        ]
    )


def build_banner():
    return html.Div(
        id='banner',
        className="banner",
        children=[
            html.H5('Manufacturing SPC Dashboard - Process Control and Exception Reporting'),
            html.Button(
                id='learn-more-button',
                children="LEARN MORE",
                n_clicks=0,
                ),
            html.Img(
                src="https://s3-us-west-1.amazonaws.com/plotly-tutorials/logo/new-branding/dash-logo-by-plotly-stripe-inverted.png")
        ]
    )


def build_tabs():
    return html.Div(
        id='tabs',
        className='row container scalable',
        children=[
            dcc.Tabs(
                id='app-tabs',
                value='tab1',
                className='custom-tabs',
                children=[
                    dcc.Tab(
                        id='Specs-tab',
                        label='Specification Settings',
                        value='tab1',
                        className='custom-tab',
                        selected_className='custom-tab--selected',
                        disabled=False
                    ),
                    dcc.Tab(
                        id='Control-chart-tab',
                        label='Control Charts Dashboard',
                        value='tab2',
                        className='custom-tab',
                        selected_className='custom-tab--selected',
                        disabled=False)
                ]
            )
        ]
    )


def init_df():
    ret = {}
    for col in list(df[1:]):
        data = df[col]
        stats = data.describe()

        std = stats['std'].tolist()
        ucl = (stats['mean'] + 3 * stats['std']).tolist()
        lcl = (stats['mean'] - 3 * stats['std']).tolist()
        usl = (stats['mean'] + stats['std']).tolist()
        lsl = (stats['mean'] - stats['std']).tolist()

        ret.update({
            col: {
                'count': stats['count'].tolist(),
                'data': data,
                'mean': stats['mean'].tolist(),
                'std': std,
                'ucl': round(ucl, 3),
                'lcl': round(lcl, 3),
                'usl': round(usl, 3),
                'lsl': round(lsl, 3),
                'min': stats['min'].tolist(),
                'max': stats['max'].tolist(),
                'ooc': populate_ooc(data, ucl, lcl)
            }
        })

    return ret


def populate_ooc(data, ucl, lcl):
    ooc_count = 0
    ret = []
    for i in range(len(data)):
        if data[i] >= ucl or data[i] <= lcl:
            ooc_count += 1
            ret.append(ooc_count / (i + 1))
        else:
            ret.append(ooc_count / (i + 1))
    return ret


state_dict = init_df()


def init_value_setter_store():
    # Initialize store data
    state_dict = init_df()
    return state_dict


def build_tab_1():
    return [
        # Manually select metrics
        html.Div(
            id='set-specs-intro-container',
            className='twelve columns',
            children=html.P("Use historical control limits to establish a benchmark, or set new values.")
        ),
        html.Div(
            className='five columns',
            children=[
                html.Label(id='metric-select-title', children='Select Metrics'),
                html.Br(),
                dcc.Dropdown(
                    id='metric-select-dropdown',
                    options=list({'label': param, 'value': param} for param in params[1:]),
                    value=params[1]
                )]),

        html.Div(
            className='five columns',
            children=[
                html.Div(
                    id='value-setter-panel'),
                html.Br(),
                html.Button('Update', id='value-setter-set-btn'),
                html.Button('View current setup', id='value-setter-view-btn', n_clicks=0),
                html.Div(id='value-setter-view-output', className='output-datatable')
            ]
        )
    ]


ud_usl_input = daq.NumericInput(id='ud_usl_input', size=200, max=9999999, style={'width': '100%', 'height': '100%'})
ud_lsl_input = daq.NumericInput(id='ud_lsl_input', size=200, max=9999999, style={'width': '100%', 'height': '100%'})
ud_ucl_input = daq.NumericInput(id='ud_ucl_input', size=200, max=9999999, style={'width': '100%', 'height': '100%'})
ud_lcl_input = daq.NumericInput(id='ud_lcl_input', size=200, max=9999999, style={'width': '100%', 'height': '100%'})


def build_value_setter_line(line_num, label, value, col3):
    return html.Div(
        id=line_num,
        children=[
            html.Label(label, className='four columns'),
            html.Label(value, className='four columns'),
            html.Div(col3, className='four columns')],
        className='row'
    )


# ===== Callbacks to update values based on store data and dropdown selection =====
@app.callback(
    output=[
        Output('value-setter-panel', 'children'),
        Output('ud_usl_input', 'value'),
        Output('ud_lsl_input', 'value'),
        Output('ud_ucl_input', 'value'),
        Output('ud_lcl_input', 'value')],
    inputs=[Input('metric-select-dropdown', 'value')],
    state=[State('value-setter-store', 'data')]
)
def build_value_setter_panel(dd_select, state_value):
    return [
               # html.Label(dd_select),
               build_value_setter_line('value-setter-panel-header', 'Specs', 'Historical Value', 'Set new value'),
               build_value_setter_line('value-setter-panel-usl', 'Upper Specification limit',
                                       state_dict[dd_select]['usl'], ud_usl_input),
               build_value_setter_line('value-setter-panel-lsl', 'Lower Specification limit',
                                       state_dict[dd_select]['lsl'], ud_lsl_input),
               build_value_setter_line('value-setter-panel-ucl', 'Upper Control limit', state_dict[dd_select]['ucl'],
                                       ud_ucl_input),
               build_value_setter_line('value-setter-panel-lcl', 'Lower Control limit', state_dict[dd_select]['lcl'],
                                       ud_lcl_input)
           ], state_value[dd_select]['usl'], state_value[dd_select]['lsl'], state_value[dd_select]['ucl'], \
           state_value[dd_select]['lcl']


# ====== Callbacks to update stored data via click =====
@app.callback(
    output=Output('value-setter-store', 'data'),
    inputs=[
        Input('value-setter-set-btn', 'n_clicks')
    ],
    state=[
        State('metric-select-dropdown', 'value'),
        State('value-setter-store', 'data'),
        State('ud_usl_input', 'value'),
        State('ud_lsl_input', 'value'),
        State('ud_ucl_input', 'value'),
        State('ud_lcl_input', 'value'),
    ]
)
def set_value_setter_store(set_btn, param, data, usl, lsl, ucl, lcl):
    if set_btn is None:
        return data
    else:
        data[param]['usl'] = usl
        data[param]['lsl'] = lsl
        data[param]['ucl'] = ucl
        data[param]['lcl'] = lcl

        # Recalculate ooc in case of param updates
        data[param]['ooc'] = populate_ooc(df[param], ucl, lcl)
        return data


@app.callback(
    output=Output('value-setter-view-output', 'children'),
    inputs=[Input('value-setter-view-btn', 'n_clicks'), Input('metric-select-dropdown', 'value'), Input('value-setter-store', 'data')]
)
def show_current_specs(n_clicks, dd_select, store_data):
    if n_clicks > 0:
        curr_col_data = store_data[dd_select]
        new_df_dict = {
            'Specs': ['Upper Specification Limit', 'Lower Specification Limit', 'Upper Control Limit',
                      'Lower Control Limit'],
            'Current Setup': [curr_col_data['usl'], curr_col_data['lsl'], curr_col_data['ucl'], curr_col_data['lcl']]
        }
        new_df = pd.DataFrame.from_dict(new_df_dict)
        return dash_table.DataTable(
            style_header={
                'backgroundColor': 'white',
                'fontWeight': 'bold'
            },
            style_cell_conditional=[
                {
                    'if': {'column_id': c},
                    'textAlign': 'left'
                } for c in ['Specs']
            ],
            data=new_df.to_dict('rows'),
            columns=[{'id': c, 'name': c} for c in ['Specs', 'Current Setup']]
        )



@app.callback(
    output=Output('app-content', 'children'),
    inputs=[Input('app-tabs', 'value')]
)
def render_content(tab):
    if tab == 'tab1':
        return build_tab_1()
    elif tab == 'tab2':
        return [
            html.Div(
                id='status-container',
                children=[
                    build_quick_stats_panel(),
                    build_top_panel(),
                    build_chart_panel(),
                ]
            )
        ]


def build_quick_stats_panel():
    return html.Div(
        id="quick-stats",
        className='row',
        children=
        [
            html.Div(
                id="card-1",
                className='four columns',
                children=[
                    html.H5("Operator ID"),
                    daq.LEDDisplay(
                        value='1704',
                        color="#000000",
                        size=50
                    )
                ]
            ),

            html.Div(
                id='card-2',
                className='four columns',
                children=[
                    html.H5("Time to completion"),
                    daq.Gauge(
                        id='progress-gauge',
                        value=0,
                        size=150,
                        max=max_length * 2,
                        min=0,
                    )
                ]
            ),

            html.Div(
                id='utility-card',
                className='four columns',
                children=[
                    daq.StopButton(id='stop-button', size=160, buttonText='start'),
                    html.Button(id='print-report', children='print report')
                ]
            )
        ]
    )


def generate_modal():
    return html.Div(
        id='markdown',
        className="modal",
        style={'display': 'none'},
        children=(
            html.Div(
                id="markdown-container",
                className="markdown-container",
                children=[
                    html.Div(
                        className='close-container',
                        children=html.Button(
                            "Close",
                            id="markdown_close",
                            n_clicks=0,
                            className="closeButton"
                        )
                    ),
                    html.Div(
                        className='markdown-text',
                        children=dcc.Markdown(
                            children=dedent('''
                        **What is this mock app about?**
                        
                        'dash-manufacture-spc-dashboard` is a dashboard for monitoring read-time process quality along manufacture production line. 

                        **What does this app shows**
                        
                        Click on buttons in `Parameter' column to visualize details of measurement trendlines on the bottom panel.
                        
                        The Sparkline on top panel and Control chart on bottom panel show Shewhart process monitor using mock data. 
                        The trend is updated every two seconds to simulate real-time measurements. Data falling outside of six-sigma control limit are signals indicating 'Out of Control(OOC)', and will 
                        trigger alerts instantly for a detailed checkup. 
                    ''')
                        )
                    )
                ]
            )
        )
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

            # Piechart
            html.Div(
                id='ooc-piechart-outer',
                className='four columns',
                children=[
                    generate_section_banner('% OOC per Parameter'),
                    generate_piechart()
                ]
            )
        ]
    )


def generate_piechart():
    return dcc.Graph(
        id='piechart',
        figure={
            'data': [
                {
                    'labels': params[1:],
                    'values': [1, 1, 1, 1, 1],
                    'type': 'pie',
                    'marker': {'colors': ['rgb(56, 75, 126)',
                                          'rgb(18, 36, 37)',
                                          'rgb(34, 53, 101)',
                                          'rgb(36, 55, 57)',
                                          'rgb(6, 4, 4)']},
                    'hoverinfo': 'label',
                    'textinfo': 'label'
                }],
            'layout': {
                'showlegend': True}
        }
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
            'children': "Pass/Fail"
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
                title="Click to visualize live SPC chart",
                n_clicks_timestamp=0,
                # style={
                #     'width': '100%'
                # }
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
            'children':
                daq.GraduatedBar(
                    id=ooc_graph_id,
                    color={"gradient": True, "ranges": {"green": [0, 3], "yellow": [3, 7], "red": [7, 15]}},
                    showCurrentValue=False,
                    max=15,
                    value=15
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
                style={
                    'display': 'flex',
                    'justifyContent': 'center'
                },
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
                n_intervals=0,
                disabled=True
            ),

            dcc.Store(
                id='control-chart-state'
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


def generate_graph(interval, specs_dict, col):
    stats = state_dict[col]
    col_data = stats['data']
    mean = stats['mean']
    ucl = specs_dict[col]['ucl']
    lcl = specs_dict[col]['lcl']
    usl = specs_dict[col]['usl']
    lsl = specs_dict[col]['lsl']

    x_array = state_dict['Batch']['data'].tolist()
    y_array = col_data.tolist()

    total_count = 0

    if interval > max_length:
        total_count = max_length - 1
    elif interval > 0:
        total_count = interval - 1

    ooc_trace = {'x': [],
                 'y': [],
                 'name': 'Out of Control',
                 'mode': 'markers',
                 'marker': dict(color='rgba(210, 77, 87, 0.7)', symbol="square", size=11)
                 }

    for index, data in enumerate(y_array[:total_count]):
        if data >= ucl or data <= lcl:
            ooc_trace['x'].append(index + 1)
            ooc_trace['y'].append(data)

    histo_trace = {
        'x': x_array[:total_count],
        'y': y_array[:total_count],
        'type': 'histogram',
        'orientation': 'h',
        'name': 'Distribution',
        'xaxis': 'x2',
        'yaxis': 'y2'
    }

    fig = {
        'data': [
            {
                'x': x_array[:total_count],
                'y': y_array[:total_count],
                'mode': 'lines+markers',
                'name': col
            },
            ooc_trace,
            histo_trace
        ]
    }

    len_figure = len(fig['data'][0]['x'])

    fig['layout'] = dict(
        title='Individual measurements',
        showlegend=True,
        xaxis={
            'zeroline': False,
            'title': 'Batch_Num',
            'showline': False,
            'domain': [0, 0.7]
        },
        yaxis={
            'title': col,
            'autorange': True
        },
        annotations=[
            {'x': len_figure + 2, 'y': lcl, 'xref': 'x', 'yref': 'y',
             'text': 'LCL:' + str(round(lcl, 3)),
             'showarrow': True},
            {'x': len_figure + 2, 'y': ucl, 'xref': 'x', 'yref': 'y',
             'text': 'UCL: ' + str(round(ucl, 3)),
             'showarrow': True},
            {'x': len_figure + 2, 'y': usl, 'xref': 'x', 'yref': 'y',
             'text': 'USL: ' + str(round(usl, 3)),
             'showarrow': True},
            {'x': len_figure + 2, 'y': lsl, 'xref': 'x', 'yref': 'y',
             'text': 'LSL: ' + str(round(lsl, 3)),
             'showarrow': True},
            {'x': len_figure + 2, 'y': mean, 'xref': 'x', 'yref': 'y',
             'text': 'Targeted mean: ' + str(round(mean, 3)),
             'showarrow': False}
        ],
        shapes=[
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
        ],
        xaxis2={
            'title': 'count',
            'domain': [0.8, 1]  # 70 to 100 % of width
        },
        yaxis2={
            'title': 'value',
            'anchor': 'x2',
            'showticklabels': False
        }
    )

    return fig


# ======= Callbacks for modal popup =======
@app.callback(Output("markdown", "style"),
              [Input("learn-more-button", "n_clicks"), Input("markdown_close", "n_clicks")])
def update_click_output(button_click, close_click):
    if button_click > close_click:
        return {"display": "block"}
    else:
        return {"display": "none"}


# Callbacks for stopping interval update
@app.callback(
    [Output('interval-component', 'disabled'),
     Output('stop-button', 'buttonText')],
    [Input('stop-button', 'n_clicks')],
    state=[State('interval-component', 'disabled')]
)
def stop_production(_, current):
    return not current, "stop" if current else "start"


# ======= update progress gauge =========
@app.callback(
    output=Output('progress-gauge', 'value'),
    inputs=[Input('interval-component', 'n_intervals')]
)
def update_gauge(interval):
    if interval < max_length:
        total_count = interval
    else:
        total_count = max_length

    return int(total_count)


# ======= update each row at interval =========
@app.callback(
    output=[
        Output('Metric1' + suffix_count, 'children'),
        Output('Metric1' + suffix_sparkline_graph, 'figure'),
        Output('Metric1' + suffix_ooc_n, 'children'),
        Output('Metric1' + suffix_ooc_g, 'value'),
        Output('Metric1' + suffix_indicator, 'color')
    ],
    inputs=[Input('interval-component', 'n_intervals')],
    state=[State('value-setter-store', 'data')]
)
def update_param1_row(interval, stored_data):
    count, ooc_n, ooc_g_value, indicator = update_count(interval, 'Metric1', stored_data)
    spark_line_graph = update_spark_line_graph(interval, 'Metric1')
    return count, spark_line_graph, ooc_n, ooc_g_value, indicator


@app.callback(
    output=[
        Output('Metric2' + suffix_count, 'children'),
        Output('Metric2' + suffix_sparkline_graph, 'figure'),
        Output('Metric2' + suffix_ooc_n, 'children'),
        Output('Metric2' + suffix_ooc_g, 'value'),
        Output('Metric2' + suffix_indicator, 'color')
    ],
    inputs=[Input('interval-component', 'n_intervals')],
    state=[State('value-setter-store', 'data')]
)
def update_param2_row(interval, stored_data):
    count, ooc_n, ooc_g_value, indicator = update_count(interval, 'Metric2', stored_data)
    spark_line_graph = update_spark_line_graph(interval, 'Metric2')
    return count, spark_line_graph, ooc_n, ooc_g_value, indicator


@app.callback(
    output=[
        Output('Metric3' + suffix_count, 'children'),
        Output('Metric3' + suffix_sparkline_graph, 'figure'),
        Output('Metric3' + suffix_ooc_n, 'children'),
        Output('Metric3' + suffix_ooc_g, 'value'),
        Output('Metric3' + suffix_indicator, 'color')
    ],
    inputs=[Input('interval-component', 'n_intervals')],
    state=[State('value-setter-store', 'data')]
)
def update_param3_row(interval, stored_data):
    count, ooc_n, ooc_g_value, indicator = update_count(interval, 'Metric3', stored_data)
    spark_line_graph = update_spark_line_graph(interval, 'Metric3')
    return count, spark_line_graph, ooc_n, ooc_g_value, indicator


@app.callback(
    output=[
        Output('Thickness1' + suffix_count, 'children'),
        Output('Thickness1' + suffix_sparkline_graph, 'figure'),
        Output('Thickness1' + suffix_ooc_n, 'children'),
        Output('Thickness1' + suffix_ooc_g, 'value'),
        Output('Thickness1' + suffix_indicator, 'color')
    ],
    inputs=[Input('interval-component', 'n_intervals')],
    state=[State('value-setter-store', 'data')]
)
def update_param4_row(interval, stored_data):
    count, ooc_n, ooc_g_value, indicator = update_count(interval, 'Thickness1', stored_data)
    spark_line_graph = update_spark_line_graph(interval, 'Thickness1')
    return count, spark_line_graph, ooc_n, ooc_g_value, indicator


@app.callback(
    output=[
        Output('Width1' + suffix_count, 'children'),
        Output('Width1' + suffix_sparkline_graph, 'figure'),
        Output('Width1' + suffix_ooc_n, 'children'),
        Output('Width1' + suffix_ooc_g, 'value'),
        Output('Width1' + suffix_indicator, 'color')
    ],
    inputs=[Input('interval-component', 'n_intervals')],
    state=[State('value-setter-store', 'data')]
)
def update_param5_row(interval, stored_data):
    count, ooc_n, ooc_g_value, indicator = update_count(interval, 'Width1', stored_data)
    spark_line_graph = update_spark_line_graph(interval, 'Width1')
    return count, spark_line_graph, ooc_n, ooc_g_value, indicator


#  ======= button to choose/update figure based on click ============
@app.callback(
    output=Output('control-chart-live', 'figure'),
    inputs=[
        Input('interval-component', 'n_intervals'),
        Input('Metric1' + suffix_button_id, 'n_clicks_timestamp'),
        Input('Metric2' + suffix_button_id, 'n_clicks_timestamp'),
        Input('Metric3' + suffix_button_id, 'n_clicks_timestamp'),
        Input('Thickness1' + suffix_button_id, 'n_clicks_timestamp'),
        Input('Width1' + suffix_button_id, 'n_clicks_timestamp'),
    ],
    state=[State("value-setter-store", 'data')]
)
def update_control_chart(interval, p1, p2, p3, p4, p5, data):
    if p1 == p2 == p3 == p4 == p5 == 0:
        p1 = time.time()

    # first find out who clicked last
    ts_list = {
        'Metric1': p1,
        'Metric2': p2,
        'Metric3': p3,
        'Thickness1': p4,
        'Width1': p5
    }
    latest_clicked = '',
    latest = 0
    for key in ts_list:
        if ts_list[key] > latest:
            latest_clicked = key
            latest = ts_list[key]

    return generate_graph(interval, data, latest_clicked)


def update_spark_line_graph(interval, col):
    if interval == 0:
        data = [{'x': [], 'y': [], 'mode': 'lines+markers',
                 'name': col}]
    # update spark line graph
    else:
        if interval >= max_length:
            total_count = max_length - 1
        else:
            total_count = interval - 1

        x_array = state_dict['Batch']['data'].tolist()
        y_array = state_dict[col]['data'].tolist()

        data = [{'x': x_array[:total_count], 'y': y_array[:total_count], 'mode': 'lines+markers',
                 'name': col}]

    new_fig = go.Figure({
        'data': data,
        'layout': {
            'margin': dict(
                l=0, r=0, t=4, b=4, pad=0
            )
        }
    })

    return new_fig


# Update batch num, ooc percentage, ooc_grad_value and indicator color
def update_count(interval, col, data):
    if interval == 0:
        return '0', '0.00%', 0, '#00cc96'

    if interval >= max_length:
        total_count = max_length - 1
    else:
        total_count = interval - 1

    ooc_percentage_f = data[col]['ooc'][total_count] * 100
    ooc_percentage_str = "%.2f" % ooc_percentage_f + '%'
    # if col == 'Para5':
    #     print(interval, total_count, ooc_percentage_f)
    if ooc_percentage_f > 15:
        ooc_percentage_f = 15

    ooc_grad_val = float(ooc_percentage_f)

    if 0 <= ooc_grad_val <= 5:
        color = '#00cc96'
    else:
        color = '#FF0000'

    return str(total_count), ooc_percentage_str, ooc_grad_val, color


# Update piechart
@app.callback(
    output=Output('piechart', 'figure'),
    inputs=[
        Input('interval-component', 'n_intervals')],
    state=[State("value-setter-store", 'data')]
)
def update_piechart(interval, stored_data):
    if interval == 0:
        return {}

    if interval >= max_length:
        total_count = max_length - 1
    else:
        total_count = interval - 1

    values = []
    colors = []
    for param in params[1:]:
        ooc_param = (stored_data[param]['ooc'][total_count] * 100) + 1
        values.append(ooc_param)
        if ooc_param > 6:
            colors.append('rgb(206,0,5)')
        else:
            colors.append('rgb(76,178,51')

    new_figure = {
        'data': [
            {
                'labels': params[1:],
                'values': values,
                'type': 'pie',
                'marker': {'colors': colors, 'line': dict(color='#FFFFFF', width=2)},
                'hoverinfo': 'label',
                'textinfo': 'label'
            }],
        'layout': {
            'showlegend': True}
    }
    return new_figure


root_layout()

# Running the server
if __name__ == '__main__':
    app.run_server(dev_tools_hot_reload=False, debug=True, host='0.0.0.0', port=8051, use_reloader=False)

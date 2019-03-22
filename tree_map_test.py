import dash
import plotly.plotly as py
import plotly.graph_objs as go
import dash_core_components as dcc
import dash_html_components as html
import plotly.figure_factory as ff
import pandas as pd

import squarify

app = dash.Dash(__name__)

x = 0.
y = 0.
width = 150.
height = 100.

# Value is z-value that equals to % OOC.
values = [55, 60, 78, 25, 25, 7]

normed = squarify.normalize_sizes(values, width, height)
rects = squarify.squarify(normed, x, y, width, height)

# Choose colors from http://colorbrewer2.org/ under "Export"
# Colorway or colorscale?
color_brewer = ['rgb(166,206,227)', 'rgb(31,120,180)', 'rgb(178,223,138)',
                'rgb(51,160,44)', 'rgb(251,154,153)', 'rgb(227,26,28)']
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
            line=dict(width=2),
            fillcolor=color_brewer[counter]
        )
    )
    annotations.append(
        dict(
            x=r['x'] + (r['dx'] / 2),
            y=r['y'] + (r['dy'] / 2),
            text=values[counter],
            showarrow=False
        )
    )
    counter = counter + 1
    if counter >= len(color_brewer):
        counter = 0

# For hover text
trace0 = go.Scatter(
    x=[r['x'] + (r['dx'] / 2) for r in rects],
    y=[r['y'] + (r['dy'] / 2) for r in rects],
    text=[str(v) for v in values],
    mode='text',
)

layout = dict(
    height=700,
    width=700,
    xaxis=dict(showgrid=False, zeroline=False),
    yaxis=dict(showgrid=False, zeroline=False),
    shapes=shapes,
    annotations=annotations,
    hovermode='closest'
)

# With hovertext
figure = dict(data=[trace0], layout=layout)


# bullet plot
data = (
  {"label": "Revenue", "sublabel": "US$, in thousands",
   "range": [150, 225, 300], "performance": [220,270], 'point': [5]},
  {"label": "Profit", "sublabel": "%", "range": [20, 25, 30],
   "performance": [21, 23], "point": [26]},
  {"label": "Order Size", "sublabel":"US$, average","range": [350, 500, 600],
   "performance": [100,320],"point": [550]},
  {"label": "New Customers", "sublabel": "count", "range": [1400, 2000, 2500],
   "performance": [1000, 1650],"point": [2100]},
  {"label": "Satisfaction", "sublabel": "out of 5","range": [3.5, 4.25, 5],
   "performance": [3.2, 4.7], "point": [4.4]}
)


ooc_bullet_df = pd.read_csv("ooc_percentage.csv")
para4_ooc = ooc_bullet_df['Para4']
print(para4_ooc)

data = {
    "range": [5, 10, 100],  # 3-item list [bad, okay, good].
    "performance":
    "measures":

}
# skip points
fig2 = ff.create_bullet(
    data, markers='point',
    measures='performance', ranges='range'
)


app.layout = html.Div(
    children=[
        dcc.Graph(figure=figure),
        dcc.Graph(figure=fig2)
    ]
)

# Running the server
if __name__ == '__main__':
    app.run_server(dev_tools_hot_reload=False, debug=True, host='0.0.0.0', port=8051, use_reloader=False)



# @app.callback(
#             output=Output(sparkline_graph_id, 'figure'),
#             inputs=[
#                 Input('interval-component', 'n_intervals')
#             ],
#             state=[
#                 State(sparkline_graph_id, 'figure')
#             ])
#         def generate_sparkline_graph(interval, curr_graph):
#             param = curr_graph['data'][0]['name']
#             dff = df[['Batch', param]][:]
#             x_array = dff['Batch'].tolist()
#             y_array = dff[param].tolist()
#             count = len(x_array)
#
#             if len(curr_graph['data'][0]['x']) < count:
#                 curr_graph['data'][0]['x'].append(x_array[len(curr_graph['data'][0]['x'])])
#                 curr_graph['data'][0]['y'].append(y_array[len(curr_graph['data'][0]['y'])])
#                 # curr_graph['layout'] = layout
#
#             return curr_graph
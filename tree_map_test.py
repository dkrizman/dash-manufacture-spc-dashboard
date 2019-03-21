import dash
import plotly.plotly as py
import plotly.graph_objs as go
import dash_core_components as dcc
import dash_html_components as html

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

app.layout = html.Div(
    children=dcc.Graph(figure=figure)
)

# Running the server
if __name__ == '__main__':
    app.run_server(dev_tools_hot_reload=False, debug=True, host='0.0.0.0', port=8051, use_reloader=False)


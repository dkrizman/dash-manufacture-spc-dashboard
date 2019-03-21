import pandas as pd

df = pd.read_csv("data/spc_data.csv").dropna(axis=0)  # 481 * 19 cols

#
# def get_graph_trends(df, param, num):
#     dff = df[['Batch', param]]
#     stats = dff[param].describe()
#
#     count = stats['count'].tolist()
#     std = stats['std'].tolist()
#     mean = stats['mean'].tolist()
#     ucl = (stats['mean'] + 3 * stats['std']).tolist()
#     lcl = (stats['mean'] - 3 * stats['std']).tolist()
#     min = stats['min'].tolist()
#     max = stats['max'].tolist()
#
#     return dff, count, mean, ucl, lcl, min, max


# Calculate OOC% for individual param
def get_graph_trends(df, param):
    dff = df[['Batch', param]][:]
    stats = dff[param].describe()

    count = stats['count'].tolist()

    std = stats['std'].tolist()  # Process standard deviation
    mean = stats['mean'].tolist()
    ucl = (stats['mean'] + 3 * stats['std']).tolist()
    lcl = (stats['mean'] - 3 * stats['std']).tolist()
    min = stats['min'].tolist()
    max = stats['max'].tolist()

    return dff, count, mean, ucl, lcl, min, max


output = get_graph_trends(df, 'Para8')
print(output[1:])
for i in output[0]['Para8']:
    ooc = 0
    if i > output[3] or i < output[4]:
        print(i)
        ooc += 1
    ooc = (ooc/len(output[0]))*100
print("ooc:", ooc, '%')

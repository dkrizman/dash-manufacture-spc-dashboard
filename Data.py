import pandas as pd

df = pd.read_csv("data/spc_data.csv")  # 653 * 28 col


def populate_ooc(col):
    data = df[col]
    stats = data.describe()
    ucl = (stats['mean'] + 3 * stats['std']).tolist()
    lcl = (stats['mean'] - 3 * stats['std']).tolist()

    occ_count = 0
    ret = []
    for i in range(len(data)):
        if data[i] >= ucl or data[i] <= lcl:
            occ_count += 1
            ret.append(occ_count/(i+1))
        else:
            ret.append(occ_count/(i+1))
    # todo this is not correct
    return ret


def init_df():
    ret = {}
    for col in list(df):
        data = df[col]
        stats = data.describe()

        ucl = (stats['mean'] + 3 * stats['std']).tolist()
        lcl = (stats['mean'] - 3 * stats['std']).tolist()
        ret.update({
            col: {
                'count': stats['count'].tolist(),
                'data': data,
                'mean': stats['mean'].tolist(),
                'ucl': ucl,
                'lcl': lcl,
                'min:': stats['min'].tolist(),
                'max': stats['max'].tolist(),
                'ooc': populate_ooc(col)
            }
        })
    return ret


# test = init_df()
# # print('test para3 ucl data :', (test['Para3']['ooc']))
#
# state_dict = init_df()

# Calculate OOC Num and index, save output to new csv
# def get_ooc_stats(param='Speed'):
#     dff, count, mean, ucl, lcl, min, max = get_graph_stats(df, param)
#     param_col = dff[param].tolist()
#     ooc_speed = np.zeros(len(dff))
#
#     index = []
#     # OOC according to time
#     for i in param_col:
#         if i >= ucl or i <= lcl:
#             index.append(param_col.index(i))
#             ooc_speed[param_col.index(i)] = 1
#
#     # Cum_sum
#     ooc_param_sum = np.cumsum(ooc_speed)
#     # print(ooc_speed_sum)
#
#     ooc_percent = []
#     if ooc_speed[0] == 0:
#         ooc_percent = [0.0]
#
#     for i in range(1, len(dff)):
#         ooc_percent.append((ooc_param_sum[i] / (i + 1)))
#     return ooc_percent, ooc_param_sum

#
# dict = {'Batch': df['Batch']}
# dict_sum = {'Batch': df['Batch']}
#
# for param in list(df)[1:]:
#     ooc_percent, ooc_param_sum = get_ooc_stats(param=param)
#     new_dict = {param: ooc_percent}
#     dict.update(new_dict)
#     new_sum_dict = {param: ooc_param_sum}
#     dict_sum.update(new_sum_dict)
#
# df_ooc = pd.DataFrame.from_dict(dict)
# df_ooc.to_csv("ooc_percentage.csv", index=False)
#
# df_ooc_sum =  pd.DataFrame.from_dict(dict_sum)
# df_ooc_sum.to_csv("ooc_counts.csv", index=False)
#
# ooc_df = pd.read_csv('ooc_percentage.csv')

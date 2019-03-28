import pandas as pd
import random

df = pd.read_csv("data/spc_data.csv")  # 653 * 28 col


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


def init_df():
    ret = {}
    for col in list(df):
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


state_dict = init_df()

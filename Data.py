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

        # Generate random number for Specification Limits
        rand1 = random.random()
        rand2 = random.random()

        usl = ucl + (1 + rand1) * std
        lsl = lcl - (1 + rand2) * std

        ret.update({
            col: {
                'count': stats['count'].tolist(),
                'data': data,
                'mean': stats['mean'].tolist(),
                'std': std,
                'ucl': ucl,
                'lcl': lcl,
                'usl': usl,
                'lsl': lsl,
                'min': stats['min'].tolist(),
                'max': stats['max'].tolist(),
                'ooc': populate_ooc(data, ucl, lcl)
            }
        })

    return ret


state_dict = init_df()

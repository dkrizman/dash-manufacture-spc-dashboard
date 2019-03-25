import pandas as pd

df = pd.read_csv("data/spc_data.csv")  # 653 * 28 col


def populate_ooc(col):
    data = df[col]
    stats = data.describe()
    ucl = (stats['mean'] + 3 * stats['std']).tolist()
    lcl = (stats['mean'] - 3 * stats['std']).tolist()

    ooc_count = 0
    ret = []
    for i in range(len(data)):
        if data[i] >= ucl or data[i] <= lcl:
            ooc_count += 1
            ret.append(ooc_count/(i+1))
        else:
            ret.append(ooc_count/(i+1))
    return ret


def init_df():
    ret = {}
    for col in list(df):
        data = df[col]
        stats = data.describe()

        std = stats['std'].tolist()
        ucl = (stats['mean'] + 3 * stats['std']).tolist()
        lcl = (stats['mean'] - 3 * stats['std']).tolist()

        usl = ucl + std
        lsl = lcl - std

        ret.update({
            col: {
                'count': stats['count'].tolist(),
                'data': data,
                'mean': stats['mean'].tolist(),
                'ucl': ucl,
                'lcl': lcl,
                'usl': usl,
                'lsl': lsl,
                'min:': stats['min'].tolist(),
                'max': stats['max'].tolist(),
                'ooc': populate_ooc(col)
            }
        })

    return ret


state_dict = init_df()


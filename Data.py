import pandas as pd
import numpy as np
import random

column = ["Parameter", "Count", "Sparkline", "%OOC", "%OOC", "Pass / Fail"]

df = pd.read_csv("data/wafer-production.csv")  # 481 * 19 cols


def get_graph_trends(df, param):
    dff = df[['Batch_Num', param]].dropna(axis=0)

    print(dff)
    stats = dff[param].describe()

    count = stats['count']
    std = stats['std']
    mean = stats['mean']
    ucl = stats['mean'] + 3 * stats['std']
    lcl = stats['mean'] - 3 * stats['std']

    # Spike in random outliers
    sampl = np.random.uniform(low=-float(std), high=std, size=(40,))
    rand_ind = np.random.randint(0, count, size=40)
    print(sampl, rand_ind)

    for i in rand_ind:
        dff[param][i] += 10

    print('new dff:', dff)

    return dff, count, mean, ucl, lcl


output = get_graph_trends(df, 'Metric1')

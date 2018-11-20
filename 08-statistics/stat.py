import pandas as pd
import sys
import json


def format_dates(df):
    df.rename(columns=lambda x: x[:10], inplace=True)
    df = df.groupby(axis=1, level=0).sum()
    return df


def format_exercises(df):
    df.rename(columns=lambda x: x[11:13], inplace=True)
    df = df.groupby(axis=1, level=0).sum()
    return df


csv_file = sys.argv[1]
df = pd.read_csv(csv_file)
df.drop('student', axis=1, inplace=True)
mode = sys.argv[2]

if mode == 'dates':
    df = format_dates(df)
elif mode == 'exercises':
    df = format_exercises(df)

dff = pd.concat([df.mean(), df.median(), df.quantile(q=0.25), df.quantile(q=0.75), df[df > 0.0].count()], axis=1)
dff.columns=["mean", "median", "first", "last", "passed"]
print(json.dumps(dff.to_dict(orient="index"), indent=2))

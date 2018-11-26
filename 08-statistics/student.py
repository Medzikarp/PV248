import pandas as pd
import numpy as np
import json
import sys
from datetime import datetime, timedelta


def format_dates(df):
    df = df.rename(index=lambda x: x[:10], inplace=False)
    df = df.groupby(axis=0, level=0).sum()
    return df


def format_exercises(df):
    df = df.rename(index=lambda x: x[11:13], inplace=False)
    df = df.groupby(axis=0, level=0).sum()
    return df


csv_file = sys.argv[1]
student = sys.argv[2]

df = pd.read_csv(csv_file)

if student == 'average':
    student_row = df.drop("student", axis=1).mean()
else:
    student_row = df.loc[df['student'] == int(student)]
    student_row = student_row.drop("student", axis=1)
    student_row = student_row.transpose()

points_by_exercises = format_exercises(student_row)
points_by_exercises.sort_index(axis=0, inplace=True)

student_row = format_dates(student_row).sort_index(axis=1, ascending=False)
cum_points_by_dates = student_row.cumsum()

dict = {}
dict['mean'] = str(points_by_exercises.mean().iloc[0])
dict['median'] = str(points_by_exercises.median().iloc[0])
dict['total'] = str(points_by_exercises.sum().iloc[0])
dict['passed'] = str(points_by_exercises[points_by_exercises > 0].count().iloc[0])

class_start = datetime.strptime('2018-09-17', "%Y-%m-%d").date()
deadlines = []
for date in cum_points_by_dates.index:
    deadlines.append(datetime.strptime(date, '%Y-%m-%d').date().toordinal() - class_start.toordinal())
deadlines = np.array(deadlines)
deadlines = np.reshape(deadlines, (deadlines.size, 1))

regression_slope = np.linalg.lstsq(deadlines, cum_points_by_dates.values)[0].item(0)
dict['regression slope'] = regression_slope
date_16 = str(class_start + timedelta(16 / regression_slope))
date_20 = str(class_start + timedelta(20 / regression_slope))
dict['date 16'] = date_16 if regression_slope != 0 else 'inf'
dict['date 20'] = date_20 if regression_slope != 0 else 'inf'

print(json.dumps(dict, indent=2, ensure_ascii = False))
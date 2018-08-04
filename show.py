# -*- coding: utf-8 -*-

##########################
# Read inp

import pandas as pd
import numpy as np
import sys
from contextlib import redirect_stdout

inp = pd.read_csv('hoursOfWork.txt',
                    sep=';',
                    header = 0,
                    comment='#',
                    skipinitialspace=True,
                    #skip_blank_lines=False,
                    #parse_dates = [0,1,2],
                    )

inp = inp.rename(columns=lambda x: x.strip())

##########################
# Do logic

data = inp.copy()

data['cStart'] = data.apply(
                    func=lambda row:
                    pd.to_datetime(
                        row['date']+' '+row['start'],
                        format='%Y.%m.%d %H:%M'),
                    axis=1)

data['cEnd'] = data.apply(
                    func=lambda row:
                    pd.to_datetime(
                        row['date']+' '+row['end'],
                        format='%Y.%m.%d %H:%M'),
                    axis=1)

data['cBreaks'] = data.apply(
                    func=lambda row:
                    pd.Timedelta(
                        value = row['breaks'],
                        unit = 'm'),
                    axis=1)

data['cDuration'] = data.apply(
                    func=lambda row:
                        row['cEnd']-row['cStart']-row['cBreaks'],
                    axis=1)

# Format duration human readable

data['cHours'] = data.apply(
                    func=lambda row:
                    row['cDuration'] / pd.Timedelta('1 hour'),              
                    axis=1)

data['duration'] = data.apply(
                    func=lambda row:
                    '{:02d}:{:02d}'.format( int(row['cHours']), int(round(row['cHours'] % 1 * 60.0, 1)) ),
                    axis=1)

#https://stackoverflow.com/a/8907269/8935243
def strfdelta(tdelta, fmt):
    d = {"D": tdelta.days}
    d["H"], rem = divmod(tdelta.seconds, 3600)
    ## Add day - duration to hour duration and delete day duration
    #d["H"] = d["H"] + d["D"] * 24.0
    #d["D"] = 0.0
    d["M"], d["S"] = divmod(rem, 60)
    return fmt.format(**d)

data['duration2'] = data.apply(
                    func=lambda row:
                    strfdelta(row['cDuration'], '{H:02}:{M:02}'),
                    axis=1)

# Calc weekly duration

data['week'] = data.apply(
                    func=lambda row:
                    row['cStart'].strftime('%Y %W'),              
                    axis=1)

weeks = data.groupby(['week'])['cHours'].sum()

data['weekly'] = data.apply(
                    func=lambda row:
                    weeks.loc[row['week']],              
                    axis=1)

##########################
# Format output

out = inp.copy()
out['duration']     = data['duration']
out['week']         = data['week']
out['weekly sum']   = data['weekly']

out = out.set_index(['week','date'])

with open('show.txt', 'w') as myFile:
    with redirect_stdout(myFile):
        # Pandas
        print(out)
        ## Tabulate
        #from tabulate import tabulate
        #print(tabulate(out, headers='keys', tablefmt='psql'))
    


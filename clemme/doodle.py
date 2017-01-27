#local database stuff
import pymongo
from pymongo import MongoClient

import pandas as pd

#auxiliary
import datetime
import pprint #pretty printing
import matplotlib.pyplot as plt
import numpy as np

def dt_to_wt(dt):
### datetime to weektime (linear from 0 to 7 with one week period. Monday 00:00 is zero)
    return dt.weekday()+(dt.hour)/24+(dt.minute)/24/60
def dt_to_dyt(dt):
### datetime to daytime (linear from 0 to 1 with one day period. 00:00 is zero)
    return (dt.hour)/24+(dt.minute)/24/60

#MAIN
print("starting")
client = MongoClient('localhost',27017) 
try:
    db = client['smartshark_test']
    commits = db['commit']
    df = pd.DataFrame(list(commits.find()))
    df['author_date_wt'] = df['author_date'].apply(dt_to_wt)
    df['committer_date_wt'] = df['committer_date'].apply(dt_to_wt)
    df['committer_date_dyt'] = df['committer_date'].apply(dt_to_dyt)
    print("done loading data")

    df.plot(kind='scatter', x='author_date_wt', y='committer_date_wt')  
    plt.savefig("authordate_vs_commitdate.png")
    plt.clf()

    df['committer_date_wt'].plot(kind='hist', bins=7)
    plt.savefig("weekperiod_rough.png")
    plt.clf()

    df['committer_date_wt'].plot(kind='hist', bins=100)
    plt.savefig("weekperiod.png")
    plt.clf()

    df['committer_date_dyt'].plot(kind='hist', bins=30)
    plt.savefig("dayperiod.png")
    plt.clf()

    daytimelist=df['committer_date_dyt'].tolist()
    #square figure forced
    fig = plt.figure(figsize=(8,8))
    ax = fig.add_axes([0.1, 0.1, 0.8, 0.8], polar=True)
    N = 100
    theta = np.arange(0.0, 2*np.pi, 2*np.pi/N)
    values = [len([t for t in daytimelist if (n/N<= t <(n+1)/N)]) for n in range(0,N)]
    width = 2*np.pi/N
    bars = ax.bar(theta, values, width=width, bottom=0.0)
    fig.savefig("dayperiod_polar.png")
finally:
    client.close()

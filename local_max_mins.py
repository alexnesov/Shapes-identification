import pandas as pd
from scipy.signal import argrelextrema
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta 
import matplotlib.pyplot as plt
import numpy as np


ticker = "MSFT"
n=3 # number of points to be checked before and after (for min/max)


def pull_data(ticker):
    pd.set_option('display.max_rows', None)
    today = str(datetime.today().strftime('%Y-%m-%d'))
    fin = yf.download(ticker, start = "2020-01-01", end = today, period = "1d")
    return fin 



def get_min_max(n):
    rs = np.array(fin['Adj Close'])
    df = pd.DataFrame(rs, columns=['Close'])
    # Find local peaks
    df['min'] = df.iloc[argrelextrema(df.Close.values, np.less_equal, order=n)[0]]['Close']
    df['max'] = df.iloc[argrelextrema(df.Close.values, np.greater_equal, order=n)[0]]['Close']
    df['Date'] = fin.index
    # Inspiration: https://stackoverflow.com/questions/48023982/pandas-finding-local-max-and-min?rq=1
    df['flag_min'] = np.where(df['min'].notna(),1,0)
    df['flag_max'] = np.where(df['max'].notna(),1,0)
    
    # We need to have Date as index for subsequent code, 
    # but if re-run this code in the same kernel session we would get an error. 
    # This is why we need this control flow tool    
    if df.index.name != 'Date':
        df = df.set_index('Date')
    else:
        pass
    return df



def generate_plot():
    fig = plt.figure(figsize=(15,8))
    ax1 = fig.add_subplot(111, ylabel='Close',xlabel='Date')
    df.Close.plot(ax=ax1, color='black', lw=2, alpha=0.4)
    ax1.plot(df.loc[df.flag_min == 1.0].index,
        df.Close[df.flag_min == 1.0],
        '^', markersize=9, color='purple', label='local min')
    ax1.plot(df.loc[df.flag_max == 1.0].index,
        df.Close[df.flag_max == 1.0],
        '*', markersize=9, color='green', label='local max')
    ax1.grid(color='grey', linestyle='-', linewidth=0.25, alpha=0.6)
    ax1.spines["top"].set_visible(False)    
    ax1.spines["bottom"].set_visible(False)    
    ax1.spines["right"].set_visible(False)    
    ax1.spines["left"].set_visible(False) 
    ax1.set_title(f"{ticker},n={n}")
    ax1.legend()



if __name__ == "__main__":
    fin = pull_data(ticker)
    df= get_min_max(n)
    generate_plot()

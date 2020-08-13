# A class with two functions that we can optionnaly call?
from scipy.signal import savgol_filter
import pandas as pd
import numpy as np
from datetime import datetime, timedelta 
import yfinance as yf
import matplotlib.pyplot as plt

# Parameters
n=5
ticker = "msft"

def pull_data(ticker):
    pd.set_option('display.max_rows', None)
    today = str(datetime.today().strftime('%Y-%m-%d'))
    fin = yf.download(ticker, start = "2020-01-01", end = today, period = "1d")
    fin = fin.reset_index()
    return fin 


def find_all(df):
    """
    returns:  list of valid indices
    """
    # all local minimums
    valid = []
    df['index'] = list(range(0,len(df)))
    # pseudo_index = list(range(0,len(df)))

    df = df.reset_index()
    for index in list(df['Close'].index):
        try:
            if df['Close'][index] < df['Close'][index-1] and \
                df['Close'][index] < df['Close'][index+1]:
                valid.append(index)
        except KeyError:
            pass

    return valid


def from_idx_to_DF(valid):
    """
    :param 1: a list if indices that represent the valid rows
    """
    ones = [1] * len(valid)
    new_zip = list(zip(valid,ones))
    new_df = pd.DataFrame(new_zip, columns=['index','flag'])
    final_df = df.set_index('index').join(new_df.set_index('index'))
    merged = df.merge(new_df, on='index', how='left')
    merged['flag_min'] = np.where(merged['flag'].notna(),1,0)
    merged = merged.set_index('Date')

    return merged


def generate_plot(df):
    fig = plt.figure(figsize=(15,8))
    ax1 = fig.add_subplot(111, ylabel='Close',xlabel='Date')
    df.Close.plot(ax=ax1, color='black', lw=2, alpha=0.4)
    ax1.plot(df.loc[df.flag_min == 1.0].index,
        df.Close[df.flag_min == 1.0],
        '^', markersize=9, color='purple', label='local min')
    # ax1.plot(df.loc[df.flag_max == 1.0].index,
    #     df.Close[df.flag_max == 1.0],
    #     '*', markersize=9, color='green', label='local max')
    ax1.grid(color='grey', linestyle='-', linewidth=0.25, alpha=0.6)
    ax1.spines["top"].set_visible(False)    
    ax1.spines["bottom"].set_visible(False)    
    ax1.spines["right"].set_visible(False)    
    ax1.spines["left"].set_visible(False) 
    ax1.set_title(f"{ticker}")
    ax1.legend()


def second_filter(n,valid):
    df = pull_data(ticker="MSFT")
    df['index'] = list(range(0,len(df)))
    # broader local minimums
    final_mins_idx = []
    for i in valid:
        try:
            print(df['Close'][i])
            start = i - n
            end = i + n 
            interval = list(range(start,end))
            in_interval = []
            prices_in_interval = []
            for v in valid:
                if v in interval:
                    in_interval.append(v)
                    prices_in_interval.append(df['Close'][v])
            
            indexes_mins = [i for i, x in enumerate(prices_in_interval) \
                if x == min(prices_in_interval)]
            
            # usualy we are going to get only one min (the probability to 
            # get exact two same prices, on decimals level on a 10 days 
            # interval for a same stock if very very mpw). but we never know
            for i in indexes_mins:
                final_mins_idx.append(in_interval[i])
        except KeyError:
            pass
    final_mins_idx_unique = np.unique(final_mins_idx)

    return final_mins_idx_unique


if __name__ == '__main__':
    df = pull_data('msft')
    valid = find_all(df)
    findAllDF = from_idx_to_DF(valid)
    generate_plot(findAllDF)
    filtered = second_filter(n,valid)
    filteredDF = from_idx_to_DF(valid=filtered)
    generate_plot(filteredDF)




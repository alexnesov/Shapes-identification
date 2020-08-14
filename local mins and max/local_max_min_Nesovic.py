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
start = "2020-01-01"

def pull_data(ticker, start):
    pd.set_option('display.max_rows', None)
    today = str(datetime.today().strftime('%Y-%m-%d'))
    fin = yf.download(ticker, start = start, end = today, period = "1d")
    fin = fin.reset_index()
    return fin 


class get_local_mins_max:
    """
    :param df: dataframe with 2 columns min: Date, Close
    :param n: n defines the level of granularity (the scope) for the second algo

    You can either go for all local mins by calling the "find_all_mins" methods
    Or you can directly call the "minsOfmins" methods
    """
    # class attributes
    def __init__(self,df,n):
        # instance attributes
        self.n = n
        self.df = df
        self.mins = []
        self.merged = None
        self.filter_one = "no"

    def from_idx_to_DF(self):
        """
        1. Takes output of first filter or second. The output we are talking about is a 
        list of indices indicate where the mins are
        2. Creates a flag column, every flag being crated thanks to this list of minds indices

        returns: dataframe
        """
        ones = [1] * len(self.mins)
        new_zip = list(zip(self.mins,ones))
        new_df = pd.DataFrame(new_zip, columns=['index','flag'])
        merged = self.df.merge(new_df, on='index', how='left')
        merged['flag_min'] = np.where(merged['flag'].notna(),1,0)
        merged = merged.set_index('Date')

        self.merged = merged
        return self.merged

    def find_all_mins(self):
        """
        returns:  list of valid indices
        """
        # all local minimums
        valid = []
        self.df['index'] = list(range(0,len(self.df)))

        self.df = self.df.reset_index()
        for index in list(self.df['Close'].index):
            try:
                if self.df['Close'][index] < self.df['Close'][index-1] and \
                    self.df['Close'][index] < self.df['Close'][index+1]:
                    valid.append(index)
            except KeyError:
                pass

        self.mins = valid
        self.merged = self.from_idx_to_DF()
        return self.mins

    def second_algorithm(self):
        df = pull_data(ticker="MSFT")
        df['index'] = list(range(0,len(df)))
        # broader local minimums
        final_mins_idx = []
        for i in self.mins:
            try:
                print(df['Close'][i])
                start = i - self.n
                end = i + self.n 
                interval = list(range(start,end))
                in_interval = []
                prices_in_interval = []
                for v in self.mins:
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

        self.mins = final_mins_idx_unique
        self.merged = self.from_idx_to_DF()
        return final_mins_idx_unique

    def minsOfmins(self):
        if self.filter_one == 'no':
            self.find_all_mins()
            self.second_algorithm()
        else:
            self.second_algorithm()

    def generate_plot(self):
        fig = plt.figure(figsize=(15,8))
        ax1 = fig.add_subplot(111, ylabel='Close',xlabel='Date')
        self.merged.Close.plot(ax=ax1, color='black', lw=2, alpha=0.4)
        ax1.plot(self.merged.loc[self.merged.flag_min == 1.0].index,
            self.merged.Close[self.merged.flag_min == 1.0],
            '^', markersize=9, color='purple', label='local min')
        # ax1.plot(self.merged.loc[self.merged.flag_max == 1.0].index,
        #     self.merged.Close[self.merged.flag_max == 1.0],
        #     '*', markersize=9, color='green', label='local max')
        ax1.grid(color='grey', linestyle='-', linewidth=0.25, alpha=0.6)
        ax1.spines["top"].set_visible(False)    
        ax1.spines["bottom"].set_visible(False)    
        ax1.spines["right"].set_visible(False)    
        ax1.spines["left"].set_visible(False) 
        ax1.set_title(f"{ticker}")
        ax1.legend()



if __name__ == '__main__':
    df = pull_data(ticker,start)
    msft = get_local_mins_max(df,n)
    msft.minsOfmins()
    msft.generate_plot()
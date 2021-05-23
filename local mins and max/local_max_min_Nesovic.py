# A class with two functions that we can optionnaly call?
from scipy.signal import savgol_filter
import pandas as pd
import numpy as np
from datetime import datetime, timedelta 
import yfinance as yf
import matplotlib.pyplot as plt
#pd.set_option('display.max_rows', None)
import sys

# Parameters
START = "2020-01-01"
tickers = ['MSFT', 'TSLA', 'AAPL', 'PG', 'INSG', 'PLUG']



def pull_data(ticker, START):
    """
    Pulls stock market data from yahoo finance

    :ticker: stock string identifier
    :param START: format yyyy-mm-dd
    """
    today = str(datetime.today().strftime('%Y-%m-%d'))
    df = yf.download(ticker, start = START, end = today, period = "1d")
    df = df.reset_index()
    return df 


df = pull_data('TSLA', '2021-01-01')

class local_extremas:
    """
    :param ticker: STRING, the ticker of the stock
    :param df: DATAFRAME, stock market data, it needs to contain:
    -A 'Date' column
    -A 'Close' column
    :param n: INT, n defines the level of granularity (the scope) for the second algo
    :args: pol and win_size are optionally modifiable for Savgol filter

    You can either go for all local mins by calling the "find_all_mins" method
    Or you can directly call the "minsOfmins" method
    """

    def __init__(self, ticker, df, n=5, pol=3, win_size=51):
        # instance attributes
        self.ticker = ticker
        self.df = df[['Date','Close']]
        self.n = n
        self.minsIDX = [] # Index of mins, not the min value itself
        self.nb_mins = 0
        self.CalculatedMinsDF = None
        self.all_local_mins = "deactivated"
        self.sav = "deactivated"
        self.localminMode = None

        # polynomial order & window_size for Savgol filter
        self.pol = pol
        self.win_size = win_size

    def __repr__(self):
        return '{Ticker:'+self.ticker+', number of local mins:'+str(self.nb_mins)+f' Mode: {self.localminMode} '+'}'

    def countMin(self):
        self.nb_mins = len(self.minsIDX)


    def mergeMinstoIntialDF(self):
        """
        1. Takes output of filter. The output is a 
        list of indices indicate where the mins are
        2. Creates a flag column, every flag being crated thanks to this list of minds indices

        returns: dataframe
        """
        ListOfOnes = [1] * len(self.minsIDX)
        minimumsZipped = list(zip(self.minsIDX,ListOfOnes))
        minimumsDF = pd.DataFrame(minimumsZipped, columns=['copyIndex','flag_min'])
        self.CalculatedMinsDF = self.df.merge(minimumsDF, on='copyIndex', how='left')
        self.CalculatedMinsDF['flag_min'] = np.where(self.CalculatedMinsDF['flag_min'].notna(),1,0)
        self.CalculatedMinsDF = self.CalculatedMinsDF.set_index('Date')

        return self.CalculatedMinsDF


    def find_all_mins(self):
        self.df['copyIndex'] = list(range(0,len(self.df)))

        for i in list(self.df.index):
            try:
                if self.df['Close'][i] < self.df['Close'][i-1] and \
                    self.df['Close'][i] < self.df['Close'][i+1]:
                    self.minsIDX.append(i)
            except KeyError:
                pass
        
        print(self.minsIDX)
        self.mergeMinstoIntialDF()
        self.countMin()
        self.localminMode = 'allMins'


    def savgol(self):
        yhat = savgol_filter(self.df.Close, self.win_size, self.pol)
        self.sav = "activated"
        self.CalculatedMinsDF['Savgol'] = yhat
        self.generate_plot()

def generate_plot(df, ticker):
    """
    """
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


def main():

    genExtremas = local_extremas('TSLA',df)
    genExtremas.df
    genExtremas.find_all_mins()
    genExtremas.mergeMinstoIntialDF()

    generate_plot(genExtremas.CalculatedMinsDF, ticker="TSLA")

if __name__ == '__main__':
    main()


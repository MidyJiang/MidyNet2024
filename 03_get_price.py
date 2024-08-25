import os
import pandas as pd
import numpy as np
import time
import  yfinance as yf

print('\n',time.ctime())

start_date = "2010-01-01"
end_date = "2024-07-20"

os.makedirs(f'price/raw/', exist_ok=True)
os.makedirs(f'price/preprocessed/', exist_ok=True)

top115 = pd.read_csv('all115.csv', index_col=0)
for i,ticker in enumerate(top115.Symbol):
    try:
        # raw to csv
        raw = yf.download(ticker, start=start_date, end=end_date)
        raw.to_csv(f'price/raw/{ticker}.csv')
        # pre-processed to txt
        df = pd.DataFrame({'mv%': raw['Close'].pct_change().shift(-1)}).dropna()
        df.to_csv(f'price/preprocessed/{ticker}.txt', sep='\t',  header=False, index=True)

        print(f"{i:<5}\t{ticker:<6}\t{raw.shape}")
    except:
        print(f"{i:<5}\t{ticker:<6}\tFalied.")

print('\n',time.ctime())
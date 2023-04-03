import pandas as pd
from pandas_datareader import wb
#from pandas_datareader import data
import yfinance as yf
import matplotlib.pyplot as plt
import seaborn as sns
from functools import reduce

pd.set_option('display.width', 320)
pd.set_option('display.max_columns', 10)

#import market cap data, set year as index and division with 1M

market_cap = pd.read_csv('https://raw.githubusercontent.com//vpuskar/stockus/main/market_cap_series.csv').set_index('Year').div(1000000)

#inspect market cap data
print(market_cap.head())

#retireve data from yfinance
tickers_list= ['AAPL', 'MSFT', 'TSLA', 'XOM', 'JNJ', 'JPM', 'AMZN', 'META', 'T', 'GOOG']
start_date='2014-01-01'
end_date='2021-12-31'
stocks = pd.DataFrame(columns=tickers_list)

#print(yf)

stocks = yf.download(tickers_list, start_date, end_date)['Adj Close']
sp500 = yf.download('^GSPC', start=start_date, end=end_date, auto_adjust=True, progress=False)[['Close']].rename(columns={'Close': 'sp500'})

stocks['sp500']=sp500
#inspect stocks
print(stocks.head())

#plot stock prices series
stocks.plot(subplots=True, title='Stocks price')
plt.show()

#normalize stock prices to be comparable

first_price=stocks.iloc[0]
normalized=stocks.div(first_price).mul(100)

normalized.plot(title='Stocks_normalized')
plt.show()


#compare stock returns against benchmark sp500
tickers=['AAPL', 'MSFT', 'TSLA', 'XOM', 'JNJ', 'JPM', 'AMZN', 'META', 'T', 'GOOG', 'sp500']
diff_benchmark = normalized[tickers].div(normalized['sp500'], axis=0)

#inspect diff_benchmark
#print(diff_benchmark.head())

diff_benchmark.plot(title='sp500 benchmark comparison')
plt.show()

#resample df to annual level and show returns correlations
stocks1=stocks.resample('A').last()
stocks_return=stocks1.pct_change()
stocks_corr=stocks_return.corr()

#inspect stocks_corr
#print(stocks_corr.head())

#visualise correlation
sns.heatmap(stocks_corr, annot=True).set_title("Stocks_correlation")
plt.legend([],[], frameon=False)
plt.show()


#mean reversion
#given that investors may overeact to the stock related news after large jumps or drops, price tend to revert to the previoous levels
#in fact a popular trading strategy is based on mean reversion
#https://www.investopedia.com/terms/m/meanreversion.asp
#folliwing we'll test weekly and annual data autocorrelation, negative autocorr means mean reverting, positive autocorr indicates trend

stocks_weekly=stocks.resample('W').last()
returns_weekly = stocks_weekly.pct_change()
stocks_annual=stocks.resample('A').last()
returns_annual = stocks_annual.pct_change()

#function to calculate autocorrelation

def stock_acorr (var):
    return var.squeeze().autocorr()

stock_names = ['AAPL', 'MSFT', 'TSLA', 'XOM', 'JNJ', 'JPM', 'AMZN', 'META', 'T', 'GOOG', 'sp500']

def calculate_acorr(data, name):
    return name + '_acorr', stock_acorr(data[name])

weekly_acorrs = {}
annual_acorrs = {}
for stock_name in stock_names:
    weekly_acorrs[stock_name], annual_acorrs[stock_name] = calculate_acorr(returns_weekly, stock_name), calculate_acorr(returns_annual, stock_name)

for name, value in weekly_acorrs.items():
    print(value)
for name, value in annual_acorrs.items():
    print(value)
#we can notice obvious deviation between weekly and annual data as expected


#compute total return from first and the last price from df
tot_return = stocks.iloc[-1].div(stocks.iloc[0]).sub(1).mul(100)
df = tot_return.to_frame().reset_index()
df = df.rename(columns= {0: 'Value'})
df.rename(columns = {'index':'ticker'}, inplace=True)

#visualise total return
sns.barplot(x="Value", y="ticker", data=df,
            label="Total", color="b").set_title("Stock Price Return")
plt.show()


#market cap variables
mcap_start=market_cap.iloc[-1]
mcap_end=market_cap.iloc[0]

#visualize market cap performance per stock
mcap=pd.concat([mcap_start,mcap_end], axis=1)
mcap.plot(kind='barh', title='markect cap')
plt.show()

#market cap index performance
mcap_index=market_cap.sum(axis=1)
mcap_index.plot(title='mcap_index')
plt.show()

#market cap index total return
mcap_index_return = ((mcap_index.iloc[0]/mcap_index.iloc[-1])-1)*100


#contribion to the index
total_market_cap = mcap_end.sum()
weights = mcap_end.div(total_market_cap)
weights.mul(mcap_index_return).sort_values().plot(kind='barh', title='contribution to the index')
plt.show()

#print(weights.sort_values())

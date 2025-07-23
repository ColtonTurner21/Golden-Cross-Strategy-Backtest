# Install required packages
!pip install yfinance --upgrade --user
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Parameters
ticker = 'MSFT'
start_date = '2019-01-01'
end_date = '2025-01-01'

# Import data and calculate moving averages
data = yf.download(ticker, start=start_date, end=end_date)
data.head()
data['SMA50'] = data['Close'].rolling(window=50).mean()
data['SMA200'] = data['Close'].rolling(window=200).mean()

# Signals
data['Signal'] = 0
data['Signal'] = np.where(data['SMA50'] > data['SMA200'], 1, 0)
data['Position'] = data['Signal'].diff()

# Plot price and signals
plt.figure(figsize=(10,5))
plt.plot(data['Close'], label='Close Price', alpha=0.5)
plt.plot(data['SMA50'], label='50-day SMA', alpha=0.85)
plt.plot(data['SMA200'], label='200-day SMA', alpha=0.85)
plt.plot(data[data['Position'] == 1].index, 
         data['SMA50'][data['Position'] == 1], 
         '^', markersize=10, color='g', label='Golden Cross (Buy)')
plt.plot(data[data['Position'] == -1].index, 
         data['SMA50'][data['Position'] == -1], 
         'v', markersize=10, color='r', label='Death Cross (Sell)')
plt.title(f"{ticker} Golden Cross/Death Cross Strategy")
plt.xlabel("Date")
plt.ylabel("Price ($)")
plt.legend()
plt.savefig("screenshots/Golden Cross vs Death Cross.png",  dpi=200)
plt.show()

# Daily Returns
data['Buyhold'] = data['Close'].pct_change()
data['Strategy'] = data['Buyhold'] * data['Signal'].shift(1)

# Cumulative Returns
data['Cumulative Buyhold'] = (1 + data['Buyhold']).cumprod()
data['Cumulative Strategy'] = (1 + data['Strategy']).cumprod()

# Sharpe Ratio
strategy_mean = data['Strategy'].mean() * 252
strategy_std = data['Strategy'].std() * np.sqrt(252)
sharpe_strategy = strategy_mean / strategy_std
buyhold_mean = data ['Buyhold'].mean() * 252
buyhold_std = data['Buyhold'].std() * np.sqrt(252)
sharpe_buyhold = buyhold_mean / buyhold_std

# Compound Annual Growth Rate (cagr)
n_years = (data.index[-1] - data.index[0]).days / 365.25
cagr_strategy = data['Cumulative Strategy'].iloc[-1] ** (1/n_years) - 1
cagr_buyhold = data['Cumulative Buyhold'].iloc[-1] ** (1/n_years) - 1

# Max Drawdown
roll_max_strategy = data['Cumulative Strategy'].cummax()
drawdown_strategy = (data['Cumulative Strategy'] - roll_max_strategy) / roll_max_strategy
max_drawdown_strategy = drawdown_strategy.min()
roll_max_buyhold = data ['Cumulative Buyhold'].cummax()
drawdown_buyhold = (data['Cumulative Buyhold'] - roll_max_buyhold) / roll_max_buyhold
max_drawdown_buyhold = drawdown_buyhold.min()

# Annualized volatility
volatility_strategy = data['Strategy'].std() * np.sqrt(252)
volatility_buyhold = data['Buyhold'].std() * np.sqrt(252)

plt.figure(figsize=(10,5))
plt.plot(data['Cumulative Buyhold'], label='Buy & Hold')
plt.plot(data['Cumulative Strategy'], label='Golden Cross Strategy')
plt.title(f"Cumulative Returns for {ticker}: (Golden Cross vs Buy & Hold)")
plt.legend()
plt.ylabel("Growth of $1")
plt.savefig("screenshots/Cumulative Returns: Golden Cross vs Buy & Hold.png", dpi=200)
plt.show()

print("\n===== Golden Cross Backtest Results ======")
print(f"Final Cumulative Return (Golden Cross): {(data['Cumulative Strategy'].iloc[-1] - 1):.2%}")
print(f"Final Cumulative Return (Buy & Hold): {(data['Cumulative Buyhold'].iloc[-1] - 1):.2%}")
print(f"Sharpe Ratio (Golden Cross): {sharpe_strategy:.2f}")
print(f"Sharpe Ratio (Buy & Hold): {sharpe_buyhold:.2f}")
print(f"CAGR (Golden Cross): {cagr_strategy:.2%}")
print(f"CAGR (Buy & Hold): {cagr_buyhold:.2%}")
print(F"Max Drawdown (Golden Cross): {max_drawdown_strategy:.2%}")
print(F"Max Drawdown (Buy & Hold): {max_drawdown_buyhold:.2%}")
print(F"Annualized Volatility (Golden Cross): {volatility_strategy:.2%}")
print(F"Annualized Volatility (Buy & Hold) {volatility_buyhold:.2%}")

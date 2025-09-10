## Golden-Cross-Strategy-Backtest
## What This Project Does
- Downloads historical stock price data for Nvidia from January 2019-Janurary 2025 using yfinance
- Calculates simple moving average(SMA) for 50 day and 200 day
- Simulates daily trading for Golden Cross and Buy & Hold
- Incorporates transaction costs to show net-of-cost returns
- Calculates key metrics to compare Golden Cross vs. Buy & Hold
- Key metrics include cumulative returns, average annual return, annualized volatility, Sharpe ratio, and maximum drawdown
- Applies statistical inference such as confidence intervals for mean returns, hypothesis tests, bootstrap Sharpe ratio, and normality checks
- Plots price, moving averages, buy/sell signals, and cumulative returns

## Results

| Metric                     | Golden Cross | Buy & Hold |
|----------------------------|--------------|------------|
| Final Cumulative Return    | 218.07%      | 342.24%    |
| Sharpe Ratio               | 0.93         | 1.00       |
| CAGR                       | 21.29%       | 28.14%     |
| Max Drawdown               | -28.04%      | -37.15%    |
| Annualized Volatility      | 24.02%       | 29.00%     |

## Insights
- The Buy & Hold strategy outperformed the Golden Cross due to the bull market during this time
- The Golden Cross strategy still had lower max drawdown and volatility
- The Golden Cross can be an effective strategy to mitigate risk especially during a choppy market

## How to Run
1. Clone the repo: 'git clone https://github.com/coltonturner21/Golden-Cross-Strategy-Backtest.git'
2. Install requirements: 'pip install yfinance pandas numpy matplotlib'
3. Open the notebook: Golden_Cross_Strategy_Backtest.ipynb in Jupyter Notebook
4. Run the single cell to generate plots and results

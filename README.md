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

## Results (NVDA, 2019–2025)

| Metric                   | Golden Cross (Gross) | Golden Cross (Net, 10 bps) | Buy & Hold |
|-------------------------|----------------------|-----------------------------|------------|
| Average Annual Return   | 77.14%               | 77.08%                      | 77.71%     |
| Annualized Volatility   | 47.33%               | 47.33%                      | 53.04%     |
| Sharpe Ratio            | 1.63                 | 1.63                        | 1.47       |
| Maximum Drawdown        | -37.55%              | -37.55%                     | -66.34%    |


## Insights
- The Buy & Hold ever so slightly out performed the Golden Cross during a period of high growth for Nvidia
- The Golden Cross strategy had lower volatility and significantly lower drawdowns, meaning it had a smoother ride with less severe losses during market pullbacks
- This shows that the Golden Cross can be an effective strategy for mitigating risk, while not losing too much on the returns side



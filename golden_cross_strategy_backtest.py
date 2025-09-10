import numpy as np
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
from scipy import stats
import os


ticker     = "NVDA"
start_date = "2019-01-01"
end_date   = "2025-01-01"

# One-way transaction cost in basis points (bps)
ONE_WAY_BPS = 10        
SLIPPAGE_BPS = 0        
TRADING_DAYS = 252

out_dir    = "screenshots"
os.makedirs(out_dir, exist_ok=True)

def bps_to_decimal(bps):  
    return bps / 10_000.0

TX_COST = bps_to_decimal(ONE_WAY_BPS + SLIPPAGE_BPS)

#  DATA 
data = yf.download(ticker, start=start_date, end=end_date, auto_adjust=True)
data = data[['Close']].copy()

# Moving averages
data['SMA50']  = data['Close'].rolling(window=50).mean()
data['SMA200'] = data['Close'].rolling(window=200).mean()
# Signals & positions (no lookahead)
data['Signal']   = (data['SMA50'] > data['SMA200']).astype(int)
data['Position'] = data['Signal'].shift(1).fillna(0)

# Daily buy/hold returns
data['BuyHold'] = data['Close'].pct_change()

# Strategy returns BEFORE costs: only earn return when in position
data['Strategy_gross'] = data['BuyHold'] * data['Position']

# Transaction costs 
# Trades happen when Position changes (0->1 buy, 1->0 sell)
# One-way cost charged ON THE DAY OF CHANGE.
data['Turnover'] = data['Position'].diff().abs().fillna(0)  # 1 on enter/exit, 0 otherwise
# Cost in return space (percentage)
data['TxCost'] = data['Turnover'] * TX_COST
data['Strategy_net'] = data['Strategy_gross'] - data['TxCost']
data = data.dropna()

# Cumulative Plots
plt.figure(figsize=(10, 5))
plt.plot((1 + data['BuyHold']).cumprod(), label='Buy & Hold')
plt.plot((1 + data['Strategy_gross']).cumprod(), label='Golden Cross (Gross)')
plt.plot((1 + data['Strategy_net']).cumprod(), label=f'Golden Cross (Net, {ONE_WAY_BPS} bps)')
plt.title(f"Cumulative Returns — {ticker} | GC vs GC Net vs Buy&Hold")
plt.ylabel("Growth of $1")
plt.legend()
plt.tight_layout()
plt.savefig(f"{out_dir}/cumulative_{ticker}_tx.png", dpi=200)
plt.close()

# METRICS 
def ann_stats(returns: pd.Series):
    mu_d  = returns.mean()
    sd_d  = returns.std(ddof=1)
    mu_a  = mu_d * TRADING_DAYS
    sd_a  = sd_d * np.sqrt(TRADING_DAYS)
    sharpe = mu_a / sd_a if sd_a > 0 else np.nan
    return {"mu_daily": mu_d, "sd_daily": sd_d, "mu_annual": mu_a, "sd_annual": sd_a, "sharpe": sharpe}

bh_stats  = ann_stats(data['BuyHold'])
gcg_stats = ann_stats(data['Strategy_gross'])
gcn_stats = ann_stats(data['Strategy_net'])

def max_drawdown(cum_curve: pd.Series):
    roll_max = cum_curve.cummax()
    dd = (cum_curve - roll_max) / roll_max
    return float(dd.min())

cum_bh  = (1 + data['BuyHold']).cumprod()
cum_gcg = (1 + data['Strategy_gross']).cumprod()
cum_gcn = (1 + data['Strategy_net']).cumprod()
mdd_bh, mdd_gcg, mdd_gcn = map(max_drawdown, [cum_bh, cum_gcg, cum_gcn])

# Statistical Analysis
def mean_ci(series: pd.Series, alpha=0.05):
    x = series.dropna().values
    n = len(x)
    mean = x.mean()
    se = stats.sem(x, ddof=1) if n > 1 else np.nan
    if n < 2 or np.isnan(se):
        return mean, np.nan, np.nan
    tcrit = stats.t.ppf(1 - alpha/2, df=n-1)
    return mean, mean - tcrit*se, mean + tcrit*se
bh_mean,  bh_lo,  bh_hi  = mean_ci(data['BuyHold'])
gcg_mean, gcg_lo, gcg_hi = mean_ci(data['Strategy_gross'])
gcn_mean, gcn_lo, gcn_hi = mean_ci(data['Strategy_net'])

# Tests
t_stat, t_p = stats.ttest_ind(data['Strategy_net'], data['BuyHold'], equal_var=False, nan_policy='omit')
u_stat, u_p = stats.mannwhitneyu(data['Strategy_net'], data['BuyHold'], alternative='two-sided')
sh_bh  = stats.shapiro(data['BuyHold'].dropna().sample(min(5000, len(data)), random_state=42))[1]
sh_gcn = stats.shapiro(data['Strategy_net'].dropna().sample(min(5000, len(data)), random_state=42))[1]

def iqr(series: pd.Series):
    q1, q3 = np.percentile(series.dropna(), [25, 75])
    return q3 - q1

bh_med,  bh_iqr  = np.median(data['BuyHold']), iqr(data['BuyHold'])
gcn_med, gcn_iqr = np.median(data['Strategy_net']), iqr(data['Strategy_net'])

def bootstrap_sharpe(returns: pd.Series, B=5000, seed=42):
    rng = np.random.default_rng(seed)
    x = returns.dropna().values
    n = len(x)
    out = np.empty(B)
    for b in range(B):
        sample = x[rng.integers(0, n, n)]
        mu_d = sample.mean()
        sd_d = sample.std(ddof=1)
        out[b] = np.nan if sd_d == 0 else (mu_d*TRADING_DAYS) / (sd_d*np.sqrt(TRADING_DAYS))
    out = out[~np.isnan(out)]
    return out.mean(), *np.percentile(out, [2.5, 97.5])

bh_sh_boot,  bh_sh_lo,  bh_sh_hi  = bootstrap_sharpe(data['BuyHold'])
gcn_sh_boot, gcn_sh_lo, gcn_sh_hi = bootstrap_sharpe(data['Strategy_net'])
# Histogram
plt.figure(figsize=(10,5))
plt.hist(data['BuyHold'].dropna(), bins=80, alpha=0.55, label='Buy & Hold')
plt.hist(data['Strategy_net'].dropna(), bins=80, alpha=0.55, label=f'GC Net ({ONE_WAY_BPS} bps)')
plt.title(f"Distribution of Daily Returns — {ticker}")
plt.xlabel("Daily Return"); plt.ylabel("Frequency")
plt.legend(); plt.tight_layout()
plt.savefig(f"{out_dir}/hist_daily_{ticker}_tx.png", dpi=200)
plt.close()

# Summary Table
def pct(x): return f"{100*x:.2f}%"
print("\n================ Golden Cross Backtest — Statistical Evaluation (with Transaction Costs) ================\n")
print(f"Ticker: {ticker}   Period: {start_date} → {end_date}   Observations: {len(data):,}")
print(f"Costs: one-way = {ONE_WAY_BPS} basis points (+ slippage {SLIPPAGE_BPS} bps). "
      f"Round-trip ≈ {2*ONE_WAY_BPS} basis points.\n")

print("Annualized Performance (per year)")
print(f"  Buy and Hold: Average Return = {pct(bh_stats['mu_annual'])}, "
      f"Volatility = {pct(bh_stats['sd_annual'])}, "
      f"Sharpe Ratio = {bh_stats['sharpe']:.2f}, "
      f"Maximum Drawdown = {pct(mdd_bh)}")

print(f"  Golden Cross Gross: Average Return = {pct(gcg_stats['mu_annual'])}, "
      f"Volatility = {pct(gcg_stats['sd_annual'])}, "
      f"Sharpe Ratio = {gcg_stats['sharpe']:.2f}, "
      f"Maximum Drawdown = {pct(mdd_gcg)}")

print(f"  Golden Cross Net: Average Return = {pct(gcn_stats['mu_annual'])}, "
      f"Volatility = {pct(gcn_stats['sd_annual'])}, "
      f"Sharpe Ratio = {gcn_stats['sharpe']:.2f}, "
      f"Maximum Drawdown = {pct(mdd_gcn)}\n")
print("Mean Daily Return with 95% Confidence Interval")
print(f"  Buy and Hold: {bh_mean:.6f}  (Range: {bh_lo:.6f} to {bh_hi:.6f})")
print(f"  Golden Cross Gross: {gcg_mean:.6f} (Range: {gcg_lo:.6f} to {gcg_hi:.6f})")
print(f"  Golden Cross Net: {gcn_mean:.6f} (Range: {gcn_lo:.6f} to {gcn_hi:.6f})\n")

print("Hypothesis Tests (Golden Cross Net vs Buy and Hold)")
print(f"  Welch t-test: t-statistic = {t_stat:.3f},  p-value = {t_p:.4f}  (H0: means are equal)")
print(f"  Mann-Whitney U test: U-statistic = {u_stat:.0f}, p-value = {u_p:.4f}  (H0: distributions are the same)\n")

print("Normality Test (Shapiro-Wilk, p-values; low p-value means data is not normal)")
print(f"  Buy and Hold: p-value = {sh_bh:.4f}")
print(f"  Golden Cross Net: p-value = {sh_gcn:.4f}\n")

print("Nonparametric Summary")
print(f"  Buy and Hold: Median = {bh_med:.6f}, Interquartile Range = {bh_iqr:.6f}")
print(f"  Golden Cross Net: Median = {gcn_med:.6f}, Interquartile Range = {gcn_iqr:.6f}\n")

print("Bootstrap Sharpe Ratio with 95% Confidence Interval")
print(f"  Buy and Hold: Average Sharpe = {bh_sh_boot:.2f}, "
      f"Range = [{bh_sh_lo:.2f}, {bh_sh_hi:.2f}]")
print(f"  Golden Cross Net: Average Sharpe = {gcn_sh_boot:.2f}, "
      f"Range = [{gcn_sh_lo:.2f}, {gcn_sh_hi:.2f}]")

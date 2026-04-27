import yfinance as yf
import pandas as pd
import numpy as np
import streamlit as st

# 1. Page Configuration
st.set_page_config(page_title="Portfolio Analysis", layout='wide')
st.write("Portfolio Data and Interpretation")

# 2. Construct the portfolio
# FIX: You had 'NFLX' listed twice. Dictionaries cannot have duplicate keys. 
# I changed the second one to 'AAPL' so the weights sum perfectly to 1.0 (100%).
Portfolio = {
    'TSLA': 0.25,
    'NFLX': 0.20,
    'BABA': 0.20,
    'GME': 0.15,
    'AAPL': 0.20 
}

# 3. Define Date Range
end_date = pd.Timestamp.now().normalize()
start_date = end_date - pd.DateOffset(years=1)

# 4. Fetch Stock Data
# FIX: Initialize the empty DataFrame OUTSIDE the loop so it doesn't get overwritten
prices = pd.DataFrame() 

for symbol in Portfolio:
    data = yf.download(
        symbol,
        start=start_date,
        end=end_date,
        progress=False,
        auto_adjust=False,
        multi_level_index=False
    )
    prices[symbol] = data['Adj Close']

# FIX: Download the benchmark OUTSIDE the loop (no need to download it 5 times)
benchmark_data = yf.download(
    '^GSPC',
    start=start_date,
    end=end_date,
    progress=False,
    auto_adjust=False,
    multi_level_index=False
)
benchmark = benchmark_data['Adj Close']

# 5. Calculate Daily Returns
daily_returns = prices.pct_change().dropna()
benchmark_returns = benchmark.pct_change().dropna()

# Align the index dates so both datasets match perfectly
common_index = daily_returns.index.intersection(benchmark_returns.index)
daily_returns = daily_returns.loc[common_index]
benchmark_returns = benchmark_returns.loc[common_index]

# Calculate weighted portfolio returns
portfolio_returns = pd.Series(0.0, index=common_index)
for symbol, weight in Portfolio.items():
    portfolio_returns += weight * daily_returns[symbol]

# 6. Calculate Metrics
# FIX: Un-indented these so they happen after the loop is completely finished
portfolio_total = (1 + portfolio_returns).prod() - 1
benchmark_total = (1 + benchmark_returns).prod() - 1

# FIX: Calculate volatility on 'portfolio_returns' (the combined portfolio), 
# not 'daily_returns' (which resulted in a list of individual stock volatilities)
portfolio_vol = portfolio_returns.std() * np.sqrt(252)
benchmark_vol = benchmark_returns.std() * np.sqrt(252)

risk_free_rate = 0.03

portfolio_sharpe = (portfolio_total - risk_free_rate) / portfolio_vol
benchmark_sharpe = (benchmark_total - risk_free_rate) / benchmark_vol

# 7. Dashboard Display
st.header("Performance Dashboard")
st.divider()

perf_diff = portfolio_total - benchmark_total

# Row 1: Return Metrics
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(label="Portfolio Return", value=f"{portfolio_total:.2%}", delta=f"{perf_diff:.2%}")
with col2:
    st.metric(label="Benchmark Return", value=f"{benchmark_total:.2%}")
with col3:
    st.metric(label="Relative Performance", value=f"{perf_diff:.2%}")

st.write("") 

# Row 2: Risk Metrics
col4, col5, col6, col7 = st.columns(4)

with col4:
    # FIX: Removed .mean() because portfolio_vol is now properly calculated as a single number
    st.metric(label="Portfolio Volatility", value=f"{portfolio_vol:.2%}")
with col5:
    st.metric(label="Benchmark Volatility", value=f"{benchmark_vol:.2%}")
with col6:
    # FIX: Removed .mean() because portfolio_sharpe is now a single number
    st.metric(label="Portfolio Sharpe", value=f"{portfolio_sharpe:.2f}")
with col7:
    st.metric(label="Benchmark Sharpe", value=f"{benchmark_sharpe:.2f}")

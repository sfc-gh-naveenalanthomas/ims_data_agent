# Home
import streamlit as st
st.set_page_config(layout="wide")


st.title("📁 Portfolio Manager Dashboard")

st.write(
   """
   This Snowflake Native App empowers **portfolio managers** with the tools needed to construct, analyze, and optimize equity portfolios using curated S&P 500 data, quantitative strategies, and backtesting insights — all within an intuitive, code-free environment.
   """
)

st.write(
   """
   ## 👋 Welcome Portfolio Manager

   Whether you're constructing new portfolios or evaluating the performance of existing ones, this dashboard provides everything you need to make informed, data-driven investment decisions.

   ### 🔍 What You Can Do Here:

   - **Construct Smart Portfolios**
     - Select stocks by sector, fundamentals, or strategy fit
     - Quickly form portfolios using performance-based filters

   - **Analyze Performance**
     - Backtest portfolios using industry-standard strategies like Equal Weight and Inverse Volatility
     - Compare against benchmarks like the S&P 500 (SPY)
     - Visualize time-series returns and key performance metrics (CAGR, Sharpe, Drawdown)

   - **Optimize Portfolio Allocation**
     - Run Monte Carlo simulations to discover optimal portfolio weights
     - Apply weights and re-run backtests for deeper comparison


   ---
   ## 🚦 Recommended Workflow

   1. **Create or import your portfolio**
   2. **Backtest with multiple weighting strategies**
   3. **Run optimization and compare results**
   4. **Evaluate performance vs. SPY and other benchmarks**

   ---

   This experience is designed to save time and unlock deep insights for modern portfolio managers — with all computations powered by Snowflake and visualized in Streamlit.
   """
)


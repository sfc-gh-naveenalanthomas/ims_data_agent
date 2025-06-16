# FSI Quantitative Research Analytics 

## Introduction
This demo shows how to use curated S&P 500 stock data to explore price trends, forecast performance, construct portfolios, compute returns using common strategies such as equal weighting and inverse volatility, and apply advanced techniques like Monte Carlo simulations. It also supports backtesting with different strategies and benchmarking against the SPY index.

While this demo touches on many areas relevant to quantitative research in financial services, it can be easily customized for specific business or client needs.

### What are the steps in the app?
The users of the app go through the following workflow:

- **Data Collection**: Market data is preloaded for the demo, primarily focused on S&P 500 constituents. No external ETL is needed.
- **Data Exploration**: The Streamlit app helps visualize moving averages, RSI plots (to detect overbought/oversold signals), and run basic time-series forecasting using ARIMA or Prophet models.
- **Portfolio Construction**: Build portfolios using ticker filters such as sector or performance, sourced from S&P 500 data.
- **Portfolio Backtesting**: Run backtests using Equal Weight and Inverse Volatility strategies. View time-series returns, weights allocation, and statistical summaries. SMA-based strategy backtesting is also included.
- **Portfolio Optimization**: Use Monte Carlo simulation to identify optimized portfolio weights. Re-run backtests with these weights and compare them to basic strategies. Visualize how the optimized portfolio performs against SPY.
- **QuantPulse Agent**: Use natural language to ask questions like “What was the Sharpe ratio of my portfolio?” or “How did it perform against SPY?”

- ### Proc Usage Examples:

    -  There are various PROCs that comes along with the app. They perform the forecasting, backtesting, monte-carlo simulation etc. They can be used in your pipeline as a simple call (if needed) to perform things in bulk.
        ```sql
        CALL <app_name>.CRM.PYTHON_FUNCTIONS.SPROC_FINAL_MODEL(VARCHAR, NUMBER) -- used for forecasting
        CALL <app_name>.CRM.PYTHON_FUNCTIONS.BT_BACKTESTING(VARCHAR, VARCHAR, VARCHAR, VARCHAR, VARCHAR, VARCHAR) -- used for backtesting
        CALL <app_name>.CRM.PYTHON_FUNCTIONS.BT_BACKTESTING_MONTE_CARLO_WEIGHTS(VARCHAR, VARCHAR, VARCHAR, VARCHAR, VARCHAR, VARCHAR, VARCHAR) -- used for backtesting using Monte-Carlo weights
        CALL <app_name>.CRM.PYTHON_FUNCTIONS.DERIVE_SMA_AGAINST_BENCHMARK(VARCHAR, VARCHAR, VARCHAR, VARCHAR, VARCHAR, VARCHAR, VARCHAR, VARCHAR, VARCHAR) -- used for performing SMA backtesting against SPY benchmark
        CALL <app_name>.CRM.PYTHON_FUNCTIONS.DERIVE_SMA_AGAINST_BENCHMARK_TW(VARCHAR, VARCHAR, VARCHAR, VARCHAR, VARCHAR, VARCHAR, VARCHAR, VARCHAR, VARCHAR) -- used for performing SMA backtesting against SPY benchmark using Monte-Carlo weights
        CALL <app_name>.CRM.PYTHON_FUNCTIONS.FORECAST_FACTSET(VARCHAR, VARCHAR, VARCHAR, VARCHAR, VARCHAR) -- used for ARIMA based forecasting of prices
        CALL <app_name>.CRM.PYTHON_FUNCTIONS.PERFORM_MONTE_CARLO_SIMULATION(NUMBER, VARCHAR, VARCHAR, VARCHAR, VARCHAR, VARCHAR) -- used for performing Monte-Carlo simulation
        CALL <app_name>.CRM.PYTHON_FUNCTIONS.PROPHET_FORECAST_FACTSET(VARCHAR, VARCHAR, VARCHAR, VARCHAR, VARCHAR) -- used for forecasting using Facebook prophet library
       
- ## 💬 Sample Questions You Can Ask the QuantPulse Assistant

### 📊 Performance & Strategy Comparison
- Which portfolio has the highest compound annual growth rate (CAGR)?
- Compare the Monte Carlo and Equal Weight strategy values for the Retail portfolio.
- What’s the return difference between equal-weight and Monte Carlo-weighted strategies for each portfolio?
- Compare EqualWeight and Monte Carlo strategy returns for all portfolios.
- Which portfolios performed better than the SPY benchmark?
- What’s the max drawdown of the CONSUMERCYCLICALS_PORTFOLIO under the inverse volatility strategy?
- Show me portfolios where the Monte Carlo strategy value is greater than 1.2 compared to the SPY benchmark value.
- Get unique list of portfolios with Calmar ratio above 0.5.

### 📈 Trend & Moving Average Analysis
- Which portfolio has outperformed its 200-day moving average the most in the last month?
- How does the 50-day SMA compare to the 200-day SMA for the HEALTHCARE portfolio?
- Is the ENERGY portfolio trading above or below its 200-day SMA?
- Show the daily Equal Weight prices for INDUSTRIALS portfolio over time.

### 🧠 Fundamentals-Driven Company Questions (Stock Profile)
- Which companies in the Business Services sector have the highest earnings yield, ordered by earnings yield in descending order?
- Which companies in the Business Services sector have the highest earnings yield?
- What are the top 10 companies in the Business Services sector based on Return on Equity (ROE)?
- List the top 10 companies by return on equity.
- Show me the earnings yield and EPS growth rate for companies in the Technology sector based on the available stock profile data.
- Which stocks in the INDUSTRIALS sector have the highest EPS growth rate?
- What is the one-day price change for Consumer Non-Cyclicals sector stocks?
- Get the top 5 companies in the Technology sector based on their Return on Invested Capital (ROIC), sorted from highest to lowest ROIC.
- Which stocks had the highest 1-day percentage gain?

### 🧬 Portfolio Attribution & Contextual Understanding
- What does the CONSUMERSERVICES_PORTFOLIO consist of?
- Which portfolio descriptions include energy or renewables?

### 📅 Time Series & Period-Based Analysis
- What is the 3-month return for each portfolio under the equal weight strategy from January 1, 2018 to March 31, 2018?
- How does the CALMAR ratio trend across portfolios over the last 5 years?
- Show me the best and worst performing portfolios based on 1-year returns.

### 🚀 Multi-Domain Insightful Portfolio Analysis
- For the UTILITIES_PORTFOLIO, compare the Monte Carlo strategy value to the SPY benchmark value over the entire available time period.
- Compare the Monte Carlo strategy value to the SPY benchmark value over the entire available time period for all my portfolio and get me the top 3.

# QuantPulse Agent

from typing import Dict, List, Optional

import _snowflake
import json
import streamlit as st
import time
from snowflake.snowpark.context import get_active_session
import snowflake.permissions as permissions

sp_session = get_active_session()

DATABASE = sp_session.sql("SELECT CURRENT_DATABASE()").collect()[0][0]
SCHEMA = "CORE"
STAGE = "LIB_STG"
FILE = "fsi_stock_ticker_agent.yaml"


st.session_state.setdefault("imported_privilege_granted", False)

def send_message(prompt: str) -> dict:
    """Calls the REST API and returns the response."""
    request_body = {
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    }
                ]
            }
        ],
        "semantic_model_file": f"@{DATABASE}.{SCHEMA}.{STAGE}/{FILE}",
    }

    resp = _snowflake.send_snow_api_request(
        "POST",
        f"/api/v2/cortex/analyst/message",
        {},
        {},
        request_body,
        {},
        30000,
    )

    if resp["status"] < 400:
        return json.loads(resp["content"])
    else:
        st.session_state.messages.pop()
        raise Exception(
            f"Failed request with status {resp['status']}: {resp}"
        )

def process_message(prompt: str) -> None:
    """Processes a message and adds the response to the chat."""
    st.session_state.messages.append(
        {"role": "user", "content": [{"type": "text", "text": prompt}]}
    )
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        with st.spinner("Generating response..."):
            response = send_message(prompt=prompt)
            request_id = response["request_id"]
            content = response["message"]["content"]
            st.session_state.messages.append(
                {**response['message'], "request_id": request_id}
            )
            display_content(content=content, request_id=request_id)  # type: ignore[arg-type]


def display_content(
    content: List[Dict[str, str]],
    request_id: Optional[str] = None,
    message_index: Optional[int] = None,
) -> None:
    """Displays a content item for a message."""
    message_index = message_index or len(st.session_state.messages)
    if request_id:
        with st.expander("Request ID", expanded=False):
            st.markdown(request_id)
    for item in content:
        if item["type"] == "text":
            st.markdown(item["text"])
        elif item["type"] == "suggestions":
            with st.expander("Suggestions", expanded=True):
                for suggestion_index, suggestion in enumerate(item["suggestions"]):
                    if st.button(suggestion, key=f"{message_index}_{suggestion_index}"):
                        st.session_state.active_suggestion = suggestion
        elif item["type"] == "sql":
            display_sql(item["statement"])


@st.cache_data
def display_sql(sql: str) -> None:
    with st.expander("SQL Query", expanded=False):
        st.code(sql, language="sql")
    with st.expander("Results", expanded=True):
        with st.spinner("Running SQL..."):
            session = get_active_session()
            df = session.sql(sql).to_pandas()
            if len(df.index) > 1:
                data_tab, line_tab, bar_tab = st.tabs(
                    ["Data", "Line Chart", "Bar Chart"]
                )
                data_tab.dataframe(df)
                if len(df.columns) > 1:
                    df = df.set_index(df.columns[0])
                try:
                    with line_tab:
                        st.line_chart(df)
                    with bar_tab:
                        st.bar_chart(df)
                except Exception as e:
                    # st.info("Multiple values so couldn't plot the graphs")
                    pass
            else:
                st.dataframe(df)


def show_conversation_history() -> None:
    for message_index, message in enumerate(st.session_state.messages):
        chat_role = "assistant" if message["role"] == "analyst" else "user"
        with st.chat_message(chat_role):
            display_content(
                content=message["content"],
                request_id=message.get("request_id"),
                message_index=message_index,
            )


def reset() -> None:
    st.session_state.messages = []
    st.session_state.suggestions = []
    st.session_state.active_suggestion = None


app_db = sp_session.sql("SELECT CURRENT_DATABASE()").collect()[0][0]
app_sch = 'CRM'
st.title("QuantPulse Agent")
st.markdown(f"Semantic Model: `{FILE}`")
with st.expander("💡 Sample Questions you can ask:", expanded=True):
    st.markdown("""
    - Which portfolio has the highest compound annual growth rate (CAGR)?  
    - What’s the return difference between equal-weight and Monte Carlo-weighted strategies for each portfolio?  
    - Which portfolios performed better than the SPY benchmark?  
    - Which companies in the Business Services sector have the highest earnings yield, ordered by earnings yield in descending order?  
    - Which portfolio has outperformed its 200-day moving average the most in Dec 2019?
    """)

with st.expander("💬 More questions that the Agent can answer", expanded=False):
    st.markdown("### 📊 Performance & Strategy Comparison")
    st.markdown("""
- Which portfolio has the highest compound annual growth rate (CAGR)?  
- Compare the Monte Carlo and Equal Weight strategy values for the Retail portfolio.  
- What’s the return difference between equal-weight and Monte Carlo-weighted strategies for each portfolio?  
- Compare EqualWeight and Monte Carlo strategy returns for all portfolios.  
- Which portfolios performed better than the SPY benchmark?  
- What’s the max drawdown of the CONSUMERCYCLICALS_PORTFOLIO under the inverse volatility strategy?  
- Show me portfolios where the Monte Carlo strategy value is greater than 1.2 compared to the SPY benchmark value.  
- Get unique list of portfolios with Calmar ratio above 0.5.
    """)

    st.markdown("### 📈 Trend & Moving Average Analysis")
    st.markdown("""
- Which portfolio has outperformed its 200-day moving average the most in the last month?  
- How does the 50-day SMA compare to the 200-day SMA for the HEALTHCARE portfolio?  
- Is the ENERGY portfolio trading above or below its 200-day SMA?  
- Show the daily Equal Weight prices for INDUSTRIALS portfolio over time.
    """)

    st.markdown("### 🧠 Fundamentals-Driven Company Questions (Stock Profile)")
    st.markdown("""
- Which companies in the Business Services sector have the highest earnings yield, ordered by earnings yield in descending order?  
- Which companies in the Business Services sector have the highest earnings yield?  
- What are the top 10 companies in the Business Services sector based on Return on Equity (ROE)?  
- List the top 10 companies by return on equity.  
- Show me the earnings yield and EPS growth rate for companies in the Technology sector based on the available stock profile data.  
- Which stocks in the INDUSTRIALS sector have the highest EPS growth rate?  
- What is the one-day price change for Consumer Non-Cyclicals sector stocks?  
- Get the top 5 companies in the Technology sector based on their Return on Invested Capital (ROIC), sorted from highest to lowest ROIC.  
- Which stocks had the highest 1-day percentage gain?
    """)

    st.markdown("### 🧬 Portfolio Attribution & Contextual Understanding")
    st.markdown("""
- What does the CONSUMERSERVICES_PORTFOLIO consist of?  
- Which portfolio descriptions include energy or renewables?
    """)

    st.markdown("### 📅 Time Series & Period-Based Analysis")
    st.markdown("""
- What is the 3-month return for each portfolio under the equal weight strategy from January 1, 2018 to March 31, 2018?  
- How does the CALMAR ratio trend across portfolios over the last 5 years?  
- Show me the best and worst performing portfolios based on 1-year returns.
    """)

    st.markdown("### 🚀 Multi-Domain Insightful Portfolio Analysis")
    st.markdown("""
- For the UTILITIES_PORTFOLIO, compare the Monte Carlo strategy value to the SPY benchmark value over the entire available time period.  
- Compare the Monte Carlo strategy value to the SPY benchmark value over the entire available time period for all my portfolio and get me the top 3.
    """)


sp_session.sql("call {0}.PYTHON_FUNCTIONS.sp_init('{0}');".format(app_db)).collect()

if not st.session_state.imported_privilege_granted:
    held_privs = permissions.get_held_account_privileges(["IMPORTED PRIVILEGES ON SNOWFLAKE DB"])

    if held_privs:
        st.session_state.imported_privilege_granted = True
    else:
        permissions.request_account_privileges(["IMPORTED PRIVILEGES ON SNOWFLAKE DB"])
        st.warning("Please grant 'IMPORTED PRIVILEGES ON SNOWFLAKE DB' to use Cortex Agent.")
        
#creating views for better bot
try:
    sql_view = """
                CREATE OR REPLACE VIEW CRM.VW_PORTFOLIO_PERFORMANCE_ENRICHED AS
                    WITH metric_lookup AS (
                        SELECT * FROM VALUES
                            ('rf', 'Risk-Free Rate'),
                            ('total_return', 'Total Return of the Portfolio'),
                            ('cagr', 'Compound Annual Growth Rate (CAGR)'),
                            ('max_drawdown', 'Maximum observed drawdown during the evaluation period'),
                            ('calmar', 'Calmar Ratio (CAGR divided by Max Drawdown)'),
                            ('mtd', 'Month-to-date return'),
                            ('three_month', 'Return over the last 3 months'),
                            ('six_month', 'Return over the last 6 months'),
                            ('ytd', 'Year-to-date return'),
                            ('one_year', 'Return over the last 1 year'),
                            ('three_year', 'Return over the last 3 years'),
                            ('five_year', 'Return over the last 5 years'),
                            ('ten_year', 'Return over the last 10 years'),
                            ('incep', 'Return since inception'),
                            ('daily_sharpe', 'Daily Sharpe Ratio'),
                            ('daily_sortino', 'Daily Sortino Ratio'),
                            ('daily_mean', 'Mean daily return'),
                            ('daily_vol', 'Daily volatility'),
                            ('daily_skew', 'Daily skewness'),
                            ('daily_kurt', 'Daily kurtosis'),
                            ('best_day', 'Best performing day'),
                            ('worst_day', 'Worst performing day'),
                            ('monthly_sharpe', 'Monthly Sharpe Ratio'),
                            ('monthly_sortino', 'Monthly Sortino Ratio'),
                            ('monthly_mean', 'Mean monthly return'),
                            ('monthly_vol', 'Monthly volatility'),
                            ('monthly_skew', 'Monthly skewness'),
                            ('monthly_kurt', 'Monthly kurtosis'),
                            ('best_month', 'Best performing month'),
                            ('worst_month', 'Worst performing month'),
                            ('yearly_sharpe', 'Yearly Sharpe Ratio'),
                            ('yearly_sortino', 'Yearly Sortino Ratio'),
                            ('yearly_mean', 'Mean yearly return'),
                            ('yearly_vol', 'Yearly volatility'),
                            ('yearly_skew', 'Yearly skewness'),
                            ('yearly_kurt', 'Yearly kurtosis'),
                            ('best_year', 'Best performing year'),
                            ('worst_year', 'Worst performing year'),
                            ('avg_drawdown', 'Average drawdown across the period'),
                            ('avg_drawdown_days', 'Average number of days in drawdowns'),
                            ('avg_up_month', 'Average monthly gain during up months'),
                            ('avg_down_month', 'Average monthly loss during down months'),
                            ('win_year_perc', 'Percentage of winning years'),
                            ('twelve_month_win_perc', 'Win percentage over the last 12 months')
                        AS METRIC_LOOKUP(METRIC, DESCRIPTION)
                    )
                    SELECT
                        perf.portfolio_name,
                        d.portfolio_description,
                        perf.index AS performance_metric,
                        m.description AS performance_metric_description,
                        ROUND(perf.EqualWeight * 100, 2) AS equal_weight_strategy_pct,
                        ROUND(perf.WeightInvVol * 100, 2) AS inverse_volatility_strategy_pct,
                        ROUND(perf.MonteCarloWeights * 100, 2) AS monte_carlo_strategy_pct,
                        ROUND(sma.SMA10, 2) AS simple_moving_avg_10d,
                        ROUND(sma.SMA20, 2) AS simple_moving_avg_20d,
                        ROUND(sma.SMA50, 2) AS simple_moving_avg_50d,
                        ROUND(sma.SMA200, 2) AS simple_moving_avg_200d,
                        ROUND(sma.SPY, 2) AS spy_benchmark_value
                    FROM CRM.BT_BACKTESTING_TW_STATS_FACTSET perf
                    LEFT JOIN CRM.FACTSET_SMA_STATS sma
                        ON perf.portfolio_name = sma.portfolio_name AND perf.index = sma.index
                    LEFT JOIN metric_lookup m
                        ON perf.index = m.metric
                    LEFT JOIN CRM.VW_ALL_PORT_DESCRIPTIONS d
                        ON sma.portfolio_name = d.portfolio_name;

                """

    sp_session.sql(sql_view).collect()

    sql_view1 = """
                CREATE OR REPLACE VIEW CRM.VW_STOCK_PROFILE AS
                    SELECT  
                        t.TICKER_REGION AS ticker_with_region,
                        t.PROPER_NAME AS company_name,
                        ROUND(t.PRICE, 2) AS stock_price,
                        ROUND(t.ONE_DAY_PCT * 100, 2) AS one_day_change_percent,
                        f.SECTOR AS sector,
                        f.INDUSTRY AS industry,
                        ROUND(f.FF_ROE * 100, 2) AS return_on_equity_pct,
                        ROUND(f.FF_ROIC * 100, 2) AS return_on_invested_capital_pct,
                        ROUND(f.EARNINGS_YIELD * 100, 2) AS earnings_yield_pct,
                        ROUND(f.EPS_GROWTH_RATE * 100, 2) AS eps_growth_rate_pct
                    FROM (
                        SELECT *
                        FROM (
                            SELECT *,
                                ROW_NUMBER() OVER (PARTITION BY TICKER_REGION ORDER BY PRICE_DATE DESC) AS rn
                            FROM CRM.FACTSET_TICKER_DATA_TABLE
                        ) latest_prices
                        WHERE rn = 1
                    ) t
                    LEFT JOIN (
                        SELECT *
                        FROM (
                            SELECT *,
                                ROW_NUMBER() OVER (PARTITION BY TICKER_REGION ORDER BY MARKET_VALUE DESC) AS rn
                            FROM CRM.FACTOR_LIBRARY_CURR_TABLE
                        ) sub
                        WHERE rn = 1
                    ) f
                    ON t.TICKER_REGION = f.TICKER_REGION;

                """

    sp_session.sql(sql_view1).collect()
    
    sql_view3 = """
                CREATE OR REPLACE VIEW CRM.VW_PORTFOLIO_TRENDS AS 
                    SELECT 
                        sma.portfolio_name, 
                        d.portfolio_description, 
                        sma.DATE AS date, 
                        ROUND(sma.sma50, 2) AS simple_moving_avg_50d, 
                        ROUND(sma.sma200, 2) AS simple_moving_avg_200d, 
                        ROUND(tw.PRICE_EqualWeight, 2) AS equal_weight_price, 
                        ROUND(tw.PRICE_MonteCarloWeights, 2) AS monte_carlo_weighted_price 
                    FROM CRM.FACTSET_SMA sma 
                    LEFT JOIN CRM.BT_BACKTESTING_TW_FACTSET tw 
                        ON sma.portfolio_name = tw.portfolio_name AND sma.DATE = tw.Datestr
                    LEFT JOIN CRM.VW_ALL_PORT_DESCRIPTIONS d
                        ON sma.portfolio_name = d.portfolio_name;
                """

    sp_session.sql(sql_view3).collect()

    sql_view4 = """
                    CREATE OR REPLACE VIEW CRM.VW_PORTFOLIO_METRICS_PIVOTED_ALL_STRATEGIES AS
                        SELECT
                        portfolio_name,

                        -- CAGR
                        MAX(CASE WHEN index = 'cagr' THEN montecarloweights END) AS cagr_montecarlo,
                        MAX(CASE WHEN index = 'cagr' THEN equalweight END) AS cagr_equalweight,
                        MAX(CASE WHEN index = 'cagr' THEN weightinvvol END) AS cagr_weightinvvol,

                        -- Sharpe Ratio
                        MAX(CASE WHEN index = 'yearly_sharpe' THEN montecarloweights END) AS sharpe_montecarlo,
                        MAX(CASE WHEN index = 'yearly_sharpe' THEN equalweight END) AS sharpe_equalweight,
                        MAX(CASE WHEN index = 'yearly_sharpe' THEN weightinvvol END) AS sharpe_weightinvvol,

                        -- Volatility
                        MAX(CASE WHEN index = 'yearly_vol' THEN montecarloweights END) AS volatility_montecarlo,
                        MAX(CASE WHEN index = 'yearly_vol' THEN equalweight END) AS volatility_equalweight,
                        MAX(CASE WHEN index = 'yearly_vol' THEN weightinvvol END) AS volatility_weightinvvol,

                        -- Max Drawdown
                        MAX(CASE WHEN index = 'max_drawdown' THEN montecarloweights END) AS drawdown_montecarlo,
                        MAX(CASE WHEN index = 'max_drawdown' THEN equalweight END) AS drawdown_equalweight,
                        MAX(CASE WHEN index = 'max_drawdown' THEN weightinvvol END) AS drawdown_weightinvvol

                        FROM CRM.BT_BACKTESTING_TW_STATS_FACTSET
                        GROUP BY portfolio_name;
                """

    sp_session.sql(sql_view4).collect()  
except Exception as e:
    st.info('Please connect your portfolios or create new ones to start chatting')

if "messages" not in st.session_state:
    reset()

with st.sidebar:
    if st.button("Reset conversation"):
        reset()

show_conversation_history()

if user_input := st.chat_input("How can I help?"):
    process_message(prompt=user_input)

if st.session_state.active_suggestion:
    process_message(prompt=st.session_state.active_suggestion)
    st.session_state.active_suggestion = None
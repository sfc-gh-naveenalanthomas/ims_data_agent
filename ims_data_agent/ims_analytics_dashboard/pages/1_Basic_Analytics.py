# Portfolio Construction S&P500
import streamlit as st
import logging ,sys
import pandas as pd
import numpy as np
import matplotlib.pylab as plt
import datetime as dt
from snowflake.snowpark.context import get_active_session
import snowflake.permissions as permissions




st.set_page_config(layout="wide")

sp_session = get_active_session()

st.session_state.setdefault("customer_table_name", None)


# Initialize session variables
if "portfolio_table_ref" not in st.session_state:
    st.session_state.portfolio_table_ref = None

if "sync_complete" not in st.session_state:
    st.session_state.sync_complete = False

@st.cache_data(ttl=5)
def get_portfolio_list(_sp_session, app_db, app_sch):
    get_portfolio_name_sql_stmt = "select SUBSTR(TABLE_NAME, 6, len(table_name)) as PORTFOLIO_NAME, * from {0}.information_schema.tables where TABLE_SCHEMA = '{1}' and TABLE_NAME like 'PORT_%' \
                                        order by last_altered desc ;".format(app_db, app_sch)
    df = _sp_session.sql(get_portfolio_name_sql_stmt).to_pandas()
    return df['PORTFOLIO_NAME'].values.tolist()


@st.cache_data(ttl=1000)
def get_factset_stock_data_updated(_sp_session, shr_db, shr_sch):
    get_factset_stock_data_sql_stmt = "select TICKER_REGION, proper_name, INDUSTRY, sector, fiscal_period_end_date, market_value, currency, \
        ff_eps_basic, prev_ff_eps_basic, eps_growth_rate, ff_roe, ff_roic, solvency_ratio, ff_net_income, \
        ff_price_close_fp, earnings_yield, all_categories_momentum from {0}.{1}.FACTOR_LIBRARY_CURR_TABLE WHERE TICKER_REGION not in ('ALL-US', 'BRK.B-US') order by market_value desc;".format(shr_db, shr_sch)
                                #where ticker_region = '{0}' ;".format(ticker_region)
    df = _sp_session.sql(get_factset_stock_data_sql_stmt).to_pandas()
    return df.drop_duplicates(ignore_index=True)


@st.cache_data(ttl=900)
def write_selected_portfolio_return_risk_returns(_sp_session, df, portfolio_name, year_start, year_end, app_db, app_sch, fun_db, fun_sch):
        #st.write(year)
   df_ticker_selected = _sp_session.sql('SELECT DISTINCT(TICKER_REGION) as TICKERS from {1}.{2}.{0}'.format('PORT_{0}'.format(portfolio_name), app_db, app_sch)).to_pandas()
   ticker_list = ''
   column_name = ''
   null_stmt = ''
   table_name_append = portfolio_name +"_" +str(year_start)+"_" +str(year_end)
   for index, row in df_ticker_selected.iterrows():
      ticker_list += "'"+row['TICKERS']+"'"+","
      column_name += row['TICKERS'].split('-')[0]+","
      null_stmt += "ifnull({0},(SELECT TOP 1 {0} from TICKER_DATA_FACTSET_{1} where {0} is not null order by date asc )) as {0},".format(row['TICKERS'].split('-')[0], table_name_append)
   sql_stmt = "create or replace table {2}.{8}.TICKER_DATA_FACTSET_{4} as SELECT * FROM ( \
      SELECT TICKER_REGION, PRICE_DATE, PRICE FROM {6}.{7}.factset_ticker_data_table where PRICE_DATE in \
   (SELECT Date from {6}.{7}.FACTSET_TICKER_INDEX_TABLE where year(date) >= {3} and year(date) <= {5})  ) PIVOT (  \
   max(price) for TICKER_REGION in ({0})  \
   ) AS p(Date, {1} ) ORDER BY Date ;".format(ticker_list[:-1], column_name[:-1], app_db, year_start, table_name_append, year_end, shr_db, shr_sch, app_sch)
   cleaned_view_stmt = "create or replace view {1}.{5}.TICKER_DATA_FACTSET_CLEANED_VW_{2} as SELECT DATE, {0} from TICKER_DATA_FACTSET_{2} where DATE in (SELECT DATE FROM {3}.{4}.FACTSET_TICKER_INDEX_TABLE);".format(null_stmt[:-1],app_db, table_name_append, shr_db, shr_sch, app_sch)
   _sp_session.sql(sql_stmt).collect()
   _sp_session.sql(cleaned_view_stmt).collect()
   _sp_session.sql("CALL {1}.{3}.bt_backtesting('{4}.{5}.TICKER_DATA_FACTSET_CLEANED_VW_{2}', \
                           'BT_BACKTESTING_FACTSET', 'BT_BACKTESTING_STATS_FACTSET', 'BT_BACKTESTING_WEIGHTS_FACTSET', '{4}','{5}', '{0}')".format(portfolio_name, fun_db, table_name_append, fun_sch, app_db, app_sch)).collect()
   df = _sp_session.sql('SELECT s1*100 as S1_RETURNS, s2*100 as S2_RETURNS FROM {1}.{2}.BT_BACKTESTING_STATS_FACTSET where index = \'total_return\' and portfolio_name = \'{0}\';'.format(portfolio_name, app_db, app_sch)).to_pandas()
   return df

# streamlit run src/streamlit/App.py
with st.container():
   st.header("Portfolio Manager")
   app_db = sp_session.sql("SELECT CURRENT_DATABASE()").collect()[0][0]
   app_sch = 'CRM'
   fun_db = app_db
   fun_sch = 'PYTHON_FUNCTIONS'
   shr_db = app_db
   shr_sch = app_sch
   year_list_df = sp_session.sql("select distinct(year(PRICE_DATE)) AS DATE from {0}.{1}.FACTSET_TICKER_DATA_TABLE ORDER BY DATE ASC;".format(shr_db, shr_sch)).to_pandas()
   year_list  = list(year_list_df['DATE'])
   values = st.slider(
                  'Select a range of year to calculate the portfolio returns',
                  year_list[0], year_list[-1], (year_list[-2], year_list[-1]))
   portfolio_mode = st.radio(
      "Choose how you want to begin:",
      ["📁 Link Existing Portfolio", "🛠️ Create a New Portfolio using S&P500 data"],
      horizontal=True, index=1
   )

   if portfolio_mode.startswith("📁"):
      st.subheader(':blue[Sync your Portfolio]')
      
      with st.expander("Connecting Existing Portfolio", expanded=True):
         # Get reference associations
         ref_associations = permissions.get_reference_associations("consumer_table")

         if ref_associations:
            st.session_state.portfolio_table_ref = ref_associations[0]
         else:
            permissions.request_reference("consumer_table")
            st.warning("Please bind your portfolio table to continue.")

         if st.session_state.portfolio_table_ref:
            st.success("Your portfolio table is linked to the app successfully!")

         existing_portfolio = st.button(
                  '🔄 Sync',
                  key='existing_port',
                  type="primary",
                  disabled=st.session_state.sync_complete
               )
         if existing_portfolio:
            df = sp_session.call("core.select_object", "consumer_table").to_pandas()
            portfolio_names = df["PORTFOLIO_NAME"].dropna().unique().tolist()
            counter = 0
            # Placeholder for dynamic success messages
            status_placeholder = st.empty()
            status_placeholder.info("📦 Total portfolios to process: {}".format(len(portfolio_names)))
            for portfolio_name in portfolio_names:
               counter += 1 
               with st.spinner(f"Processing portfolio: {portfolio_name}..."):                  
                  selected_df = df[df["PORTFOLIO_NAME"] == portfolio_name]
                  sp_session.write_pandas(selected_df.drop_duplicates(ignore_index=True), 'PORT_{0}'.format(portfolio_name), auto_create_table=True, overwrite=True, database=app_db, schema=app_sch)
                  df_risk_return = write_selected_portfolio_return_risk_returns(sp_session,selected_df, portfolio_name, 
                                                                                 str(values[0]), str(values[1]), app_db, app_sch, fun_db, fun_sch)
                  sp_session.sql("CALL {3}.{4}.derive_sma_against_benchmark('TICKER_DATA_FACTSET_CLEANED_VW_{2}_{0}_{1}','FACTSET_TICKER_INDEX_TABLE',  \
                                 '{3}.{5}.data_stg','{2}', 'FACTSET_SMA','FACTSET_SMA_STATS',  \
                                 'FACTSET_SMA_WEIGHTS', '{3}', '{5}', '{6}', '{7}');".format(str(values[0]), str(values[1]), portfolio_name, app_db, fun_sch, app_sch, shr_db, shr_sch)).collect()

                  sp_session.sql("CALL {4}.{5}.perform_monte_carlo_simulation({3}, 'TICKER_DATA_FACTSET_{0}_{1}_{2}', '{0}' , 'MONTE_CARLO', '{4}', '{6}' )".format(portfolio_name, str(values[0]), str(values[1]), 10000, app_db, fun_sch, app_sch)).collect()

                  table_name_append = portfolio_name +"_" +str(str(values[0]))+"_" +str(str(values[1]))
                  sp_session.sql("CALL {1}.{4}.bt_backtesting_monte_carlo_weights('TICKER_DATA_FACTSET_CLEANED_VW_{2}', \
                              'BT_BACKTESTING_TW_FACTSET', 'BT_BACKTESTING_TW_STATS_FACTSET', 'BT_BACKTESTING_TW_WEIGHTS_FACTSET', '{0}', '{1}', '{3}')".format(portfolio_name ,app_db, table_name_append, app_sch, fun_sch)).collect() 

               # ✅ Update the same success box in-place
               status_placeholder.success(
                  f"✅ {portfolio_name} loading, backtesting and optimisation is completed!. {len(portfolio_names)-counter} portfolios remaining..."
               )
            st.session_state.sync_complete = True
            # creating combined view of the portfolios and portfolio_description for the bot
            union_clauses = []
            for name in portfolio_names:
               table_name = f"CRM.PORT_{name}"
               union_clauses.append(f"SELECT DISTINCT portfolio_name, portfolio_description FROM {table_name}")
            
            union_sql = "\nUNION ALL\n".join(union_clauses)
            sql_view = f"""
                        CREATE OR REPLACE VIEW CRM.VW_ALL_PORT_DESCRIPTIONS AS
                        {union_sql};

                        """
            sp_session.sql(sql_view).collect()
            status_placeholder.success("🎉 All the {0} portfolios processed!".format(len(portfolio_names)))

   else:
      st.subheader(':blue[Portfolio Construction]')
      
      with st.expander("Portfolio Construction", expanded=True):
         df_ticker = get_factset_stock_data_updated(sp_session, shr_db, shr_sch)  

         options_list = get_portfolio_list(sp_session, app_db, app_sch)

         # Input field with callback
         Portfolio_Name = st.text_input(
            "Please key in the portfolio name:",
            "DEMO_PORT"
         )
         Portfolio_Name = Portfolio_Name.strip()
         st.info("Please input without any spaces (as they will be stripped out) and click ENTER before selecting the stocks")
         Portfolio_Name = Portfolio_Name.upper()
         if not Portfolio_Name:
            st.warning("❗ Please enter a valid name without only spaces.")


         col1, col2, col3, col4 = st.columns(4)
         with col1:
            saved = st.button('Create Portfolio :white_check_mark:', key='save', type="primary")
         
         df_ticker.insert(0, "SELECT", False)
         edited_df = st.data_editor(df_ticker)      
         try:
            if saved:
               selected_df = edited_df.loc[edited_df['SELECT'] == True]
               sp_session.write_pandas(selected_df.drop_duplicates(ignore_index=True), 'PORT_{0}'.format(Portfolio_Name), auto_create_table=True, overwrite=True, database=app_db, schema=app_sch)
               df_risk_return = write_selected_portfolio_return_risk_returns(sp_session,selected_df, Portfolio_Name, 
                                                                                 str(values[0]), str(values[1]), app_db, app_sch, fun_db, fun_sch)
               st.subheader('Your Selected List of Portfolio')
               st.dataframe(selected_df)
               st.subheader('Returns for the Selected Years')

               col1, col2 = st.columns(2)
               col1.metric(label="Returns % - Equal Weight Strategy", value=round(df_risk_return['S1_RETURNS'][0],2))
               col2.metric(label="Returns % - Weight Inverse volatility Strategy", value=round(df_risk_return['S2_RETURNS'][0],2))
               st.session_state['Returns of Equal Weight'] = round(df_risk_return['S1_RETURNS'][0],2)
               st.session_state['Returns of Weight Inverse volatility'] = round(df_risk_return['S2_RETURNS'][0],2)
               
         except Exception as e:
            print(e)

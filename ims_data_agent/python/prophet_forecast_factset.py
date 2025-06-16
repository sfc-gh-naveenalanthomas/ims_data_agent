import pandas as pd
import snowflake.snowpark

def prophet_forecast_factset(session: snowflake.snowpark.Session, raw_table: str, out_table_name: str, 
                             stock: str, app_db: str, app_sch: str) -> str:
    import pandas as pd
    from prophet import Prophet
    df = session.sql("select PRICE_DATE as \"ds\", PRICE as \"y\" from {1} where TICKER_REGION = concat('{0}','-US')".format(stock, raw_table)).to_pandas()
    m = Prophet()
    m.fit(df)
    future = m.make_future_dataframe(periods=100, include_history=True)
    future.tail()
    forecast = m.predict(future)
    forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail()
    df['forecast'] = forecast['yhat']
    df1 = pd.concat([forecast, df], axis=1)[["ds", "y", "yhat"]]
    df1.columns = ['Date','ds', 'actual', 'predicted']

    snowpark_df = session.write_pandas(df1, out_table_name, auto_create_table=True, overwrite=True, database=app_db, schema=app_sch)
    return 'Table Inserted'
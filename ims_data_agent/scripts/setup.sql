-- Set up script for the Hello Snowflake! application.
CREATE APPLICATION ROLE IF NOT EXISTS APP_PUBLIC;
CREATE SCHEMA IF NOT EXISTS CORE;
GRANT USAGE ON SCHEMA CORE TO APPLICATION ROLE APP_PUBLIC;

CREATE SCHEMA IF NOT EXISTS TASKS;
GRANT USAGE ON SCHEMA TASKS TO APPLICATION ROLE APP_PUBLIC;

-- 2nd Part
CREATE OR ALTER VERSIONED SCHEMA CRM;
GRANT USAGE ON SCHEMA CRM TO APPLICATION ROLE APP_PUBLIC;

CREATE OR ALTER VERSIONED SCHEMA PYTHON_FUNCTIONS;
GRANT USAGE ON SCHEMA PYTHON_FUNCTIONS TO APPLICATION ROLE APP_PUBLIC;

CREATE OR REPLACE STAGE CORE.LIB_STG directory = (enable = true)
comment = 'used for holding udfs and procs.';

grant read, write on stage CORE.LIB_STG 
    to application role APP_PUBLIC;

create or replace procedure PYTHON_FUNCTIONS.sp_init(app_database varchar)
returns string
language python 
runtime_version = 3.11
handler = 'main'
packages = ('snowflake-snowpark-python', 'yaml')
as 
$$

from io import BytesIO
import snowflake.snowpark
import snowflake.snowpark.types as T
import yaml
import os

def main(session: snowflake.snowpark.Session, app_database: str):

    try:
        # move this to a parameter into the SP
        output_list = []
        output_list.append('Begin')
        
        output_list.append('file read attempt')
        input_file = session.file.get_stream('/fsi_stock_ticker_agent.yaml')
        output_list.append('file read complete')
        output_list.append('yml file creation attempt')
        session.file.put_stream(
            input_stream=input_file,
            stage_location='@CORE.LIB_STG/fsi_stock_ticker_agent.yaml',
            auto_compress = False,
            source_compression = 'NONE',
            parallel = 1, 
            overwrite = True)
        output_list.append('yml file create complete')
        
        output_list.append('process complete')
        return_str = str(output_list)
    except Exception as e:
        return_str = str(output_list)
    return return_str

$$
;

grant usage on procedure PYTHON_FUNCTIONS.sp_init(varchar) 
    to application role app_public;



CREATE OR REPLACE STREAMLIT CORE.HOME
  FROM '/ims_analytics_dashboard'
  MAIN_FILE = '/Home.py'
;

GRANT USAGE ON STREAMLIT CORE.HOME TO APPLICATION ROLE APP_PUBLIC;

create or replace stage CRM.data_stg
	directory = ( enable = true )
    comment = 'used for holding data.';


GRANT READ ON STAGE CRM.data_stg TO APPLICATION ROLE APP_PUBLIC;
GRANT WRITE ON STAGE CRM.data_stg TO APPLICATION ROLE APP_PUBLIC;


create or replace stage CORE.UDF
	directory = ( enable = true )
    comment = 'used for holding UDFs.';

GRANT READ ON STAGE CORE.UDF TO APPLICATION ROLE APP_PUBLIC;
GRANT WRITE ON STAGE CORE.UDF TO APPLICATION ROLE APP_PUBLIC;


-- Example functions from python files

create or replace procedure PYTHON_FUNCTIONS.prophet_forecast_factset(raw_table varchar, out_table_name varchar, stock varchar, app_db varchar, app_sch varchar)
    returns varchar
    language python
    runtime_version = '3.8'
    packages = ('snowflake-snowpark-python', 'holidays==0.18','prophet', 'numpy' )
    imports = ('/python/prophet_forecast_factset.py')
    handler = 'prophet_forecast_factset.prophet_forecast_factset'
    ;

GRANT USAGE ON PROCEDURE PYTHON_FUNCTIONS.prophet_forecast_factset(varchar, varchar, varchar, varchar, varchar) TO APPLICATION ROLE APP_PUBLIC;

-- Example functions from python files

CREATE OR REPLACE SECURE VIEW CRM.SAMPLE_DATA_VW AS SELECT * FROM SHARED_CONTENT.SAMPLE_DATA_VW;
GRANT SELECT ON VIEW CRM.SAMPLE_DATA_VW TO APPLICATION ROLE APP_PUBLIC;

CREATE OR ALTER VERSIONED SCHEMA CONFIG;
GRANT USAGE ON SCHEMA CONFIG TO APPLICATION ROLE APP_PUBLIC;

CREATE OR REPLACE PROCEDURE CONFIG.REGISTER_SINGLE_REFERENCE(ref_name STRING, operation STRING, ref_or_alias STRING)
  RETURNS STRING
  LANGUAGE SQL
  AS $$
    BEGIN
      CASE (operation)
        WHEN 'ADD' THEN
          SELECT SYSTEM$SET_REFERENCE(:ref_name, :ref_or_alias);
        WHEN 'REMOVE' THEN
          SELECT SYSTEM$REMOVE_REFERENCE(:ref_name);
        WHEN 'CLEAR' THEN
          SELECT SYSTEM$REMOVE_REFERENCE(:ref_name);
      ELSE
        RETURN 'unknown operation: ' || operation;
      END CASE;
      RETURN NULL;
    END;
  $$;

GRANT USAGE ON PROCEDURE CONFIG.REGISTER_SINGLE_REFERENCE(STRING, STRING, STRING)
  TO APPLICATION ROLE APP_PUBLIC;

-- This procedure allows a select statement on a table, view or external table.
CREATE OR REPLACE PROCEDURE CORE.SELECT_OBJECT(ref_name VARCHAR)
RETURNS TABLE()
LANGUAGE SQL
AS $$
    BEGIN
    let res RESULTSET := (SELECT * FROM REFERENCE(:ref_name));
        RETURN TABLE(res);
    END;
$$;

GRANT USAGE ON PROCEDURE CORE.SELECT_OBJECT(VARCHAR)
  TO APPLICATION ROLE app_public;
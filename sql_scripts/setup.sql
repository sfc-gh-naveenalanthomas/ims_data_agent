-- =========================
-- Define Databases
-- =========================
create or replace database IMS_DATA_AGENT_DB comment = 'used for demonstrating Snowflake for IMS Team';
create or replace schema IMS_DATA_AGENT_DB.DEMO;

-- =========================
-- Define stages
-- =========================
use schema IMS_DATA_AGENT_DB.DEMO;

create or replace stage lib_stg 
	directory = ( enable = true )
    comment = 'used for holding udfs and procs.';

create or replace stage data_stg directory = (enable = true)
    comment = 'used for holding data.';

create or replace stage scripts_stg 
    comment = 'used for holding scripts.';


-- --------------------------------------

use database IMS_DATA_AGENT_DB;
use schema demo;



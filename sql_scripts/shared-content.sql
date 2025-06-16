-- mark that our application package depends on an external database in
-- the provider account. By granting "reference_usage", the proprietary data
-- in the provider_data database can be shared through the app
grant reference_usage on database IMS_DATA_AGENT_DB
    to share in application package {{ package_name }};

-- now that we can reference our proprietary data, let's create some views
-- this "package schema" will be accessible inside of our setup script
create schema if not exists {{ package_name }}.SHARED_CONTENT;
use schema {{ package_name }}.SHARED_CONTENT;
grant usage on schema {{ package_name }}.SHARED_CONTENT
  to share in application package {{ package_name }};

use schema {{ package_name }}.SHARED_CONTENT;

-- Our actual data share. Only visible to APP_PRIMARY without further grants.
create or replace view SHARED_CONTENT.SAMPLE_DATA_VW as
    select *
    from IMS_DATA_AGENT_DB.DEMO.SAMPLE_DATA_VW;

grant select on view SHARED_CONTENT.SAMPLE_DATA_VW
  to share in application package {{ package_name }};

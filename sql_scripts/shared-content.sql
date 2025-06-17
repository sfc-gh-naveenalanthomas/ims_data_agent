grant reference_usage on database IMS_DATA_DB
    to share in application package {{ package_name }};

create schema if not exists {{ package_name }}.SHARED_CONTENT;
use schema {{ package_name }}.SHARED_CONTENT;

-- Our actual data share. Only visible to APP_PRIMARY without further grants.
create or replace secure view SHARED_CONTENT.SAMPLE_DATA_VW as
    select *
    from IMS_DATA_DB.PUBLIC.SAMPLE_DATA;

grant usage on schema {{ package_name }}.SHARED_CONTENT
  to share in application package {{ package_name }};

grant select on view SHARED_CONTENT.SAMPLE_DATA_VW
  to share in application package {{ package_name }};

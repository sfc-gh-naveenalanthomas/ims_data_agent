
# cd sfguide-marketing-data-foundation-starter
snow sql -f sql_scripts/setup.sql
# snow object stage copy data/worldcities.csv @MANUFACTURING_OT_IT_CASTING_USECASE_DB.public.data_stg/data
# snow object stage copy data/sf_data/ @MANUFACTURING_OT_IT_CASTING_USECASE_DB.public.data_stg/data/sf_data/ --parallel 10
# snow object stage copy data/ga_data/ @MANUFACTURING_OT_IT_CASTING_USECASE_DB.public.data_stg/data/ga_data/ --parallel 20
# snow object stage copy data/sample_data.gz @MANUFACTURING_OT_IT_CASTING_USECASE_DB.public.data_stg/data/
snow sql -f sql_scripts/build_views.sql
snow sql -f sql_scripts/shared-content.sql
# snow app deploy
# snow app run

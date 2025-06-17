# Portfolio Construction S&P500
import streamlit as st
import pandas as pd
from snowflake.snowpark.context import get_active_session
import snowflake.permissions as permissions




st.set_page_config(layout="wide")
st.title("📡 Ericsson IMS Native App Dashboard")

sp_session = get_active_session()

st.session_state.setdefault("customer_table_name", None)


# Initialize session variables
if "table_ref" not in st.session_state:
    st.session_state.table_ref = None

if "sync_complete" not in st.session_state:
    st.session_state.sync_complete = False

@st.cache_data(ttl=500)
def get_data(_sp_session, app_db, app_sch):
    get_data_stmt = "SELECT * FROM {0}.{1}.SAMPLE_DATA_VW".format(app_db, app_sch)
    df = _sp_session.sql(get_data_stmt).to_pandas()
    return df


with st.container():
   st.header("Data Analytics")
   app_db = sp_session.sql("SELECT CURRENT_DATABASE()").collect()[0][0]
   app_sch = 'CRM'
   fun_db = app_db
   fun_sch = 'PYTHON_FUNCTIONS'
   shr_db = app_db
   shr_sch = app_sch
   data_mode = st.radio(
      "Choose how you want to begin:",
      ["📁 Link Existing Data", "🛠️ See analytics on Ericsson Data"],
      horizontal=True, index=1
   )

   df = get_data(sp_session, app_db, app_sch)

   if data_mode.startswith("📁"):
      st.subheader(':blue[Sync your Data]')
      
      with st.expander("Connecting Existing Customer Table", expanded=True):
         # Get reference associations
         ref_associations = permissions.get_reference_associations("consumer_table")

         if ref_associations:
            st.session_state.table_ref = ref_associations[0]
         else:
            permissions.request_reference("consumer_table")
            st.warning("Please bind your portfolio table to continue.")

         if st.session_state.table_ref:
            st.success("Your table is linked to the app successfully!")

         

   else:
      st.subheader(':blue[Analytics on Ericsson Data]')
      tab1, tab2, tab3, tab4, tab5 = st.tabs([
         "📊 Call Overview",
         "🕒 Duration Analysis",
         "⚠️ Call Results",
         "🌐 Node & User Stats",
         "🔍 Call Search"
      ])
      # --- Tab 1: Overview ---
      with tab1:
         st.subheader("📊 Call Overview")
         st.metric("Total Calls", len(df))
         st.dataframe(df.head(10))

      # --- Tab 2: Duration ---
      with tab2:
         st.subheader("🕒 Call Duration Analysis")
         df["CALL_DURATION"] = (df["STOP_TIME"].astype(int) - df["START_TIME"].astype(int)) / 1000
         st.bar_chart(df["CALL_DURATION"])
         st.dataframe(df[["CALLID", "CALL_DURATION"]].sort_values("CALL_DURATION", ascending=False).head(10))

      # --- Tab 3: Result Metrics ---
      with tab3:
         st.subheader("⚠️ Call Result Metrics")
         result_counts = df["RESULT"].value_counts()
         st.bar_chart(result_counts)

      # --- Tab 4: Node/User Stats ---
      with tab4:
         st.subheader("🌐 Node & User Behavior")
         st.write("📍 Calls per Node")
         st.bar_chart(df["NODE_ID"].value_counts())

         st.write("📞 Top FROM_IDs")
         st.write(df["FROM_ID"].value_counts().head(10))

      # --- Tab 5: Call Search ---
      with tab5:
         st.subheader("🔍 Call Search Tool")
         callid_input = st.text_input("Enter CALLID to search:")
         if callid_input:
            match = df[df["CALLID"].str.contains(callid_input, case=False, na=False)]
            st.dataframe(match if not match.empty else pd.DataFrame([{"Result": "No match found"}]))
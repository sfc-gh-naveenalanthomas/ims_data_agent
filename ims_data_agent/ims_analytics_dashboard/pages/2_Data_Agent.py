# QuantPulse Agent

from typing import Dict, List, Optional

import _snowflake
import json
import streamlit as st
from snowflake.snowpark.context import get_active_session
import snowflake.permissions as permissions

sp_session = get_active_session()

DATABASE = sp_session.sql("SELECT CURRENT_DATABASE()").collect()[0][0]
SCHEMA = "CORE"
STAGE = "LIB_STG"
FILE = "ims_data_agent.yaml"


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
st.title("Ericsson Data Agent")
st.markdown(f"Semantic Model: `{FILE}`")
with st.expander("💡 Sample Questions you can ask:", expanded=True):
    st.markdown("""
        - What is the average call duration for all successful calls?  
        - How many calls did user `+36123456789` make in the last 7 days?  
        - Show all failed calls that lasted more than 30 seconds.  
        - Which node handled the most calls this week?  
        - At what time of day do most call failures occur?  
        """)

with st.expander("💬 More questions that the Agent can answer", expanded=False):

    st.markdown("### 📞 Call & Performance Exploration")
    st.markdown("""
    - What was the duration of the call with ID `TTCN3_985217_2121_1121@...`?  
    - Show all calls longer than 60 seconds that failed.  
    - What is the average call duration for successful calls?  
    - Which call had the longest setup time this week?  
    - What’s the success rate of calls made today?  
    - Show all calls that occurred between 8AM and 10AM.  
    """)

    st.markdown("### 👤 User-Level Analysis")
    st.markdown("""
    - How many calls did user `+36123456789` make last week?  
    - Which users had the highest average call duration?  
    - Who are the top 5 users by call volume?  
    - What is the call failure rate for each user?  
    - List users who made calls from more than one node.  
    """)

    st.markdown("### 🕒 Time-of-Day & Hourly Behavior")
    st.markdown("""
    - What time of day has the most call traffic?  
    - Compare call volume between morning and evening.  
    - Show call failures by hour of day.  
    - How many calls were made at night in the last 7 days?  
    """)

    st.markdown("### 🌐 Node & Network Diagnostics")
    st.markdown("""
    - Which node handled the most calls?  
    - How many unique users were served by each node?  
    - List failed calls grouped by `NODE_ID`.  
    - Which node has the highest call setup time average?  
    """)

    st.markdown("### 📊 Call Result Insights")
    st.markdown("""
    - How many calls were successful vs failed today?  
    - What percentage of calls failed last week?  
    - Show all calls where the `RESULT` is not `_0`.  
    - Which event IDs are associated with failed calls?  
    """)

    st.markdown("### 🔍 Call Search & Debugging")
    st.markdown("""
    - Find the call with ID `TTCN3_985288_2015_1005@...` and show all its details.  
    - Show all calls made by `+36123000121` today.  
    - Which calls had duration above 2 minutes and failed?  
    - Show the top 10 longest calls made in the last 24 hours.  
    """)



sp_session.sql("call {0}.PYTHON_FUNCTIONS.sp_init('{0}');".format(app_db)).collect()

if not st.session_state.imported_privilege_granted:
    held_privs = permissions.get_held_account_privileges(["IMPORTED PRIVILEGES ON SNOWFLAKE DB"])

    if held_privs:
        st.session_state.imported_privilege_granted = True
    else:
        permissions.request_account_privileges(["IMPORTED PRIVILEGES ON SNOWFLAKE DB"])
        st.warning("Please grant 'IMPORTED PRIVILEGES ON SNOWFLAKE DB' to use Cortex Agent.")
        

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
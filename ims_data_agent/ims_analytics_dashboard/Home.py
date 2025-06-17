# Home
import streamlit as st
st.set_page_config(layout="wide")


st.title("📞 Ericsson IMS Native App")

st.write(
   """
   This Snowflake Native App empowers **telecom engineers and analysts** with deep visibility into IMS call behavior, network patterns, and user activity using enriched signaling data — all inside an intuitive, interactive dashboard powered by Streamlit and Snowflake Cortex.
   """
)

st.write(
   """
   ## 👋 Welcome IMS Analyst

   Whether you're troubleshooting call failures, analyzing node behavior, or summarizing user trends, this dashboard provides everything you need to make informed, real-time telecom decisions.

   ### 🔍 What You Can Do Here:

   - **Analyze Call Behavior**
     - View total calls, duration trends, and time-of-day patterns
     - Search and investigate specific call records

   - **Understand Call Outcomes**
     - Track success vs failure rates by event ID or user
     - Spot anomalies in call setup time or unusual durations

   - **Summarize User & Network Activity**
     - Identify top users by volume and duration
     - Analyze node usage across the network

   - **Ask Natural Language Questions**
     - Use the embedded Cortex chat agent to ask:
       - "What was the longest failed call yesterday?"
       - "How many calls did user +36123456789 make last week?"

   ---
   ## 🧭 Recommended Workflow

   1. **Explore call trends and search for issues**
   2. **Review user and node-level summaries**
   3. **Use filters and duration metrics to isolate problems**
   4. **Ask the Cortex Agent questions about call patterns**

   ---

   This experience is designed to simplify telecom diagnostics and insights — with all logic and visualizations powered by Snowflake, Snowpark, and Streamlit.
   """
)

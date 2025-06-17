# Ericsson IMS Native App

## 📡 Introduction

This demo showcases how to use Ericsson IMS (IP Multimedia Subsystem) signaling data for telecom analytics, network behavior insights, call diagnostics, and AI-powered chatbot exploration — all powered by Snowflake Native App capabilities, Cortex Agent, and Streamlit.

The app provides detailed call analytics, node behavior trends, failure diagnostics, and user-level summaries. It also enables natural language exploration through an embedded chat interface powered by Snowflake Cortex.

### 🔁 Workflow Overview

The app follows a streamlined workflow for telecom engineers, analysts, and operations teams:

- **Data Loading**: IMS call signaling logs (e.g., SIP messages, timestamps, identities) are ingested into a Snowflake table.
- **Data Enhancement**: A curated view is built on top of raw data, enriching it with call duration, user identity extraction, status classification, and call metadata.
- **Interactive Dashboard**: A native Streamlit dashboard is embedded with multiple tabs to analyze call outcomes, durations, node behaviors, and specific call records.
- **User Summaries**: A user-level aggregation view summarizes activity, performance, and success/failure metrics for each unique caller.
- **Chat-Driven Insights**: Cortex Agent integration enables natural language queries over the enhanced view, allowing users to explore call performance and investigate issues conversationally.

---

## 📊 What Are the Steps in the App?

- **Call Overview**: View total call count, recent call samples, and table previews.
- **Call Duration Analysis**: Explore how long calls last, distribution of durations, and top/bottom duration calls.
- **Call Result Metrics**: Understand call outcome trends (success vs failure), result codes, and frequency.
- **Node and User Behavior**: Analyze usage by `NODE_ID`, top users by volume, and behavior distribution.
- **Call Search Tool**: Locate specific calls by ID or user identity for debugging or audit.
- **User Summary View**: Aggregated stats per caller including total calls, average duration, failure count, and node usage.

---

## 🧱 Views Used in the App

- **`IMS_ENHANCED_VIEW`**: Enriched call data with fields like:
  - `CALL_DURATION_SEC`, `CALL_STATUS`, `CALL_HOUR`, `TIME_OF_DAY`
  - Cleaned `CALLER_NUMBER`, `ASSERTED_NUMBER`, `CALL_TYPE`
- **`IMS_USER_SUMMARY_VIEW`**: Aggregated user statistics:
  - `TOTAL_CALLS`, `SUCCESSFUL_CALLS`, `FAILED_CALLS`
  - Duration stats, node diversity, and caller ID extraction

---

## 🤖 Cortex Agent Integration

The app includes a Cortex Agent that allows users to query the IMS data in plain English, such as:

### 📈 Call & Performance Queries
- What is the average call duration?
- Show all failed calls in the last hour.
- Which user had the longest call today?
- What time of day do most calls occur?
- Which node has the highest call volume?

### 🧑‍💼 User Behavior
- How many calls did +36123456789 make last week?
- Which users had failed calls over 30 seconds long?
- List top 5 users by average call duration.

### 🛠 Debugging & Investigations
- Show me all calls from user +36123480015 that failed.
- Why did call ID `TTCN3_985217_2121_1121@2001:...` fail?
- Which calls used multiple nodes or had setup times above 500 ms?

---

## 🧪 Future Enhancements

- SIP flow reconstruction using EVENT_ID sequences
- Integration of `USER_AGENT_OF_CALLER` once populated
- Real-time call stream simulation
- Anomaly detection using Snowpark ML or Cortex ML functions

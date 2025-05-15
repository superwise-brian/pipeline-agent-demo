import streamlit as st
import json
import requests
from superwise_api.superwise_client import SuperwiseClient
from dsl_spa.pipeline.pipeline import DashboardPipeline
import os

def ask_swe_application_via_api(sw: SuperwiseClient, app: str, user_input: str) -> str:
    endpoint_url = f"https://api.superwise.ai/v1/app-worker/{app}/v1/ask"
    
    token = str(sw.application.get_by_id(_id=app).api_token)
        
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "x-api-token": token
    }
    payload = {
        "chat_history": [],
        "input": user_input
    }
    
    resp = requests.post(endpoint_url, json=payload, headers=headers)
    app_response = resp.json()
    return app_response["output"]

if "dashboard_chat_history" not in st.session_state:
    st.session_state["dashboard_chat_history"] = []

if "dashboard" not in st.session_state:
    with open("pipelines/dashboard_pipeline_schema.json", 'r') as f:
        schema_text = f.read()
        schema = json.loads(schema_text)
    
    dashboard = DashboardPipeline({}, schema, st.session_state["connectors"],functions=st.session_state["pipeline_functions"])
    dashboard.initialize_data()
    dashboard.process_data()
    st.session_state["dashboard"] = dashboard
    st.session_state["options"] = dashboard.get_filters()["primary_project"]["values"]
else:
    dashboard = st.session_state["dashboard"]

dashboard_tab,summary,schema_tab = st.tabs(["Dashboard","Summary","Schema"])

with dashboard_tab:
    primary,secondary,chat = st.columns(3)

    with primary:
        primary_option = st.selectbox("Primary Project", st.session_state["options"],index=0)
        dashboard.update_filter(filter_name="primary_project",value=primary_option)
        dashboard.process_data()
        
        visualizations = dashboard.get_visualizations()
        line_graph = visualizations["Primary Project Progress"]["vega_lite"]
        pie_1 = visualizations["Primary Project Activities By Status"]["vega_lite"]
        pie_2 = visualizations["Primary Project Activity Status by Days"]["vega_lite"]
        st.vega_lite_chart(line_graph)
        primary_left,primary_right = st.columns(2)
        with primary_left:
            st.vega_lite_chart(pie_1)
        with primary_right:
            st.vega_lite_chart(pie_2)

    with secondary:
        secondary_option = st.selectbox("Secondary Project", st.session_state["options"],index=1)
        dashboard.update_filter(filter_name="secondary_project",value=secondary_option)
        dashboard.process_data()
        
        visualizations = dashboard.get_visualizations()
        line_graph = visualizations["Secondary Project Progress"]["vega_lite"]
        pie_1 = visualizations["Secondary Project Activities By Status"]["vega_lite"]
        pie_2 = visualizations["Secondary Project Activity Status by Days"]["vega_lite"]
        st.vega_lite_chart(line_graph)
        secondary_left,secondary_right = st.columns(2)
        with secondary_left:
            st.vega_lite_chart(pie_1)
        with secondary_right:
            st.vega_lite_chart(pie_2)
            
    with chat:
        question = st.chat_input("How may I assist you today?")
        if question:   
            summary_text = st.session_state["dashboard"].get_summary()
            
            swe_app_input = f"""Summary: {summary_text}
            Question: {question}
            """
            
            sw_response = ask_swe_application_via_api(st.session_state["superwise_client"], app=os.environ["SUMMARY_APPLICATION_ID"], user_input=swe_app_input)
            st.session_state["dashboard_chat_history"].extend([question,sw_response])
            
        roles = ["user","assistant"]
        role_id = 0
        for chat in st.session_state["dashboard_chat_history"]:
            message = st.chat_message(roles[role_id])
            message.write(chat)
            role_id = not role_id
            
with summary:
    st.write(st.session_state["dashboard"].get_summary())
    
with schema_tab:
    with open("pipelines/dashboard_pipeline_schema.json", 'r') as f:
        schema_text = f.read()
        schema = json.loads(schema_text)
    st.write(schema)
import streamlit as st
import json
import requests
from superwise_api.superwise_client import SuperwiseClient
from dsl_spa.pipeline.pipeline import StandardPipeline
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

st.set_page_config(layout="centered")
    
if "input_fields" not in st.session_state and "pipeline" in st.session_state:
    del st.session_state["pipeline"]

project_id = st.selectbox("Project ID", options=["P001","P002","P003","P004","P005"])
    
with open("pipelines/project_pipeline_schema.json", 'r') as f:
    schema_text = f.read()
    schema = json.loads(schema_text)

pipeline = StandardPipeline({"project_id": project_id}, schema, connectors=st.session_state["connectors"],functions=st.session_state["pipeline_functions"])
pipeline.initialize_data()
pipeline.process_data()
st.session_state["pipeline"] = pipeline
    
chat,graphs = st.tabs(["Chat","Visualizations"])

with chat:        
    question = st.chat_input("How may I assist you today?")
    if question:
        visualization_dicts = st.session_state["pipeline"].get_visualizations()
        
        descriptions = ""
        for title in visualization_dicts.keys():
            description = visualization_dicts[title]["description"]
            descriptions += f"\n{title} - {description}"
        swe_app_input = f"""Visualizations: {descriptions}
        Question: {question}
        """
        sw_response = ask_swe_application_via_api(st.session_state["superwise_client"], app=os.environ["VISUALIZATION_APPLICATION_ID"], user_input=swe_app_input)
        response = json.loads(sw_response)
        
        if "title" in response.keys():
            graph_name = response["title"]
            description = visualization_dicts[graph_name]["description"]
            graph = visualization_dicts[graph_name]["vega_lite"]
            st.write(f"{graph_name} - {description}")
            st.vega_lite_chart(graph)
        elif "error" in response.keys():
            st.write(response["error"])
        
with graphs:
    if "pipeline" in st.session_state:
        visualizations = st.session_state["pipeline"].get_visualizations()
        if len(visualizations) > 0:
            num_columns = 4
            if len(visualizations) <= 4:
                num_columns = len(visualizations)
            columns = st.columns(num_columns)
            graph_names = list(visualizations.keys())
            
            for i in range(num_columns):
                column = columns[i]
                with column:
                    if num_columns == 4:
                        for j in range(i,len(visualizations),step=4):
                            graph_name = graph_names[i+j]
                            description = visualizations[graph_name]["description"]
                            graph = visualizations[graph_name]["vega_lite"]
                            st.write(f"{graph_name} - {description}")
                            st.vega_lite_chart(graph)
                    else:
                        graph_name = graph_names[i]
                        description = visualizations[graph_name]["description"]
                        graph = visualizations[graph_name]["vega_lite"]
                        st.write(f"{graph_name} - {description}")
                        st.vega_lite_chart(graph)
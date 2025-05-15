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

st.set_page_config(layout="wide")

if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []
    
if "input_fields" not in st.session_state and "pipeline" in st.session_state:
    del st.session_state["pipeline"]
    
if st.button("Clear"):
    if "pipeline" in st.session_state:
        del st.session_state["pipeline"]
    if "chat_history" in st.session_state:
        st.session_state["chat_history"] = []
    if "scope" in st.session_state:
        del st.session_state["scope"]
    if "scope_description" in st.session_state:
        del st.session_state["scope_description"]    
    
chat,dsl,summary = st.tabs(["Chat","DSL","Summary"])

with chat:
    if "pipeline" not in st.session_state:
        st.write("Prompt for details for your project ID (P001-P005) and then chat with the pipeline. (Ex. \"What's the status of project P001?\")")
    else:
        scope = st.session_state["pipeline"].get_scope()
        scope_description = st.session_state["pipeline"].get_scope_description()
        st.write(f"Ask questions about {scope} - {scope_description}")
        
    try:
        question = st.chat_input("How may I assist you today?")
        if question:
            if "pipeline" not in st.session_state:
                sw_response = ask_swe_application_via_api(st.session_state["superwise_client"], 
                                                        app=os.environ["PIPELINE_SCHEMA_APPLICATION_ID"], 
                                                        user_input=question)
                fields = json.loads(sw_response)
                
                st.session_state["input_fields"] = fields
                
                with open("pipelines/project_pipeline_schema.json", 'r') as f:
                    schema_text = f.read()
                    schema = json.loads(schema_text)
                    
                pipeline = StandardPipeline(fields, json_schema=schema,connectors=st.session_state["connectors"],functions=st.session_state["pipeline_functions"])
                pipeline.initialize_data()
                pipeline.process_data()
                st.session_state["schema"] = schema
                st.session_state["pipeline"] = pipeline
                project_id = fields["project_id"]
                st.session_state["chat_history"].extend([question,f"Pipeline loaded for project {project_id}!"])
            else:            
                summary_text = st.session_state["pipeline"].get_summary()
                
                swe_app_input = f"""Summary: {summary_text}
                Question: {question}
                """
                
                sw_response = ask_swe_application_via_api(st.session_state["superwise_client"], app=os.environ["SUMMARY_APPLICATION_ID"], user_input=swe_app_input)
                st.session_state["chat_history"].extend([question,sw_response])
    except Exception as e:
        st.session_state["chat_history"].extend([question,"This was not a valid request. Make sure to follow the instructions above!"])
        
    roles = ["user","assistant"]
    role_id = 0
    for chat in st.session_state["chat_history"]:
        message = st.chat_message(roles[role_id])
        message.write(chat)
        role_id = not role_id
        
with dsl:
    if "pipeline" in st.session_state:
        superwise_response = st.session_state["input_fields"]
        st.write(superwise_response)
    else:
        st.write("Use the chat tab to ask an initial question so that Superwise may generate the pipeline fields for you")
        
with summary:
    if "pipeline" in st.session_state:
        summary_text = st.session_state["pipeline"].get_summary()
        st.write(summary_text)
    else:
        st.write("Use the chat tab to ask an initial question so that Superwise may generate the pipeline fields for you")

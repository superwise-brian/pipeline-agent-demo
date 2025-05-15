import streamlit as st
import json

st.set_page_config(layout="wide")

project,dashboard = st.tabs(["Project Pipeline","Dashboard Pipeline"])

with project:
    left,right = st.columns(2)
    with left:
        st.header("Python SDK")
        with open("pipelines/project_pipeline_schema.txt", 'r') as f:
            code = f.read()
        st.code(code)
    with right:
        st.header("JSON Schema")
        with open("pipelines/project_pipeline_schema.json", 'r') as f:
            schema = json.loads(f.read())
        st.write(schema)
    
with dashboard:
    
    left,right = st.columns(2)
    with left:
        st.header("Python SDK")
        with open("pipelines/dashboard_pipeline_schema.txt", 'r') as f:
            code = f.read()
        st.code(code)
    
    with right:
        st.header("JSON Schema")
        with open("pipelines/dashboard_pipeline_schema.json", 'r') as f:
            schema = json.loads(f.read())
        st.write(schema)
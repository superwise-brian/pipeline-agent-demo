import streamlit as st
import pandas as pd
from dsl_spa.pipeline.pipeline import StandardPipeline
import json

st.set_page_config(layout="wide")

if "pipeline" not in st.session_state:
    with open("pipelines/project_pipeline_schema.json", 'r') as f:
        schema_text = f.read()
        schema = json.loads(schema_text)
    pipeline = StandardPipeline({"project_id": "P001"}, json_schema=schema,connectors=st.session_state["connectors"],functions=st.session_state["pipeline_functions"])
    pipeline.initialize_data()
    pipeline.process_data()
    st.session_state["schema"] = schema
    st.session_state["pipeline"] = pipeline
    
schema,datasets,summary,graphs = st.tabs(["Schema","Datasets","Summary","Graphs"])
    
with schema:
    st.write(st.session_state["schema"])

with datasets:
    datasets = st.session_state["pipeline"].get_datasets()
    for dataset_name in datasets.keys():
        st.write(dataset_name)
        st.table(datasets[dataset_name])
        
with summary:
    st.write(st.session_state["pipeline"].get_summary())
    
with graphs:
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
                    
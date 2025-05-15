import streamlit as st
import pandas as pd
import os
from dsl_spa.pipeline.connector import LocalCSVConnector
from dsl_spa.pipeline.pipeline_functions import pipeline_functions_dict
from superwise_api.superwise_client import SuperwiseClient
from dotenv import load_dotenv

load_dotenv(".env")
st.set_page_config(layout="wide")

def change_column_names(df: pd.DataFrame, old_column_name: str, new_column_name: str) -> pd.DataFrame:
    columns = df.columns
    df.columns = list(map(lambda x: x if x != old_column_name else new_column_name, columns))
    return df

def remove_days_from_date_string(df: pd.DataFrame, date_column: str) -> pd.DataFrame:
    values = list(map(lambda x: x[:7],df[date_column].values))
    df[date_column] = values
    return df

def drop_column(df: pd.DataFrame, column_name: str) -> pd.DataFrame:
    return df.drop(columns=[column_name])

if "connectors" not in st.session_state:
    st.session_state["connectors"] = {
        "csvs": LocalCSVConnector("./data")
    }
    
pipeline_functions = pipeline_functions_dict
pipeline_functions["change_column_names"] = change_column_names
pipeline_functions["remove_days_from_date_string"] = remove_days_from_date_string
pipeline_functions["drop_column"] = drop_column
st.session_state["pipeline_functions"] = pipeline_functions

sw_client = SuperwiseClient(client_id=os.environ["SUPERWISE_CLIENT_ID"], client_secret=os.environ["SUPERWISE_CLIENT_SECRET"])
st.session_state["superwise_client"] = sw_client

homepage,data = st.columns(2)

with homepage:    
    st.title("Pipeline Agent")
    st.write("Welcome to the Pipeline Agent Demo. Pipeline Agent is an LLM-Agnostic tool. It can be connected to any LLM to build agents to complete your tasks. For this demo we used the superwise platform to build the necessary LLM applications.")
    
    st.header("Pipeline Output")
    st.write("Checkout the inner workings of a pipeline in Pipeline Output. You can explore Pipeline schema, the generated datasets, the Pipeline summary, and the visualizations of the data.")
    
    st.header("Chat")
    st.write("You can chat with the pipeline as well! Start a chat to populate the pipeline fields and then ask your questions specific to the scope of the pipeline.")
    
    st.header("Visualization Picker")
    st.write("If you just want a visualization, you can do that too. Send a request to the Pipeline for a specific visualization and if it can it will present it to you.")
    
    st.header("Dashboard with Chat")
    st.write("You can even generate a dashboard from a pipeline and then chat with that dashboard.")
    
with data:
    st.header("Datasets")
    st.write("Explore the three csvs this Pipeline is built on top of. Don't forget though that the Pipeline Agent becomes even more powerful when combined with the querying capabilities of SQL!")
    stadium_projects,project_updates,activities = st.tabs(["stadium_projects.csv","project_updates.csv","activities,csv"])
    with activities:
        st.table(data=pd.read_csv("data/activities.csv"))
    with project_updates:
        st.table(data=pd.read_csv("data/project_updates.csv"))
    with stadium_projects:
        st.table(data=pd.read_csv("data/stadium_projects.csv"))
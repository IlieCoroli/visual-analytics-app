import streamlit as st
import pandas as pd

def ensure_dataframe_loaded(controller):
    if controller.df is None or controller.df.empty:
        st.warning("Please import a dataset first (Navigation → Import Data).")
        st.stop()

def numeric_columns(df: pd.DataFrame):
    return [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]

def all_columns(df: pd.DataFrame):
    return list(df.columns)

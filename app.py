import streamlit as st
import pandas as pd

from app.controller.app_controller import AppController
from app.utils.validators import ensure_dataframe_loaded, numeric_columns, all_columns

st.set_page_config(page_title="CS6P05 Visual Analytics", layout="wide")

controller = AppController()

st.title("Interactive Data Visualisation & Analytics (Prototype)")

# Sidebar navigation (task-based)
page = st.sidebar.radio(
    "Navigation",
    ["Import Data", "Profile", "Clean & Transform", "Visualise", "Export", "Saved Snapshots"],
    index=0
)

# Shared state display
with st.sidebar.expander("Current dataset", expanded=False):
    meta = controller.get_active_metadata()
    if meta:
        st.write(meta)
    else:
        st.write("No dataset loaded.")

if page == "Import Data":
    st.header("Import Data")
    st.caption("Upload a CSV dataset to begin analysis.")
    uploaded = st.file_uploader("Upload CSV", type=["csv"])
    if uploaded is not None:
        try:
            controller.load_csv(uploaded, dataset_name=uploaded.name)
            st.success(f"Loaded dataset: {uploaded.name}")
            st.dataframe(controller.preview(), use_container_width=True)
        except Exception as e:
            st.error(f"Failed to load CSV: {e}")

    st.divider()
    st.subheader("Optional: Load sample dataset")
    if st.button("Load Iris (built-in sample)"):
        controller.load_sample_iris()
        st.success("Loaded Iris sample dataset.")
        st.dataframe(controller.preview(), use_container_width=True)

elif page == "Profile":
    st.header("Dataset Profile")
    ensure_dataframe_loaded(controller)
    st.dataframe(controller.preview(), use_container_width=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Rows", controller.row_count())
    with col2:
        st.metric("Columns", controller.column_count())
    with col3:
        st.metric("Missing values (total)", controller.total_missing())

    st.subheader("Column types")
    st.dataframe(controller.column_types_df(), use_container_width=True)

    st.subheader("Missing values by column")
    st.dataframe(controller.missing_by_column_df(), use_container_width=True)

    st.subheader("Descriptive statistics (numeric)")
    stats = controller.describe_numeric()
    if stats is None or stats.empty:
        st.info("No numeric columns detected.")
    else:
        st.dataframe(stats, use_container_width=True)

elif page == "Clean & Transform":
    st.header("Clean & Transform")
    ensure_dataframe_loaded(controller)

    tab_clean, tab_filter, tab_sort, tab_group = st.tabs(["Missing Values", "Filter", "Sort", "Group & Aggregate"])

    with tab_clean:
        st.subheader("Handle missing values")
        strategy = st.selectbox("Strategy", ["Drop rows with missing", "Fill missing (mean)", "Fill missing (median)", "Fill missing (0)", "Fill missing (custom)"])
        custom_val = None
        if strategy == "Fill missing (custom)":
            custom_val = st.text_input("Custom fill value (applies to all columns where possible)", value="0")

        if st.button("Apply missing value operation"):
            try:
                controller.apply_missing_strategy(strategy, custom_val)
                st.success("Applied missing value operation.")
                st.dataframe(controller.preview(), use_container_width=True)
            except Exception as e:
                st.error(f"Operation failed: {e}")

    with tab_filter:
        st.subheader("Filter rows")
        cols = all_columns(controller.df)
        col = st.selectbox("Column", cols)
        if col in numeric_columns(controller.df):
            op = st.selectbox("Operator", [">", ">=", "==", "<=", "<"])
            val = st.number_input("Value", value=0.0)
        else:
            op = st.selectbox("Operator", ["contains", "equals", "starts_with", "ends_with"])
            val = st.text_input("Value", value="")

        if st.button("Apply filter"):
            try:
                controller.apply_filter(col, op, val)
                st.success("Filter applied.")
                st.dataframe(controller.preview(), use_container_width=True)
            except Exception as e:
                st.error(f"Filter failed: {e}")

    with tab_sort:
        st.subheader("Sort")
        cols = all_columns(controller.df)
        sort_cols = st.multiselect("Sort columns", cols, default=cols[:1] if cols else [])
        asc = st.checkbox("Ascending", value=True)
        if st.button("Apply sort"):
            try:
                controller.apply_sort(sort_cols, asc)
                st.success("Sort applied.")
                st.dataframe(controller.preview(), use_container_width=True)
            except Exception as e:
                st.error(f"Sort failed: {e}")

    with tab_group:
        st.subheader("Group and aggregate")
        cols = all_columns(controller.df)
        num_cols = numeric_columns(controller.df)
        group_cols = st.multiselect("Group by columns", cols, default=cols[:1] if cols else [])
        agg_col = st.selectbox("Aggregate column (numeric)", num_cols) if num_cols else None
        agg_fn = st.selectbox("Aggregation", ["mean", "sum", "min", "max", "count"])
        if st.button("Apply groupby"):
            try:
                controller.apply_groupby(group_cols, agg_col, agg_fn)
                st.success("Groupby aggregation applied.")
                st.dataframe(controller.preview(), use_container_width=True)
            except Exception as e:
                st.error(f"Groupby failed: {e}")

elif page == "Visualise":
    st.header("Visualise")
    ensure_dataframe_loaded(controller)

    chart_type = st.selectbox("Chart type", ["Bar", "Line", "Scatter", "Histogram", "Correlation Heatmap"])
    df = controller.df

    fig = None
    if chart_type in ["Bar", "Line", "Scatter"]:
        x = st.selectbox("X axis", all_columns(df))
        y_candidates = numeric_columns(df) if chart_type != "Bar" else all_columns(df)
        y = st.selectbox("Y axis", y_candidates)
        color = st.selectbox("Color (optional)", ["(none)"] + all_columns(df))
        color = None if color == "(none)" else color
        fig = controller.make_xy_chart(chart_type, x, y, color=color)

    elif chart_type == "Histogram":
        col = st.selectbox("Column", numeric_columns(df))
        bins = st.slider("Bins", min_value=5, max_value=100, value=30)
        fig = controller.make_histogram(col, bins)

    elif chart_type == "Correlation Heatmap":
        cols = st.multiselect("Columns (numeric)", numeric_columns(df), default=numeric_columns(df)[:6])
        fig = controller.make_correlation(cols)

    if fig is not None:
        st.plotly_chart(fig, use_container_width=True)
        controller.set_last_figure(fig)

elif page == "Export":
    st.header("Export")
    ensure_dataframe_loaded(controller)

    st.subheader("Export cleaned/transformed dataset")
    export_name = st.text_input("CSV filename", value="cleaned_dataset.csv")
    if st.button("Download CSV"):
        csv_bytes = controller.export_csv_bytes()
        st.download_button("Click to download", data=csv_bytes, file_name=export_name, mime="text/csv")

    st.divider()
    st.subheader("Export last chart (PNG)")
    if controller.last_figure is None:
        st.info("No chart generated yet. Go to Visualise and create a chart first.")
    else:
        fig_name = st.text_input("Chart filename", value="chart.png")
        if st.button("Generate PNG"):
            try:
                png_bytes = controller.export_last_chart_png_bytes()
                st.download_button("Click to download chart", data=png_bytes, file_name=fig_name, mime="image/png")
            except Exception as e:
                st.error(f"Chart export failed: {e}")

elif page == "Saved Snapshots":
    st.header("Saved Snapshots")
    st.caption("Save/load snapshots to demonstrate persistence and reproducibility.")
    ensure_dataframe_loaded(controller)

    name = st.text_input("Snapshot name", value="snapshot_1")
    if st.button("Save snapshot"):
        try:
            snap_id = controller.save_snapshot(name)
            st.success(f"Saved snapshot '{name}' (ID: {snap_id})")
        except Exception as e:
            st.error(f"Save failed: {e}")

    st.divider()
    st.subheader("Available snapshots")
    snaps = controller.list_snapshots()
    if not snaps:
        st.info("No snapshots saved yet.")
    else:
        st.dataframe(pd.DataFrame(snaps), use_container_width=True)
        snap_ids = [s["dataset_id"] for s in snaps]
        chosen = st.selectbox("Select snapshot ID to load", snap_ids)
        if st.button("Load selected snapshot"):
            try:
                controller.load_snapshot(chosen)
                st.success(f"Loaded snapshot ID {chosen}")
                st.dataframe(controller.preview(), use_container_width=True)
            except Exception as e:
                st.error(f"Load failed: {e}")

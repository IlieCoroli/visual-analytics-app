from __future__ import annotations
from pathlib import Path
import pandas as pd
import streamlit as st

from app.model.dataset_manager import DatasetManager
from app.services.transformation_engine import TransformationEngine
from app.services.visualisation_engine import VisualisationEngine
from app.services.export_manager import ExportManager
from app.services.persistence_manager import PersistenceManager

class AppController:
    def __init__(self):
        # Streamlit session state init
        if "df" not in st.session_state:
            st.session_state.df = None
        if "last_fig" not in st.session_state:
            st.session_state.last_fig = None
        if "dataset_name" not in st.session_state:
            st.session_state.dataset_name = None

        self.dataset_manager = DatasetManager()
        self.transformer = TransformationEngine()
        self.visualiser = VisualisationEngine()
        self.exporter = ExportManager()
        self.persistence = PersistenceManager(db_path="app.db")

        # Re-sync manager with session df (so MVC stays consistent)
        if st.session_state.df is not None:
            self.dataset_manager.set_active(
                st.session_state.df,
                name=st.session_state.dataset_name or "dataset",
                source_type="Session",
                source_reference=""
            )

    @property
    def df(self) -> pd.DataFrame | None:
        return st.session_state.df

    @property
    def last_figure(self):
        return st.session_state.last_fig

    def set_last_figure(self, fig):
        st.session_state.last_fig = fig

    # -------- Import ----------
    def load_csv(self, uploaded_file, dataset_name: str = "dataset"):
        df = pd.read_csv(uploaded_file)
        st.session_state.df = df
        st.session_state.dataset_name = dataset_name
        self.dataset_manager.set_active(df, name=dataset_name, source_type="CSV", source_reference=dataset_name)

    def load_sample_iris(self):
        # simple sample dataset (no sklearn dependency)
        data = {
            "sepal_length":[5.1,4.9,4.7,4.6,5.0,5.4,4.6,5.0],
            "sepal_width":[3.5,3.0,3.2,3.1,3.6,3.9,3.4,3.4],
            "petal_length":[1.4,1.4,1.3,1.5,1.4,1.7,1.4,1.5],
            "petal_width":[0.2,0.2,0.2,0.2,0.2,0.4,0.3,0.2],
            "species":["setosa","setosa","setosa","setosa","setosa","setosa","setosa","setosa"]
        }
        df = pd.DataFrame(data)
        st.session_state.df = df
        st.session_state.dataset_name = "iris_sample.csv"
        self.dataset_manager.set_active(df, name="Iris Sample", source_type="Sample", source_reference="Built-in")

    # -------- Profile ----------
    @st.cache_data(show_spinner=False)
    def preview(_self):
        df = _self.df
        return df.head(30) if df is not None else pd.DataFrame()

    def row_count(self): return int(self.df.shape[0]) if self.df is not None else 0
    def column_count(self): return int(self.df.shape[1]) if self.df is not None else 0
    def total_missing(self): 
        return int(self.df.isna().sum().sum()) if self.df is not None else 0

    @st.cache_data(show_spinner=False)
    def column_types_df(_self):
        df = _self.df
        if df is None: return pd.DataFrame()
        return pd.DataFrame({"column": df.columns, "dtype": [str(df[c].dtype) for c in df.columns]})

    @st.cache_data(show_spinner=False)
    def missing_by_column_df(_self):
        df = _self.df
        if df is None: return pd.DataFrame()
        miss = df.isna().sum().sort_values(ascending=False)
        return pd.DataFrame({"column": miss.index, "missing_count": miss.values})

    @st.cache_data(show_spinner=False)
    def describe_numeric(_self):
        df = _self.df
        if df is None: return pd.DataFrame()
        num = df.select_dtypes(include="number")
        return num.describe().T if not num.empty else pd.DataFrame()

    def column_types(self):
        if self.df is None: return {}
        return {c: str(self.df[c].dtype) for c in self.df.columns}

    def get_active_metadata(self):
        return self.dataset_manager.get_meta()

    # -------- Transform ----------
    def _invalidate_caches(self):
        # Streamlit cache invalidation
        st.cache_data.clear()

    def apply_missing_strategy(self, strategy: str, custom_val: str | None):
        df2 = self.transformer.handle_missing(self.df, strategy, custom_val)
        st.session_state.df = df2
        self.dataset_manager.set_active(df2, name=st.session_state.dataset_name or "dataset", source_type="Transformed")
        self._invalidate_caches()

    def apply_filter(self, column: str, op: str, value):
        df2 = self.transformer.filter_rows(self.df, column, op, value)
        st.session_state.df = df2
        self.dataset_manager.set_active(df2, name=st.session_state.dataset_name or "dataset", source_type="Transformed")
        self._invalidate_caches()

    def apply_sort(self, columns: list[str], ascending: bool):
        df2 = self.transformer.sort(self.df, columns, ascending)
        st.session_state.df = df2
        self.dataset_manager.set_active(df2, name=st.session_state.dataset_name or "dataset", source_type="Transformed")
        self._invalidate_caches()

    def apply_groupby(self, group_cols: list[str], agg_col: str | None, agg_fn: str):
        df2 = self.transformer.group_aggregate(self.df, group_cols, agg_col, agg_fn)
        st.session_state.df = df2
        self.dataset_manager.set_active(df2, name=st.session_state.dataset_name or "dataset", source_type="Transformed")
        self._invalidate_caches()

    # -------- Visualise ----------
    def make_xy_chart(self, chart_type: str, x: str, y: str, color: str | None = None):
        return self.visualiser.xy_chart(chart_type, self.df, x, y, color)

    def make_histogram(self, column: str, bins: int):
        return self.visualiser.histogram(self.df, column, bins)

    def make_correlation(self, columns: list[str]):
        return self.visualiser.correlation_heatmap(self.df, columns)

    # -------- Export ----------
    def export_csv_bytes(self) -> bytes:
        return self.exporter.csv_bytes(self.df)

    def export_last_chart_png_bytes(self) -> bytes:
        if self.last_figure is None:
            raise ValueError("No chart available.")
        return self.exporter.fig_png_bytes(self.last_figure)

    # -------- Snapshots ----------
    def save_snapshot(self, name: str) -> int:
        df = self.df
        if df is None:
            raise ValueError("No dataset loaded.")
        safe = "".join([c for c in name if c.isalnum() or c in ("-","_")]).strip() or "snapshot"
        path = Path("data/snapshots") / f"{safe}.parquet"
        return self.persistence.save_snapshot(
            name=safe,
            df=df,
            snapshot_path=path,
            source_type="Snapshot",
            source_reference=st.session_state.dataset_name or ""
        )

    def list_snapshots(self):
        return self.persistence.list_snapshots()

    def load_snapshot(self, dataset_id: int):
        df = self.persistence.load_snapshot_df(int(dataset_id))
        st.session_state.df = df
        st.session_state.dataset_name = f"snapshot_{dataset_id}"
        self.dataset_manager.set_active(df, name=st.session_state.dataset_name, source_type="Snapshot")
        self._invalidate_caches()

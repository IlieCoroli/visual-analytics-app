import pandas as pd
import plotly.express as px

from app.services.export_manager import ExportManager
from app.services.transformation_engine import TransformationEngine
from app.services.visualisation_engine import VisualisationEngine
from app.services.persistence_manager import PersistenceManager


class AppController:
    def __init__(self):
        self.df: pd.DataFrame | None = None
        self.dataset_name: str | None = None
        self.last_figure = None

        self.transform = TransformationEngine()
        self.viz = VisualisationEngine()
        self.persist = PersistenceManager()

    # -------------------------
    # Dataset loading / metadata
    # -------------------------
    def load_csv(self, uploaded_file, dataset_name: str = "dataset.csv"):
        self.df = pd.read_csv(uploaded_file)
        self.dataset_name = dataset_name

    def load_sample_iris(self):
        iris = px.data.iris()
        self.df = iris.copy()
        self.dataset_name = "iris_sample"

    def get_active_metadata(self):
        if self.df is None:
            return None
        return {
            "name": self.dataset_name,
            "rows": int(self.df.shape[0]),
            "columns": int(self.df.shape[1]),
        }

    def preview(self, n: int = 20) -> pd.DataFrame:
        return self.df.head(n) if self.df is not None else pd.DataFrame()

    def row_count(self) -> int:
        return int(self.df.shape[0]) if self.df is not None else 0

    def column_count(self) -> int:
        return int(self.df.shape[1]) if self.df is not None else 0

    def total_missing(self) -> int:
        return int(self.df.isna().sum().sum()) if self.df is not None else 0

    def column_types_df(self) -> pd.DataFrame:
        if self.df is None:
            return pd.DataFrame()
        return pd.DataFrame({"column": self.df.columns, "dtype": self.df.dtypes.astype(str)})

    def missing_by_column_df(self) -> pd.DataFrame:
        if self.df is None:
            return pd.DataFrame()
        return pd.DataFrame({"column": self.df.columns, "missing": self.df.isna().sum().values})

    def describe_numeric(self) -> pd.DataFrame:
        if self.df is None:
            return pd.DataFrame()
        num = self.df.select_dtypes(include="number")
        return num.describe() if not num.empty else pd.DataFrame()

    # -------------------------
    # Cleaning / transformations
    # -------------------------
    def apply_missing_strategy(self, strategy: str, custom_val=None):
        if self.df is None:
            return
        self.df = self.transform.apply_missing_strategy(self.df, strategy, custom_val)

    def apply_filter(self, col: str, op: str, val):
        if self.df is None:
            return
        self.df = self.transform.apply_filter(self.df, col, op, val)

    def apply_sort(self, sort_cols: list[str], ascending: bool = True):
        if self.df is None:
            return
        self.df = self.transform.apply_sort(self.df, sort_cols, ascending)

    def apply_groupby(self, group_cols: list[str], agg_col: str | None, agg_fn: str):
        if self.df is None:
            return
        self.df = self.transform.apply_groupby(self.df, group_cols, agg_col, agg_fn)

    # -------------------------
    # Visualisations
    # -------------------------
    def make_xy_chart(self, chart_type: str, x: str, y: str, color: str | None = None):
        if self.df is None:
            return None
        return self.viz.make_xy_chart(self.df, chart_type, x, y, color)

    def make_histogram(self, col: str, bins: int = 30):
        if self.df is None:
            return None
        return self.viz.make_histogram(self.df, col, bins)

    def make_correlation(self, cols: list[str]):
        if self.df is None:
            return None
        return self.viz.make_correlation(self.df, cols)

    def set_last_figure(self, fig):
        self.last_figure = fig

    # -------------------------
    # Export
    # -------------------------
    def export_csv_bytes(self) -> bytes:
        if self.df is None:
            return b""
        return ExportManager.dataframe_to_csv_bytes(self.df)

    def export_last_chart_png_bytes(self) -> bytes:
    if self.last_figure is None:
        raise ValueError("No chart generated yet. Create a chart in Visualise first.")
    return self.export_manager.fig_png_bytes(self.last_figure, scale=2)


def export_last_chart_svg_bytes(self) -> bytes:
    if self.last_figure is None:
        raise ValueError("No chart generated yet. Create a chart in Visualise first.")
    return self.export_manager.fig_svg_bytes(self.last_figure)

    # -------------------------
    # Snapshots (optional)
    # -------------------------
    def save_snapshot(self, name: str):
        if self.df is None:
            raise ValueError("No dataset loaded.")
        return self.persist.save_snapshot(name, self.df)

    def list_snapshots(self):
        return self.persist.list_snapshots()

    def load_snapshot(self, dataset_id: str):
        self.df = self.persist.load_snapshot(dataset_id)
        self.dataset_name = f"snapshot_{dataset_id}"

import pandas as pd
import plotly.express as px


class VisualisationEngine:
    """
    Plotly visualisations used by the Streamlit app.
    Designed to be robust for typical CSV datasets.
    """

    def make_xy_chart(
        self,
        df: pd.DataFrame,
        chart_type: str,
        x: str,
        y: str,
        color: str | None = None,
    ):
        if df is None or df.empty:
            raise ValueError("Dataset is empty. Please import data first.")
        if x not in df.columns or y not in df.columns:
            raise ValueError("Selected columns do not exist in the dataset.")

        # Clean up color
        if not color or color == "(none)":
            color = None
        if color is not None and color not in df.columns:
            color = None

        # BAR: aggregate so it is meaningful and doesn't crash on large x
        if chart_type == "Bar":
            if pd.api.types.is_numeric_dtype(df[y]):
                # Sum y by x (and by color if present)
                group_cols = [x] + ([color] if color else [])
                agg = df.groupby(group_cols, dropna=False)[y].sum().reset_index()
                fig = px.bar(agg, x=x, y=y, color=color)
            else:
                # If y is not numeric, count occurrences
                group_cols = [x] + ([color] if color else [])
                agg = df.groupby(group_cols, dropna=False).size().reset_index(name="count")
                fig = px.bar(agg, x=x, y="count", color=color)

            fig.update_layout(title=f"Bar chart: {y} by {x}")
            return fig

        # LINE
        if chart_type == "Line":
            if not pd.api.types.is_numeric_dtype(df[y]):
                raise ValueError("Line chart requires a numeric Y column.")
            fig = px.line(df, x=x, y=y, color=color)
            fig.update_layout(title=f"Line chart: {y} over {x}")
            return fig

        # SCATTER
        if chart_type == "Scatter":
            if not pd.api.types.is_numeric_dtype(df[y]):
                raise ValueError("Scatter chart requires a numeric Y column.")
            fig = px.scatter(df, x=x, y=y, color=color)
            fig.update_layout(title=f"Scatter: {y} vs {x}")
            return fig

        raise ValueError(f"Unsupported chart type: {chart_type}")

    def make_histogram(self, df: pd.DataFrame, col: str, bins: int = 30):
        if df is None or df.empty:
            raise ValueError("Dataset is empty. Please import data first.")
        if col not in df.columns:
            raise ValueError("Selected column does not exist in the dataset.")
        if not pd.api.types.is_numeric_dtype(df[col]):
            raise ValueError("Histogram requires a numeric column.")

        fig = px.histogram(df, x=col, nbins=bins)
        fig.update_layout(title=f"Histogram: {col}")
        return fig

    def make_correlation(self, df: pd.DataFrame, cols: list[str]):
        if df is None or df.empty:
            raise ValueError("Dataset is empty. Please import data first.")

        cols = [c for c in cols if c in df.columns]
        if len(cols) < 2:
            raise ValueError("Select at least 2 numeric columns for correlation.")

        num = df[cols].select_dtypes(include="number")
        if num.shape[1] < 2:
            raise ValueError("Correlation heatmap needs at least 2 numeric columns.")

        corr = num.corr(numeric_only=True)
        fig = px.imshow(
            corr,
            text_auto=True,
            aspect="auto",
            title="Correlation Heatmap",
        )
        return fig

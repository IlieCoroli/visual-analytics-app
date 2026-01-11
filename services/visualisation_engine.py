from __future__ import annotations
import pandas as pd
import plotly.express as px

class VisualisationEngine:
    def xy_chart(self, chart_type: str, df: pd.DataFrame, x: str, y: str, color: str | None = None):
        if chart_type == "Bar":
            return px.bar(df, x=x, y=y, color=color)
        if chart_type == "Line":
            return px.line(df, x=x, y=y, color=color)
        if chart_type == "Scatter":
            return px.scatter(df, x=x, y=y, color=color)
        raise ValueError("Unsupported chart type.")

    def histogram(self, df: pd.DataFrame, column: str, bins: int = 30):
        return px.histogram(df, x=column, nbins=bins)

    def correlation_heatmap(self, df: pd.DataFrame, columns: list[str]):
        if not columns:
            raise ValueError("Select at least one numeric column.")
        corr = df[columns].corr(numeric_only=True)
        return px.imshow(corr, text_auto=True, aspect="auto")

import pandas as pd
import plotly.io as pio


class ExportManager:
    """Exports datasets and charts as bytes for Streamlit download buttons."""

    @staticmethod
    def dataframe_to_csv_bytes(df: pd.DataFrame) -> bytes:
        if df is None or df.empty:
            return b""
        return df.to_csv(index=False).encode("utf-8")

    @staticmethod
    def fig_png_bytes(fig, scale: int = 2) -> bytes:
        """
        PNG export that works with:
        plotly==5.24.1 + kaleido==0.2.1 (no system Chrome required)
        """
        if fig is None:
            raise ValueError("No figure provided.")
        return pio.to_image(fig, format="png", scale=scale)

    @staticmethod
    def fig_svg_bytes(fig) -> bytes:
        """SVG fallback (useful if PNG fails anywhere)."""
        if fig is None:
            raise ValueError("No figure provided.")
        return pio.to_image(fig, format="svg")

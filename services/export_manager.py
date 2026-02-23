import pandas as pd
import plotly.io as pio


class ExportManager:
    """
    Handles exporting datasets and figures into downloadable bytes.
    Uses plotly.io.to_image which works with kaleido==0.2.1 without system Chrome.
    """

    @staticmethod
    def dataframe_to_csv_bytes(df: pd.DataFrame) -> bytes:
        if df is None or df.empty:
            return b""
        return df.to_csv(index=False).encode("utf-8")

    @staticmethod
    def figure_to_png_bytes(fig, scale: int = 2) -> bytes:
        if fig is None:
            raise ValueError("No figure provided for export.")
        # PNG bytes using Kaleido
        return pio.to_image(fig, format="png", scale=scale)

    @staticmethod
    def figure_to_svg_bytes(fig) -> bytes:
        if fig is None:
            raise ValueError("No figure provided for export.")
        # SVG is a good fallback (often works even when PNG fails)
        return pio.to_image(fig, format="svg")

from __future__ import annotations
import io
import pandas as pd
import plotly.io as pio

class ExportManager:
    @staticmethod
    def figure_to_png_bytes(fig, scale: int = 2) -> bytes:
        # Works with kaleido==0.2.1 (no system Chrome required)
        return pio.to_image(fig, format="png", scale=scale)

class ExportManager:
    def csv_bytes(self, df: pd.DataFrame) -> bytes:
        return df.to_csv(index=False).encode("utf-8")

    def fig_png_bytes(self, fig) -> bytes:
        # Plotly uses kaleido for static image export
        buf = io.BytesIO()
        fig.write_image(buf, format="png")
        return buf.getvalue()

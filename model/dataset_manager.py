from __future__ import annotations
from dataclasses import dataclass
import pandas as pd

@dataclass
class DatasetMeta:
    name: str
    source_type: str
    source_reference: str
    rows: int
    cols: int

class DatasetManager:
    def __init__(self):
        self.active_df: pd.DataFrame | None = None
        self.meta: DatasetMeta | None = None

    def set_active(self, df: pd.DataFrame, name: str, source_type: str, source_reference: str = ""):
        self.active_df = df
        self.meta = DatasetMeta(
            name=name,
            source_type=source_type,
            source_reference=source_reference,
            rows=int(df.shape[0]),
            cols=int(df.shape[1])
        )

    def get_active(self) -> pd.DataFrame | None:
        return self.active_df

    def get_meta(self) -> dict | None:
        return self.meta.__dict__ if self.meta else None

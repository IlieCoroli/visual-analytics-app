from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import json
import pandas as pd
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.db.schema import Base, Dataset, ColumnProfile, TransformationLog

@dataclass
class SnapshotInfo:
    dataset_id: int
    name: str
    source_type: str
    created_at: str
    row_count: int
    column_count: int
    snapshot_path: str

class PersistenceManager:
    def __init__(self, db_path: str = "app.db"):
        self.engine = create_engine(f"sqlite:///{db_path}", future=True)
        Base.metadata.create_all(self.engine)

    def save_snapshot(self, name: str, df: pd.DataFrame, snapshot_path: Path, source_type: str = "CSV", source_reference: str = "") -> int:
        # Save dataframe as parquet for efficient reload
        snapshot_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_parquet(snapshot_path, index=False)

        with Session(self.engine) as session:
            ds = Dataset(
                name=name,
                source_type=source_type,
                source_reference=source_reference,
                row_count=int(df.shape[0]),
                column_count=int(df.shape[1]),
                snapshot_path=str(snapshot_path)
            )
            session.add(ds)
            session.flush()  # assign dataset_id

            # Column profiles
            for col in df.columns:
                series = df[col]
                prof = ColumnProfile(
                    dataset_id=ds.dataset_id,
                    column_name=str(col),
                    dtype=str(series.dtype),
                    missing_count=int(series.isna().sum()),
                    unique_count=int(series.nunique(dropna=True)),
                    summary_json=json.dumps(self._summary_for(series), ensure_ascii=False)
                )
                session.add(prof)

            session.commit()
            return ds.dataset_id

    def list_snapshots(self) -> list[SnapshotInfo]:
        with Session(self.engine) as session:
            rows = session.execute(select(Dataset).order_by(Dataset.created_at.desc())).scalars().all()
            return [
                SnapshotInfo(
                    dataset_id=r.dataset_id,
                    name=r.name,
                    source_type=r.source_type,
                    created_at=r.created_at.isoformat(timespec="seconds"),
                    row_count=r.row_count,
                    column_count=r.column_count,
                    snapshot_path=r.snapshot_path
                ).__dict__
                for r in rows
            ]

    def load_snapshot_df(self, dataset_id: int) -> pd.DataFrame:
        with Session(self.engine) as session:
            ds = session.get(Dataset, dataset_id)
            if ds is None:
                raise ValueError(f"Snapshot ID {dataset_id} not found.")
            path = Path(ds.snapshot_path)
            if not path.exists():
                raise FileNotFoundError(f"Snapshot file missing: {path}")
            return pd.read_parquet(path)

    def log_transformation(self, dataset_id: int | None, operation: str, params: dict):
        # dataset_id optional for first load; can be None
        with Session(self.engine) as session:
            log = TransformationLog(dataset_id=dataset_id or 0, operation=operation, parameters_json=json.dumps(params, ensure_ascii=False))
            session.add(log)
            session.commit()

    def _summary_for(self, series: pd.Series) -> dict:
        # Safe summary for both numeric and non-numeric
        if pd.api.types.is_numeric_dtype(series):
            s = series.dropna()
            if s.empty:
                return {}
            return {
                "min": float(s.min()),
                "max": float(s.max()),
                "mean": float(s.mean()),
                "std": float(s.std()) if len(s) > 1 else 0.0
            }
        return {
            "example_values": [str(v) for v in series.dropna().astype(str).head(5).tolist()]
        }

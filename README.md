# CS6P05 Phase 3 Prototype — Interactive Visual Analytics (Streamlit)

## Quick start
1) Create a virtual environment
- Windows:
  - `python -m venv .venv`
  - `.venv\Scripts\activate`
- macOS/Linux:
  - `python3 -m venv .venv`
  - `source .venv/bin/activate`

2) Install dependencies
- `pip install -r requirements.txt`

3) Run
- `streamlit run app.py`

## What this prototype includes (Phase 3)
- CSV import
- Dataset profiling (missing values, dtypes, basic stats)
- Cleaning: drop missing / fill missing (mean/median/0/custom)
- Transformations: filter (numeric/text), sort, groupby aggregate
- Interactive Plotly charts: bar/line/scatter/histogram/correlation heatmap
- Persistence: save/load snapshots (Parquet files + metadata in SQLite)
- Export: CSV + chart export (PNG) using Kaleido

## Notes
- Snapshots are stored under `data/snapshots/` and indexed in SQLite (`app.db`).
- For chart export to PNG, `kaleido` must be installed (already in requirements).

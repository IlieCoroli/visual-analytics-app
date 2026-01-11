from __future__ import annotations
import pandas as pd

class TransformationEngine:
    def handle_missing(self, df: pd.DataFrame, strategy: str, custom_val: str | None = None) -> pd.DataFrame:
        if strategy == "Drop rows with missing":
            return df.dropna()
        if strategy == "Fill missing (mean)":
            return df.fillna(df.mean(numeric_only=True))
        if strategy == "Fill missing (median)":
            return df.fillna(df.median(numeric_only=True))
        if strategy == "Fill missing (0)":
            return df.fillna(0)
        if strategy == "Fill missing (custom)":
            if custom_val is None:
                raise ValueError("Custom fill value is required.")
            # Try numeric where possible, otherwise keep as string
            try:
                v = float(custom_val)
                # Fill numeric columns with numeric, others with string
                df2 = df.copy()
                for c in df2.columns:
                    if pd.api.types.is_numeric_dtype(df2[c]):
                        df2[c] = df2[c].fillna(v)
                    else:
                        df2[c] = df2[c].fillna(custom_val)
                return df2
            except ValueError:
                return df.fillna(custom_val)
        raise ValueError(f"Unknown strategy: {strategy}")

    def filter_rows(self, df: pd.DataFrame, column: str, op: str, value) -> pd.DataFrame:
        if column not in df.columns:
            raise ValueError("Invalid column selected.")

        s = df[column]
        if pd.api.types.is_numeric_dtype(s):
            v = float(value)
            if op == ">": return df[s > v]
            if op == ">=": return df[s >= v]
            if op == "==": return df[s == v]
            if op == "<=": return df[s <= v]
            if op == "<": return df[s < v]
            raise ValueError("Invalid operator for numeric filter.")
        else:
            text = s.astype(str)
            v = str(value)
            if op == "contains": return df[text.str.contains(v, na=False, case=False)]
            if op == "equals": return df[text.str.lower() == v.lower()]
            if op == "starts_with": return df[text.str.lower().str.startswith(v.lower(), na=False)]
            if op == "ends_with": return df[text.str.lower().str.endswith(v.lower(), na=False)]
            raise ValueError("Invalid operator for text filter.")

    def sort(self, df: pd.DataFrame, columns: list[str], ascending: bool = True) -> pd.DataFrame:
        if not columns:
            return df
        for c in columns:
            if c not in df.columns:
                raise ValueError(f"Invalid sort column: {c}")
        return df.sort_values(by=columns, ascending=ascending)

    def group_aggregate(self, df: pd.DataFrame, group_cols: list[str], agg_col: str | None, agg_fn: str) -> pd.DataFrame:
        if not group_cols:
            raise ValueError("Select at least one group-by column.")
        for c in group_cols:
            if c not in df.columns:
                raise ValueError(f"Invalid group-by column: {c}")

        if agg_fn == "count":
            return df.groupby(group_cols, dropna=False).size().reset_index(name="count")

        if agg_col is None:
            raise ValueError("Select an aggregation column.")
        if agg_col not in df.columns:
            raise ValueError("Invalid aggregation column.")
        if not pd.api.types.is_numeric_dtype(df[agg_col]):
            raise ValueError("Aggregation column must be numeric (except count).")

        agg_map = {"mean":"mean","sum":"sum","min":"min","max":"max"}
        if agg_fn not in agg_map:
            raise ValueError("Invalid aggregation function.")
        return df.groupby(group_cols, dropna=False)[agg_col].agg(agg_map[agg_fn]).reset_index()

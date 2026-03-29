import pandas as pd
from dataclasses import dataclass, field
from typing import Any


@dataclass
class DataProfile:
    total_rows: int
    total_columns: int
    duplicate_rows: int
    columns: list[dict[str, Any]] = field(default_factory=list)


def profile_dataframe(df: pd.DataFrame) -> DataProfile:
    columns = []
    for col in df.columns:
        col_data = df[col]
        columns.append({
            "name": col,
            "dtype": str(col_data.dtype),
            "null_count": int(col_data.isnull().sum()),
            "null_pct": round(col_data.isnull().mean() * 100, 2),
            "unique_count": int(col_data.nunique()),
            "sample_values": col_data.dropna().head(3).tolist(),
        })
    return DataProfile(
        total_rows=len(df),
        total_columns=len(df.columns),
        duplicate_rows=int(df.duplicated().sum()),
        columns=columns,
    )
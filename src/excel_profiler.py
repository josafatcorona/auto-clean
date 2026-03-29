import pandas as pd
from dataclasses import dataclass, field


@dataclass
class SheetProfile:
    name: str
    total_rows: int
    total_cols: int
    detected_header_row: int
    sample_headers: list[str] = field(default_factory=list)
    looks_like_metadata: bool = False


@dataclass
class ExcelProfile:
    file_path: str
    total_sheets: int
    sheets: list[SheetProfile] = field(default_factory=list)


def detect_header_row(df_raw: pd.DataFrame, max_scan: int = 10) -> int:
    """Scan first N rows to find where the real header is."""
    scan = df_raw.head(max_scan)
    for i, row in scan.iterrows():
        non_empty = row.notna().sum()
        total = len(row)
        # Header row: mostly non-empty, mostly strings
        if non_empty / total >= 0.5:
            string_like = sum(isinstance(v, str) for v in row if pd.notna(v))
            if string_like / non_empty >= 0.5:
                return i
    return 0


def profile_excel(file_path: str) -> ExcelProfile:
    """Read Excel file structure without loading full data."""
    xl = pd.ExcelFile(file_path)
    sheets = []

    for sheet_name in xl.sheet_names:
        # Read raw without assuming header
        df_raw = pd.read_excel(
            file_path,
            sheet_name=sheet_name,
            header=None,
            nrows=200  # enough to profile, not full load
        )

        header_row = detect_header_row(df_raw)

        # Re-read with correct header
        df = pd.read_excel(
            file_path,
            sheet_name=sheet_name,
            header=header_row
        )

        # Heuristic: very few rows = likely metadata/config sheet
        looks_like_metadata = len(df) < 10 and len(df.columns) < 5

        sheets.append(SheetProfile(
            name=sheet_name,
            total_rows=len(df),
            total_cols=len(df.columns),
            detected_header_row=header_row,
            sample_headers=list(df.columns[:5]),
            looks_like_metadata=looks_like_metadata,
        ))

    return ExcelProfile(
        file_path=file_path,
        total_sheets=len(xl.sheet_names),
        sheets=sheets,
    )
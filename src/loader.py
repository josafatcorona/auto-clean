import pandas as pd
from pathlib import Path
from src.excel_profiler import profile_excel, ExcelProfile


SUPPORTED_EXTENSIONS = {".csv", ".xlsx", ".xls", ".txt"}


def detect_txt_delimiter(file_path: str) -> str:
    """Sniff the delimiter from the first line of a TXT file."""
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        first_line = f.readline()
    for delimiter in ["\t", "|", ";", ","]:
        if delimiter in first_line:
            return delimiter
    return ","  # fallback


def load_file(
    file_path: str,
    encoding: str = "utf-8",
    sheet_name: str | None = None,
    header_row: int = 0,
) -> pd.DataFrame:
    """
    Load any supported file into a DataFrame.
    For Excel, sheet_name and header_row come from excel_profiler.
    """
    ext = Path(file_path).suffix.lower()

    if ext == ".csv":
        return pd.read_csv(file_path, encoding=encoding)

    elif ext in {".xlsx", ".xls"}:
        return pd.read_excel(
            file_path,
            sheet_name=sheet_name,
            header=header_row,
        )

    elif ext == ".txt":
        delimiter = detect_txt_delimiter(file_path)
        return pd.read_csv(
            file_path,
            sep=delimiter,
            encoding=encoding,
            errors="replace",
        )

    else:
        raise ValueError(
            f"Unsupported file type: {ext}. "
            f"Supported: {', '.join(SUPPORTED_EXTENSIONS)}"
        )


def get_excel_profile(file_path: str) -> ExcelProfile:
    return profile_excel(file_path)
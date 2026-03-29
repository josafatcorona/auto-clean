import pandas as pd
import numpy as np
from scipy import stats
from dataclasses import dataclass
from src.config import CleaningConfig
from src.profiler import DataProfile


@dataclass
class CleaningResult:
    df_cleaned: pd.DataFrame
    rows_before: int
    rows_after: int
    duplicates_removed: int
    nulls_filled: int
    outliers_removed: int
    columns_renamed: dict


def clean(df: pd.DataFrame, config: CleaningConfig, profile: DataProfile) -> CleaningResult:
    result = df.copy()
    duplicates_removed = 0
    nulls_filled = 0
    outliers_removed = 0
    columns_renamed = {}

    # Fix column names
    if config.fix_column_names:
        new_cols = {c: c.lower().strip().replace(" ", "_") for c in result.columns}
        columns_renamed = {k: v for k, v in new_cols.items() if k != v}
        result.rename(columns=new_cols, inplace=True)

    # Remove duplicates
    if config.remove_duplicates:
        before = len(result)
        result.drop_duplicates(inplace=True)
        duplicates_removed = before - len(result)

    # Fill nulls
    if config.fill_nulls:
        for col in result.select_dtypes(include="number").columns:
            null_count = result[col].isnull().sum()
            if null_count > 0:
                if config.fill_strategy == "mean":
                    result[col] = result[col].fillna(result[col].mean())
                elif config.fill_strategy == "median":
                    result[col] = result[col].fillna(result[col].median())
                elif config.fill_strategy == "mode":
                    result[col] = result[col].fillna(result[col].mode()[0])
                elif config.fill_strategy == "drop":
                    result =result.dropna(subset=[col])
                nulls_filled += null_count

    # Remove outliers
    if config.remove_outliers:
        numeric_cols = result.select_dtypes(include="number").columns
        before = len(result)
        if config.outlier_method == "iqr":
            for col in numeric_cols:
                Q1 = result[col].quantile(0.25)
                Q3 = result[col].quantile(0.75)
                IQR = Q3 - Q1
                result = result[
                    (result[col] >= Q1 - 1.5 * IQR) &
                    (result[col] <= Q3 + 1.5 * IQR)
                ]
        elif config.outlier_method == "zscore":
            z_scores = np.abs(stats.zscore(result[numeric_cols]))
            result = result[(z_scores < 3).all(axis=1)]
        outliers_removed = before - len(result)

    return CleaningResult(
        df_cleaned=result,
        rows_before=profile.total_rows,
        rows_after=len(result),
        duplicates_removed=duplicates_removed,
        nulls_filled=int(nulls_filled),
        outliers_removed=outliers_removed,
        columns_renamed=columns_renamed,
    )
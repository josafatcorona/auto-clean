import yaml
from dataclasses import dataclass


@dataclass
class CleaningConfig:
    file_path: str
    encoding: str
    separator: str
    remove_duplicates: bool
    fill_nulls: bool
    fill_strategy: str
    remove_outliers: bool
    outlier_method: str
    fix_column_names: bool
    output_folder: str
    save_cleaned_csv: bool
    generate_report: bool


def load_config(path: str = "config.yaml") -> CleaningConfig:
    with open(path, "r") as f:
        raw = yaml.safe_load(f)
    return CleaningConfig(
        file_path=raw["input"]["file_path"],
        encoding=raw["input"]["encoding"],
        separator=raw["input"]["separator"],
        remove_duplicates=raw["cleaning"]["remove_duplicates"],
        fill_nulls=raw["cleaning"]["fill_nulls"],
        fill_strategy=raw["cleaning"]["fill_strategy"],
        remove_outliers=raw["cleaning"]["remove_outliers"],
        outlier_method=raw["cleaning"]["outlier_method"],
        fix_column_names=raw["cleaning"]["fix_column_names"],
        output_folder=raw["output"]["folder"],
        save_cleaned_csv=raw["output"]["save_cleaned_csv"],
        generate_report=raw["output"]["generate_report"],
    )
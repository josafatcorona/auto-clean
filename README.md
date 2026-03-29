# 🧹 AutoClean

> Stop cleaning data by hand. AutoClean does it in seconds

**AutoClean** AutoClean is a command-line tool that cleans messy CSV files automatically and generates a visual HTML report — no manual work required.
It prepares datasets quickly and reliably, generating a **HTML report** with statistics and a cleaned CSV file ready for use.

---
## 💡 Why I built this

Every data project starts the same way: loading a CSV and spending
the first hour fixing column names, hunting for nulls, and removing
duplicates. AutoClean automates that first hour so you can focus on
the analysis that actually matters.

## 🚀 Features

- Automated data cleaning:
  - Remove duplicate rows
  - Fill missing values (strategies: `mean`, `median`, `mode`, `drop`)
  - Detect and remove outliers (`iqr` or `zscore`)
  - Standardize column names  (`Column Sample` → `column_sample`)
- Generate a **HTML report** with:
  - General summary: original rows, cleaned rows, duplicates removed, nulls filled, outliers removed
  - Column analysis:
    - Name
    - Data type (`dtype`)
    - Null count and percentage
    - Unique values count
    - Sample values
- Export results:
  - Cleaned CSV
  - HTML report

---

## 📂 Project Structure
```text
├── README.md
├── config.yaml
├── data
│   └── sample.csv
├── docs
├── main.py
├── output
│   ├── cleaned.csv
│   └── report.html
├── src
│   ├── cleaner.py
│   ├── config.py
│   ├── profiler.py
│   └── reporter.py
├── templates
│   └── report.html
└── test
...

---

## ⚙️ Configuration (`config.yaml`)

```yaml
input:
  file_path: "data/sample.csv"
  encoding: "utf-8"
  separator: ","

cleaning:
  remove_duplicates: true
  fill_nulls: true
  fill_strategy: "mean"        # options: mean, median, mode, drop
  remove_outliers: true
  outlier_method: "iqr"        # options: iqr, zscore
  fix_column_names: true

output:
  folder: "output"
  save_cleaned_csv: true
  generate_report: true
▶️ Usage
Run it from your terminal:

bash
python main.py
Example output:

Code
🧹 auto-clean starting...

✔ Loaded: 210 rows × 5 columns
    Cleaning Summary
    ┌────────────────────┬────────┐
    │ Action             │ Result │
    ├────────────────────┼────────┤
    │ Duplicates removed │ 10     │
    │ Nulls filled       │ 30     │
    │ Outliers removed   │ 4      │
    │ Rows before        │ 210    │
    │ Rows after         │ 196    │
    └────────────────────┴────────┘

✔ Saved CSV: output/cleaned.csv
✔ Report: output/report.html

✅ Done.
📊 Report Example
The HTML report includes:

Cleaning summary

Column statistics:

Name

Data type

Null count and percentage

Unique values count

Sample values

## 🛠️ Installation

Requires Python 3.10+ and [uv](https://github.com/astral-sh/uv).
```bash
git clone https://github.com/YOUR_USERNAME/auto-clean.git
cd auto-clean
source setup.sh
```

That's it. The script creates the virtual environment and installs
all dependencies automatically.

To activate the environment in future sessions:
```bash
source .venv/bin/activate
```
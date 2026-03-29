import typer
import pandas as pd
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt
from rich import box
import os

from src.config import load_config
from src.profiler import profile_dataframe
from src.cleaner import clean
from src.reporter import generate_report
from src.loader import load_file, get_excel_profile, detect_txt_delimiter

app = typer.Typer()
console = Console()


def print_excel_structure(excel_profile):
    """Print a rich table showing Excel file structure."""
    console.print(f"\n[bold blue]📊 Excel Structure Report[/bold blue]")
    console.print(f"   File: [dim]{excel_profile.file_path}[/dim]")
    console.print(f"   Sheets found: [bold]{excel_profile.total_sheets}[/bold]\n")

    table = Table(box=box.ROUNDED, show_header=True, header_style="bold blue")
    table.add_column("Sheet", style="bold")
    table.add_column("Rows", justify="right")
    table.add_column("Columns", justify="right")
    table.add_column("Header at row", justify="right")
    table.add_column("Sample columns")
    table.add_column("Note", style="dim")

    for sheet in excel_profile.sheets:
        note = "⚠ looks like metadata" if sheet.looks_like_metadata else ""
        table.add_row(
            sheet.name,
            str(sheet.total_rows),
            str(sheet.total_cols),
            str(sheet.detected_header_row),
            ", ".join(str(h) for h in sheet.sample_headers),
            note,
        )

    console.print(table)


def process_sheet(sheet_name, header_row, file_path, config):
    """Run the full clean pipeline on a single sheet."""
    console.print(f"\n[bold]→ Processing sheet:[/bold] [cyan]{sheet_name}[/cyan]")

    df = load_file(
    file_path,
    encoding=config.encoding,
    sheet_name=sheet_name,
    header_row=header_row,
    )
    console.print(f"[green]✓ Loaded:[/green] {len(df)} rows × {len(df.columns)} columns")

    profile = profile_dataframe(df)
    result = clean(df, config, profile)

    # Summary table
    table = Table(
        title=f"Cleaning Summary — {sheet_name}",
        show_header=True,
        header_style="bold blue",
        box=box.SIMPLE
    )
    table.add_column("Action", style="dim")
    table.add_column("Result", justify="right")
    table.add_row("Duplicates removed", str(result.duplicates_removed))
    table.add_row("Nulls filled",       str(result.nulls_filled))
    table.add_row("Outliers removed",   str(result.outliers_removed))
    table.add_row("Rows before",        str(result.rows_before))
    table.add_row("Rows after",         str(result.rows_after))
    console.print(table)

    # Save outputs
    os.makedirs(config.output_folder, exist_ok=True)
    safe_name = sheet_name.lower().replace(" ", "_")

    if config.save_cleaned_csv:
        out_csv = os.path.join(config.output_folder, f"cleaned_{safe_name}.csv")
        result.df_cleaned.to_csv(out_csv, index=False)
        console.print(f"[green]✓ Saved CSV:[/green] {out_csv}")

    if config.generate_report:
        report_path = os.path.join(config.output_folder, f"report_{safe_name}.html")
        generate_report(profile, result, config.output_folder, report_name=f"report_{safe_name}.html")
        console.print(f"[green]✓ Report:[/green]   {report_path}")


@app.command()
def run(
    file: str = typer.Option(None, help="Path to input file (overrides config.yaml)"),
    sheet: str = typer.Option(None, help="Sheet name to process (Excel only)"),
    all_sheets: bool = typer.Option(False, "--all-sheets", help="Process all sheets"),
    config_path: str = typer.Option("config.yaml", help="Path to config.yaml"),
):
    """auto-clean: Automated data cleaning for CSV, Excel and TXT files."""

    console.print("\n[bold blue]🧹 auto-clean starting...[/bold blue]\n")

    config = load_config(config_path)
    file_path = file or config.file_path
    ext = Path(file_path).suffix.lower()

    # ── Excel flow ──────────────────────────────────────────────
    if ext in {".xlsx", ".xls"}:
        excel_profile = get_excel_profile(file_path)
        print_excel_structure(excel_profile)

        # Resolve which sheets to process
        if all_sheets:
            sheets_to_process = excel_profile.sheets
        elif sheet:
            match = next((s for s in excel_profile.sheets if s.name == sheet), None)
            if not match:
                console.print(f"[red]❌ Sheet '{sheet}' not found.[/red]")
                raise typer.Exit(1)
            sheets_to_process = [match]
        else:
            # Interactive selection
            choices = [s.name for s in excel_profile.sheets] + ["All sheets"]
            console.print("\n[bold]Which sheet do you want to clean?[/bold]")
            for i, name in enumerate(choices, 1):
                console.print(f"  [cyan]{i}[/cyan]. {name}")

            choice = Prompt.ask(
                "\nEnter number",
                choices=[str(i) for i in range(1, len(choices) + 1)],
            )
            idx = int(choice) - 1

            if idx == len(excel_profile.sheets):
                sheets_to_process = excel_profile.sheets
            else:
                sheets_to_process = [excel_profile.sheets[idx]]

        for s in sheets_to_process:
            process_sheet(s.name, s.detected_header_row, file_path, config)

    # ── CSV / TXT flow ───────────────────────────────────────────
    else:
        if ext == ".txt":
            delim = detect_txt_delimiter(file_path)
            console.print(f"[dim]TXT file detected — delimiter: '{delim}'[/dim]")

        df = load_file(file_path, encoding=config.encoding)
        console.print(f"[green]✓ Loaded:[/green] {len(df)} rows × {len(df.columns)} columns")

        profile = profile_dataframe(df)
        result = clean(df, config, profile)

        table = Table(title="Cleaning Summary", show_header=True, header_style="bold blue")
        table.add_column("Action", style="dim")
        table.add_column("Result", justify="right")
        table.add_row("Duplicates removed", str(result.duplicates_removed))
        table.add_row("Nulls filled",       str(result.nulls_filled))
        table.add_row("Outliers removed",   str(result.outliers_removed))
        table.add_row("Rows before",        str(result.rows_before))
        table.add_row("Rows after",         str(result.rows_after))
        console.print(table)

        os.makedirs(config.output_folder, exist_ok=True)

        if config.save_cleaned_csv:
            out_path = os.path.join(config.output_folder, "cleaned.csv")
            result.df_cleaned.to_csv(out_path, index=False)
            console.print(f"[green]✓ Saved CSV:[/green] {out_path}")

        if config.generate_report:
            generate_report(profile, result, config.output_folder)
            console.print(f"[green]✓ Report:[/green]   {config.output_folder}/report.html")

    console.print("\n[bold green]✅ Done.[/bold green]\n")


if __name__ == "__main__":
    app()
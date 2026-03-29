import typer
import pandas as pd
from rich.console import Console
from rich.table import Table
import os

from src.config import load_config
from src.profiler import profile_dataframe
from src.cleaner import clean
from src.reporter import generate_report

app = typer.Typer()
console = Console()


@app.command()
def run(
    config_path: str = typer.Option("config.yaml", help="Path to config.yaml")
):
    """auto-clean: Automated data cleaning and profiling tool."""

    console.print("\n[bold blue]🧹 auto-clean starting...[/bold blue]\n")

    # Load config
    config = load_config(config_path)

    # Load data
    df = pd.read_csv(config.file_path, encoding=config.encoding, sep=config.separator)
    console.print(f"[green]✓ Loaded:[/green] {len(df)} rows × {len(df.columns)} columns")

    # Profile
    profile = profile_dataframe(df)

    # Clean
    result = clean(df, config, profile)

    # Summary table
    table = Table(title="Cleaning Summary", show_header=True, header_style="bold blue")
    table.add_column("Action", style="dim")
    table.add_column("Result", justify="right")
    table.add_row("Duplicates removed", str(result.duplicates_removed))
    table.add_row("Nulls filled",       str(result.nulls_filled))
    table.add_row("Outliers removed",   str(result.outliers_removed))
    table.add_row("Rows before",        str(result.rows_before))
    table.add_row("Rows after",         str(result.rows_after))
    console.print(table)

    # Save cleaned CSV
    if config.save_cleaned_csv:
        os.makedirs(config.output_folder, exist_ok=True)
        out_path = os.path.join(config.output_folder, "cleaned.csv")
        result.df_cleaned.to_csv(out_path, index=False)
        console.print(f"[green]✓ Saved CSV:[/green] {out_path}")

    # Generate report
    if config.generate_report:
        report_path = generate_report(profile, result, config.output_folder)
        console.print(f"[green]✓ Report:[/green]   {report_path}")

    console.print("\n[bold green]✅ Done.[/bold green]\n")


if __name__ == "__main__":
    app()
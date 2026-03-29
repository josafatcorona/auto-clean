import boto3
import tempfile
import os
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich import box

console = Console()


def get_s3_client():
    """
    Returns S3 client using whatever credentials are available:
    IAM role (EC2), environment variables, or ~/.aws/credentials.
    No hardcoded keys — ever.
    """
    return boto3.client("s3")


def list_bucket_files(
    bucket: str,
    prefix: str = "",
    extensions: tuple = (".csv", ".xlsx", ".xls", ".txt"),
) -> list[dict]:
    """
    List files in a bucket filtered by extension.
    Returns list of dicts with key, size, last_modified.
    """
    s3 = get_s3_client()
    paginator = s3.get_paginator("list_objects_v2")
    files = []

    for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
        for obj in page.get("Contents", []):
            key = obj["Key"]
            if any(key.lower().endswith(ext) for ext in extensions):
                files.append({
                    "key": key,
                    "size_kb": round(obj["Size"] / 1024, 1),
                    "last_modified": obj["LastModified"].strftime("%Y-%m-%d %H:%M"),
                })

    return files


def print_bucket_files(files: list[dict], bucket: str):
    """Print a rich table of available files."""
    table = Table(
        title=f"Files in s3://{bucket}",
        box=box.ROUNDED,
        show_header=True,
        header_style="bold blue"
    )
    table.add_column("#", justify="right", style="dim", width=4)
    table.add_column("File", style="bold")
    table.add_column("Size (KB)", justify="right")
    table.add_column("Last modified")

    for i, f in enumerate(files, 1):
        table.add_row(str(i), f["key"], str(f["size_kb"]), f["last_modified"])

    console.print(table)


def download_from_s3(bucket: str, key: str) -> str:
    """
    Download file from S3 to a local temp directory.
    Returns the local file path.
    """
    s3 = get_s3_client()
    filename = Path(key).name
    tmp_dir = tempfile.mkdtemp(prefix="autoclean_")
    local_path = os.path.join(tmp_dir, filename)

    console.print(f"[dim]→ Downloading s3://{bucket}/{key}...[/dim]")
    s3.download_file(bucket, key, local_path)
    console.print(f"[green]✓ Downloaded:[/green] {local_path}")

    return local_path


def upload_to_s3(local_path: str, bucket: str, s3_key: str):
    """Upload a local file back to S3."""
    s3 = get_s3_client()
    s3.upload_file(local_path, bucket, s3_key)
    console.print(f"[green]✓ Uploaded:[/green] s3://{bucket}/{s3_key}")
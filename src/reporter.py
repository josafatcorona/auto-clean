from jinja2 import Environment, FileSystemLoader
from datetime import datetime
import os


def generate_report(profile, result, output_folder: str) -> str:
    env = Environment(loader=FileSystemLoader("templates"))
    template = env.get_template("report.html")
    html = template.render(
        profile=profile,
        result=result,
        generated_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )
    os.makedirs(output_folder, exist_ok=True)
    path = os.path.join(output_folder, "report.html")
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    return path
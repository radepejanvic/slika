import os
from datetime import datetime


def write_report(errors, path):
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    content = _render_txt(errors)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return path


def _timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _render_txt(errors):
    sep = "=" * 70
    lines = [
        sep,
        "SLIKA BATCH PROCESSING REPORT",
        sep,
        f"Generated: {_timestamp()}",
        f"Failed items: {len(errors)}",
        "",
    ]
    for i, err in enumerate(errors, 1):
        lines.append(f"[{i}] {err.filename}")
        lines.append("-" * 70)
        lines.append(f"Step:  {err.step_name}")
        lines.append(f"Error: {type(err.original_exception).__name__}: {err.original_exception}")
        lines.append("")
        lines.append("Traceback:")
        lines.append(err.traceback_str.rstrip())
        lines.append("")
        lines.append(sep)
        lines.append("")
    return "\n".join(lines)
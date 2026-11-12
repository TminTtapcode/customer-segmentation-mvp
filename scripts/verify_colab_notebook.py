"""Đọc notebook bằng nbformat và chạy các ô local theo thứ tự trong process mới.

Không mô phỏng Colab/Drive, không ghi dataset hoặc lưu output vào notebook.
nbformat chỉ dùng cho công cụ kiểm tra này, không phải dependency của bài Colab.
"""
from __future__ import annotations

import argparse
from contextlib import redirect_stderr, redirect_stdout
from datetime import datetime, timezone
import hashlib
import io
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from tempfile import TemporaryDirectory

sys.dont_write_bytecode = True
PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT / ".tmp/notebook-validation"))
import nbformat

NOTEBOOK = PROJECT / "notebooks/01_data_exploration.ipynb"


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run_cells(case):
    book = nbformat.read(NOTEBOOK, as_version=4)
    nbformat.validate(book)
    namespace = {"__name__": "__main__"}
    records = []
    failure = None
    for cell in book.cells:
        if cell.cell_type != "code":
            continue
        capture = io.StringIO()
        try:
            with redirect_stdout(capture), redirect_stderr(capture):
                exec(compile(cell.source, "<notebook cell: " + cell.id + ">", "exec"), namespace)
        except Exception as exc:
            failure = {"cell": cell.id, "type": type(exc).__name__, "message": str(exc)}
        records.append({"cell": cell.id, "output": capture.getvalue(), "failed": failure is not None})
        if failure:
            break
    result = {
        "case": case, "running_in_colab": namespace.get("IN_COLAB"),
        "cells_attempted": len(records), "cells": records, "failure": failure,
        "summary": namespace.get("summary"), "file_checks": namespace.get("checks"),
        "actual_sha256": namespace.get("actual_sha256"),
    }
    # JSON ASCII giúp terminal Windows không lỗi mã hóa; không có user IDs.
    print(json.dumps(result))
    return 0 if failure is None else 2


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, help="Project cũ; chỉ đọc buyer_features.parquet")
    parser.add_argument("--case", choices=["present", "missing"], help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.case:
        return run_cells(args.case)

    audit = json.loads((PROJECT / "results/p0_t1/audit.json").read_text(encoding="utf-8"))
    source = (args.source or Path(audit["source_root"])).resolve()
    data_root = source / "data"
    buyer_file = data_root / "features/buyer_features.parquet"
    if not buyer_file.is_file():
        parser.error("Thiếu buyer_features.parquet ở project nguồn; không tạo dữ liệu thay thế")
    output = PROJECT / "results/p0_t3"
    output.mkdir(parents=True, exist_ok=True)
    before = {"sha256": sha256(buyer_file), "bytes": buyer_file.stat().st_size,
              "mtime_ns": buyer_file.stat().st_mtime_ns}
    notebook_hash = sha256(NOTEBOOK)
    book = nbformat.read(NOTEBOOK, as_version=4)
    nbformat.validate(book)
    for cell in book.cells:
        if cell.cell_type == "code":
            compile(cell.source, "<syntax check>", "exec")

    def scenario(case, root):
        command = [sys.executable, "-B", str(Path(__file__).resolve()), "--case", case]
        env = dict(os.environ, REES46_DATA_ROOT=str(root), PYTHONDONTWRITEBYTECODE="1")
        result = subprocess.run(command, cwd=PROJECT, env=env, text=True, encoding="utf-8",
                                capture_output=True, timeout=120)
        if not result.stdout.strip():
            raise RuntimeError(result.stderr or "Không nhận được output từ process kiểm tra")
        return {"command": command, "exit_code": result.returncode,
                "stderr": result.stderr, "result": json.loads(result.stdout)}

    present = scenario("present", data_root)
    (PROJECT / ".tmp").mkdir(exist_ok=True)
    with TemporaryDirectory(prefix="p0t3-missing-", dir=PROJECT / ".tmp") as missing:
        absent = scenario("missing", Path(missing))
    after = {"sha256": sha256(buyer_file), "bytes": buyer_file.stat().st_size,
             "mtime_ns": buyer_file.stat().st_mtime_ns}
    expected = next(x for x in audit["inventory"] if x["path"] == "data/features/buyer_features.parquet")
    good = present["result"]
    bad = absent["result"]
    checks = {
        "nbformat_read_and_validate": True,
        "all_code_cells_execute_locally": present["exit_code"] == 0 and good["cells_attempted"] == 9,
        "all_eight_file_checks": bool(good["file_checks"]) and all(good["file_checks"].values()),
        "row_count_matches_P0T1": good["summary"] is not None and good["summary"]["rows"] == expected["rows"],
        "source_sha256_matches_P0T1": before["sha256"] == expected["sha256"],
        "missing_data_stops_clearly": absent["exit_code"] == 2 and bad["failure"] is not None
            and bad["failure"]["type"] == "FileNotFoundError" and bad["failure"]["cell"] == "require-file"
            and bad["file_checks"] is None,
        "no_Colab_or_Drive_execution_claim": good["running_in_colab"] is False and bad["running_in_colab"] is False,
        "no_Windows_paths_in_notebook": re.search(r"(?i)(?<![a-z0-9])[a-z]:[\\/]", "\n".join(c.source for c in book.cells)) is None,
        "notebook_outputs_cleared": all(c.execution_count is None and not c.outputs for c in book.cells if c.cell_type == "code"),
        "source_file_unchanged": before == after,
        "notebook_file_unchanged_by_execution": sha256(NOTEBOOK) == notebook_hash,
    }
    evidence = {
        "task": "P0-T3", "checked_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "READY FOR STUDENT TEST" if all(checks.values()) else "NEEDS REVIEW",
        "execution_method": "nbformat.read/validate; exec each code cell in order inside a fresh Python subprocess per case; not a Jupyter/Colab kernel",
        "environment": {"python": sys.version, "executable": sys.executable, "nbformat": nbformat.__version__,
                        "nbformat_install": "isolated .tmp/notebook-validation; not added to MVP runtime requirements"},
        "checks": checks, "passed": sum(checks.values()), "total": len(checks),
        "source_relative_file": "data/features/buyer_features.parquet", "source_before": before, "source_after": after,
        "notebook_sha256": notebook_hash, "present": present, "missing": absent,
        "limits": ["No Colab account, Drive mount, upload or sharing change executed",
                   "No full MVP environment install/import or version lock",
                   "No EDA, feature generation, model load/training or source modification",
                   "File checks do not resolve the P0-T1 cleaning/buyer/rounding/February issues"],
    }
    (output / "verification.json").write_text(json.dumps(evidence, indent=2, ensure_ascii=False)+"\n", encoding="utf-8")
    text = []
    for scenario_result in [present, absent]:
        text.append("CASE: " + scenario_result["result"]["case"] + " / exit " + str(scenario_result["exit_code"]))
        for cell in scenario_result["result"]["cells"]:
            text.append("CELL: " + cell["cell"] + "\n" + cell["output"])
        if scenario_result["result"]["failure"]:
            text.append(json.dumps(scenario_result["result"]["failure"], ensure_ascii=False))
    (output / "local_run.txt").write_text("\n".join(text)+"\n", encoding="utf-8")
    print(json.dumps({"status": evidence["status"], "checks": checks,
                      "passed": evidence["passed"], "total": evidence["total"],
                      "summary": good["summary"], "file_checks": good["file_checks"]}, indent=2))
    return 0 if all(checks.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())

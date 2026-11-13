"""P2-T1: read CSV headers/bounded samples and Parquet footers, without cleaning.

Exit 0: inspection ready for student review; exit 2: required raw schema blocked.
Only DuckDB is needed in addition to the Python standard library.
"""
from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import hashlib
from itertools import islice
import json
import os
from pathlib import Path
import platform
import re
import sys
import uuid

import duckdb

from data_paths import PROJECT_ROOT, data_root

RAW_MONTHS = ["2019-Oct", "2019-Nov", "2019-Dec", "2020-Jan"]
RAW_COLUMNS = ["event_time", "event_type", "product_id", "category_id",
               "category_code", "brand", "price", "user_id", "user_session"]
PARQUET_FILES = ["cleaned/observation_events.parquet", "cleaned/clean_events.parquet",
                 "cleaned/holdout_events.parquet", "features/customer_features.parquet",
                 "features/buyer_features.parquet", "features/non_buyer_features.parquet"]


def file_metadata(path):
    s = path.stat()
    return {"bytes": s.st_size, "mtime_ns": s.st_mtime_ns}


def parse_time(value):
    # Parse a copy in memory; never assume an absent timezone means UTC.
    text = value[:-4] + "+00:00" if value.endswith(" UTC") else value
    return datetime.fromisoformat(text)


def time_summary(values):
    parsed, failures = [], 0
    for value in values:
        try:
            parsed.append(parse_time(value))
        except ValueError:
            failures += 1
    aware = [d for d in parsed if d.utcoffset() is not None]
    offsets = sorted({int(d.utcoffset().total_seconds()) for d in aware})
    return {"scope": "bounded prefix only", "nonempty_values": len(values),
            "parsed": len(parsed), "parse_failures": failures,
            "explicit_timezone": len(aware), "without_timezone": len(parsed)-len(aware),
            "utc_suffix": sum(v.endswith(" UTC") for v in values),
            "offset_seconds_observed": offsets,
            "first_timestamp_text": values[0] if values else None,
            "sample_min_utc": min(aware).astimezone(timezone.utc).isoformat() if aware else None,
            "sample_max_utc": max(aware).astimezone(timezone.utc).isoformat() if aware else None}


def sample_columns(con, header, rows):
    # DuckDB casts only this small in-memory table, never the original CSV.
    con.execute("DROP TABLE IF EXISTS csv_sample")
    con.execute("CREATE TEMP TABLE csv_sample (" + ",".join(
        '"' + n.replace('"', '""') + '" VARCHAR' for n in header) + ")")
    if rows:
        con.executemany("INSERT INTO csv_sample VALUES (" + ",".join("?" for _ in header) + ")", rows)
    result = []
    for i, name in enumerate(header):
        column = '"' + name.replace('"', '""') + '"'
        values = [r[i] for r in rows if r[i] != ""]
        counts = {}
        for kind in ["BIGINT", "DOUBLE"]:
            counts[kind] = con.execute(
                f"SELECT count(try_cast({column} AS {kind})) FROM csv_sample WHERE {column} <> ''"
            ).fetchone()[0]
        inferred = "UNDETERMINED" if not values else "VARCHAR"
        integer_text = sum(bool(re.fullmatch(r"[+-]?[0-9]+", v)) for v in values)
        if values:
            # TRY_CAST('1.25' AS BIGINT) rounds, so cast success alone is insufficient.
            if counts["BIGINT"] == integer_text == len(values):
                inferred = "BIGINT"
            elif counts["DOUBLE"] == len(values):
                inferred = "DOUBLE"
        item = {"name": name, "stored_type": "CSV text (no embedded column type)",
                "sample_inferred_type": inferred, "nonempty_sample_values": len(values),
                "empty_sample_values": len(rows)-len(values), "integer_text_values": integer_text,
                "try_cast_successes": counts}
        if name == "event_time":
            item["time"] = time_summary(values)
            if values and item["time"]["parsed"] == len(values):
                item["sample_inferred_type"] = ("TIMESTAMP WITH TIME ZONE" if
                    item["time"]["explicit_timezone"] == len(values) else
                    "TIMESTAMP" if item["time"]["without_timezone"] == len(values) else "MIXED_TIMEZONE")
        if name == "user_session":
            valid = 0
            for value in values:
                try:
                    uuid.UUID(value)
                    valid += 1
                except ValueError:
                    pass
            item["uuid_parse_successes"] = valid
        result.append(item)
    return result


def inspect_csv(path, con, limit, sample):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.reader(stream, strict=True)
        header = next(reader)
        if not header or len(set(n.lower() for n in header)) != len(header):
            raise ValueError("empty or duplicate header")
        rows = list(islice(reader, limit)) if sample else []
    valid_rows = [r for r in rows if len(r) == len(header)]
    return {"inspection": "header + bounded prefix" if sample else "header only; no event rows",
            "header": header, "sample_rows_read": len(rows), "sample_rows_with_matching_width": len(valid_rows),
            "sample_rows_with_wrong_width": len(rows)-len(valid_rows),
            "columns": sample_columns(con, header, valid_rows) if sample else [
                {"name": n, "stored_type": "CSV text (no embedded column type)",
                 "sample_inferred_type": "NOT SAMPLED"} for n in header],
            "sample_event_types": sorted({r[header.index("event_type")] for r in valid_rows}) if "event_type" in header else [],
            "sample_fingerprint_sha256": hashlib.sha256(json.dumps(rows,ensure_ascii=False).encode("utf-8")).hexdigest() if sample else None}


def inspect_parquet(path, con):
    described = con.execute("DESCRIBE SELECT * FROM read_parquet(?)", [str(path)]).fetchall()
    internal = con.execute("SELECT name,type,converted_type,logical_type FROM parquet_schema(?)", [str(path)]).fetchall()
    stored = {r[0]: r for r in internal if r[1] is not None}
    metadata = con.execute("SELECT num_rows,num_row_groups FROM parquet_file_metadata(?)", [str(path)]).fetchone()
    return {"inspection": "Parquet footer/schema only; no event/customer rows",
            "footer_rows": metadata[0], "row_groups": metadata[1], "sample_rows_read": 0,
            "columns": [{"name": r[0], "stored_physical_type": stored[r[0]][1],
                         "stored_converted_type": stored[r[0]][2], "stored_logical_type": stored[r[0]][3],
                         "duckdb_type": r[1], "sample_inferred_type": "NOT SAMPLED"} for r in described]}


def inspect(root, sample_rows):
    con = duckdb.connect(":memory:", config={"threads": 1, "memory_limit": "256MB"})
    con.execute("SET TimeZone='UTC'")
    required = [f"raw/{m}.csv" for m in RAW_MONTHS]
    paths = sorted(set(required + [p.relative_to(root).as_posix() for p in root.rglob("*")
                                  if p.is_file() and p.suffix.lower() in {".csv", ".parquet"}]))
    files, blockers = [], []
    try:
        for name in paths:
            path = root/name
            item = {"path": name, "required_observation_raw": name in required}
            try:
                before = file_metadata(path)
                item.update(before)
                if name in required or (name.startswith("raw/") and path.suffix.lower() == ".csv"):
                    item.update(inspect_csv(path, con, sample_rows, name in required))
                    item["status"] = "INSPECTED"
                    if name in required and (not set(RAW_COLUMNS).issubset(item["header"]) or
                                             not item["sample_rows_read"] or item["sample_rows_with_wrong_width"]):
                        blockers.append({"path": name, "reason": "required columns/sample structure incomplete"})
                elif name in PARQUET_FILES:
                    item.update(inspect_parquet(path, con))
                    item["status"] = "INSPECTED"
                else:
                    item.update(status="EXCLUDED", inspection="file metadata only; not an MVP input")
                item["metadata_preserved"] = before == file_metadata(path)
                if not item["metadata_preserved"]:
                    blockers.append({"path": name, "reason": "source metadata changed during inspection"})
            except (OSError, ValueError, StopIteration, csv.Error, duckdb.Error) as exc:
                # Do not publish exception messages that could contain row values or IDs.
                item.update(status="UNREADABLE", error_type=type(exc).__name__, errno=getattr(exc,"errno",None))
                if name in required:
                    blockers.append({"path": name, "reason": "required raw header/sample unreadable", "error_type": type(exc).__name__})
            files.append(item)
    finally:
        con.close()
    raw = [f for f in files if f["path"] in required and f["status"] == "INSPECTED"]
    common = sorted(set.intersection(*(set(f["header"]) for f in raw))) if raw else []
    return {"files": files, "blockers": blockers,
            "status": "BLOCKED" if blockers else "READY FOR STUDENT REVIEW",
            "raw_schema_comparison": {"required_files": len(required), "headers_read": len(raw),
                "all_readable_observation_headers_equal": bool(raw) and all(f["header"]==raw[0]["header"] for f in raw),
                "common_columns_readable_only": common, "unreadable_months_not_inferred": True}}


def write_evidence(output, result):
    output.mkdir(parents=True, exist_ok=False)
    (output/"inspection.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n", encoding="utf-8")
    fields = ["file", "column", "stored_type", "reader_or_sample_type", "scope", "other_readable_raw_files_with_column", "note"]
    with (output/"schema.csv").open("w",encoding="utf-8",newline="") as stream:
        writer = csv.DictWriter(stream,fieldnames=fields); writer.writeheader()
        readable = [f for f in result["files"] if f["required_observation_raw"] and f["status"]=="INSPECTED"]
        for f in result["files"]:
            for c in f.get("columns", [{"name":"UNVERIFIED"}]):
                writer.writerow({"file": f["path"], "column": c["name"],
                    "stored_type": c.get("stored_type",c.get("stored_physical_type","UNVERIFIED")),
                    "reader_or_sample_type": c.get("duckdb_type",c.get("sample_inferred_type","UNVERIFIED")),
                    "scope": f.get("inspection", f["status"]),
                    "other_readable_raw_files_with_column": ";".join(x["path"] for x in readable if x["path"]!=f["path"] and c["name"] in x["header"]),
                    "note": "Full logical/converted types and sample limits are in inspection.json; no business policy validated."})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-root", type=Path, help="Root with raw/, cleaned/, features/; or REES46_DATA_ROOT")
    parser.add_argument("--sample-rows", type=int, default=1000)
    parser.add_argument("--output", type=Path, default=Path("results/p2_t1"))
    args = parser.parse_args()
    root = args.data_root.expanduser() if args.data_root else data_root()
    root = (PROJECT_ROOT/root).resolve() if not root.is_absolute() else root.resolve()
    output = (PROJECT_ROOT/args.output).resolve()
    if not 1 <= args.sample_rows <= 5000:
        parser.error("--sample-rows must be between 1 and 5000")
    if not root.is_dir():
        parser.error("--data-root does not exist")
    if (not output.is_relative_to(PROJECT_ROOT) or output==PROJECT_ROOT or
            output.is_relative_to(root) or root.is_relative_to(output) or output.exists()):
        parser.error("--output must be a new folder inside MVP, outside the source data tree")
    result = inspect(root, args.sample_rows)
    result.update(task="P2-T1", checked_at_utc=datetime.now(timezone.utc).isoformat(),
        data_root_relative_to_repository=os.path.relpath(root,PROJECT_ROOT).replace("\\","/"),
        environment={"python": sys.version, "duckdb": duckdb.__version__, "os": platform.platform(),
                     "threads":1,"memory_limit":"256MB","session_timezone":"UTC"},
        command=["python","-B","scripts/inspect_schema.py",*sys.argv[1:]],
        code_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), sample_rows_limit_per_observation_csv=args.sample_rows,
        limits=["Prefix samples are not representative/full quality checks or full timestamp ranges.",
                "CSV inferred types use DuckDB TRY_CAST on a bounded in-memory copy; not CSV embedded types or read_csv auto-inference.",
                "Timestamp inference also checks Python ISO parsing and explicit timezone text; session UTC alone proves no source timezone.",
                "February CSV header only; mixed/future Parquet footer only. No February outcomes.",
                "No cleaning, policy choice, features, model, full raw hashes, or raw-to-clean rebuild.",
                "No raw identifier values are written. Source preservation uses size/mtime; separate QA checks small source hashes."])
    write_evidence(output,result)
    print(json.dumps({"task":"P2-T1","status":result["status"],"files":len(result["files"]),
        "sample_rows_read":sum(f.get("sample_rows_read",0) for f in result["files"]),
        "blockers":result["blockers"],"output":str(output.relative_to(PROJECT_ROOT))}))
    return 2 if result["blockers"] else 0


if __name__ == "__main__":
    raise SystemExit(main())

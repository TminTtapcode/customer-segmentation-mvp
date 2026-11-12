"""P0-T1: chỉ đọc project cũ; ghi inventory và kiểm chứng vào repo MVP.

Không import pipeline cũ, không fit model, không phân tích outcome February.
Phụ thuộc duy nhất ngoài standard library: duckdb.
"""
from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import time

sys.dont_write_bytecode = True
import duckdb

PROJECT = Path(__file__).resolve().parents[1]
EXCLUDED = {".git", ".venv", "venv", "__pycache__", ".tmp", "node_modules", ".ipynb_checkpoints"}
FEATURES = ["recency_days", "frequency", "monetary", "sessions_30d", "views_30d"]


def digest(path):
    result = hashlib.sha256()
    try:
        with path.open("rb") as stream:
            for block in iter(lambda: stream.read(4 * 1024 * 1024), b""):
                result.update(block)
    except OSError as exc:
        raise OSError(f"Cannot hash {path}: {exc}") from exc
    return result.hexdigest()


def files_under(root):
    for parent, dirs, files in os.walk(root, followlinks=False):
        dirs[:] = sorted(d for d in dirs if d not in EXCLUDED and not (Path(parent) / d).is_symlink())
        for name in sorted(files):
            path = Path(parent) / name
            if not path.is_symlink() and name not in {".env", ".envrc"}:
                yield path


def snapshot(root):
    result = {}
    for path in files_under(root):
        stat = path.stat()
        entry = {"bytes": stat.st_size, "mtime_ns": stat.st_mtime_ns, "sha256": None}
        try:
            entry["sha256"] = digest(path)
        except OSError as exc:
            entry["hash_error"] = str(exc)
        result[path.relative_to(root).as_posix()] = entry
    return result


def git(root, *args):
    env = dict(os.environ, GIT_OPTIONAL_LOCKS="0")
    return subprocess.check_output(["git", "-C", str(root), *args], env=env, text=True).strip()


def sql_path(path):
    return "'" + path.as_posix().replace("'", "''") + "'"


def decision(relative):
    if relative == "data/cleaned/observation_events.parquet":
        return "event", "preferred_candidate_pending_P2_cleaning_policy", "scripts/phase2_etl.py"
    if relative.startswith("data/raw/") and relative.endswith(".csv"):
        reuse = "future_archive_metadata_only" if "Feb" in relative else "raw_rebuild_reference"
        return "event", reuse, "configs/project.yaml:dataset.url; download receipt unavailable"
    if relative == "data/cleaned/holdout_events.parquet":
        return "event", "future_archive_metadata_only", "scripts/phase2_etl.py"
    if relative == "data/cleaned/clean_events.parquet":
        return "event", "mixed_observation_future_do_not_use_directly", "scripts/phase2_etl.py"
    if relative in {"data/features/buyer_features.parquet", "data/features/customer_features.parquet"}:
        return "user", "five_columns_candidate_pending_P2_policy", "scripts/phase3_feature_engineering.py"
    if relative == "data/features/non_buyer_features.parquet":
        return "user", "engagement_description_only_no_clustering", "scripts/phase3_feature_engineering.py"
    if relative.endswith(".ipynb"):
        return "notebook", "review_for_teaching_only", "local notebook; inspect metadata"
    if "buyer_clusters" in relative or relative.endswith(".joblib") or "recommendations" in relative or "dashboard" in relative:
        return "downstream", "exclude_from_MVP_research_input", "legacy pipeline; model/decisions/display"
    return "reference", "provenance_or_reference_only", "legacy project"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--output", type=Path, default=PROJECT / "results/p0_t1")
    args = parser.parse_args()
    source, output = args.source.resolve(), args.output.resolve()
    if not source.is_dir() or not (source / "AGENTS.md").is_file():
        parser.error("--source phải là project cũ có AGENTS.md")
    if source == PROJECT or source.is_relative_to(PROJECT):
        parser.error("--source phải độc lập với repo MVP")
    if not output.is_relative_to(PROJECT) or output.is_relative_to(source):
        parser.error("--output phải nằm trong repo MVP và ngoài project nguồn")
    output.mkdir(parents=True, exist_ok=True)
    started = time.perf_counter()
    evidence = {
        "task": "P0-T1", "checked_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_root": str(source), "source_git_head": git(source, "rev-parse", "HEAD"),
        "source_git_status_before": git(source, "status", "--short"),
        "environment": {"python": sys.version, "executable": sys.executable,
                        "os": platform.platform(), "duckdb": duckdb.__version__,
                        "duckdb_threads": 4, "duckdb_memory_limit": "1GB",
                        "measurement": "audit duration only; not pipeline benchmark"},
        "limits": ["No raw-to-clean rebuild or validation of 7-vs-9-field dedup equivalence",
                   "CSV schema is header only; no fresh full CSV row counts",
                   "Future and full mixed partitions read as metadata/opaque hashes only",
                   "No February outcomes, model loading/training, EDA or dashboard",
                   "Old source origin URL is documented; acquisition receipt/license not verified",
                   "TIMESTAMP columns lack timezone annotation; UTC follows source contract",
                   "Historical manifests are reference evidence, not new measurements"],
    }
    print("Hashing source files (no writes to source)...", flush=True)
    before = snapshot(source)
    evidence["source_fingerprints_before"] = before
    con = duckdb.connect(":memory:", config={"threads": 4, "memory_limit": "1GB",
                        "temp_directory": str(output / ".duckdb_temp")})

    def rows(sql):
        cur = con.execute(sql)
        names = [c[0] for c in cur.description]
        return [dict(zip(names, row)) for row in cur.fetchall()]

    inventory = []
    for relative, fingerprint in sorted(before.items()):
        path = source / relative
        grain, reuse, provenance = decision(relative)
        item = {"path": relative, **fingerprint, "grain": grain, "reuse_decision": reuse,
                "provenance": provenance, "rows": None, "schema": None,
                "inspection": "file metadata and opaque SHA256"}
        if path.suffix.lower() == ".parquet":
            item["rows"] = con.execute("SELECT num_rows FROM parquet_file_metadata(?)", [str(path)]).fetchone()[0]
            item["schema"] = [{"name": r[0], "type": r[1]} for r in con.execute(
                "DESCRIBE SELECT * FROM read_parquet(?)", [str(path)]).fetchall()]
            item["inspection"] += "; Parquet footer/schema"
        elif relative.startswith("data/raw/") and path.suffix.lower() == ".csv":
            try:
                with path.open(encoding="utf-8-sig", newline="") as stream:
                    item["schema"] = [{"name": name, "type": "CSV text; inference pending P2"}
                                      for name in next(csv.reader(stream))]
                item["inspection"] += "; CSV header only"
            except OSError as exc:
                item["inspection"] += "; CSV header unreadable"
                item["read_error"] = str(exc)
        elif path.suffix.lower() == ".ipynb":
            book = json.loads(path.read_text(encoding="utf-8"))
            item["notebook"] = {"cells": len(book.get("cells", [])),
                                "executed_cells": sum(c.get("execution_count") is not None for c in book.get("cells", []))}
        inventory.append(item)
    evidence["inventory"] = inventory
    evidence["notebook_search"] = {"root": str(source), "excluded_directories": sorted(EXCLUDED),
                                    "count": sum(p["path"].endswith(".ipynb") for p in inventory)}

    obs = sql_path(source / "data/cleaned/observation_events.parquet")
    customer = sql_path(source / "data/features/customer_features.parquet")
    buyer = sql_path(source / "data/features/buyer_features.parquet")
    nonbuyer = sql_path(source / "data/features/non_buyer_features.parquet")
    con.execute(f"CREATE VIEW obs AS SELECT * FROM read_parquet({obs})")
    print("Checking observation boundaries, flags and session keys...", flush=True)
    evidence["observation"] = rows("""
        SELECT COUNT(*) AS rows, MIN(event_time)::VARCHAR AS min_time, MAX(event_time)::VARCHAR AS max_time,
          COUNT(DISTINCT user_id) AS users,
          COUNT(*) FILTER (WHERE event_time IS NULL OR event_time < TIMESTAMP '2019-10-01' OR event_time >= TIMESTAMP '2020-02-01') AS invalid_time_rows,
          COUNT(*) FILTER (WHERE split_partition IS DISTINCT FROM 'observation') AS wrong_partition_rows,
          COUNT(*) FILTER (WHERE user_id IS NULL) AS missing_user_rows,
          COUNT(*) FILTER (WHERE session_id IS NULL) AS missing_session_rows,
          COUNT(*) FILTER (WHERE event_type='purchase') AS purchase_events,
          COUNT(*) FILTER (WHERE event_type='purchase' AND (price IS NULL OR price <= 0)) AS nonpositive_or_missing_purchase_price,
          COUNT(*) FILTER (WHERE is_valid_for_monetary IS DISTINCT FROM (event_type='purchase' AND price>0 AND user_id IS NOT NULL)) AS monetary_flag_mismatches,
          COUNT(*) FILTER (WHERE user_session_id IS DISTINCT FROM CASE WHEN user_id IS NOT NULL AND session_id IS NOT NULL THEN CAST(user_id AS VARCHAR)||'_'||session_id END) AS session_key_mismatches,
          ROUND(SUM(price) FILTER (WHERE event_type='purchase' AND price>0 AND user_id IS NOT NULL),2) AS monetary
        FROM obs
    """)[0]
    evidence["shared_session_tokens"] = rows("""
        SELECT COUNT(*) AS tokens_shared_across_users FROM
        (SELECT session_id FROM obs WHERE session_id IS NOT NULL GROUP BY session_id HAVING COUNT(DISTINCT user_id)>1)
    """)[0]
    # Reconstruct only the five candidate features in memory. Explicit criteria,
    # using (user_id, session_id) rather than trusting stored composite keys/flags.
    print("Reconciling five stored features against all observation events...", flush=True)
    con.execute("""
        CREATE TEMP TABLE expected AS
        SELECT user_id,
          ROUND(EXTRACT(EPOCH FROM (TIMESTAMP '2020-02-01' - MAX(event_time) FILTER (WHERE event_type='purchase' AND price>0 AND user_id IS NOT NULL)))/86400.0,2) AS recency_days,
          COUNT(DISTINCT session_id) FILTER (WHERE event_type='purchase' AND price>0 AND user_id IS NOT NULL) AS frequency,
          ROUND(COALESCE(SUM(price) FILTER (WHERE event_type='purchase' AND price>0 AND user_id IS NOT NULL),0),2) AS monetary,
          COUNT(DISTINCT session_id) FILTER (WHERE event_time>=TIMESTAMP '2020-01-02' AND event_time<TIMESTAMP '2020-02-01') AS sessions_30d,
          COUNT(*) FILTER (WHERE event_type='view' AND event_time>=TIMESTAMP '2020-01-02' AND event_time<TIMESTAMP '2020-02-01') AS views_30d
        FROM obs GROUP BY user_id
    """)
    evidence["reconciliations"] = {}
    for label, path, where in [("customer", customer, "TRUE"), ("buyer", buyer, "frequency>0 AND monetary>0"),
                                ("nonbuyer", nonbuyer, "NOT (frequency>0 AND monetary>0)")]:
        differences = " OR ".join(f"e.{f} IS DISTINCT FROM a.{f}" for f in FEATURES)
        evidence["reconciliations"][label] = rows(f"""
            WITH e AS (SELECT * FROM expected WHERE {where}), a AS (SELECT * FROM read_parquet({path}))
            SELECT COUNT(*) FILTER (WHERE e.user_id IS NULL) AS unexpected_users,
              COUNT(*) FILTER (WHERE a.user_id IS NULL) AS missing_users,
              COUNT(*) FILTER (WHERE e.user_id IS NOT NULL AND a.user_id IS NOT NULL AND ({differences})) AS feature_mismatch_users
            FROM e FULL OUTER JOIN a USING(user_id)
        """)[0]
        evidence["reconciliations"][label]["duplicate_or_null_ids"] = rows(f"""
            SELECT COUNT(*)-COUNT(DISTINCT user_id) AS n FROM read_parquet({path})
        """)[0]["n"]
    evidence["cohorts"] = rows(f"""
        SELECT COUNT(*) AS customers, COUNT(*) FILTER (WHERE is_buyer) AS buyers,
          COUNT(*) FILTER (WHERE NOT is_buyer) AS nonbuyers,
          COUNT(*) FILTER (WHERE is_buyer IS DISTINCT FROM (frequency>0 AND monetary>0)) AS buyer_flag_mismatches,
          COUNT(*) FILTER (WHERE NOT is_buyer AND recency_days IS NOT NULL) AS nonbuyer_recency_not_null,
          COUNT(*) FILTER (WHERE is_buyer AND (recency_days IS NULL OR recency_days<0 OR frequency<=0 OR monetary<=0)) AS invalid_buyer_rows
        FROM read_parquet({customer})
    """)[0]
    con.close()
    print("Verifying source preservation...", flush=True)
    after = snapshot(source)
    evidence["source_git_status_after"] = git(source, "status", "--short")
    changed = [p for p in sorted(before.keys() | after.keys()) if before.get(p) != after.get(p)]
    unhashed = [p for p,v in before.items() if v["sha256"] is None]
    evidence["preservation"] = {"inventoried_files": len(before),
                                "hashed_files": len(before)-len(unhashed),
                                "hashed_bytes": sum(v["bytes"] for v in before.values() if v["sha256"] is not None),
                                "unhashed_paths": unhashed,
                                "changed_paths": changed, "readable_file_hashes_unchanged": not changed,
                                "git_status_unchanged": evidence["source_git_status_before"] == evidence["source_git_status_after"],
                                "excluded": "Git internals, environments, temp/cache directories, symlinks, .env/.envrc"}
    obs_result = evidence["observation"]
    cohort = evidence["cohorts"]
    checks = {
        "observation_contract": all(obs_result[k] == 0 for k in ["invalid_time_rows", "wrong_partition_rows", "missing_user_rows", "monetary_flag_mismatches", "session_key_mismatches"]),
        "five_features_reconcile": all(all(v==0 for v in r.values()) for r in evidence["reconciliations"].values()),
        "cohort_contract": all(cohort[k]==0 for k in ["buyer_flag_mismatches", "nonbuyer_recency_not_null", "invalid_buyer_rows"]),
        "cohort_count": cohort["customers"] == cohort["buyers"] + cohort["nonbuyers"] == obs_result["users"],
        "source_preserved": not changed and evidence["preservation"]["git_status_unchanged"],
    }
    evidence["verification"] = {"checks": checks, "passed": sum(checks.values()), "total": len(checks),
                                "technical_checks_pass": all(checks.values()), "acceptance": "NEEDS REVIEW by students; P2 policy decisions pending"}
    evidence["audit_duration_seconds"] = round(time.perf_counter()-started, 3)
    (output / "audit.json").write_text(json.dumps(evidence, indent=2, ensure_ascii=False, default=str)+"\n", encoding="utf-8")
    columns = ["path", "bytes", "sha256", "grain", "rows", "reuse_decision", "provenance", "inspection"]
    with (output / "inventory.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(inventory)
    print(json.dumps({"observation": evidence["observation"], "cohorts": evidence["cohorts"],
                      "reconciliations": evidence["reconciliations"], "preservation": evidence["preservation"],
                      "verification": evidence["verification"], "audit_duration_seconds": evidence["audit_duration_seconds"]}, indent=2))
    return 0 if all(checks.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())

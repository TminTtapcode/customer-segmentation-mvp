"""Kiểm chứng P0-T1 bằng dữ liệu thật và tổng hợp Python trên mẫu phân tầng.

DuckDB chỉ đọc các event của mẫu; phép gom nhóm/tính RFM bên dưới dùng Python.
Không ghi user IDs ra kết quả và không dùng dữ liệu tương lai.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
import duckdb

from audit_existing_artifacts import FEATURES, PROJECT, digest, sql_path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--audit", type=Path, default=PROJECT / "results/p0_t1/audit.json")
    args = parser.parse_args()
    audit_path = args.audit.resolve()
    if not audit_path.is_relative_to(PROJECT):
        parser.error("Audit evidence phải nằm trong repo MVP")
    evidence = json.loads(audit_path.read_text(encoding="utf-8"))
    source = Path(evidence["source_root"])
    con = duckdb.connect(":memory:", config={"threads": 4, "memory_limit": "1GB"})
    buyer = sql_path(source / "data/features/customer_features.parquet")
    obs = sql_path(source / "data/cleaned/observation_events.parquet")
    # Tối đa 5 users mỗi tổ hợp: buyer/nonbuyer, có phiên recent, repeat buyer.
    stored = con.execute(f"""
        SELECT user_id, recency_days, frequency, monetary, sessions_30d, views_30d
        FROM read_parquet({buyer})
        QUALIFY ROW_NUMBER() OVER (
          PARTITION BY is_buyer, sessions_30d>0, frequency>1 ORDER BY user_id
        ) <= 5
        ORDER BY user_id
    """).fetchall()
    user_ids = [r[0] for r in stored]
    assert user_ids, "Mẫu dữ liệu thật không được rỗng"
    cutoff = datetime(2020, 2, 1)
    recent = cutoff - timedelta(days=30)
    summary = {u: {"purchases": set(), "last_purchase": None, "monetary": Decimal(0),
                   "sessions": set(), "views": 0} for u in user_ids}
    placeholders = ",".join("?" for _ in user_ids)
    cursor = con.execute(f"""
        SELECT user_id, session_id, event_time, event_type, price
        FROM read_parquet({obs}) WHERE user_id IN ({placeholders})
    """, user_ids)
    read_events = 0
    while batch := cursor.fetchmany(10000):
        for user, session, moment, event, price in batch:
            assert datetime(2019, 10, 1) <= moment < cutoff
            read_events += 1
            data = summary[user]
            if event == "purchase" and price is not None and price > 0:
                if session is not None:
                    data["purchases"].add(session)
                data["last_purchase"] = max(data["last_purchase"] or moment, moment)
                data["monetary"] += Decimal(str(price))
            if recent <= moment < cutoff:
                if session is not None:
                    data["sessions"].add(session)
                if event == "view":
                    data["views"] += 1
    mismatches = {f: 0 for f in FEATURES}
    for user, *actual in stored:
        data = summary[user]
        recency = None
        if data["last_purchase"] is not None:
            seconds = Decimal(str((cutoff-data["last_purchase"]).total_seconds()))
            recency = float((seconds/Decimal(86400)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))
        expected = [recency, len(data["purchases"]),
                    float(data["monetary"].quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)),
                    len(data["sessions"]), data["views"]]
        for name, a, e in zip(FEATURES, actual, expected):
            equal = (a is None and e is None) or (a is not None and e is not None and abs(a-e)<1e-7)
            mismatches[name] += not equal
    checked_paths = ["data/cleaned/observation_events.parquet", "data/features/customer_features.parquet",
                     "data/features/buyer_features.parquet", "data/features/non_buyer_features.parquet"]
    current_fingerprints_match = all(digest(source/p)==evidence["source_fingerprints_before"][p]["sha256"]
                                     for p in checked_paths)
    con.close()
    checks = {"main_audit_checks": evidence["verification"]["technical_checks_pass"],
              "independent_python_sample": all(v==0 for v in mismatches.values()),
              "four_candidate_hashes_match": current_fingerprints_match,
              "observation_footer_row_count": next(x["rows"] for x in evidence["inventory"] if x["path"]==checked_paths[0])==evidence["observation"]["rows"]}
    result = {"method": "stratified deterministic real users; Python sets/datetime/Decimal aggregation",
              "sample_users": len(stored), "sample_events": read_events,
              "mismatches_by_feature": mismatches, "checks": checks,
              "passed": sum(checks.values()), "total": len(checks),
              "limits": "Sample corroborates aggregate SQL; not proof of raw cleaning policy or all-user independent implementation. No user IDs exported."}
    (audit_path.parent / "independent_verification.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False)+"\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0 if all(checks.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())

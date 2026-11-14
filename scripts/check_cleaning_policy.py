"""P2-T3: test cleaning choices on raw CSVs; export aggregates, not observation.

Full event tables exist only in an ignored temporary DuckDB database.
"""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import platform
import sys
import tempfile
import time

import duckdb

from assess_quality import COLUMNS, MONTHS, START, END, UUID_PATTERN, sha256, stat, write_csv
from data_paths import PROJECT_ROOT, data_root

WINDOW = "TIMESTAMPTZ '2020-01-02 00:00:00+00'"
VALID_PURCHASE = "event_type='purchase' AND price>0 AND user_session IS NOT NULL"
OUTPUT_COLUMNS = "event_time,event_type,user_id,user_session,price"


def typed_sql(table):
    # Deduplication always happens on raw text, before these conversions.
    return f"""SELECT *, try_cast(event_time AS TIMESTAMPTZ) AS ts,
        try_cast(user_id AS BIGINT) AS uid,
        try_cast(price AS DECIMAL(18,2)) AS amount,
        CASE WHEN regexp_full_match(user_session,'{UUID_PATTERN}')
             THEN user_session END AS session_id,
        CASE
          WHEN try_cast(event_time AS TIMESTAMPTZ) IS NULL
            OR NOT isfinite(try_cast(event_time AS TIMESTAMPTZ))
            OR NOT coalesce(regexp_matches(event_time,'( UTC|Z|[+-][0-9]{{2}}:?[0-9]{{2}})$'),false)
            THEN 'invalid_timestamp'
          WHEN try_cast(event_time AS TIMESTAMPTZ)<{START}
            OR try_cast(event_time AS TIMESTAMPTZ)>={END} THEN 'outside_observation'
          WHEN NOT coalesce(regexp_full_match(user_id,'[0-9]+'),false)
            OR try_cast(user_id AS BIGINT) IS NULL OR try_cast(user_id AS BIGINT)<=0
            THEN 'invalid_user'
          WHEN event_type IS NULL OR event_type NOT IN ('view','cart','remove_from_cart','purchase')
            THEN 'unknown_event_type'
          ELSE 'kept' END AS reason FROM {table}"""


def prepare_policy(con):
    # DECIMAL must never silently round a source price with extra digits.
    unsupported = con.execute("""SELECT count(*) FROM raw
        WHERE isfinite(try_cast(price AS DOUBLE)) AND
          (NOT regexp_full_match(price,'[-+]?[0-9]+(\\.[0-9]{1,2})?')
           OR try_cast(price AS DECIMAL(18,2)) IS NULL)""").fetchone()[0]
    if unsupported:
        raise ValueError(f'{unsupported} finite prices need a new precision policy; no rounding applied')
    con.execute('CREATE TABLE dedup AS SELECT '+','.join(COLUMNS)+',count(*) AS n FROM raw GROUP BY '+','.join(COLUMNS))
    for source in ('raw', 'dedup'):
        con.execute(f'CREATE VIEW typed_{source} AS '+typed_sql(source))
        con.execute(f"""CREATE VIEW events_{source} AS SELECT ts AS event_time,event_type,
            uid AS user_id,session_id AS user_session,amount AS price
            FROM typed_{source} WHERE reason='kept'""")


def metrics(con, table):
    cur = con.execute(f"""SELECT count(*) AS event_rows,
        count(*) FILTER(WHERE event_type='view') AS view_events,
        count(*) FILTER(WHERE event_type='purchase') AS purchase_events,
        count(*) FILTER(WHERE {VALID_PURCHASE}) AS eligible_purchase_events,
        count(*) FILTER(WHERE event_type='purchase' AND (price IS NULL OR price<=0)) AS invalid_price_purchase_events,
        count(*) FILTER(WHERE user_session IS NULL) AS events_without_session,
        count(DISTINCT user_id) FILTER(WHERE {VALID_PURCHASE}) AS eligible_buyers,
        count(DISTINCT (user_id,user_session)) FILTER(WHERE event_type='purchase'
            AND user_session IS NOT NULL) AS all_purchase_sessions,
        count(DISTINCT (user_id,user_session)) FILTER(WHERE {VALID_PURCHASE}) AS purchase_sessions,
        coalesce(sum(price) FILTER(WHERE event_type='purchase'),0) AS all_purchase_price_sum,
        coalesce(sum(price) FILTER(WHERE {VALID_PURCHASE}),0) AS purchase_price_sum,
        count(DISTINCT (user_id,user_session)) FILTER(WHERE event_time>={WINDOW}
            AND user_session IS NOT NULL) AS sessions_30d_all_users,
        count(*) FILTER(WHERE event_time>={WINDOW} AND event_type='view') AS views_30d_all_users,
        count(*) FILTER(WHERE event_time>={WINDOW} AND event_type='view'
            AND user_session IS NULL) AS views_30d_without_session
        FROM {table}""")
    return dict(zip([c[0] for c in cur.description],cur.fetchone()))


def check_policy(root, output):
    started = time.perf_counter()
    inputs = [root/'raw'/f'{name}.csv' for name in MONTHS]
    before = [dict(path='raw/'+p.name, **stat(p)) for p in inputs]
    december = next(p for p in inputs if p.name=='2019-Dec.csv')
    december_hash = sha256(december)
    PROJECT_ROOT.joinpath('.tmp').mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='p2t3-',dir=PROJECT_ROOT/'.tmp') as temp:
        con = duckdb.connect(str(Path(temp)/'policy.duckdb'))
        try:
            con.execute("SET threads=2; SET memory_limit='768MB'; SET TimeZone='UTC'")
            for i,p in enumerate(inputs):
                header=con.execute("DESCRIBE SELECT * FROM read_csv(?,header=true,all_varchar=true,nullstr='',strict_mode=true)",[str(p)]).fetchall()
                if [c[0] for c in header]!=COLUMNS:
                    raise ValueError('Unexpected raw schema: '+p.name)
                con.execute(('CREATE TABLE raw AS ' if i==0 else 'INSERT INTO raw ')+
                    "SELECT * FROM read_csv(?,header=true,all_varchar=true,nullstr='',strict_mode=true)",[str(p)])
            assert [c[0] for c in con.execute('DESCRIBE raw').fetchall()]==COLUMNS
            prepare_policy(con)
            raw_count = con.execute('SELECT count(*) FROM raw').fetchone()[0]
            unique_count, weights = con.execute('SELECT count(*),sum(n) FROM dedup').fetchone()
            assert weights==raw_count
            reasons = dict(con.execute('SELECT reason,count(*) FROM typed_dedup GROUP BY reason').fetchall())
            assert sum(reasons.values())==unique_count
            summaries = [dict(stage=stage,**metrics(con,table)) for stage,table in
                         [('before_dedup_valid_keys','events_raw'),('after_policy','events_dedup')]]
            kept = summaries[1]['event_rows']
            assert kept==reasons.get('kept',0)
            counts = [dict(metric='raw_rows',count=raw_count,meaning='input'),
                      dict(metric='duplicate_extras_removed',count=raw_count-unique_count,meaning='removed_first')]
            for reason in ('invalid_timestamp','outside_observation','invalid_user','unknown_event_type'):
                counts.append(dict(metric=reason,count=reasons.get(reason,0),meaning='removed_after_dedup_exclusive'))
            counts.append(dict(metric='output_rows_dry_run',count=kept,meaning='retained'))
            assert raw_count==sum(c['count'] for c in counts if c['meaning'].startswith('removed'))+kept
            # No second DISTINCT after projection: distinct product events may now look identical.
            projected = con.execute('SELECT count(*) FROM (SELECT DISTINCT '+OUTPUT_COLUMNS+' FROM events_dedup)').fetchone()[0]
            counts.append(dict(metric='distinct_raw_events_sharing_projection',count=kept-projected,meaning='retained_not_deduplicated_again'))
            last = con.execute(f"""WITH p AS (SELECT user_id,max(event_time) AS last_any,
                max(event_time) FILTER(WHERE {VALID_PURCHASE}) AS last_valid
                FROM events_dedup WHERE event_type='purchase' GROUP BY user_id)
                SELECT count(*) FILTER(WHERE last_valid IS NULL),
                    count(*) FILTER(WHERE last_valid IS NOT NULL AND last_valid<>last_any) FROM p""").fetchone()
            counts += [dict(metric='users_no_eligible_purchase',count=last[0],meaning='outside_buyer_cohort_not_deleted'),
                       dict(metric='buyers_last_purchase_changed',count=last[1],meaning='recency_changes_vs_any_purchase')]
            schema = [dict(column=r[0],dtype=r[1],nullable=r[2]) for r in con.execute('DESCRIBE events_dedup').fetchall()]
            assert [c['column'] for c in schema]==OUTPUT_COLUMNS.split(',')
            after = [dict(path='raw/'+p.name,**stat(p)) for p in inputs]
            assert before==after and december_hash==sha256(december)
            output.mkdir(parents=True,exist_ok=False)
            write_csv(output/'stage_summary.csv',summaries,list(summaries[0]))
            write_csv(output/'policy_counts.csv',counts,['metric','count','meaning'])
            manifest = dict(task='P2-T3',scope='policy dry run; no official Parquet or customer features',
                checked_at_utc=datetime.now(timezone.utc).isoformat(),command=['python','-B',*sys.argv[0:]],
                code_sha256=sha256(Path(__file__)),python=platform.python_version(),duckdb=duckdb.__version__,
                threads=2,memory_limit='768MB',elapsed_seconds=time.perf_counter()-started,
                inputs=before,input_metadata_unchanged=True,december_sha256=december_hash,
                dedup_key=COLUMNS,price_precision_guard_passed=True,output_schema=schema,
                limitations=['Local hash is not publisher authentication','No RSS or Colab measurement',
                             'No event_id: exact-duplicate removal is a research assumption'])
            (output/'run_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
            print(json.dumps(dict(raw=raw_count,unique=unique_count,kept=kept,counts=counts,summary=summaries),default=str))
        finally:
            con.close()


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data-root',type=Path)
    parser.add_argument('--output',type=Path,default=Path('results/p2_t3'))
    args=parser.parse_args()
    root=(args.data_root or data_root()).resolve()
    output=args.output.resolve()
    if output.exists() or not output.is_relative_to(PROJECT_ROOT.resolve()) or output.is_relative_to(root):
        parser.error('Choose a new output directory inside the MVP repository and outside source data')
    check_policy(root,output)

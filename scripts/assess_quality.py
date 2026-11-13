"""P2-T2: full counts on four raw observation CSVs; never clean source data.

Uses a private temporary DuckDB database, then exports only aggregates and plots.
"""
from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys
import tempfile
import time

import duckdb

from data_paths import PROJECT_ROOT, data_root

MONTHS = {"2019-Oct": "2019-10", "2019-Nov": "2019-11", "2019-Dec": "2019-12", "2020-Jan": "2020-01"}
COLUMNS = ["event_time", "event_type", "product_id", "category_id", "category_code", "brand", "price", "user_id", "user_session"]
KEY7 = [c for c in COLUMNS if c not in {"brand", "category_code"}]
START = "TIMESTAMPTZ '2019-10-01 00:00:00+00'"
END = "TIMESTAMPTZ '2020-02-01 00:00:00+00'"
UUID_PATTERN = "[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}"


def missing(column):
    return f"({column} IS NULL OR trim({column})='')"


def prepare_checks(con):
    # All original fields remain text. Typed values are diagnostic expressions only.
    con.execute("""CREATE OR REPLACE VIEW checked AS SELECT *,
        try_cast(price AS DOUBLE) AS p,
        try_cast(event_time AS TIMESTAMPTZ) AS ts,
        try_cast(user_id AS BIGINT) AS uid FROM raw""")


def diagnostic_flags():
    return {
        "price_missing": missing("price"),
        "price_unparseable": f"NOT {missing('price')} AND p IS NULL",
        "price_nonfinite": "p IS NOT NULL AND NOT isfinite(p)",
        "price_negative": "isfinite(p) AND p<0",
        "price_zero": "isfinite(p) AND p=0",
        "price_positive": "isfinite(p) AND p>0",
        "user_id_bad_format": f"NOT {missing('user_id')} AND (NOT regexp_full_match(user_id,'[0-9]+') OR uid IS NULL)",
        "user_id_nonpositive": "uid<=0",
        "session_bad_format": f"NOT {missing('user_session')} AND NOT regexp_full_match(user_session,'{UUID_PATTERN}')",
        "time_missing": missing("event_time"),
        "time_unparseable": f"NOT {missing('event_time')} AND ts IS NULL",
        "time_nonfinite": "ts IS NOT NULL AND NOT isfinite(ts)",
        "time_without_explicit_zone": f"NOT {missing('event_time')} AND NOT regexp_matches(event_time,'( UTC|Z|[+-][0-9]{{2}}:?[0-9]{{2}})$')",
        "time_not_UTC_suffix": f"NOT {missing('event_time')} AND NOT ends_with(event_time,' UTC')",
        "time_outside_observation": f"isfinite(ts) AND (ts<{START} OR ts>={END})",
        "time_in_observation": f"isfinite(ts) AND ts>={START} AND ts<{END}",
        "time_wrong_source_month": "isfinite(ts) AND strftime(ts,'%Y-%m')<>source_month",
    }


def grouped_quality(con):
    expressions = {"missing_"+c: missing(c) for c in COLUMNS} | diagnostic_flags()
    counts = ",".join(f"count(*) FILTER (WHERE {expr}) AS {name}" for name, expr in expressions.items())
    cur = con.execute(f"""SELECT
        CASE WHEN grouping(source_month)=1 AND grouping(event_type)=1 THEN 'all'
             WHEN grouping(event_type)=1 THEN 'month'
             WHEN grouping(source_month)=1 THEN 'event' ELSE 'month_event' END AS scope,
        CASE WHEN grouping(source_month)=1 THEN 'ALL' ELSE source_month END AS month,
        CASE WHEN grouping(event_type)=1 THEN 'ALL' ELSE coalesce(event_type,'<MISSING>') END AS event_type,
        count(*) AS rows, {counts}
        FROM checked GROUP BY GROUPING SETS ((),(source_month),(event_type),(source_month,event_type))
        ORDER BY scope,month,event_type""")
    names = [c[0] for c in cur.description]
    return [dict(zip(names, row)) for row in cur.fetchall()]


def duplicate_counts(con):
    # These are frequency tables, not cleaned event tables. NULLs group together.
    # Equality is on the original CSV text values, without trimming/canonicalizing.
    con.execute("CREATE TABLE groups9 AS SELECT " + ",".join(COLUMNS) + ",count(*) AS n FROM raw GROUP BY " + ",".join(COLUMNS))
    result = []
    for size, keys, relation in [(9, COLUMNS, "groups9"), (7, KEY7, "groups7")]:
        if size == 7:
            con.execute("CREATE TABLE groups7 AS SELECT " + ",".join(keys) + ",sum(n)::BIGINT AS n FROM groups9 GROUP BY " + ",".join(keys))
        cur = con.execute(f"""SELECT count(*) AS unique_keys, sum(n)::BIGINT AS total_rows,
            count(*) FILTER (WHERE n>1) AS duplicate_groups,
            coalesce(sum(n) FILTER (WHERE n>1),0)::BIGINT AS rows_in_duplicate_groups,
            sum(n-1)::BIGINT AS extra_rows,
            coalesce(sum(n-1) FILTER (WHERE event_type='view'),0)::BIGINT AS extra_view_rows,
            coalesce(sum(n-1) FILTER (WHERE event_type='purchase'),0)::BIGINT AS extra_purchase_rows,
            coalesce(sum((n-1)*try_cast(price AS DOUBLE)) FILTER (
                WHERE event_type='purchase' AND isfinite(try_cast(price AS DOUBLE)) AND try_cast(price AS DOUBLE)>0),0)
                AS extra_positive_purchase_price FROM {relation}""")
        result.append({"key_fields": size, **dict(zip([c[0] for c in cur.description], cur.fetchone()))})
    return result


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8*1024*1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def stat(path):
    s = path.stat()
    return {"bytes": s.st_size, "mtime_ns": s.st_mtime_ns}


def write_csv(path, rows, fields):
    with path.open("w",encoding="utf-8",newline="") as stream:
        writer = csv.DictWriter(stream,fieldnames=fields)
        writer.writeheader(); writer.writerows(rows)


def plots(output, overall, event_rows, duplicates, histogram, price_range):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.ticker import FuncFormatter
    plt.rcParams.update({"font.size":10,"axes.spines.top":False,"axes.spines.right":False})
    folder=output/"figures"; folder.mkdir()
    fmt=FuncFormatter(lambda x,pos:f"{x:,.0f}")
    def save(fig,name):
        fig.tight_layout();fig.savefig(folder/name,dpi=150,bbox_inches="tight");plt.close(fig)
    fig,ax=plt.subplots(figsize=(8,4))
    rates=[100*overall['missing_'+c]/overall['rows'] for c in COLUMNS]
    ax.barh(COLUMNS,rates,color=['#245879' if v==max(rates) else '#b8c8d2' for v in rates])
    ax.set(title="Tỷ lệ thiếu theo cột — bốn CSV gốc",xlabel="% sự kiện (NULL hoặc chuỗi chỉ có khoảng trắng)",ylabel="Cột")
    ax.invert_yaxis(); save(fig,"missing.png")
    fig,ax=plt.subplots(figsize=(7,4))
    events=sorted(event_rows,key=lambda v:v['rows'],reverse=True)
    ax.bar([v['event_type'] for v in events],[v['rows'] for v in events],color='#91adbf')
    ax.set(title="Số sự kiện theo loại — chưa loại trùng",xlabel="Loại sự kiện",ylabel="Số sự kiện")
    ax.yaxis.set_major_formatter(fmt);save(fig,"event_types.png")
    fig,ax=plt.subplots(figsize=(6,4))
    ax.bar(["9 trường","7 trường"],[v['extra_rows'] for v in duplicates],color=['#b8c8d2','#245879'])
    ax.set(title="Số dòng dư nếu chỉ giữ một dòng mỗi khóa",xlabel="Định nghĩa khóa trùng trên giá trị CSV gốc",ylabel="Số dòng = tổng (n − 1)")
    ax.yaxis.set_major_formatter(fmt);save(fig,"duplicates.png")
    fig,axes=plt.subplots(1,2,figsize=(10,4),sharex=True,sharey=True)
    lo,hi=price_range; width=(hi-lo)/60 if hi>lo else 1
    for ax,col,title in zip(axes,['all_count','positive_count'],['Mọi giá hữu hạn','Chỉ nhóm giá > 0 (đối chiếu)']):
        ax.bar([lo+v['bin']*width for v in histogram],[v[col] for v in histogram],width=width,align='edge',color='#91adbf',edgecolor='white',linewidth=.3)
        ax.set(title=title,xlabel="Price (đơn vị giá nguồn chưa xác minh)",ylabel="Số sự kiện, thang log")
        ax.set_yscale('log')
    fig.suptitle("Phân phối price cùng 60 khoảng — chưa tạo dữ liệu sạch")
    save(fig,"price.png")


def assess(root, output):
    started=time.perf_counter()
    inputs={month:root/"raw"/(name+".csv") for name,month in MONTHS.items()}
    before={month:stat(path) for month,path in inputs.items()}
    for path in inputs.values():
        with path.open(encoding="utf-8-sig",newline="") as stream:
            if next(csv.reader(stream)) != COLUMNS:
                raise ValueError("Unexpected CSV header: "+path.name)
    december_hash=sha256(inputs['2019-12'])
    scratch=PROJECT_ROOT/".tmp";scratch.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="p2t2-",dir=scratch) as work:
        work=Path(work).resolve()
        assert work.is_relative_to(scratch.resolve())
        con=duckdb.connect(str(work/'quality.duckdb'),config={"threads":2,"memory_limit":"768MB","temp_directory":str(work/'spill'),"preserve_insertion_order":False})
        con.execute("SET TimeZone='UTC'")
        try:
            for i,(month,path) in enumerate(inputs.items()):
                print("Reading all rows:",path.name,flush=True)
                statement=("CREATE TABLE raw AS " if i==0 else "INSERT INTO raw ")
                con.execute(statement+"SELECT ? AS source_month,* FROM read_csv(?,header=true,all_varchar=true,nullstr='',strict_mode=true)",[month,str(path)])
            prepare_checks(con)
            grouped=grouped_quality(con)
            overall=next(g for g in grouped if g['scope']=='all')
            total=overall['rows']
            print("Rows read:",total,"; comparing duplicate keys...",flush=True)
            duplicates=duplicate_counts(con)
            sessions=con.execute(f"""SELECT count(*) AS reused_tokens,coalesce(sum(n),0)::BIGINT AS affected_rows FROM (
                SELECT user_session,count(*) AS n FROM raw
                WHERE NOT {missing('user_session')} AND NOT {missing('user_id')}
                GROUP BY user_session HAVING count(DISTINCT user_id)>1)""").fetchone()
            bounds=con.execute("""SELECT source_month,count(*) AS rows,
                CAST(min(ts) FILTER(WHERE isfinite(ts)) AS VARCHAR),
                CAST(max(ts) FILTER(WHERE isfinite(ts)) AS VARCHAR)
                FROM checked GROUP BY source_month ORDER BY source_month""").fetchall()
            prices=con.execute("""SELECT min(p),max(p) FROM checked WHERE isfinite(p)""").fetchone()
            q1,q3=con.execute("""SELECT quantile_cont(p,0.25),quantile_cont(p,0.75) FROM checked
                WHERE event_type='purchase' AND isfinite(p) AND p>0""").fetchone()
            threshold=q3+3*(q3-q1)
            outliers=con.execute("SELECT count(*) FROM checked WHERE event_type='purchase' AND isfinite(p) AND p>?",[threshold]).fetchone()[0]
            lo,hi=prices; width=(hi-lo)/60 if hi>lo else 1
            histogram=[{'bin':r[0],'all_count':r[1],'positive_count':r[2]} for r in con.execute("""
                SELECT least(59,greatest(0,floor((p-?)/?)::INT)) AS bin,
                count(*) AS all_count,count(*) FILTER(WHERE p>0) AS positive_count
                FROM checked WHERE isfinite(p) GROUP BY bin ORDER BY bin""",[lo,width]).fetchall()]
            purchase=next(g for g in grouped if g['scope']=='event' and g['event_type']=='purchase')
            assert sum(g['rows'] for g in grouped if g['scope']=='month')==total
            assert sum(g['rows'] for g in grouped if g['scope']=='event')==total
            assert all(d['total_rows']==total for d in duplicates)
            assert 0<=duplicates[0]['extra_rows']<=duplicates[1]['extra_rows']<=total
            assert sum(overall[n] for n in ['price_missing','price_unparseable','price_nonfinite','price_negative','price_zero','price_positive'])==total
            assert sum(overall[n] for n in ['time_missing','time_unparseable','time_nonfinite','time_outside_observation','time_in_observation'])==total
            assert sum(v['all_count'] for v in histogram)==overall['price_negative']+overall['price_zero']+overall['price_positive']
            assert all(g['missing_'+c]<=g['rows'] for g in grouped for c in COLUMNS)
            details=[]
            def detail(category,scope,month,event,metric,value,denominator=None):
                details.append(dict(category=category,scope=scope,month=month,event_type=event,metric=metric,value=value,denominator=denominator,pct=100*value/denominator if denominator else None))
            for g in grouped:
                for name,value in g.items():
                    if name in {'scope','month','event_type'}:continue
                    detail('missing' if name.startswith('missing_') else 'quality',g['scope'],g['month'],g['event_type'],name,value,g['rows'])
            for d in duplicates:
                for name,value in d.items():
                    if name!='key_fields':detail('duplicates','all','ALL','ALL',f"key{d['key_fields']}_{name}",value,total if name!='extra_positive_purchase_price' else None)
            for month,n,tmin,tmax in bounds:
                for name,value in [('rows',n),('min_utc',tmin),('max_utc',tmax)]:
                    details.append(dict(category='time_bounds',scope='month',month=month,event_type='ALL',metric=name,value=value,denominator=None,pct=None))
            for v in histogram:
                for name in ['all_count','positive_count']:detail('price_histogram','all','ALL','ALL',f"bin_{v['bin']}_{name}",v[name],total)
            detail('sessions','all','ALL','ALL','tokens_shared_by_multiple_users',sessions[0])
            detail('sessions','all','ALL','ALL','rows_with_shared_session_token',sessions[1],total)
            for name,value in [('min_finite_price',lo),('max_finite_price',hi),('purchase_positive_q1',q1),('purchase_positive_q3',q3),('purchase_positive_upper_3iqr',threshold)]:
                detail('price_statistics','all','ALL','purchase' if name.startswith('purchase') else 'ALL',name,value)
            detail('price_statistics','all','ALL','purchase','positive_purchase_above_3iqr',outliers,purchase['price_positive'])
            summary=[]
            def issue(name,count,denom,impact,next_step):
                summary.append(dict(issue=name,count=int(count),denominator=int(denom),pct=100*count/denom if denom else None,impact=impact,next_step=next_step))
            issue('Thiếu brand',overall['missing_brand'],total,'Diễn giải thương hiệu; không phải đầu vào 5D','P2-T3: chưa tự điền thiếu')
            issue('Thiếu category_code',overall['missing_category_code'],total,'Chưa xác minh phân cấp danh mục','P2-T3: không suy nhóm cấp cao từ ID')
            issue('Thiếu user_id',overall['missing_user_id'],total,'Không gom đúng khách cho cả năm biến','P2-T3: quy tắc định danh')
            issue('Thiếu user_session',overall['missing_user_session'],total,'Frequency và Sessions 30d; chưa mặc định loại Views','P2-T3: quy tắc phiên')
            issue('user_id sai dạng số nguyên hoặc vượt BIGINT',overall['user_id_bad_format'],total,'Khóa khách; không đưa ID vào khoảng cách','P2-T3: xác minh ID, chưa sửa')
            issue('Session không đúng dạng UUID',overall['session_bad_format'],total,'Rủi ro định dạng token, chưa phải bằng chứng event sai','P2-T3: không tự xóa')
            issue('Event dùng token session chung nhiều user',sessions[1],total,'Phải ghép user_id với session','P2-T3: không lấy riêng token làm khóa')
            for key,label in [('price_negative','Giá âm'),('price_zero','Giá bằng 0'),('price_missing','Thiếu giá'),('price_unparseable','Giá không parse được'),('price_nonfinite','Giá không hữu hạn')]:
                issue(label,overall[key],total,'Monetary và cách hiểu event','P2-T3: kiểm tra theo loại event')
            bad=sum(purchase[n] for n in ['price_missing','price_unparseable','price_nonfinite','price_negative','price_zero'])
            issue('Purchase có giá thiếu/lỗi/không dương',bad,purchase['rows'],'Buyer, Recency, Frequency và Monetary có thể đổi','P2-T3: chốt điều kiện mua hợp lệ')
            issue('Purchase dương vượt Q3 + 3 IQR',outliers,purchase['price_positive'],'Giá trị cực đoan có thể chi phối Monetary','Chỉ dấu xem xét, không tự coi là lỗi')
            for d in duplicates:
                issue(f"Dòng dư theo {d['key_fields']} trường",d['extra_rows'],total,'Views và Monetary có thể tăng khi lặp event','P2-T3: cân nhắc giả định trùng, chưa xóa')
            for name,label in [('time_unparseable','Timestamp không parse được'),('time_without_explicit_zone','Timestamp thiếu thông tin timezone'),('time_outside_observation','Timestamp ngoài observation'),('time_wrong_source_month','Timestamp không khớp tháng tệp')]:
                issue(label,overall[name],total,'Recency và cửa sổ Sessions/Views 30d','P2-T3: kiểm tra thời gian, chưa lọc')
            december_after=sha256(inputs['2019-12'])
            after={month:stat(path) for month,path in inputs.items()}
            assert before==after and december_hash==december_after
            output.mkdir(parents=True,exist_ok=False)
            write_csv(output/'quality_summary.csv',summary,['issue','count','denominator','pct','impact','next_step'])
            write_csv(output/'quality_details.csv',details,['category','scope','month','event_type','metric','value','denominator','pct'])
            plots(output,overall,[g for g in grouped if g['scope']=='event'],duplicates,histogram,prices)
            manifest={'task':'P2-T2','status':'READY FOR STUDENT REVIEW','checked_at_utc':datetime.now(timezone.utc).isoformat(),
                'command':['python','-B','scripts/assess_quality.py',*sys.argv[1:]],'code_sha256':sha256(Path(__file__)),
                'environment':{'python':sys.version,'duckdb':duckdb.__version__,'os':platform.platform(),'threads':2,'memory_limit':'768MB'},
                'inputs':[{ 'path':'raw/'+name+'.csv','month':month,**before[month]} for name,month in MONTHS.items()],
                'december_sha256_before':december_hash,'december_sha256_after':december_after,'input_metadata_unchanged':before==after,
                'total_rows':total,'rows_in_observation':overall['time_in_observation'],'duplicate_key9':COLUMNS,'duplicate_key7':KEY7,
                'duplicate_equality':'Original CSV text; empty CSV fields read as NULL; no trimming/case/numeric/time normalization; source_month not a key.',
                'counts_checked':True,'csv_errors_ignored':False,'elapsed_seconds':time.perf_counter()-started,
                'limits':['Four source CSVs fully scanned; no February or legacy Parquet event data read.',
                    'All rows in these files stay in diagnostic denominators; invalid/outside timestamps reported separately.',
                    'Duplicate rows are repeated key values, not proof of technical errors; typed-key equivalence with old ETL is not assumed.',
                    'Positive-price subset and 3-IQR flag are diagnostic comparisons, not accepted cleaning policies.',
                    'Local SHA256 stability does not authenticate the publisher or acquisition history.',
                    'Elapsed time is for this assessment, not a model benchmark; RSS not measured; engine memory_limit is not a hard RSS cap.']}
            (output/'run_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
            print(json.dumps({'status':manifest['status'],'total_rows':total,'duplicates':duplicates,'shared_session_tokens':sessions[0],
                'december_sha256':december_hash,'output':str(output.relative_to(PROJECT_ROOT))},ensure_ascii=False),flush=True)
        finally:
            con.close()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data-root',type=Path)
    parser.add_argument('--output',type=Path,default=Path('results/p2_t2'))
    args=parser.parse_args()
    source=(PROJECT_ROOT/args.data_root).resolve() if args.data_root else data_root()
    output=(PROJECT_ROOT/args.output).resolve()
    if not source.is_dir() or output.exists() or output==PROJECT_ROOT or not output.is_relative_to(PROJECT_ROOT) or output.is_relative_to(source) or source.is_relative_to(output):
        parser.error('Use an existing data root and a new output folder inside MVP, outside source data.')
    assess(source,output)


if __name__=='__main__':
    main()

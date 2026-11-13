"""Small calculation examples for the quality script, not REES46 research data."""
import sys
import csv
import contextlib
import io
import json
import tempfile
from pathlib import Path
import unittest

import duckdb

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from assess_quality import COLUMNS, MONTHS, PROJECT_ROOT, assess, prepare_checks, grouped_quality, duplicate_counts


class QualityTests(unittest.TestCase):
    def setUp(self):
        self.con=duckdb.connect(':memory:')
        self.con.execute("SET TimeZone='UTC'")
        self.con.execute('CREATE TABLE raw(source_month VARCHAR,'+','.join(c+' VARCHAR' for c in COLUMNS)+')')

    def tearDown(self):
        self.con.close()

    def row(self,**changes):
        values=dict(source_month='2019-10',event_time='2019-10-01 00:00:00 UTC',event_type='view',
            product_id='1',category_id='2',category_code=None,brand='A',price='1.25',user_id='11',
            user_session='aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee')
        values.update(changes)
        return [values[n] for n in ['source_month',*COLUMNS]]

    def load(self,rows):
        self.con.executemany('INSERT INTO raw VALUES ('+','.join('?' for _ in range(10))+')',rows)
        prepare_checks(self.con)
        return grouped_quality(self.con)

    def test_duplicate_7_9_and_row_conservation(self):
        self.load([self.row(),self.row(),self.row(brand='B'),self.row(event_type='purchase',price='0'),self.row(event_type='purchase',price='-1')])
        a,b=duplicate_counts(self.con)
        self.assertEqual((a['total_rows'],a['unique_keys'],a['extra_rows'],a['rows_in_duplicate_groups']),(5,4,1,2))
        self.assertEqual((b['total_rows'],b['unique_keys'],b['extra_rows'],b['rows_in_duplicate_groups']),(5,3,2,3))
        self.assertEqual((a['extra_view_rows'],b['extra_view_rows']),(1,2))

    def test_price_categories_are_disjoint(self):
        overall=next(g for g in self.load([self.row(price=p) for p in ['1.25','0','-2',None,'bad','NaN']]) if g['scope']=='all')
        for metric in ['price_positive','price_zero','price_negative','price_missing','price_unparseable','price_nonfinite']:
            self.assertEqual(overall[metric],1,metric)

    def test_time_offset_cutoff_and_missing_zone(self):
        times=['2019-10-01 00:00:00 UTC','2020-02-01 00:00:00 UTC','2019-10-01 00:30:00+07:00','2019-10-01 00:00:00','bad',None]
        overall=next(g for g in self.load([self.row(event_time=t) for t in times]) if g['scope']=='all')
        self.assertEqual([overall[n] for n in ['time_in_observation','time_outside_observation','time_unparseable','time_missing']],[2,2,1,1])
        self.assertEqual(overall['time_without_explicit_zone'],2)
        self.assertEqual(overall['time_wrong_source_month'],2)

    def test_missing_by_month_and_event_and_bad_ids(self):
        grouped=self.load([self.row(),self.row(brand=None,user_id='bad',user_session='bad'),self.row(source_month='2020-01',event_type='purchase',brand=' ',category_code=' ')])
        overall=next(g for g in grouped if g['scope']=='all')
        jan=next(g for g in grouped if g['scope']=='month_event' and g['month']=='2020-01')
        self.assertEqual((overall['rows'],overall['missing_brand'],overall['missing_category_code']),(3,2,3))
        self.assertEqual((overall['user_id_bad_format'],overall['session_bad_format']),(1,1))
        self.assertEqual((jan['rows'],jan['missing_brand']),(1,1))

    def test_full_export_on_private_software_fixture(self):
        scratch=PROJECT_ROOT/'.tmp'
        with tempfile.TemporaryDirectory(prefix='quality-test-',dir=scratch) as temp:
            temp=Path(temp).resolve()
            self.assertTrue(temp.is_relative_to(scratch.resolve()))
            data=temp/'data';(data/'raw').mkdir(parents=True)
            before={}
            for name,month in MONTHS.items():
                path=data/'raw'/(name+'.csv')
                with path.open('w',encoding='utf-8',newline='') as f:
                    w=csv.writer(f);w.writerow(COLUMNS)
                    for kind,price in [('view','1'),('purchase','2')]:
                        w.writerow(self.row(event_time=month+'-01 00:00:00 UTC',event_type=kind,price=price)[1:])
                before[path]=path.read_bytes()
            out=temp/'output'
            with contextlib.redirect_stdout(io.StringIO()):assess(data,out)
            manifest=json.loads((out/'run_manifest.json').read_text(encoding='utf-8'))
            self.assertEqual(manifest['total_rows'],8)
            self.assertEqual(manifest['december_sha256_before'],manifest['december_sha256_after'])
            self.assertEqual(len(list((out/'figures').glob('*.png'))),4)
            self.assertTrue(all(path.read_bytes()==content for path,content in before.items()))


if __name__=='__main__':
    unittest.main()

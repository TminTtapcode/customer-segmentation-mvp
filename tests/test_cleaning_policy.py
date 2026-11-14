"""Small private fixtures verify policy; these are not research observations."""
from decimal import Decimal
from pathlib import Path
import sys
import tempfile
import unittest

import duckdb

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from check_cleaning_policy import COLUMNS, VALID_PURCHASE, metrics, prepare_policy

TOKEN='aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee'


def event(**changes):
    row=dict(zip(COLUMNS,['2020-01-20 00:00:00 UTC','purchase','1','10',None,None,'1.20','1',TOKEN]))
    row.update(changes)
    return tuple(row[c] for c in COLUMNS)


class PolicyTests(unittest.TestCase):
    def setUp(self):
        self.con=duckdb.connect()
        self.con.execute("SET TimeZone='UTC'")
        self.con.execute('CREATE TABLE raw('+','.join(c+' VARCHAR' for c in COLUMNS)+')')

    def tearDown(self):
        self.con.close()

    def load(self,rows):
        self.con.executemany('INSERT INTO raw VALUES ('+','.join('?' for _ in COLUMNS)+')',rows)
        prepare_policy(self.con)

    def test_dedup_before_projection_preserves_products_categories_and_brand(self):
        self.load([event(),event(),event(product_id='2'),event(category_id='11'),event(brand='A')])
        self.assertEqual(self.con.execute('SELECT sum(n),count(*) FROM dedup').fetchone(),(5,4))
        self.assertEqual(self.con.execute('SELECT count(*) FROM events_dedup').fetchone()[0],4)
        self.assertEqual(self.con.execute('SELECT count(*) FROM (SELECT DISTINCT * FROM events_dedup)').fetchone()[0],1)

    def test_price_eligibility_and_shared_session_composite_key(self):
        self.load([event(price='0.10'),event(product_id='2',price='0.20'),
                   event(price='-1',event_time='2020-01-31 00:00:00 UTC'),
                   event(user_id='2',price='0'),event(user_id='3',price='2'),
                   event(user_id='4',price='3',user_session=None),
                   event(event_type='view',user_session=None,price=None)])
        got=metrics(self.con,'events_dedup')
        self.assertEqual(got['event_rows'],7)
        self.assertEqual(got['eligible_buyers'],2)
        self.assertEqual(got['purchase_sessions'],2)
        self.assertEqual(got['purchase_price_sum'],Decimal('2.30'))
        self.assertEqual(got['views_30d_without_session'],1)
        self.assertEqual(got['sessions_30d_all_users'],3)
        last=self.con.execute(f"SELECT cast(max(event_time) FILTER(WHERE {VALID_PURCHASE}) AS VARCHAR) FROM events_dedup WHERE user_id=1").fetchone()[0]
        self.assertTrue(last.startswith('2020-01-20'))

    def test_exclusive_rejections_timezone_cutoff_and_window(self):
        self.load([event(event_time='2020-02-01 00:00:00 UTC',user_id=None),
                   event(event_time='2020-01-01 00:00:00'),event(user_id='1.25'),
                   event(event_type='unexpected'),event(event_type='view',event_time='2020-01-02 01:00:00+01:00'),
                   event(event_type='view',event_time='2020-01-02 00:59:59+01:00')])
        reasons=dict(self.con.execute('SELECT reason,count(*) FROM typed_dedup GROUP BY reason').fetchall())
        self.assertEqual(reasons,dict(outside_observation=1,invalid_timestamp=1,invalid_user=1,unknown_event_type=1,kept=2))
        self.assertEqual(metrics(self.con,'events_dedup')['views_30d_all_users'],1)

    def test_precision_guard_refuses_silent_rounding(self):
        self.con.execute('INSERT INTO raw VALUES ('+','.join('?' for _ in COLUMNS)+')',event(price='0.005'))
        with self.assertRaisesRegex(ValueError,'precision policy'):
            prepare_policy(self.con)

    def test_parquet_schema_projection_and_no_second_dedup(self):
        self.load([event(),event(product_id='2'),event(event_type='view',user_session='bad-token')])
        with tempfile.TemporaryDirectory() as temp:
            path=str(Path(temp)/'fixture.parquet')
            self.con.execute('COPY events_dedup TO ? (FORMAT PARQUET)',[path])
            description=self.con.execute('DESCRIBE SELECT * FROM read_parquet(?)',[path]).fetchall()
            self.assertEqual([(r[0],r[1]) for r in description],
                             [('event_time','TIMESTAMP WITH TIME ZONE'),('event_type','VARCHAR'),
                              ('user_id','BIGINT'),('user_session','VARCHAR'),('price','DECIMAL(18,2)')])
            self.assertEqual(self.con.execute('SELECT count(*) FROM read_parquet(?)',[path]).fetchone()[0],3)
            plan=self.con.execute("EXPLAIN SELECT event_time,user_id FROM read_parquet(?)",[path]).fetchone()[1]
            self.assertIn('Projections:',plan)
            self.assertNotIn('user_session',plan)


if __name__=='__main__':
    unittest.main()

"""Small software fixtures only, never substitute data for REES46 research."""
import csv
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/"scripts"))
import inspect_schema as schema
import duckdb


class InspectSchemaTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.con = duckdb.connect(":memory:")

    def tearDown(self):
        self.con.close()
        self.temp.cleanup()

    def csv_file(self, rows):
        path = self.root/"sample.csv"
        with path.open("w",encoding="utf-8",newline="") as f:
            writer=csv.writer(f); writer.writerow(schema.RAW_COLUMNS); writer.writerows(rows)
        return path

    def row(self, user="123456789123", time="2019-10-01 00:00:00 UTC"):
        return [time,"view","123","456","","brand-example","1.25",user,"aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"]

    def test_bound_and_source_unchanged(self):
        path=self.csv_file([self.row(), self.row(), ["wrong width beyond limit"]])
        before=path.read_bytes(); meta=schema.file_metadata(path)
        result=schema.inspect_csv(path,self.con,2,True)
        self.assertEqual(result["sample_rows_read"],2)
        self.assertEqual(result["sample_rows_with_wrong_width"],0)
        self.assertEqual(path.read_bytes(),before)
        self.assertEqual(schema.file_metadata(path),meta)

    def test_types_all_empty_and_identifier_privacy(self):
        result=schema.inspect_csv(self.csv_file([self.row()]),self.con,1,True)
        columns={c["name"]:c for c in result["columns"]}
        self.assertEqual(columns["category_code"]["sample_inferred_type"],"UNDETERMINED")
        self.assertEqual(columns["user_id"]["sample_inferred_type"],"BIGINT")
        self.assertEqual(columns["price"]["sample_inferred_type"],"DOUBLE")
        self.assertNotIn("123456789123",json.dumps(result))
        self.assertNotIn("aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",json.dumps(result))

    def test_timezone_not_assumed(self):
        result=schema.time_summary(["2019-10-01 00:00:00","2019-10-01 01:00:00+01:00","bad"])
        self.assertEqual(result["without_timezone"],1)
        self.assertEqual(result["explicit_timezone"],1)
        self.assertEqual(result["parse_failures"],1)
        self.assertEqual(result["sample_min_utc"],"2019-10-01T00:00:00+00:00")

    def test_future_header_only_even_with_bad_data_row(self):
        result=schema.inspect_csv(self.csv_file([["bad-width"]]),self.con,1000,False)
        self.assertEqual(result["sample_rows_read"],0)
        self.assertEqual(result["sample_event_types"],[])
        self.assertEqual(len(result["columns"]),9)

    def test_parquet_metadata_and_reader_types(self):
        path=self.root/"fixture.parquet"
        self.con.execute("COPY (SELECT TIMESTAMP '2020-01-01' AS event_time, 1::BIGINT AS user_id) TO ? (FORMAT PARQUET)",[str(path)])
        result=schema.inspect_parquet(path,self.con)
        self.assertEqual(result["footer_rows"],1)
        self.assertEqual(result["sample_rows_read"],0)
        self.assertEqual(result["columns"][0]["duckdb_type"],"TIMESTAMP")

    def test_missing_required_raw_blocks_and_does_not_create_data(self):
        result=schema.inspect(self.root,1)
        self.assertEqual(result["status"],"BLOCKED")
        self.assertEqual(len(result["blockers"]),4)
        self.assertEqual(list(self.root.iterdir()),[])

    def test_evidence_does_not_overwrite(self):
        out=self.root/"evidence"; out.mkdir(); marker=out/"keep.txt"; marker.write_text("keep")
        with self.assertRaises(FileExistsError):
            schema.write_evidence(out,{"files":[]})
        self.assertEqual(marker.read_text(),"keep")


if __name__ == "__main__":
    unittest.main()

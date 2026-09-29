"""Tests for clean_exceptions.py. Run: python3 -m unittest -v test_clean_exceptions.py"""
import csv
import tempfile
import unittest
from pathlib import Path

import clean_exceptions as ce

HERE = Path(__file__).parent


class HappyPath(unittest.TestCase):
    """The real client file gives the answer I worked out by hand before writing code."""

    def setUp(self):
        self.cleaned, self.counts = ce.process(ce.read_csv(HERE / "exceptions_raw.csv"))
        self.by_id = {r["exception_id"]: r for r in self.cleaned}

    def test_counts_match_hand_count(self):
        self.assertEqual(dict(self.counts),
                         {"missed_pickup": 2, "doc_mismatch": 2, "carrier_substitution": 1})

    def test_nothing_lost(self):
        self.assertEqual(len(self.cleaned), 5)

    def test_all_terminals_consistent(self):
        self.assertEqual({r["terminal"] for r in self.cleaned}, {"Terminal 3"})

    def test_carriers_upper_case(self):
        self.assertEqual(self.by_id["CPX-88213"]["carrier_code"], "SWFT")
        self.assertEqual(self.by_id["CPX-88215"]["carrier_code"], "SWFT")

    def test_all_timestamps_one_format(self):
        for r in self.cleaned:
            self.assertRegex(r["event_ts"], r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$")

    def test_exactly_the_right_rows_flagged(self):
        flagged = {r["exception_id"] for r in self.cleaned if r["status"] == "FLAGGED"}
        self.assertEqual(flagged, {"CPX-88215", "CPX-88216"})
        self.assertIn("UTC", self.by_id["CPX-88215"]["issues"])
        self.assertIn("blank", self.by_id["CPX-88216"]["issues"])


class Positive(unittest.TestCase):
    """Different messy spellings all land on the same clean value."""

    def test_terminal_variants(self):
        for raw in ["T3", "t3", "Terminal 3", "TERMINAL 3", " term-3 ", "Terminal 03"]:
            self.assertEqual(ce.clean_terminal(raw), ("Terminal 3", None), raw)

    def test_carrier_variants(self):
        for raw in ["swft", "Swft", " SWFT "]:
            self.assertEqual(ce.clean_carrier(raw), ("SWFT", None), raw)

    def test_timestamp_variants_agree(self):
        for raw in ["2026-08-14 09:12:00", "2026-08-14 09:12", "08/14/2026 09:12", "2026-08-14T09:12:00"]:
            value, issues = ce.clean_timestamp(raw)
            self.assertEqual(value, "2026-08-14 09:12:00", raw)
            self.assertEqual(issues, [], raw)


class Negative(unittest.TestCase):
    """Bad data is flagged with a reason, never silently 'fixed'."""

    def test_unknown_terminal(self):
        self.assertIsNotNone(ce.clean_terminal("Terminal 9")[1])
        self.assertIsNotNone(ce.clean_terminal("Dock B")[1])

    def test_bad_carrier(self):
        self.assertIsNotNone(ce.clean_carrier("")[1])
        self.assertIsNotNone(ce.clean_carrier("SW1FT")[1])

    def test_bad_timestamps(self):
        self.assertTrue(ce.clean_timestamp("yesterday")[1])
        self.assertTrue(ce.clean_timestamp("")[1])
        self.assertTrue(ce.clean_timestamp("02/30/2026 10:00")[1])   # not a real date

    def test_ambiguous_date_is_flagged(self):
        value, issues = ce.clean_timestamp("03/04/2026 10:00")
        self.assertEqual(value, "2026-03-04 10:00:00")
        self.assertIn("ambiguous", issues[0])

    def test_unknown_or_blank_event_type(self):
        self.assertEqual(ce.clean_row({"exception_id": "X1", "terminal": "T1", "event_type": "",
                                       "carrier_code": "RLCX", "event_ts": "2026-08-14 09:00"})["event_type"], "unknown")
        row = ce.clean_row({"exception_id": "X2", "terminal": "T1", "event_type": "alien_landing",
                            "carrier_code": "RLCX", "event_ts": "2026-08-14 09:00"})
        self.assertEqual(row["status"], "FLAGGED")

    def test_duplicate_ids_flagged(self):
        row = {"exception_id": "X1", "terminal": "T1", "event_type": "missed_pickup",
               "carrier_code": "RLCX", "event_ts": "2026-08-14 09:00"}
        cleaned, counts = ce.process([row, dict(row)])
        self.assertTrue(all("duplicate" in r["issues"] for r in cleaned))
        self.assertEqual(counts["missed_pickup"], 2)   # still counted, but visibly flagged

    def test_missing_column_is_a_clear_error(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "bad.csv"
            p.write_text("exception_id,terminal\nX1,T1\n")
            with self.assertRaisesRegex(ValueError, "missing required column"):
                ce.read_csv(p)

    def test_empty_file_with_header(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "empty.csv"
            p.write_text(",".join(ce.REQUIRED_COLUMNS) + "\n")
            cleaned, counts = ce.process(ce.read_csv(p))
            self.assertEqual((cleaned, sum(counts.values())), ([], 0))
            self.assertIn("Rows in: 0", ce.write_outputs(cleaned, counts, Path(d) / "out"))


class EndToEnd(unittest.TestCase):
    """Running the script as a user would writes both output files."""

    def test_cli_writes_files(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(ce.main(["x", str(HERE / "exceptions_raw.csv"), d]), 0)
            with open(Path(d) / "exceptions_clean.csv") as f:
                self.assertEqual(len(list(csv.DictReader(f))), 5)
            self.assertIn("Flagged: 2", (Path(d) / "summary.md").read_text())

    def test_cli_missing_file(self):
        self.assertEqual(ce.main(["x", "does_not_exist.csv"]), 1)



DATA = HERE / "test_data"


def run(name):
    cleaned, counts = ce.process(ce.read_csv(DATA / name))
    flagged = [r for r in cleaned if r["status"] == "FLAGGED"]
    return cleaned, counts, flagged


class PositiveFile(unittest.TestCase):
    """test_data/positive.csv: messy but fixable, so every row should be CLEAN."""

    def test_all_clean(self):
        cleaned, counts, flagged = run("positive.csv")
        self.assertEqual(len(cleaned), 7)
        self.assertEqual(flagged, [], [r["issues"] for r in flagged])
        self.assertEqual(dict(counts), {"missed_pickup": 3, "doc_mismatch": 2, "carrier_substitution": 2})

    def test_values_normalised(self):
        cleaned, _, _ = run("positive.csv")
        by_id = {r["exception_id"]: r for r in cleaned}
        self.assertEqual(by_id["P-004"]["terminal"], "Terminal 1")
        self.assertEqual(by_id["P-004"]["carrier_code"], "UPSN")
        self.assertEqual(by_id["P-005"]["event_ts"], "2026-08-20 17:45:30")
        self.assertEqual(by_id["P-007"]["event_type"], "missed_pickup")


class NegativeFile(unittest.TestCase):
    """test_data/negative.csv: every row is broken, so every row must be FLAGGED with a reason."""

    def test_every_row_flagged_with_reason(self):
        cleaned, counts, flagged = run("negative.csv")
        self.assertEqual(len(cleaned), 12)
        self.assertEqual(len(flagged), 12)
        self.assertTrue(all(r["issues"] for r in flagged))
        self.assertEqual(sum(counts.values()), 12)   # nothing dropped

    def test_reasons_are_specific(self):
        cleaned, _, _ = run("negative.csv")
        by_id = {r["exception_id"]: r["issues"] for r in cleaned}
        expected = {"N-001": "not one of", "N-002": "not recognised", "N-003": "terminal is blank",
                    "N-004": "blank", "N-005": "2-4 letter", "N-006": "2-4 letter",
                    "N-007": "unknown format", "N-008": "event_ts is blank", "N-009": "not a real date",
                    "N-010": "not a known exception type", "N-011": "event_type is blank",
                    "": "exception_id is blank"}
        for row_id, phrase in expected.items():
            self.assertIn(phrase, by_id[row_id], row_id)


class EdgeCaseFile(unittest.TestCase):
    """test_data/edge_cases.csv: boundaries where a naive script would quietly get it wrong."""

    def test_exact_flags(self):
        cleaned, counts, flagged = run("edge_cases.csv")
        self.assertEqual(len(cleaned), 11)
        self.assertEqual(sorted(r["exception_id"] for r in flagged),
                         ["E-001", "E-003", "E-004", "E-004", "E-007", "E-010"])
        self.assertEqual(dict(counts), {"missed_pickup": 5, "doc_mismatch": 4, "carrier_substitution": 2})

    def test_boundary_values(self):
        cleaned, _, _ = run("edge_cases.csv")
        by_id = {r["exception_id"]: r for r in cleaned}
        self.assertEqual(by_id["E-002"]["status"], "CLEAN")                  # 04/04 is not ambiguous
        self.assertEqual(by_id["E-005"]["event_ts"], "2028-02-29 10:00:00")  # leap day
        self.assertEqual(by_id["E-009"]["carrier_code"], "SWFT")             # whitespace trimmed
        self.assertEqual(by_id["E-009"]["status"], "CLEAN")

if __name__ == "__main__":
    unittest.main(verbosity=2)

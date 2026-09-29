# Test data

Built from the shape of the client's export (`../exceptions_raw.csv`). Each file has a known expected result, checked in `../test_clean_exceptions.py`.

| File | Purpose | Rows | Expected |
|---|---|---|---|
| `positive.csv` | Messy but fixable: every row should come out CLEAN | 7 | 7 clean, 0 flagged. missed_pickup 3, doc_mismatch 2, carrier_substitution 2 |
| `negative.csv` | Broken data: every row must be FLAGGED with a reason, never "fixed" | 12 | 0 clean, 12 flagged |
| `edge_cases.csv` | Tricky boundaries | 11 | 5 clean, 6 flagged |

## Edge cases explained

| Row | Input | Expected | Why |
|---|---|---|---|
| E-001 | `03/04/2026` | FLAGGED | March 4 or April 3? Can't tell |
| E-002 | `04/04/2026` | CLEAN | Same either way, so no ambiguity |
| E-003 | `...T10:03:00Z` | FLAGGED | UTC, but other rows have no timezone |
| E-004 (x2) | Same ID twice | FLAGGED (both) | Duplicate exception, same risk as Priya's double-push |
| E-005 | `02/29/2028` | CLEAN | Real leap-year date |
| E-006 | `12/31/2026 23:59` | CLEAN | Year-end boundary |
| E-007 | `SW FT` | FLAGGED | Space inside carrier code |
| E-008 | Normal row | CLEAN | Control row |
| E-009 | Extra spaces everywhere | CLEAN | Whitespace is trimmed |
| E-010 | `+05:30` offset | FLAGGED | Unknown timestamp format: don't guess the timezone |

# Exception summary

Rows in: 5 | Clean: 3 | Flagged: 2

| Event type | Count |
|---|---|
| doc_mismatch | 2 |
| missed_pickup | 2 |
| carrier_substitution | 1 |

## Records I could not confidently clean

- **CPX-88215**: timestamp is in UTC ('Z') but other rows have no timezone; need the terminal's local timezone before times can be compared
- **CPX-88216**: carrier_code is blank; can't tell which carrier this is

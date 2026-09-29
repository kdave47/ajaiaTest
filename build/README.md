# Exception cleaner (Task 2)

Cleans Corrigan Peak's exception export and counts exceptions by event type. Python 3, standard library only.

## Run
```
python3 clean_exceptions.py exceptions_raw.csv      # writes output/exceptions_clean.csv and output/summary.md
python3 -m unittest -v test_clean_exceptions.py     # 25 tests: happy path, positive, negative, edge cases, end-to-end
```

## Files
- `clean_exceptions.py` - the script
- `test_clean_exceptions.py` - tests
- `exceptions_raw.csv` - the export exactly as the client sent it
- `test_data/` - positive, negative and edge-case files with expected results
- `output/` - cleaned CSV (with a status + reason per row) and summary

Part of the Ajaia TPM assessment - https://ajaia.ai

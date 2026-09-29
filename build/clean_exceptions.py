"""
Clean the Corrigan Peak exception export and summarise it by event type.

Usage:
    python3 clean_exceptions.py exceptions_raw.csv [output_dir]

What it does, per row:
  1. terminal     -> "Terminal N"             ("T3", "term 3", "Terminal 3" all become "Terminal 3")
  2. carrier_code -> upper-case code           ("swft", "Swft" -> "SWFT"); blank or odd codes are flagged
  3. event_ts     -> "YYYY-MM-DD HH:MM:SS"     (several input formats accepted)
  4. anything we can't clean *confidently* is kept, marked FLAGGED, and the reason is written down.

Rule of thumb: never guess silently. If a fix needs an assumption, flag it.
"""
import csv
import re
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

REQUIRED_COLUMNS = ["exception_id", "terminal", "event_type", "carrier_code", "event_ts"]
KNOWN_TERMINALS = {"1", "2", "3"}              # Corrigan Peak runs three terminals
KNOWN_EVENT_TYPES = {"missed_pickup", "doc_mismatch", "carrier_substitution"}
CARRIER_PATTERN = re.compile(r"^[A-Z]{2,4}$")  # carrier codes (SCAC) are 2-4 letters
TERMINAL_PATTERN = re.compile(r"^(?:t|term|terminal)[\s\-_]*(\d+)$", re.IGNORECASE)
OUT_TS = "%Y-%m-%d %H:%M:%S"


def clean_terminal(raw):
    """Return (value, issue). issue is None when clean."""
    if not (raw or "").strip():
        return "", "terminal is blank"
    match = TERMINAL_PATTERN.match((raw or "").strip())
    if not match:
        return (raw or "").strip(), f"terminal '{raw}' not recognised"
    number = str(int(match.group(1)))
    if number not in KNOWN_TERMINALS:
        return f"Terminal {number}", f"terminal {number} is not one of Corrigan Peak's three terminals"
    return f"Terminal {number}", None


def clean_carrier(raw):
    value = (raw or "").strip().upper()
    if not value:
        return "", "carrier_code is blank; can't tell which carrier this is"
    if not CARRIER_PATTERN.match(value):
        return value, f"carrier_code '{raw}' doesn't look like a 2-4 letter carrier code"
    return value, None


def clean_timestamp(raw):
    """Return (value, issues list). Accepts ISO, ISO with Z, and US-style MM/DD/YYYY."""
    text = (raw or "").strip()
    issues = []
    if not text:
        return "", ["event_ts is blank"]

    # ISO with a trailing Z means UTC. Every other row has no timezone at all.
    if text.endswith("Z"):
        try:
            parsed = datetime.strptime(text, "%Y-%m-%dT%H:%M:%SZ")
        except ValueError:
            return text, [f"event_ts '{text}' could not be parsed"]
        issues.append("timestamp is in UTC ('Z') but other rows have no timezone; "
                      "need the terminal's local timezone before times can be compared")
        return parsed.strftime(OUT_TS), issues

    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%dT%H:%M:%S"):
        try:
            return datetime.strptime(text, fmt).strftime(OUT_TS), issues
        except ValueError:
            pass

    # Slash dates: assume US MM/DD/YYYY, but flag it if the day could also be a month.
    slash = re.match(r"^(\d{1,2})/(\d{1,2})/(\d{4}) (\d{1,2}):(\d{2})(?::(\d{2}))?$", text)
    if slash:
        first, second = int(slash.group(1)), int(slash.group(2))
        try:
            parsed = datetime(int(slash.group(3)), first, second,
                              int(slash.group(4)), int(slash.group(5)), int(slash.group(6) or 0))
        except ValueError:
            return text, [f"event_ts '{text}' is not a real date"]
        if first <= 12 and second <= 12 and first != second:
            issues.append(f"event_ts '{text}' is ambiguous (MM/DD or DD/MM?); read as MM/DD")
        return parsed.strftime(OUT_TS), issues

    return text, [f"event_ts '{text}' is in an unknown format"]


def clean_row(row):
    issues = []
    terminal, issue = clean_terminal(row.get("terminal"))
    if issue:
        issues.append(issue)
    carrier, issue = clean_carrier(row.get("carrier_code"))
    if issue:
        issues.append(issue)
    event_ts, ts_issues = clean_timestamp(row.get("event_ts"))
    issues.extend(ts_issues)

    event_type = (row.get("event_type") or "").strip().lower()
    if not event_type:
        issues.append("event_type is blank")
        event_type = "unknown"
    elif event_type not in KNOWN_EVENT_TYPES:
        issues.append(f"event_type '{event_type}' is not a known exception type")

    exception_id = (row.get("exception_id") or "").strip()
    if not exception_id:
        issues.append("exception_id is blank")

    return {
        "exception_id": exception_id,
        "terminal": terminal,
        "event_type": event_type,
        "carrier_code": carrier,
        "event_ts": event_ts,
        "status": "FLAGGED" if issues else "CLEAN",
        "issues": "; ".join(issues),
    }


def process(rows):
    """Clean every row, catch duplicate IDs, and count by event type."""
    cleaned = [clean_row(r) for r in rows]
    id_counts = Counter(r["exception_id"] for r in cleaned if r["exception_id"])
    for r in cleaned:
        if id_counts.get(r["exception_id"], 0) > 1:
            note = "duplicate exception_id (appears more than once in the export)"
            r["issues"] = "; ".join(filter(None, [r["issues"], note]))
            r["status"] = "FLAGGED"
    counts = Counter(r["event_type"] for r in cleaned)

    # Self-check: nothing lost, nothing invented.
    assert sum(counts.values()) == len(rows), "row count mismatch between input and summary"
    return cleaned, counts


def read_csv(path):
    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        missing = [c for c in REQUIRED_COLUMNS if c not in (reader.fieldnames or [])]
        if missing:
            raise ValueError(f"input is missing required column(s): {', '.join(missing)}")
        return list(reader)


def write_outputs(cleaned, counts, out_dir):
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    with open(out_dir / "exceptions_clean.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(cleaned[0].keys()) if cleaned
                                else REQUIRED_COLUMNS + ["status", "issues"])
        writer.writeheader()
        writer.writerows(cleaned)

    flagged = [r for r in cleaned if r["status"] == "FLAGGED"]
    lines = ["# Exception summary", "",
             f"Rows in: {len(cleaned)} | Clean: {len(cleaned) - len(flagged)} | Flagged: {len(flagged)}", "",
             "| Event type | Count |", "|---|---|"]
    lines += [f"| {k} | {v} |" for k, v in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))]
    lines += ["", "## Records I could not confidently clean", ""]
    lines += [f"- **{r['exception_id'] or '(no id)'}**: {r['issues']}" for r in flagged] or ["- None"]
    summary = "\n".join(lines) + "\n"
    (out_dir / "summary.md").write_text(summary)
    return summary


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 1
    out_dir = argv[2] if len(argv) > 2 else Path(argv[1]).parent / "output"
    try:
        rows = read_csv(argv[1])
    except (OSError, ValueError) as err:
        print(f"ERROR: {err}")
        return 1
    cleaned, counts = process(rows)
    print(write_outputs(cleaned, counts, out_dir))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

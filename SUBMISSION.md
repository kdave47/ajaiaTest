# Ajaia – Technical Project Manager Assessment

**Video walkthrough:** <VIDEO_LINK>
**Candidate:** Krunal Dave · krunal.dave88@gmail.com
**Build file:** [`build/`](./build) · **Repo:** https://github.com/kdave47/ajaiaTest
**Engagement:** Ajaia – https://ajaia.ai
**Optional public work:** <GITHUB / PORTFOLIO – or leave blank>

---

## Task 1 - Triage

We have one engineer (Priya) and about three weeks to a date Dana has already given her board. So I ranked these by one question: what hurts the product most if we ignore it? Then by how soon it bites.

| Rank | Item | This week | Why |
|---|---|---|---|
| 1 | **C. DET-121: Terminal 3 scores coming back null** | **Worked.** I'm emailing Dana today for her IT contact and I'll chase it myself. | This is the big one. Scoring is the whole point of the tool, and right now it doesn't work for one of three terminals. It's been sitting since 8/6, we can't fix it without Corrigan Peak, and it's two days of work once they answer. Every day we wait comes straight out of our buffer. |
| 2 | **B. Priya's retry issue (same exception pushed twice)** | **Worked.** The PR doesn't merge until an exception can only be routed once and two polls can't run at the same time. | Priya was right to flag it. If a dispatcher gets the same exception twice in week one, they stop trusting the queue. To answer her question: it's a today problem. It's cheapest to fix before merge and it's fully in our hands. |
| 3 | **D. DET-118: nobody has booked the terminal-lead review** | **Worked.** That's my job, not Priya's. I'll send the invites today. | Small task, real consequence. If the routing rules are wrong, the tool sends exceptions to the wrong people. It takes me half an hour, and it only gets harder the closer we get to launch. |
| 4 | **A. COO's request to auto-reassign carriers on a missed pickup** | **Deferred.** Not for Sept 8. I'll offer Dana a short Phase 2 scoping call. | This is the one that only looks urgent. It's a good idea, but it changes the tool from "flag it for a person" to "the system makes the call." That needs carrier rules, testing, and a way to undo it. We can't do that safely in three weeks with one engineer. I'd rather give Dana a clear "yes, next" to take back to her COO than a rushed yes that puts the date at risk. |
| 5 | **E. Marcus: a different shade of blue** | **Declined for launch.** Added to the post-launch list. | This is the noise. It was a passing comment, not a request, and it changes nothing about what the tool does. Even a quick CSS change is Priya's time, and her time goes to B and C. |

**What moves to protect Sept 8:** Terminal 3's two days come out of our buffer. The auto-reassign feature and the colour change are out of launch scope. Priya works on B and C only. If Corrigan Peak's IT hasn't answered within two business days, I'll tell Dana in writing that the date is at risk, not wait and hope.

---

## Task 2 - Build

**Files:** [`build/clean_exceptions.py`](./build/clean_exceptions.py) (script), [`build/test_clean_exceptions.py`](./build/test_clean_exceptions.py) (25 tests), [`build/test_data/`](./build/test_data) (positive, negative and edge-case files). Python 3, no extra libraries.

**Run it:**
```
cd build
python3 clean_exceptions.py exceptions_raw.csv
python3 -m unittest -v test_clean_exceptions.py
```

**Result on the client's file:**

| Event type | Count |
|---|---|
| doc_mismatch | 2 |
| missed_pickup | 2 |
| carrier_substitution | 1 |

5 rows in, 3 clean, 2 flagged:
- **CPX-88215:** the only timestamp in UTC ("Z"). The other rows have no timezone, so I can't line them up without knowing Terminal 3's local zone.
- **CPX-88216:** carrier code is blank, so there's no way to tell which carrier it was.

**What it does and how I checked it:** The script reads the export, makes terminals, carrier codes and timestamps consistent (`T3` becomes `Terminal 3`, `swft` becomes `SWFT`, every date becomes `YYYY-MM-DD HH:MM:SS`), counts exceptions by type, and writes a cleaned CSV plus a summary. The rule I built it around is "flag, don't guess": if a fix needs an assumption, the row is kept, marked FLAGGED, and the reason is written next to it. To check it actually worked and didn't just run, I counted the five rows by hand before writing any code (2 missed pickups, 2 doc mismatches, 1 carrier substitution, and the same two rows I'd expect to be unsure about), and the tests assert the script lands on exactly that. The script also checks that every input row is counted once, so nothing gets dropped quietly. Then I wrote test files in the same shape as the client's export: 7 messy-but-fixable rows that must all come out clean, 12 broken rows that must all be flagged with a specific reason, and 11 edge cases where a naive script would get it quietly wrong (`03/04` could be March or April, a leap day, a duplicate ID, a `+05:30` offset). Testing caught one thing: a blank terminal produced a confusing message, so I fixed it. The two flags on the real file point at the same Terminal 3 feed problem as DET-121, which is one more reason to get Corrigan Peak's IT contact this week.

---

## Task 3 - Client status update

**To:** Dana Okafor, VP Operations, Corrigan Peak Logistics
**Subject:** Dispatch Exception Triage: status update and correction to last week's report

Hi Dana,

I need to correct last Friday's update. We reported Green with no blockers, which did not reflect the full picture. **Current status is Amber.** The September 8 go-live remains achievable, subject to one input from your team.

| Item | Current status | Next step |
|---|---|---|
| **Terminal 3 data** | Some Terminal 3 exceptions are not receiving urgency scores because the feed sends different fields than expected. This was raised internally on 8/6 and was not actioned promptly; that is our miss. | We need your IT contact to confirm the fields. Estimated 2 days to resolve after that. |
| **Duplicate alerts** | Code review identified a case where the same exception could be routed to a dispatcher twice. It has not been released. | Fix in progress; it will be resolved before release. |
| **Terminal-lead review** | Contrary to last week's note, outreach to the terminal leads had not started. | Invitations to all three leads go out today. |
| **Auto-reassign request (from your COO)** | A valuable addition, but it moves the tool from flagging decisions to making them, which requires carrier rules and testing we cannot complete safely before September 8. | Launch as planned and scope it as Phase 2. I'm happy to join a call with you and your COO next week. |

**Action needed:** Please share your Terminal 3 IT contact **by Thursday**. If we have not heard back by then, I will follow up directly with the impact on the go-live date.

The next update will follow on Friday.

Best regards,
Krunal Dave
Technical Project Manager, Ajaia

---

## Task 4 – How I used AI

- **Where I used it:**
- **What I kept human:**
- **One thing I checked or rejected:**

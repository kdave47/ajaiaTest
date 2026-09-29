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

## Task 2 – Build

- **What it is:**
- **File:** `build/...`
- **How to run:**
- **What it does / doesn't do:**

---

## Task 3 – Correcting the status update (to client)

**Subject:**

> Draft here

---

## Task 4 – How I used AI

- **Where I used it:**
- **What I kept human:**
- **One thing I checked or rejected:**

# Session Summary — Building the STITCH MISO/ERCOT Brief

Plain-English record of what we did and why, written so you (or anyone) can
re-read it later and understand the whole thing without industry or math
background. Date: 2026-06-21. Webinar: 2026-06-23.

---

## 1. Where this started

You registered for a webinar. It's a U.S. Department of Energy program
(**i2X / STITCH**), run with **Berkeley Lab** and the nonprofit **ESIG**, that
tours the country comparing how different regions connect new power projects to
the grid. The June 23 session compares two regions: **MISO** (the Midwest) and
**ERCOT** (Texas).

You'd already touched this world: your `komposos-grid` repo pulls in data from
these grid operators. You replied to their email, and registration auto-accepted
you. You asked: *can my repo say anything useful about this webinar's topic?*

The answer turned out to be yes — because your repo already had the exact public
dataset this webinar is about.

---

## 2. What "interconnection" is (the whole topic in 3 sentences)

When someone wants to build a power plant, solar farm, or big battery, they
can't just plug it into the grid. They have to get **studied** first (will it
overload the wires? who pays for upgrades?), which takes years and money. Most
projects give up before they're ever built — and *that* slow, leaky process is
the single biggest thing holding back new power in the U.S.

The webinar is about making that process **faster and more consistent across
regions** ("harmonization").

---

## 3. What we built

A small, self-contained packet in `reports/stitch_2026-06-23/`:

| File | What it is |
|---|---|
| `queue_process_brief.html` | the shareable one-page report (open in any browser) |
| `queue_process_brief.md` / `.json` | same content as text/data |
| `PLAIN_ENGLISH_BRIEF.md` | your personal cheat-sheet (no jargon, who-cares-about-what) |
| `README.md` | the index: webinar topic → what the repo shows → the number |
| `SESSION_SUMMARY.md` | this file |

Plus two code files that generate the brief from the public data:
- `domains/grid/run_stitch_brief.py` — the new report generator
- `domains/grid/sources/lbnl_queue.py` — small additions so it can read the
  cluster/batch labels and the dates

You run it with one command and it regenerates everything:

```
python -m domains.grid.run_stitch_brief \
    --queue domains/grid/data/LBNL_Ix_Queue_Data_File_thru2026.xlsx \
    --out reports/stitch_2026-06-23
```

---

## 4. What the data actually says (the findings)

All from one public Berkeley Lab dataset ("Queued Up"), sliced to MISO and ERCOT.

**Finding 1 — Texas builds a bigger share of what's proposed.**
Of all requests from 2000–2020: MISO built ~**18%**, ERCOT built ~**30%**.

**Finding 2 — (the best one) The "green light" means different things.**
Once a project signs its connection agreement: ERCOT builds it ~**80%** of the
time, MISO only ~**35%**. Same official milestone, very different meaning by
region. *This is the fact worth remembering.*

**Finding 3 — (the myth-buster) Texas isn't actually faster end-to-end.**
ERCOT clears the study stage faster (~20 vs ~30 months), but takes longer to
build afterward, so the *total* time from request to switched-on is about the
same (~3.5–4 years either way). ERCOT's edge is **certainty**, not raw speed.

**Finding 4 — The Midwest's recent reforms are visibly weeding projects out.**
MISO groups projects into big numbered batches ("clusters") and recently
tightened the rules; the newest batches show lots of early quitting.

**Finding 5 — They don't even organize the work the same way.**
MISO uses cluster batches; ERCOT has none. They don't share a unit of work —
itself a harmonization gap.

---

## 5. The number correction — why it changed, and why that's *honest*

This is the part that confused you, so here it is carefully.

**Early in the session, the brief showed "94% vs 30%" for Finding 2.** Later it
became **"80% vs 35%."** You (rightly) asked: *isn't changing numbers
cherry-picking?*

**No — and the direction is the proof.**

- **Cherry-picking** = trying several ways to measure, and keeping the one that
  makes your story look *best*.
- **What we did** = the first number used a homemade definition that happened to
  look *more* dramatic. We checked it against **Berkeley Lab's own official
  definition**, which gave a *less* dramatic number — and we switched to theirs.

Giving up the flashier number for the standard one is the **opposite** of
cherry-picking.

**Were the old numbers fake?** No. Both were arithmetically correct; they just
answered slightly different questions:

| | The question it answered |
|---|---|
| First number (94/30) | "Of projects that signed, by one labeling shortcut, what share built?" — the shortcut quietly skipped some projects that signed and *then* quit |
| Corrected (80/35) | Berkeley Lab's method: counts the projects that signed and then withdrew too — the fuller, fairer picture |

**What "honest" means here:**
1. Use the **same ruler** the experts use (Berkeley Lab's published definition), and
2. **Say which ruler** you used (we added a "definitions" footnote).

Honest is not "numbers never change." Honest is "measure the standard way and be
upfront about it." Numbers *should* change when you discover the standard method
differs from your first guess.

**Why the gap shrank:** the homemade version left out projects still waiting and
counted a wave of recent withdrawals, which happened to push the two regions
further apart. Berkeley Lab's standard slice puts them closer. Importantly, the
**story survives either way** — ERCOT's signed projects build far more often than
MISO's. We just moved to the version no one can argue with.

---

## 6. The verification (why you can trust the numbers now)

We didn't just compute numbers — we checked them against Berkeley Lab's own
published tables inside the same file. **Your project counts match theirs
exactly** (e.g. ERCOT 459 built / 795 withdrawn; MISO 509 / 1936). That means:

- Your data pipeline is correct (not made up, not buggy).
- Any difference from their headline rate is purely a *definition* choice, not an
  error — and we resolved it by adopting their definition.

So the final brief uses Berkeley Lab's definitions **and** reproduces Berkeley
Lab's counts. It is as defensible as it can be.

---

## 7. What this is for, realistically

- You are an **attendee**, not a presenter. The bar was "register." You cleared
  it. You can show up, listen, and never say a word — that's a fine outcome.
- If a moment opens in the Q&A/chat, you have **one sentence** (in
  `PLAIN_ENGLISH_BRIEF.md`, section 7): *"after an IA is executed, ERCOT builds
  ~80% but MISO only ~35% — the milestone isn't equivalent across regions."*
- The HTML brief is a **follow-up** tool — something to link in a one-to-one
  email afterward, *not* to blast into the public chat.
- The realistic win is a warm follow-up with one person, or simply learning the
  field. Not "contribute to the national report." Anything beyond that is bonus.

---

## 8. What's deliberately NOT here (so you don't worry it's missing)

- No category theory / "OPTIMUS" / sheaf math in anything an expert sees. That
  machinery is the repo's engine; it isn't needed to read these numbers and it
  would only distract this audience. It stays in the engine room.
- No deeper data (substation-level, congestion modeling). Real but out of scope
  for an attendee, and only worth doing later if a relationship forms.

---

## 9. One-line takeaway

You took a public government dataset, analyzed it, matched the national lab's own
published numbers to the integer, and packaged one genuinely interesting,
defensible finding. That is a real, credible piece of work — and it's plenty for
walking into a webinar you're attending to learn from.

# Your Plain-English Brief — MISO vs ERCOT, in normal words

This is for **you**, written assuming you don't work in the power industry.
It explains what the webinar is about, what your repo actually found, what each
number means in human terms, and who in the room will care about what. No math,
no jargon. (If anyone asks "how did you compute this?" there's a one-paragraph
answer at the very bottom.)

---

## 1. The 30-second version

When someone wants to build a new power plant, solar farm, or big battery, they
can't just plug it into the grid. They have to get **studied** first (will this
overload the wires? who pays to upgrade them?). That study process is slow,
expensive, and **most projects give up before they're ever built.**

This webinar is a meeting of grid experts comparing **how two regions run that
study process**: **MISO** (the Midwest) and **ERCOT** (Texas). Your repo
already had the public data on this and produced a clean comparison of the two.
The headline your repo found:

> **In Texas (ERCOT), a bigger share of proposed projects actually get built
> than in the Midwest (MISO) — and once a Texas project signs its connection
> contract, it usually gets built (about 80% of the time). In the Midwest, even
> after signing, most still quit (only about 35% get built). But oddly, the
> total time from "I want to connect" to "it's running" is about the same in
> both. So ERCOT's advantage isn't raw speed — it's certainty.**

That one paragraph is the whole thing. Everything below is detail and proof.

---

## 2. The words you need (and nothing more)

- **The grid** — the network of wires that moves electricity around.
- **Interconnection** — the process of plugging a new power project into that
  network. The whole webinar is about this one word.
- **The queue** — the waiting line of projects that want to connect. Like a
  DMV line, but it takes *years* and you pay as you go.
- **A study** — the engineering homework done on each project: will it cause
  problems, and what wires need upgrading (and who pays).
- **IA = Interconnection Agreement** — the signed contract that says "OK, you're
  cleared to connect." Think of it as getting the green light.
- **COD = Commercial Operation Date** — the day the project actually turns on.
- **IR = Interconnection Request** — the day a project got in line.
- **Completion** — did the project actually get built and turn on (vs. give up)?
- **MISO** and **ERCOT** — two big regional grid operators. MISO runs the
  Midwest; ERCOT runs Texas. They do interconnection *very differently*, which
  is exactly why this webinar pairs them.
- **i2X / STITCH** — the U.S. Department of Energy program (run with a research
  lab, Berkeley Lab, and the nonprofit ESIG) that's touring the country trying
  to figure out how to make this whole process faster and more consistent. The
  webinar is one stop on that tour. STITCH = "Studies, Tools, and
  Interconnection Consistency and Harmonization."

That's it. If you know those, you can follow the entire discussion.

---

## 3. The 5 W's and the H — of this whole situation

**WHO** is involved:
- *The grid operators*: MISO and ERCOT — the referees who run the study process.
- *The developers*: companies like **Engie** (presenting) who actually build the
  projects and live or die by how fast/predictable the process is.
- *The organizers*: the **DOE** (government), **Berkeley Lab** (researchers), and
  **ESIG** (industry nonprofit) — they're writing a report on how to fix things.
- *You*: an independent person who analyzed the public data and happened to land
  on exactly their topic.

**WHAT** is being discussed: the *differences* between how MISO and ERCOT study
and approve new projects — and where those differences could be **harmonized**
(made more consistent across the country) to speed things up.

**WHERE**: a virtual webinar (online).

**WHEN**: June 23, 2026. It's one session in a longer series.

**WHY** it matters: the U.S. wants to add huge amounts of new power (solar,
batteries, gas) fast. The #1 thing slowing that down is **not** building the
projects — it's this study/approval queue. Most proposed power never gets built
because the process is too slow and uncertain. That's a national problem worth
billions and years.

**HOW** they'll discuss it: each region presents how its process works, then a
developer (Engie) says what it's like on the receiving end, then open
discussion about what could be made consistent.

---

## 4. What your repo actually found — fact by fact, in plain terms

These are all from the same public Berkeley Lab dataset, sliced to the two
regions. Each one is a real, defensible number.

> **Note on the numbers:** every figure below uses *Berkeley Lab's own
> definitions*, and the project counts behind them match Berkeley Lab's
> published tables exactly. That's deliberate — so nobody can say you picked
> favorable math. If anyone checks, your numbers and theirs are the same.

### Fact 1 — Texas builds a bigger share of what's proposed.
- Of MISO requests (2000–2020), **18%** are built.
- Of ERCOT requests (2000–2020), **30%** are built.
- **Plain meaning:** in the Midwest, fewer than 1 in 5 proposed projects gets
  built; in Texas it's closer to 1 in 3. Texas's process lets more projects
  through. (These are Berkeley Lab's own published completion rates.)

### Fact 2 (the most interesting one) — In Texas, the green light means something. In the Midwest, it often doesn't.
- ERCOT projects that signed their connection agreement: about **80%** got built.
- MISO projects that signed their agreement: only about **35%** got built.
- **Plain meaning:** in Texas, once you're cleared to connect, you usually do.
  In the Midwest, about **two-thirds quit even after getting cleared.** So the
  same "green light" is close to a promise in one region and closer to a
  coin-flip in the other. That inconsistency — the same official step meaning
  very different things in different places — is exactly what the "harmonization"
  report is hunting for. **This is your single best fact.**

### Fact 3 (the myth-buster) — Texas isn't actually faster overall.
- Time to get *cleared* (the study stage): MISO ~**30 months**, ERCOT ~**20
  months**. Texas is faster *here*.
- Time to *build* after clearing: MISO ~**19 months**, ERCOT ~**26 months**.
  Texas is *slower* here.
- Total time, request to switched-on: MISO ~**39 months**, ERCOT ~**44 months**
  — basically **a tie** (~3.5–4 years either way).
- **Plain meaning:** "Texas is just faster" is too simple. Texas is faster and
  more certain at the *approval* stage, but the total clock to actually turn on
  is about the same. ERCOT's real edge is **certainty and a faster green light**,
  not raw end-to-end speed. Saying this out loud signals you actually understand
  the data, not just the headline.

### Fact 4 — The Midwest's recent reforms are visibly weeding projects out.
- MISO's older project batches built better; recent batches show **huge numbers
  of projects quitting early** (one recent 2022 batch already had 522 of 911
  projects drop out).
- **Plain meaning:** MISO recently tightened its rules to scare off non-serious
  projects sooner. The data shows that's happening — lots of early quitting in
  the new batches. Whether that's "good winnowing" or "good projects giving up"
  is genuinely the open question, and a fair thing to raise.

### Fact 5 — The two regions don't even organize the work the same way.
- MISO groups projects into big numbered **batches ("clusters")** and studies
  them together. ERCOT **doesn't do this at all** — it has no cluster batches.
- **Plain meaning:** they're so different that they don't even share the same
  unit of work. That's a real harmonization gap before you even get to numbers.

---

## 5. Who in the room wants which fact (so you can aim it)

- **MISO staff** → care most about **Fact 2 and Fact 4**. "Why do so many of our
  projects quit even after we clear them, and are our new rules helping?" is
  their live question.
- **ERCOT staff** → like **Fact 1 and 2** (makes them look good) but should hear
  **Fact 3** (the total-time tie keeps it honest and shows you're not a fanboy).
- **The developer (Engie)** → cares most about **Fact 2 (certainty)**. An ~80%
  vs ~35% build-after-signing gap tells them where their money is safer.
  Predictability is everything to a builder.
- **DOE / Berkeley Lab / ESIG (the report writers)** → care about **Fact 2 and
  Fact 5** — the "same step means different things across regions" and "they
  don't even share a unit of work." That's literally what their harmonization
  report is about. This is your best material for them.

---

## 6. Honest caveats (say these — they build trust, they don't weaken you)

- These rates count only projects that reached a **final answer** (built or quit).
  Projects still waiting in line aren't counted as failures.
- The "time to build after clearing" numbers only include projects that **did**
  finish, so they describe the winners, not everyone.
- **A big chunk of this — completion rates, time durations — Berkeley Lab itself
  already publishes.** Don't walk in claiming you discovered it. Your genuinely
  fresh angles are **Fact 2** (the green-light-means-different-things point) and
  **Fact 3** (the study-stage-vs-total-time split). Lead with those.

---

## 7. How to actually use this

- **In the chat / Q&A:** if it fits, one line — *"Looking at the LBNL data, the
  thing that jumped out is that an executed IA predicts completion ~80% in ERCOT
  but only ~35% in MISO — the milestone isn't equivalent across regions."* That's
  a credible, on-topic contribution.
- **In a follow-up email (the icebreaker):** open with that same fact, offer to
  share the one-page brief, and ask if it's useful for their report. Don't pitch
  your software. Let the analysis do the talking.
- **The shareable file:** `queue_process_brief.html` in this folder — opens in any
  browser, no setup. That's the thing you attach or link.

---

## 8. If someone asks "how did you get these numbers?" (the only technical bit)

You took **Berkeley Lab's public "Queued Up" dataset** (it tracks essentially
every U.S. interconnection request and whether it got built or quit), filtered it
to MISO and ERCOT, counted the build-vs-quit outcomes, and measured the months
between the dates each project recorded (got in line → cleared → turned on).
Nothing exotic — careful counting of a public dataset, with the projects still
waiting left out so they don't get mislabeled as failures. The math machinery in
the rest of the repo isn't needed to read any of these numbers.

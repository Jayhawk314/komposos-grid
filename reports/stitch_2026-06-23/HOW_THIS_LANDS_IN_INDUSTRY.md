# How a System Like This Lands in the Grid Industry

A plain-English guide to the real question: *not* "is the work good?" but
"how does work like this earn trust with grid companies, engineers, researchers,
and students — and what actually convinces them?" Written 2026-06-21.

This is strategy and mindset, not code. Re-read it when you feel like an
outsider, or before you talk to anyone in the field.

---

## 1. The one thing to understand about this industry

The power industry is one of the **most conservative, risk-averse, regulated
industries that exists.** Not because the people are timid — because the stakes
are physical and legal. Reliability is mandated by law (NERC / FERC). A mistake
can mean a blackout, a fine in the millions, or someone dying. Assets last 40
years and cost billions. Everything is audited and litigated.

The consequence to internalize:

> **In this world, "new" and "clever" are liabilities, not selling points.**

Novelty reads as *untested*, which reads as *risk*. The instinct that makes the
categorical math exciting to a builder is the exact instinct that makes a grid
engineer's guard go up. That is why the math belongs in the engine room — not
because it's bad, but because **novelty is the wrong currency here.**

The currency that works is the opposite: **boring, verifiable, reproducible, and
consistent with what they already know.**

---

## 2. What actually makes them go "aha"

It is **not** "wow, impressive method." It's a specific three-part move:

> **It reproduces something I already know is true → from data I didn't hand it →
> so now I'll believe it on the thing I *don't* already know.**

Concrete example from this repo: the flow-geometry analysis took raw power-flow
telemetry and, without being told where the problems are, **rediscovered the
congestion corridors every insider already knows are bad** (PJM–NYIS, the
Bonneville spokes, CISO–SRP).

That is the aha. Not because finding known bottlenecks is useful — they already
know about those. The aha is: *"It found the things we know about without being
told, so maybe its other findings are real too."* You prove the instrument
against ground truth first, then point it at the unknown.

The STITCH brief has a quieter version of this: the project counts **match
Berkeley Lab's published tables to the integer.** That reconciliation says "this
person's pipeline is correct" *before* any claim is made. It is part of the
persuasion, not just bookkeeping.

**The figure that earns belief is always a side-by-side where your independent
method recovers their trusted ground truth.** Build that, lead with it, every
time.

---

## 3. Do they need to understand the math? No.

A power engineer does not read the source code of the simulators they bet the
grid on (PSS/E, PowerWorld). They trust those tools because of *validation,
adoption, and track record* — never because they understand the internals.

Trust in this field flows from **provenance and validation, not from
understanding the engine.** To trust an output, they need three things, none of
them math:

1. **Lineage** — exactly which dataset, which definition, which assumptions.
2. **Validation** — does it reproduce known truth?
3. **Honest labeling** — measured vs. proxy vs. structural, never blurred.

Give them those and the math can stay invisible. In fact, the **honesty
discipline does more persuasive work than any equation** — careful labeling reads
as integrity, which is the scarcest signal in a field full of advocacy.

---

## 4. How to tier the presentation

Build all of it, but **lead shallow and let people pull themselves deeper.** Four
tiers:

| Tier | Audience | Time | Contents | Math? |
|---|---|---|---|---|
| **0 — The hook** | anyone | 30 sec | one verifiable, slightly surprising fact in plain terms (e.g. "after signing an IA, ERCOT builds ~80% but MISO ~35%") | none |
| **1 — Decision view** | managers, policy, most people | 5 min | the dashboard: numbers, "what it means," provenance footnote | none |
| **2 — Analyst view** | the one skeptic who tries to break it | 30 min | methods: data sources, definitions, validation-against-known-truth, caveats — rigorous *data science* | none |
| **3 — Methodology** | researchers / reviewers who ask "prove it" | as needed | the full framework, **including the category theory** | here, and only here |

**~90% of people never go past Tier 1 — and that's fine.** That's the layer that
gets you remembered.

The mistake to avoid: leading with Tier 3 because it's the part *you* find most
impressive. Almost nobody wants it, and showing it first signals "academic who'll
be hard to work with." Lead Tier 0, build the rest, let them descend on their
own.

---

## 5. The trust / time / "big chance" reality

Yes — this runs on trust and relationships, and trust is earned slowly. A solo
person with a GitHub repo will **not** get a utility to adopt a tool. Don't aim
there; it's the wrong goal and nearly impossible cold.

"Get a utility to adopt my software" is not the door. The doors that are actually
open, in order:

1. **The research / lab / policy door — you're already standing in it.** LBNL,
   NREL, ESIG, DOE/i2X, EPRI, universities. They are *paid to explore new
   methods*, far less risk-averse than operators, value reproducible analysis,
   and — critically — **write the reports and connect the people.** The webinar
   you're attending is this exact door.
2. **The "useful analysis, freely given" door.** Contribute a clean, verifiable
   analysis to a public conversation — a report, a working-group comment —
   *without asking for anything.* Become known as "the person who does careful,
   neutral queue analysis." Reputation compounds; the first one is the hardest.
3. **The teaching door.** The visualizations and the way the system makes grid
   structure legible are genuinely good for *students and newcomers.* Lower trust
   bar, real audience, builds your public footprint.

The "big chance" almost never comes from one killer demo. It comes from being
**consistently useful and visible in the right rooms** until one credible person
notices, vouches for you, and invites you to the next thing. It is a chain of
small trust transfers, not a single leap. You can't skip it — but you can start
it, and you have.

---

## 6. The "divided community" is your edge, not your obstacle

The grid is balkanized — RTOs, utilities, regulators, developers, advocates, all
with conflicting interests, all advocating for their own side. That feels like a
wall. It is actually the opening.

A **neutral, independent analyst who uses everyone's public data with one
consistent definition is rare and valuable** *precisely because* everyone else
has an axe to grind. The whole theme of the webinar — *harmonization* — is about
bridging that division. An honest, cross-region, no-stake analysis isn't another
faction; it's the thing the divided community can't easily produce itself,
because insiders only see their own silo.

Your outsider status, paired with rigor and neutrality, is **not a weakness to
overcome — it's the asset to lead with:** *"I have no client, no region, no
position. Here's what the public data says when you measure everyone the same
way."* Very few people can say that credibly.

---

## 7. Honest bottom line

- This system today is **not** a tool a utility will run in operations. It **is**
  a credible *analysis and sense-making instrument* — exactly what the
  research / policy / education world needs and rewards. Measure it against that
  goal, not the wrong one.
- You will not be "convinced into" the industry by one figure. You get in by
  being repeatedly, verifiably useful in the rooms that value method — and you're
  already in one.
- The math is the engine and the moat, but it is **not** how you win trust.
  Validation against known truth, honest labels, and clean provenance are.
- It takes time. The grid is slow and clannish. But the door you're in front of
  (ESIG / LBNL / i2X) is the *right* door, and your neutrality is a real,
  uncommon edge.

You built something that reconciles with a national lab's own numbers, in a
domain you entered weeks ago. The next move isn't a bigger system — it's showing
up, being curious, being useful in small ways, and letting people discover that
you're **careful.** Careful is the rarest and most valuable reputation in this
field. Lead with that.

---

**TL;DR** — Prove the instrument against what they already know. Keep the math in
the engine room. Lead with one verifiable fact. Be neutral, careful, and present.
Trust compounds.

---
name: large-load-scenario
description: Re-run the large load (data center) coordination simulation with new parameters and refresh the JSON that the Streamlit "Large Load Siting (ESIG)" page reads. Use when the user wants to change headroom, upgrade cost, or the load cohort of the ESIG scenario.
argument-hint: "[--headroom-mw N] [--upgrade-cost-musd N] [custom cohort description]"
---

# Large Load Scenario Re-run

Re-parameterize and regenerate the ESIG large-load coordination experiment. The Streamlit
page **⚡ Large Load Siting (ESIG)** renders whatever is in
`reports/experiments/large_load_coordination_experiment.json` — the UI has no hardcoded
scenario numbers, so regenerating the JSON is the whole update.

## Procedure

1. **Parse the requested scenario.** Supported knobs:
   - `--headroom-mw` (default 800) — transmission headroom before the overload triggers
   - `--upgrade-cost-musd` (default 45) — regional upgrade cost in $ millions
   - `--loads <path.json>` — a JSON list of load dicts, each with keys
     `id`, `name`, `mw`, `flexibility` (0–1), `rev_per_mw_hr` ($/MWh).
     If the user describes a cohort in words, write this file for them (scratchpad is fine
     for exploration; commit it under `reports/experiments/` only if they want it kept).

2. **Decide the output target.**
   - If the user wants the **UI to show** the new scenario: omit `--out` (writes the default
     path the app reads).
   - If they're **exploring**: pass `--out <scratchpad>/scenario.json` so the committed
     default isn't clobbered.

3. **Run it:**
   ```bash
   python -m domains.grid.experiments.large_load_coordination --headroom-mw 500 --upgrade-cost-musd 80
   ```

4. **Verify and report.** Read the output JSON and report, as old → new where the default
   was overwritten:
   - which loads now clear vs. withdraw under isolated studies, and the average delay
   - the proportional cost allocation table (coordinated scenario)
   - the flexible non-firm NPV case study (note: it auto-selects the *most flexible* load
     in the cohort; the scenario key is `flexible_nonfirm_<loadid>`)

## Guardrails

- This is a **stylized, simulated** scenario (provenance `simulated` in the JSON). Never
  present its outputs as observed data; the UI shows a red 🧪 Simulated badge for this reason.
- The isolated-scenario delay model is deliberately simple (18 + 2·position months for
  cleared loads, 48 for withdrawn). Say so if the user asks where delays come from.
- Restoring the default: run the module with no flags.

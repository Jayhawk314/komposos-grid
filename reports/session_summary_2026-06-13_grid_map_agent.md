# Session Summary - 2026-06-13 Grid Map + Local Agent

## Commit / Push

- Pushed to `grid/master`:
  `93f5daf Grid map manual and local agent chat`
- Remote: https://github.com/Jayhawk314/komposos-grid.git
- Final push verification before this summary:
  `git rev-list --left-right --count grid/master...HEAD` returned `0 0`.

## What Shipped

### Interactive Network Map

- Source: `domains/grid/network_map.py`
- Runner: `domains/grid/run_network_map.py`
- Output: `docs/network_map.html`
- Multi-year map for 2023/2024/2025 EIA-930 interchange.
- Geographic and spectral layouts.
- Touch support: pan, pinch zoom, tap selection.
- Mobile layout: inspector stacks below map, legend defaults collapsed.
- What-if mode: cut ties, outage BAs, add hypothetical links, undo, inspect
  islanding/connectivity impacts.

### Local AI Bridge

- `domains/grid/agent_server.py`
  - Serves the map and exposes `POST /api/grid/chat`.
  - Start with:
    `python -m domains.grid.agent_server --port 8000`
  - Open:
    `http://127.0.0.1:8000/network_map.html`
- `domains/grid/agent_tools.py`
  - Grounded JSON tools: `ba`, `tie`, `path`, `similar`, `bottlenecks`,
    `seam`, `whatif`, `gaps`, plus `manifest` and `prompt`.
- `domains/grid/agent_contract.py`
  - Shared tool manifest/prompt contract.
- `domains/grid/AGENTS.md`
  - Local-agent playbook.

Important: the AI tab requires `agent_server.py`. A plain static server or
GitHub Pages cannot run Python tools; in that case the panel shows a fallback
message telling users to start the local bridge.

### AI UX

- Natural-language routing handles:
  - `where is power getting stuck?`
  - `what areas act like PJM?`
  - `why is PJM-NYIS important?`
  - `what breaks if PJM-NYIS fails?`
  - `what should I look at next?`
- Result cards include provenance.
- Result cards can include actions:
  - `Highlight on map`
  - `Apply cut to map`
- `Apply cut to map` switches to What-if mode and disables the returned tie(s).

Current implementation is a grounded tool-running local API, not a hosted LLM.
A future model adapter can sit behind `/api/grid/chat` if needed, but must
preserve the tool/provenance contract.

### Manual

- Added `docs/grid_map_manual.html`.
- Dark by default.
- Linked from the map toolbar as `Manual`.
- Covers:
  - how to use the UI
  - EIA-930/gross/net/demand/queue/congestion terms
  - curvature, Fiedler seam, similarity, what-if interpretation
  - evidence levels
  - major findings
  - limits and honesty rules

### System Overview Assets

- Added `domains/grid/system_overview.py`.
- Added `reports/system_overview.json` and `reports/SYSTEM_OVERVIEW.md`.
- Added overview figures under `reports/figures/`.
- Map overlays now use report artifacts through `domains/grid/map_overlays.py`.

## Verification

Before commit/push:

- Grid test suite:
  `169 passed`
- Focused local-agent/map tests:
  `23 passed`
- Generated `docs/network_map.html` JS:
  `node --check` passed.
- Headless Playwright UI check:
  - opened `network_map.html`
  - clicked AI tab
  - asked natural-language questions
  - saw result cards
  - saw `Highlight on map`
  - saw `Apply cut to map`
  - zero console errors

## Current Known Incomplete / Next Work

- Phase 0 reproducibility still needs true clean-room test:
  fresh clone, fresh venv, full re-download, expected headline number matches.
- Archive evidence-chain inputs off-machine, especially perishable OASIS data.
- Human review pass on `reports/ba_review_template.csv` remains pending.
- External reproduction (M1), expert review (M2), and first paying design
  partner (M3) remain product/maturity milestones, not code-complete items.
- Rerun CHPE event study after more post-commercial-operation months are
  available.
- If continuing the AI feature:
  - add COG claim verification tool cards
  - add deeper OPTIMUS relief explanations
  - optionally add a real model adapter behind `/api/grid/chat`
  - preserve the measured/proxy/screening evidence separation

## Gotchas

- Use `grid` remote, not `origin`, for the public grid repo.
- For AI testing, use `python -m domains.grid.agent_server --port 8000`.
- Do not use plain `http.server` if testing `/api/grid/chat`.
- PowerShell does not expand `tests/test_grid_*.py` for pytest; enumerate files:
  `$tests = Get-ChildItem tests -Filter 'test_grid_*.py' | % FullName; python -m pytest @tests -q`

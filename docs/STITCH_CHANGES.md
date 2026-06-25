# STITCH / i2X Changes — komposos-grid

## What changed and why

### `streamlit_app.py` — complete rewrite of the navigation layer

The original had 4 static pages routing to pre-generated HTML files.
The new version adds 2 new pages and upgrades the sidebar — the
underlying domain logic (`run_stitch_brief.py`, `run_network_map.py`,
`sources/lbnl_queue.py`) is **untouched**.

---

### New pages added

#### `🗺️ Harmonization Matrix`
The i2X STITCH core deliverable. A cross-region matrix of 13 study
parameters (N-1 standard, IBR modeling, cluster grouping, automation
level, etc.) with ✅ / ⚠️ / ❌ alignment scores per region.

- Sidebar region multiselect filters the matrix live
- Per-region alignment score metric cards at top
- Priority gap table: ❌ = High, ⚠️ = Medium
- Pinned STITCH key finding (cluster vs. serial asymmetry)

To extend: edit the `HARM_DATA` dict in the page section —
add a row per parameter, a column per region.

#### `📅 STITCH Session Notes`
Structured meeting reference for each STITCH session.
Covers: presenter roster, standard topic checklist (with completion
status), key discussion outputs, harmonization opportunities found,
links, and a future-session tracker.

---

### Changes to existing pages

#### `📊 MISO vs ERCOT Queue Study`
- Added `_stitch_badge()` header with session date
- Added presenter credits (Hickey · Fernandes · Sankaran)
- Wrapped in 3 tabs: Full Brief / Session Context / Export
  - **Session Context tab**: agenda, STITCH description, structural
    differences table (MISO DPP cluster vs. ERCOT serial)
  - **Export tab**: one-click download of .md / .json / .html brief;
    graceful message if files not yet generated

#### Sidebar
- Added **STITCH session selector** (future sessions drop in here)
- Added **Region Filter** multiselect (MISO/ERCOT/PJM/CAISO/SPP/NYISO/ISO-NE)
  used by the Harmonization Matrix page
- Updated title to "Komposos Grid · i2X STITCH"

---

### No changes needed in

- `domains/grid/run_stitch_brief.py` — already STITCH-native
- `domains/grid/run_network_map.py` — unchanged
- `domains/grid/sources/lbnl_queue.py` — unchanged
- `.streamlit/config.toml` — unchanged
- `requirements.txt` — no new deps (pandas is already pulled by streamlit)

---

### To deploy

```bash
# Drop the new streamlit_app.py in place, then:
git add streamlit_app.py
git commit -m "feat: STITCH harmonization matrix + session notes pages"
git push
```

Streamlit Cloud will pick up the push automatically.

---

### Roadmap for future STITCH sessions

1. Add the new session to the `stitch_session` selectbox in the sidebar
2. Add a new tab in `📅 STITCH Session Notes` for that session
3. Run `run_stitch_brief.py --with-peers` to add CAISO/PJM etc. to the brief
4. Update `HARM_DATA` in the Harmonization Matrix with any new findings

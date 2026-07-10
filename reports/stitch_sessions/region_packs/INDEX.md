# Cross-Region Comparison — the IA-Certainty Spectrum

> 📏 **Measured** — every figure derives from the LBNL *Queued Up* data file (through 2026); headline counts reconcile to the published tables. Regenerate with `python -m domains.grid.run_region_packs`.

One table the STITCH panel has likely never seen: **what an executed IA is worth, by region.** The same contract milestone carries very different completion information depending on where it is signed.

| Region | Requests | LBNL completion | Post-IA completion | Study (Req→IA) | Build (IA→COD) |
|---|---:|---:|---:|---:|---:|
| [CAISO](caiso.md) | 2,868 | 12.1% | **90.7%** | 44.4 mo | 28.6 mo |
| [PJM](pjm.md) | 7,666 | 20.5% | **85.9%** | 35.5 mo | 22.8 mo |
| [ERCOT](ercot.md) | 3,757 | 29.6% | **79.7%** | 20.3 mo | 25.9 mo |
| [ISO-NE](iso_ne.md) | 1,282 | 26.8% | **75.2%** | 33.7 mo | — |
| [West (non-ISO)](west.md) | 8,097 | 16.9% | **71.9%** | 17.5 mo | 5.8 mo |
| [NYISO](nyiso.md) | 1,936 | 19.4% | **70.0%** | 41.2 mo | 20.4 mo |
| [Southeast (non-market)](southeast.md) | 4,334 | 15.8% | **55.4%** | 21.2 mo | 23.2 mo |
| [MISO](miso.md) | 5,424 | 18.1% | **34.9%** | 29.8 mo | 18.8 mo |
| [SPP](spp.md) | 2,837 | 16.5% | — *(not tracked)* | — | — |

*"Not tracked" is a finding, not a gap in our pipeline: those regions' LBNL records do not record IA execution for withdrawn projects, so the milestone's certainty content cannot be computed there — direct evidence that milestone data coverage itself needs harmonizing.*

Sessions this feeds: *Regional Study Processes Cont.* — 2026-07-28, 2026-08-18, 2026-09-22 (ESIG i2X STITCH). When a session's presenters are announced, start from that region's pack and fill in the Session prep notes.

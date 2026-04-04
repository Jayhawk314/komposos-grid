# CLAUDE.md - KOMPOSOS-IV

## Project Identity

**KOMPOSOS-IV** is the fused categorical runtime. It merges KOMPOSOS-III's
mathematical power with Orion's "runtime IS the category" architecture.

One class (Category) replaces III's KomposOSStore + Category + EnrichedCategory +
StoreAdapter. Objects and morphisms persist automatically, carry enrichment
natively, and optionally execute.

**Author:** James Ray Hawkins
**License:** Apache 2.0 / Commercial dual license
**Python:** 3.10+

## Architecture

```
Category = Store + Enriched Category + Hook Runtime
  - Objects persist on add (SQLite, automatic)
  - Morphisms carry confidence as enriched hom-values
  - Composition applies quantale tensor + persists + fires hooks
  - Morphisms optionally execute (callable)
  - Path finding via Dijkstra on enriched weights
```

## Key Files

| File | Purpose |
|------|---------|
| `core/types.py` | Object, Morphism, Path, HigherMorphism, EquivalenceClass |
| `core/enrichment.py` | MonoidalStructure, 5 quantales |
| `core/persistence.py` | SQLiteBackend (internal, never used directly) |
| `core/hooks.py` | HookRegistry, event system |
| `core/category.py` | THE fused categorical runtime |
| `core/bridge.py` | Thin domain bridge ABC |

## Math Modules (ported from III-CORE)

| Module | Purpose |
|--------|---------|
| `categorical/` | 17 pure math files + shim (category.py re-exports from core) |
| `cubical/` | Cubical type theory: paths, Kan operations |
| `game/` | Open games, Nash equilibrium |
| `topology/` | Persistent homology, temporal sheaves, persistent sheaves |
| `hott/` | HoTT: identity types, path induction, homotopy |
| `geometry/` | Ollivier-Ricci curvature, discrete Ricci flow, spectral analysis |
| `zfc/` | Set-theoretic reasoning: universe, logic, well-ordering, separation, proof engine, meta-kan, store adapter, dual-engine bridge, proof bridge |
| `oracle/` | Categorical oracle: 9 inference strategies, coherence checker, conjecture engine, categorical verifier, ZFC verifier |
| `data/` | Embeddings engine (Sentence Transformers), CategoryEmbedder |

## API Quick Reference

All modules use the IV API (not III):
- `category.objects()` not `store.list_objects(limit=N)`
- `category.morphisms()` not `store.list_morphisms(limit=N)`
- `category.get(name)` not `store.get_object(name)`
- `category.morphisms_from(src)` not `store.get_morphisms_from(src)`
- `mor.source` / `mor.target` not `mor.source_name` / `mor.target_name`
- `Object` / `Morphism` from `core.types`, not `StoredObject` / `StoredMorphism`
- `Category(db_path=":memory:")` not `create_memory_store()`

## Rules

- Category owns persistence. Never use SQLiteBackend directly.
- Enrichment is intrinsic. Morphism.confidence IS the hom-value.
- Bridge is just a loader. Analysis lives on Category or standalone modules.
- Do NOT add domain-specific code here. Domain code goes in domain repos.
- All math modules use IV's Category API. No III-era `KomposOSStore` references.

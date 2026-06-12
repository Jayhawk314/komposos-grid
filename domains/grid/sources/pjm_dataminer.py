# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 James Hawkins / Komposos-Labs

"""PJM Data Miner 2 client (PLAN A2, keyed half).

API: https://api.pjm.com/api/v1/<feed> with the subscription key in
the Ocp-Apim-Subscription-Key header. Keys come from a free
apiportal.pjm.com account (Profile -> Subscriptions -> Primary key).

The key is NEVER stored in the repo: pass --api-key or set the
PJM_API_KEY environment variable.

Feeds used here:

- ``da_transconstraints``: day-ahead transmission constraints, hourly
  rows with constraint name and shadow price -- PJM's analogue of
  MISO's da_bc, enabling the same severity ranking.
- ``da_hrl_lmps``: day-ahead hourly LMPs with congestion/loss
  components per pricing node; pnode type INTERFACE prices PJM's
  external interfaces, enabling seam spreads from the PJM side
  (PJM-NYIS cross-check, CPLE seam).

Responses are JSON with paging (startRow/rowCount, max 50000); pages
are cached to disk keyed by feed+params so reruns are free.
"""

from __future__ import annotations

import hashlib
import json
import os
import time
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Dict, Iterator, List, Optional

BASE_URL = "https://api.pjm.com/api/v1"
KEY_ENV = "PJM_API_KEY"
MAX_ROWS = 50000
POLITE_DELAY_S = 0.5


class PJMError(RuntimeError):
    pass


def resolve_api_key(explicit: Optional[str] = None) -> str:
    key = explicit or os.environ.get(KEY_ENV, "")
    if not key:
        raise PJMError(
            f"No PJM API key: pass --api-key or set {KEY_ENV}. "
            "Get one free at apiportal.pjm.com (Profile -> Subscriptions)."
        )
    return key


def _cache_path(cache_dir: Path, feed: str, params: Dict[str, str]) -> Path:
    digest = hashlib.sha256(
        json.dumps(params, sort_keys=True).encode()
    ).hexdigest()[:16]
    return cache_dir / f"{feed}_{digest}.json"


def fetch_feed(
    feed: str,
    params: Dict[str, str],
    api_key: str,
    cache_dir: str | Path,
) -> List[dict]:
    """All rows for a feed query, paged and cached."""
    cache_dir = Path(cache_dir)
    cache_dir.mkdir(parents=True, exist_ok=True)
    cached = _cache_path(cache_dir, feed, params)
    if cached.exists():
        return json.loads(cached.read_text(encoding="utf-8"))

    rows: List[dict] = []
    start = 1
    while True:
        q = dict(params)
        q.update({"startRow": str(start), "rowCount": str(MAX_ROWS)})
        url = f"{BASE_URL}/{feed}?{urllib.parse.urlencode(q)}"
        req = urllib.request.Request(
            url,
            headers={
                "Ocp-Apim-Subscription-Key": api_key,
                "User-Agent": "Mozilla/5.0 (komposos-grid-domain)",
                "Accept": "application/json",
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=180) as resp:
                payload = json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            if exc.code in (401, 403):
                raise PJMError(
                    f"PJM rejected the API key (HTTP {exc.code}); check the "
                    "subscription key from apiportal.pjm.com"
                ) from exc
            raise
        time.sleep(POLITE_DELAY_S)

        items = payload.get("items", [])
        rows.extend(items)
        total = int(payload.get("totalRows", len(rows)))
        if start + len(items) > total or not items:
            break
        start += len(items)

    cached.write_text(json.dumps(rows), encoding="utf-8")
    return rows


def month_windows(year: int) -> Iterator[tuple]:
    """(start, end) date strings per month -- Data Miner range params."""
    for m in range(1, 13):
        nxt_y, nxt_m = (year + 1, 1) if m == 12 else (year, m + 1)
        yield (f"{m}/1/{year} 00:00", f"{nxt_m}/1/{nxt_y} 00:00")


def fetch_da_constraints_year(
    year: int,
    api_key: str,
    cache_dir: str | Path,
) -> List[dict]:
    """Day-ahead transmission constraints for a year (monthly pages)."""
    rows: List[dict] = []
    for start, end in month_windows(year):
        rows.extend(
            fetch_feed(
                "da_transconstraints",
                {"datetime_beginning_ept": f"{start}to{end}"},
                api_key,
                cache_dir,
            )
        )
    return rows


def aggregate_pjm_constraints(rows: List[dict]) -> List[dict]:
    """Severity table: per constraint name, binding hours and
    |shadow price| totals (same semantics as MISO's severity index)."""
    table: Dict[str, dict] = {}
    for row in rows:
        name = str(
            row.get("monitored_facility")
            or row.get("constraint_name")
            or row.get("facility")
            or "unknown"
        )
        sp = abs(float(row.get("shadow_price") or 0.0))
        entry = table.setdefault(
            name, {"constraint_name": name, "binding_hours": 0,
                   "severity": 0.0, "max_abs_sp": 0.0},
        )
        entry["binding_hours"] += 1
        entry["severity"] += sp
        entry["max_abs_sp"] = max(entry["max_abs_sp"], sp)
    return sorted(table.values(), key=lambda e: -e["severity"])

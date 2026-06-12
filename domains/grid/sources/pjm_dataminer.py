# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 James Hawkins / Komposos-Labs

"""PJM Data Miner 2 client (PLAN A2, keyed half).

API: https://api.pjm.com/api/v1/<feed> with the subscription key in
the Ocp-Apim-Subscription-Key header. Keys come from a free
apiportal.pjm.com account (Profile -> Subscriptions -> Primary key).

The key is NEVER stored in the repo: pass --api-key or set the
PJM_API_KEY environment variable.

Feeds used here (probed June 2026):

- ``da_marginal_value``: day-ahead constraint marginal values --
  hourly rows with monitored_facility and shadow_price; PJM's
  analogue of MISO's da_bc, enabling the same severity ranking.
  (``da_transconstraints`` lists congestion events but carries no
  shadow prices.)
- ``da_hrl_lmps``: day-ahead hourly LMPs with congestion/loss
  components per pricing node; pnode type INTERFACE prices PJM's
  external interfaces, enabling seam spreads from the PJM side
  (PJM-NYIS cross-check, CPLE seam).

Responses are JSON with paging (startRow/rowCount, max 50000); pages
are cached to disk keyed by feed+params so reruns are free.
"""

from __future__ import annotations

import hashlib
import http.client
import json
import os
import socket
import ssl
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Dict, Iterator, List, Optional

BASE_URL = "https://api.pjm.com/api/v1"
SETTINGS_URL = "https://dataminer2.pjm.com/config/settings.json"
KEY_ENV = "PJM_API_KEY"
MAX_ROWS = 50000
POLITE_DELAY_S = 0.5


class PJMError(RuntimeError):
    pass


# ---------------------------------------------------------------- DNS
# Some resolvers intermittently NXDOMAIN api.pjm.com while Google's
# resolver serves it fine. Fallback: resolve over Google's DoH JSON
# endpoint (reached by bare IP, whose cert carries an 8.8.8.8 SAN) and
# connect to the IP with SNI pinned to the real hostname.

_DOH_URL = "https://8.8.8.8/resolve?name={host}&type=A"
_resolved: Dict[str, str] = {}


def _doh_resolve(host: str) -> str:
    if host in _resolved:
        return _resolved[host]
    req = urllib.request.Request(
        _DOH_URL.format(host=host), headers={"Accept": "application/dns-json"}
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        payload = json.loads(resp.read().decode("utf-8"))
    answers = [a["data"] for a in payload.get("Answer", []) if a.get("type") == 1]
    if not answers:
        raise PJMError(f"DoH fallback found no A record for {host}")
    _resolved[host] = answers[0]
    return answers[0]


class _PinnedHTTPSConnection(http.client.HTTPSConnection):
    """Connects to a fixed IP while presenting SNI/Host for the real name."""

    def __init__(self, host, ip, timeout=None, context=None):
        super().__init__(host, timeout=timeout, context=context)
        self._ip = ip
        self._ssl_context = context or ssl.create_default_context()

    def connect(self):
        sock = socket.create_connection((self._ip, self.port), self.timeout)
        self.sock = self._ssl_context.wrap_socket(sock, server_hostname=self.host)


def _urlopen_resilient(req: urllib.request.Request, timeout: int):
    """urlopen, falling back to DoH + pinned-IP connect on DNS failure."""
    try:
        return urllib.request.urlopen(req, timeout=timeout)
    except urllib.error.URLError as exc:
        if not isinstance(getattr(exc, "reason", None), socket.gaierror):
            raise
    host = urllib.parse.urlparse(req.full_url).hostname
    ip = _doh_resolve(host)

    class _Handler(urllib.request.HTTPSHandler):
        def https_open(self, r):
            return self.do_open(
                lambda h, timeout=None, context=None: _PinnedHTTPSConnection(
                    h, ip, timeout=timeout, context=context
                ),
                r,
            )

    return urllib.request.build_opener(_Handler()).open(req, timeout=timeout)


def fetch_public_key() -> str:
    """PJM's public subscription key, published in the Data Miner web
    app's own config (the same path the gridstatus library uses).
    Rate-limited harder than a registered key; fine for yearly batch
    pulls with paging delays."""
    req = urllib.request.Request(
        SETTINGS_URL, headers={"User-Agent": "Mozilla/5.0 (komposos-grid)"}
    )
    with _urlopen_resilient(req, timeout=60) as resp:
        settings = json.loads(resp.read().decode("utf-8"))
    key = settings.get("subscriptionKey", "")
    if not key:
        raise PJMError("public settings.json had no subscriptionKey")
    return key


def resolve_api_key(explicit: Optional[str] = None) -> str:
    key = explicit or os.environ.get(KEY_ENV, "")
    if key:
        return key
    try:
        return fetch_public_key()
    except Exception as exc:
        raise PJMError(
            f"No PJM API key: pass --api-key, set {KEY_ENV}, or ensure "
            f"{SETTINGS_URL} is reachable (public-key fallback failed: {exc})"
        ) from exc


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
            with _urlopen_resilient(req, timeout=180) as resp:
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
    """Day-ahead constraint marginal values for a year (monthly pages)."""
    rows: List[dict] = []
    for start, end in month_windows(year):
        rows.extend(
            fetch_feed(
                "da_marginal_value",
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

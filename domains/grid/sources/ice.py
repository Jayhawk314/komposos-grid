# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 James Hawkins / Komposos-Labs

"""EIA ICE electric hub-price evidence for Western congestion proxies."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List


PRICE_HUB = "Price hub"
DELIVERY_DATE = "Delivery start date"
WEIGHTED_PRICE = "Wtd avg price $/MWh"
DAILY_VOLUME = "Daily volume MWh"

BA_COLUMN = "Balancing Authority"
DIBA_COLUMN = "Directly Interconnected Balancing Authority"
DATE_COLUMN = "Data Date"
FLOW_COLUMN = "Interchange (MW)"


@dataclass(frozen=True)
class HubPairSpec:
    ba_a: str
    ba_b: str
    hub_a: str
    hub_b: str
    label: str
    note: str = ""


@dataclass(frozen=True)
class HubPairAudit:
    ba_a: str
    ba_b: str
    hub_a: str
    hub_b: str
    label: str
    annual_vw_price_a: float
    annual_vw_price_b: float
    annual_vw_spread_usd_mwh: float
    overlap_days: int
    overlap_peak_hours: int
    daily_mean_abs_spread_usd_mwh: float
    daily_volume_weighted_abs_spread_usd_mwh: float
    daily_max_abs_spread_usd_mwh: float
    share_hub_b_above_a: float
    net_flow_mwh_a_to_b: float
    flow_alignment_day_share: float
    flow_alignment_weighted_share: float
    note: str = ""

    @property
    def evidence_method(self) -> str:
        return "hub_daily_overlap_proxy"

    @property
    def conservative_spread_usd_mwh(self) -> float:
        return abs(self.annual_vw_spread_usd_mwh)

    @property
    def alignment_note(self) -> str:
        if self.flow_alignment_weighted_share >= 0.65:
            return "flow/price alignment is directionally supportive"
        if self.flow_alignment_weighted_share >= 0.45:
            return "flow/price alignment is mixed"
        return "flow/price alignment is weak"

    def to_evidence_row(self) -> dict:
        return {
            "ba_a": self.ba_a,
            "ba_b": self.ba_b,
            "evidence_source": "EIA ICE daily wholesale prices 2023 + EIA-930 interchange",
            "evidence_method": self.evidence_method,
            "mean_price_spread_usd_mwh": self.conservative_spread_usd_mwh,
            "max_price_spread_usd_mwh": self.daily_max_abs_spread_usd_mwh,
            "congestion_cost_usd": "",
            "hours_observed": self.overlap_peak_hours,
            "notes": (
                f"{self.hub_a} ${self.annual_vw_price_a:.2f} vs "
                f"{self.hub_b} ${self.annual_vw_price_b:.2f}; "
                f"daily overlap mean |spread| ${self.daily_mean_abs_spread_usd_mwh:.2f}/MWh; "
                f"flow-weighted alignment {self.flow_alignment_weighted_share:.1%}; "
                f"{self.alignment_note}. {self.note}".strip()
            ),
        }

    def to_row(self) -> dict:
        return {
            "ba_a": self.ba_a,
            "ba_b": self.ba_b,
            "hub_a": self.hub_a,
            "hub_b": self.hub_b,
            "label": self.label,
            "annual_vw_price_a": self.annual_vw_price_a,
            "annual_vw_price_b": self.annual_vw_price_b,
            "annual_vw_spread_usd_mwh": self.annual_vw_spread_usd_mwh,
            "conservative_spread_usd_mwh": self.conservative_spread_usd_mwh,
            "overlap_days": self.overlap_days,
            "overlap_peak_hours": self.overlap_peak_hours,
            "daily_mean_abs_spread_usd_mwh": self.daily_mean_abs_spread_usd_mwh,
            "daily_volume_weighted_abs_spread_usd_mwh": (
                self.daily_volume_weighted_abs_spread_usd_mwh
            ),
            "daily_max_abs_spread_usd_mwh": self.daily_max_abs_spread_usd_mwh,
            "share_hub_b_above_a": self.share_hub_b_above_a,
            "net_flow_mwh_a_to_b": self.net_flow_mwh_a_to_b,
            "flow_alignment_day_share": self.flow_alignment_day_share,
            "flow_alignment_weighted_share": self.flow_alignment_weighted_share,
            "alignment_note": self.alignment_note,
            "note": self.note,
        }


def default_western_hub_pairs() -> List[HubPairSpec]:
    return [
        HubPairSpec(
            ba_a="CISO",
            ba_b="SRP",
            hub_a="SP15 EZ Gen DA LMP Peak",
            hub_b="Palo Verde Peak",
            label="SP15 vs Palo Verde",
        ),
        HubPairSpec(
            ba_a="BPAT",
            ba_b="CISO",
            hub_a="Mid C Peak",
            hub_b="NP15 EZ Gen DA LMP Peak",
            label="Mid C vs NP15",
            note="NP15 volume is thin, so keep this as a hub-screening proxy.",
        ),
        HubPairSpec(
            ba_a="BPAT",
            ba_b="NEVP",
            hub_a="Mid C Peak",
            hub_b="Palo Verde Peak",
            label="Mid C vs Palo Verde",
            note="NEVP is approximated by Palo Verde.",
        ),
        HubPairSpec(
            ba_a="PACW",
            ba_b="CISO",
            hub_a="Mid C Peak",
            hub_b="NP15 EZ Gen DA LMP Peak",
            label="Mid C vs NP15",
            note="PACW and CISO are approximated by Mid C and NP15.",
        ),
    ]


def load_ice_prices(workbook_path: str | Path):
    import pandas as pd

    df = pd.read_excel(workbook_path)
    df.columns = [str(c).replace("\n", " ").strip() for c in df.columns]
    df[DELIVERY_DATE] = pd.to_datetime(df[DELIVERY_DATE])
    df[WEIGHTED_PRICE] = pd.to_numeric(df[WEIGHTED_PRICE], errors="coerce")
    df[DAILY_VOLUME] = pd.to_numeric(df[DAILY_VOLUME], errors="coerce")
    return df.dropna(subset=[PRICE_HUB, DELIVERY_DATE, WEIGHTED_PRICE])


def load_interchange_daily(csv_paths: Iterable[str | Path]):
    import pandas as pd

    frames = []
    for path in csv_paths:
        df = pd.read_csv(
            path,
            usecols=[BA_COLUMN, DIBA_COLUMN, DATE_COLUMN, FLOW_COLUMN],
            thousands=",",
        )
        df[FLOW_COLUMN] = pd.to_numeric(df[FLOW_COLUMN], errors="coerce")
        df[DATE_COLUMN] = pd.to_datetime(df[DATE_COLUMN])
        frames.append(df.dropna(subset=[FLOW_COLUMN]))
    return pd.concat(frames, ignore_index=True)


def build_western_hub_audits(
    ice_workbook: str | Path,
    interchange_csvs: Iterable[str | Path],
    specs: Iterable[HubPairSpec] | None = None,
) -> List[HubPairAudit]:
    prices = load_ice_prices(ice_workbook)
    flows = load_interchange_daily(interchange_csvs)
    return [
        audit_hub_pair(prices, flows, spec)
        for spec in (list(specs) if specs is not None else default_western_hub_pairs())
    ]


def audit_hub_pair(prices, flows, spec: HubPairSpec) -> HubPairAudit:
    import pandas as pd

    annual_a = _volume_weighted_price(prices, spec.hub_a)
    annual_b = _volume_weighted_price(prices, spec.hub_b)
    price_pivot = prices[prices[PRICE_HUB].isin([spec.hub_a, spec.hub_b])].pivot_table(
        index=DELIVERY_DATE,
        columns=PRICE_HUB,
        values=WEIGHTED_PRICE,
        aggfunc="mean",
    )
    volume_pivot = prices[prices[PRICE_HUB].isin([spec.hub_a, spec.hub_b])].pivot_table(
        index=DELIVERY_DATE,
        columns=PRICE_HUB,
        values=DAILY_VOLUME,
        aggfunc="sum",
    )
    price_overlap = price_pivot.dropna(subset=[spec.hub_a, spec.hub_b])
    spread_b_minus_a = price_overlap[spec.hub_b] - price_overlap[spec.hub_a]
    overlap_volumes = volume_pivot.reindex(price_overlap.index)[[spec.hub_a, spec.hub_b]]
    weights = overlap_volumes.min(axis=1).fillna(0.0)
    if float(weights.sum()) <= 0:
        weighted_abs = float(spread_b_minus_a.abs().mean())
    else:
        weighted_abs = float((spread_b_minus_a.abs() * weights).sum() / weights.sum())

    daily_flow = _daily_flow_a_to_b(flows, spec.ba_a, spec.ba_b)
    common = pd.DataFrame({
        "flow": daily_flow,
        "price_b_minus_a": spread_b_minus_a,
    }).dropna()
    aligned = common["flow"] * common["price_b_minus_a"] > 0
    flow_weight = common["flow"].abs()
    weighted_alignment = (
        float((aligned * flow_weight).sum() / flow_weight.sum())
        if float(flow_weight.sum()) > 0
        else 0.0
    )

    return HubPairAudit(
        ba_a=spec.ba_a,
        ba_b=spec.ba_b,
        hub_a=spec.hub_a,
        hub_b=spec.hub_b,
        label=spec.label,
        annual_vw_price_a=annual_a,
        annual_vw_price_b=annual_b,
        annual_vw_spread_usd_mwh=float(annual_b - annual_a),
        overlap_days=int(len(common)),
        overlap_peak_hours=int(len(common) * 16),
        daily_mean_abs_spread_usd_mwh=float(common["price_b_minus_a"].abs().mean()),
        daily_volume_weighted_abs_spread_usd_mwh=weighted_abs,
        daily_max_abs_spread_usd_mwh=float(common["price_b_minus_a"].abs().max()),
        share_hub_b_above_a=float((common["price_b_minus_a"] > 0).mean()),
        net_flow_mwh_a_to_b=float(common["flow"].sum()),
        flow_alignment_day_share=float(aligned.mean()) if len(common) else 0.0,
        flow_alignment_weighted_share=weighted_alignment,
        note=spec.note,
    )


def _volume_weighted_price(prices, hub: str) -> float:
    df = prices[prices[PRICE_HUB] == hub]
    volume = df[DAILY_VOLUME].fillna(0.0)
    if float(volume.sum()) <= 0:
        return float(df[WEIGHTED_PRICE].mean())
    return float((df[WEIGHTED_PRICE] * volume).sum() / volume.sum())


def _daily_flow_a_to_b(flows, ba_a: str, ba_b: str):
    a, b = sorted((ba_a, ba_b))
    df = flows[(flows[BA_COLUMN] == a) & (flows[DIBA_COLUMN] == b)].copy()
    daily = df.groupby(DATE_COLUMN)[FLOW_COLUMN].sum()
    if (a, b) == (ba_a, ba_b):
        return daily
    return -daily

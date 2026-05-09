"""
Case sheet for hand-reading 20 bin-4 k=5 cases against the silence-manufacture frame.

The conditional-findings note (2026-05-08) interprets bin-4 k=5 cases as
"wealthy borrowers who came to LC despite having traditional bank credit."
That interpretation rests on aggregate medians over the four wedge features.
This script pulls 20 actual cases, joins them back to the LC CSV for richer
context (purpose, home_ownership, verification_status, etc.), and prints a
hand-readable sheet.

Sampling: all charged-off bin-4 k=5 cases (the apparent counter-examples to
the frame), plus a deterministic random sample of paid-in-full to reach 20.
Vintage: 2015Q4 (largest n in bin-4 k=5 per the conditional-findings note).
"""

from __future__ import annotations

import json
import math
import random
from pathlib import Path

import pandas as pd

from wedge.collectors.lendingclub import filter_to_vintage, normalize_emp_length

JSONL = "runs/2026-05-08T17-44-39Z.jsonl"
VINTAGE = "2015Q4"
TERM = "36 months"
N_T_BINS = 5
TARGET_BIN = 3  # bin-4 in 1-indexed talk
N_TARGET = 20
SEED = 20260508

CSV_ENRICH_COLS = [
    "loan_amnt",
    "int_rate",
    "grade",
    "purpose",
    "title",
    "home_ownership",
    "verification_status",
    "addr_state",
    "emp_title",
    "revol_util",
    "inq_last_6mths",
]


def is_atypical_local_density(model_record: dict) -> bool:
    for ind in model_record.get("indeterminacy", []):
        if ind.get("species") == "local_density" and ind.get("direction") == "atypical":
            return True
    return False


def load_jsonl(path: Path) -> list[dict]:
    out = []
    for line in path.open():
        rec = json.loads(line)
        if rec.get("origin") != "real":
            continue
        Ts = [m["T"] for m in rec["per_model"]]
        out.append(
            {
                "case_id": rec["case_id"],
                "T_mean": sum(Ts) / len(Ts),
                "T_spread": max(Ts) - min(Ts),
                "k": sum(1 for m in rec["per_model"] if is_atypical_local_density(m)),
                "label": int(rec["label"]),
                "features": rec["features"],
            }
        )
    return out


def quintile_edges(values: list[float], n: int) -> list[float]:
    s = sorted(values)
    return [s[int(len(s) * i / n)] for i in range(1, n)]


def assign_bin(t: float, edges: list[float]) -> int:
    for i, e in enumerate(edges):
        if t < e:
            return i
    return len(edges)


def select_cases(cases: list[dict]) -> list[dict]:
    edges = quintile_edges([c["T_mean"] for c in cases], N_T_BINS)
    in_bin_k5 = [c for c in cases if assign_bin(c["T_mean"], edges) == TARGET_BIN and c["k"] == 5]
    charged_off = [c for c in in_bin_k5 if c["label"] == 1]
    paid = [c for c in in_bin_k5 if c["label"] == 0]
    rng = random.Random(SEED)
    rng.shuffle(paid)
    n_paid_needed = max(0, N_TARGET - len(charged_off))
    selected = charged_off + paid[:n_paid_needed]
    if len(selected) < N_TARGET:
        # Pad with extra charged-off, but there shouldn't be — log it.
        pass
    return selected[:N_TARGET], len(in_bin_k5), len(charged_off), len(paid)


def load_csv_subset(repo: Path) -> pd.DataFrame:
    needed = {
        "issue_d", "term", "loan_status",
        "fico_range_low", "dti", "annual_inc", "emp_length",
        *CSV_ENRICH_COLS,
    }
    df = pd.read_csv(
        repo / "data" / "accepted_2007_to_2018Q4.csv",
        usecols=lambda c: c in needed,
        low_memory=False,
    )
    df = filter_to_vintage(df, vintage=VINTAGE, term=TERM)
    df["emp_length_num"] = normalize_emp_length(df["emp_length"])
    return df


def join_one(case: dict, csv_df: pd.DataFrame) -> tuple[list[pd.Series], int]:
    f = case["features"]
    mask = (
        (csv_df["fico_range_low"].astype(float) == f["fico_range_low"])
        & (csv_df["dti"].astype(float) == f["dti"])
        & (csv_df["annual_inc"].astype(float) == f["annual_inc"])
    )
    el = f.get("emp_length")
    if el is None or (isinstance(el, float) and math.isnan(el)):
        mask &= csv_df["emp_length_num"].isna()
    else:
        mask &= csv_df["emp_length_num"] == el
    matches = csv_df[mask]
    return list(matches.iterrows()), len(matches)


def fmt_money(v) -> str:
    if v is None or (isinstance(v, float) and math.isnan(v)):
        return "—"
    return f"${v:,.0f}"


def fmt_num(v, decimals=2) -> str:
    if v is None or (isinstance(v, float) and math.isnan(v)):
        return "—"
    return f"{v:.{decimals}f}"


def fmt_str(v) -> str:
    if v is None or (isinstance(v, float) and math.isnan(v)):
        return "—"
    s = str(v).strip()
    return s if s else "—"


def render_case(idx: int, case: dict, matches: list, n_matches: int) -> str:
    f = case["features"]
    label_str = "**CHARGED OFF**" if case["label"] == 1 else "paid in full"
    lines = []
    lines.append(f"### Case {idx:2d} — {label_str}")
    lines.append("")
    lines.append(f"`{case['case_id']}`")
    lines.append("")
    lines.append("**Wedge view (what the methodology saw):**")
    lines.append(f"- T_mean: {case['T_mean']:.3f}  (spread across 5 models: {case['T_spread']:.3f})")
    lines.append(f"- FICO low: {fmt_num(f['fico_range_low'], 0)} | DTI: {fmt_num(f['dti'])} | "
                 f"income: {fmt_money(f['annual_inc'])} | emp_length: {fmt_num(f.get('emp_length'), 1)}")
    lines.append("")
    if n_matches == 0:
        lines.append("**CSV match: NONE** — could not join back to LC CSV row.")
    elif n_matches > 1:
        lines.append(f"**CSV match: {n_matches} rows** — non-unique 6-tuple. Showing first match.")
        idx0, row = matches[0]
        lines.extend(_render_csv_row(row))
    else:
        idx0, row = matches[0]
        lines.append("**LC CSV enrichment:**")
        lines.extend(_render_csv_row(row))
    lines.append("")
    return "\n".join(lines)


def _render_csv_row(row: pd.Series) -> list[str]:
    out = []
    out.append(f"- loan: {fmt_money(row.get('loan_amnt'))} @ {fmt_str(row.get('int_rate'))} "
               f"(grade {fmt_str(row.get('grade'))})")
    out.append(f"- purpose: **{fmt_str(row.get('purpose'))}** "
               f"— *{fmt_str(row.get('title'))}*")
    out.append(f"- home: {fmt_str(row.get('home_ownership'))} | "
               f"verification: {fmt_str(row.get('verification_status'))} | "
               f"state: {fmt_str(row.get('addr_state'))}")
    out.append(f"- employer: {fmt_str(row.get('emp_title'))}")
    out.append(f"- revol_util: {fmt_str(row.get('revol_util'))} | "
               f"inq_last_6mths: {fmt_str(row.get('inq_last_6mths'))}")
    return out


def main() -> None:
    repo = Path(__file__).resolve().parent.parent
    cases = load_jsonl(repo / JSONL)
    selected, n_pool, n_co, n_paid = select_cases(cases)
    csv_df = load_csv_subset(repo)

    print(f"# Bin-4 k=5 case sheet — {VINTAGE} ({TERM})")
    print()
    print(f"**Pool:** {n_pool} bin-4 k=5 cases ({n_co} charged-off, {n_paid} paid).")
    print(f"**Sample:** all {n_co} charged-off + {N_TARGET - n_co} paid (deterministic, seed={SEED}).")
    print()
    print("**Frame under test (from 2026-05-08 conditional-findings note §4):**")
    print("> Consensus on atypicality across R(ε) members identifies cases the trained model class")
    print("> systematically mis-prices in the direction of capacity limits relative to the tail of the")
    print("> population distribution. The signal is informative conditional on T: it refines T-based")
    print("> predictions in the moderate-to-upper T range where the model class under-predicts")
    print("> creditworthiness.")
    print()
    print("**Narrative claim under test (same note §1):**")
    print("> Bin-4 k=5 cases are wealthy, low-leverage borrowers — borrowers who came to LC despite")
    print("> having access to traditional bank credit.")
    print()
    print("---")
    print()

    join_stats = {"unique": 0, "multi": 0, "none": 0}
    for i, case in enumerate(selected, 1):
        matches, n = join_one(case, csv_df)
        if n == 0:
            join_stats["none"] += 1
        elif n == 1:
            join_stats["unique"] += 1
        else:
            join_stats["multi"] += 1
        print(render_case(i, case, matches, n))

    print("---")
    print()
    print("**Join stats:** "
          f"unique={join_stats['unique']}, "
          f"multi={join_stats['multi']}, "
          f"none={join_stats['none']} of {len(selected)}")


if __name__ == "__main__":
    main()

"""Step 2 (r5): P (compiled written policy) vs G (generic monotone) on LendingClub decisions, 2011-01-06 to 2012-05-31.

Implements docs/superpowers/specs/2026-10-27-lc-step2-policy-vs-generic-prereg-DRAFT.md (r5). G = unconstrained CART
filtered by an exact, held-out leaf-box monotonicity check. "Compiling" the policy = gating P(accept) to 0 where the
written rule (with tolerances) declines. The primary quantity is epsilon* = the relative log-loss excess at which the
near-optimal band starts to be dominated by trees that the record materially corrects. Verdict regions are fixed in
the pre-reg. `main()` reads the real files and must not run before the freeze commit.
"""
from __future__ import annotations

import json
import math
import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.tree import DecisionTreeClassifier

sys.path.insert(0, str(Path(__file__).resolve().parent))
from governs import parse_pct  # noqa: E402  (step 1's frozen parser)

FEATURES = ["score", "dti", "amount", "emp"]
SCORE, DTI, AMT, EMP_ = 0, 1, 2, 3
MONO = {SCORE: +1, DTI: -1, AMT: 0, EMP_: 0}
SUBSETS = [[0, 1], [0, 1, 2], [0, 1, 3], [0, 1, 2, 3]]   # every G tree uses score and DTI (credit priors, no policy numbers)
SEED = 20261027
SEEDS = [SEED + k for k in range(5)]
N_TREES = 4000          # set by the pre-freeze power check (pre-reg §5)
BOOT = 100_000          # bootstrap sample per tree
EPSILONS = [0.005, 0.01, 0.02]
PRIMARY_EPS = 0.01
MIN_G = 200
DEPTHS, LEAVES = (2, 3, 4), (1000, 3000)
RHO = 0.01              # a leaf "accepts" if its P(accept) exceeds this (diagnostic only)
DELTA = 0.02            # monotonicity tolerance floor on leaf P(accept) (r1 adversary finding 2)
Z_MONO = 3.0            # ...and at least this many standard errors of the leaf-pair difference (leaf noise)
MIN_MASS = 10           # a violation needs at least this many test applicants inside it
DTI_TOL, SCORE_TOL = 0.5, 5.0
WINDOW = ("2011-01-06", "2012-05-31")
ACC_MONTHS = ("2011-03", "2012-05")   # r5: from 2011-03, so issue months can't predate the 2011-01-06 rule
EPS_GRID = np.round(np.geomspace(1e-4, 0.05, 60), 6)
EPS_STAR_KILL, EPS_STAR_MATTERS = 0.02, 0.005
CONSTRUCT_MAX_SHARE = 0.005       # accepts inside the tolerant gate, as a share of accepts (adversary 3: 0.05% was ~17 loans)
CAPACITY_DEPTHS = (5, 6)          # capacity check (adversary 3, finding 1)
CAPACITY_SEEDS = 3
MIN_LEAF_HELDOUT = 100


# ---------- the written rule ----------

def written_rule_declines(score, dti, tol_dti=0.0, tol_score=0.0):
    """V5/V6: decline if FICO < 660, or DTI >= 25 with FICO < 720, or DTI >= 30 with FICO >= 720.
    With tolerances, each declined region shrinks inward: DTI by tol_dti, the 720 boundary by tol_score each side."""
    score, dti = np.asarray(score, float), np.asarray(dti, float)
    return ((score < 660) | ((score < 720 - tol_score) & (dti >= 25 + tol_dti))
            | ((score >= 720 + tol_score) & (dti >= 30 + tol_dti)) | ((score >= 660) & (dti >= 30 + tol_dti)))


def floors_declines(score, dti, tol_dti=0.0, tol_score=0.0):
    """Decomposition: the univariate part only (FICO >= 660 and DTI < 30 for everyone)."""
    score, dti = np.asarray(score, float), np.asarray(dti, float)
    return (score < 660) | (dti >= 30 + tol_dti)


def true_reasons(score: float, dti: float) -> set[str]:
    """The written rule's own reasons for a decline. FICO < 720 with DTI in [25, 30): DTI, or score (reaching 720 makes
    it eligible). DTI >= 30: DTI. FICO < 660 (with an eligible DTI): score."""
    r = set()
    if score < 660:
        r.add("score")
    if dti >= 30:
        r.add("dti")
    elif dti >= 25 and score < 720:
        r |= {"dti", "score"}
    return r


# ---------- trees and leaf boxes ----------

def bucket5(x):
    return np.floor(np.asarray(x, dtype=float) / 5.0) * 5.0


EMP = {"< 1 year": 0, "1 year": 1, "10+ years": 10, "n/a": -1}
EMP.update({f"{k} years": k for k in range(2, 10)})


def emp_code(s) -> float:
    if s is None or (isinstance(s, float) and math.isnan(s)):
        return -1.0
    return float(EMP.get(str(s).strip(), -1))


@dataclass
class Member:
    tree: DecisionTreeClassifier
    cols: list[int]
    depth: int
    leaf: int
    val_loss: float = 0.0


def p_accept(m: Member, X: np.ndarray) -> np.ndarray:
    p = m.tree.predict_proba(X[:, m.cols])
    return p[:, list(m.tree.classes_).index(1)] if 1 in m.tree.classes_ else np.zeros(len(X))


def leaf_boxes(m: Member, with_n: bool = False) -> list:
    """Every leaf as ({feature: (lo, hi)} on the FULL feature index, P(accept)[, n samples]). Intervals are (lo, hi]:
    sklearn sends x <= t left."""
    tr = m.tree.tree_
    k1 = list(m.tree.classes_).index(1) if 1 in m.tree.classes_ else None
    out = []

    def walk(node, box):
        if tr.children_left[node] == -1:
            v = tr.value[node][0]
            p = float(v[k1] / v.sum()) if k1 is not None and v.sum() > 0 else 0.0
            out.append((dict(box), p, int(tr.n_node_samples[node]), int(node)) if with_n else (dict(box), p))
            return
        f, t = m.cols[tr.feature[node]], float(tr.threshold[node])
        lo, hi = box.get(f, (-np.inf, np.inf))
        box[f] = (lo, min(hi, t)); walk(tr.children_left[node], box)
        box[f] = (max(lo, t), hi); walk(tr.children_right[node], box)
        box[f] = (lo, hi)

    walk(0, {})
    return out


def in_box(X: np.ndarray, box: dict) -> np.ndarray:
    ok = np.ones(len(X), bool)
    for f, (lo, hi) in box.items():
        ok &= (X[:, f] > lo) & (X[:, f] <= hi)
    return ok


def violation_mass(m: Member, Xmass: np.ndarray, rule=written_rule_declines) -> int:
    """Test applicants inside an accepting leaf (P > RHO) that the rule (with tolerances) declines. Exact over the
    leaf boxes: every amount and employment value is covered, not a median grid (adversary finding 6)."""
    declined = rule(Xmass[:, SCORE], Xmass[:, DTI], DTI_TOL, SCORE_TOL)
    hit = np.zeros(len(Xmass), bool)
    for box, p in leaf_boxes(m):
        if p > RHO:
            hit |= in_box(Xmass, box) & declined
    return int(hit.sum())


def violates(m: Member, Xmass: np.ndarray, rule=written_rule_declines) -> bool:
    return violation_mass(m, Xmass, rule) >= MIN_MASS


def logloss(y, p):
    p = np.clip(p, 1e-6, 1 - 1e-6)
    return float(-np.mean(y * np.log(p) + (1 - y) * np.log(1 - p)))


def sample_trees(Xtr, ytr, Xva, yva, seed: int, n: int = N_TREES) -> list[Member]:
    rng = np.random.RandomState(seed)
    out = []
    for i in range(n):
        cols = SUBSETS[rng.randint(len(SUBSETS))]
        depth, leaf = int(rng.choice(DEPTHS)), int(rng.choice(LEAVES))
        rows = rng.randint(0, len(Xtr), min(BOOT, len(Xtr)))
        # Unconstrained, then filtered by the exact leaf-box monotonicity check. NOT sklearn's monotonic_cst: its
        # midpoint bounds are sufficient but not necessary, and forbid the 720 interaction leaf the written rule needs
        # (constructed follower: monotonic_cst gain 0.08, unconstrained 0.0).
        t = DecisionTreeClassifier(max_depth=depth, min_samples_leaf=leaf,
                                   random_state=(seed * 10_000 + i) % 4_294_967_295)
        t.fit(Xtr[rows][:, cols], ytr[rows])
        m = Member(t, cols, depth, leaf)
        m.val_loss = logloss(yva, p_accept(m, Xva))
        out.append(m)
    return out


def gate_mask(X: np.ndarray, rule=None) -> np.ndarray:
    """Where the compiled rule sets P(accept) to 0: the written rule with the diagnostic tolerances (0.5 DTI points,
    one score bucket at 720), so borderline accepts (DTI exactly 25.00, a 715 bucket) aren't forced to 0
    (adversary 2, finding 1)."""
    rule = rule or written_rule_declines
    return rule(X[:, SCORE], X[:, DTI], DTI_TOL, SCORE_TOL)


def p_gated(m: Member, X: np.ndarray, rule=None) -> np.ndarray:
    """The compiled model: the member's P(accept), set to 0 wherever the compiled rule declines. Log loss clips P to
    [1e-6, 1 - 1e-6], so an accepted row inside the gate costs 13.8 nats: that's why the construct check exists."""
    return np.where(gate_mask(X, rule), 0.0, p_accept(m, X))


def construct_share(X: np.ndarray, y: np.ndarray) -> float:
    """Accepts inside the compiled gate, as a share of accepts. Above CONSTRUCT_MAX_SHARE the gate would mostly
    measure data mismatch between the two files, not model misstatement: CONSTRUCT_INVALID."""
    acc = y == 1
    return float(np.mean(gate_mask(X[acc]))) if acc.any() else float("nan")


def row_losses(y, p):
    p = np.clip(p, 1e-6, 1 - 1e-6)
    return -(y * np.log(p) + (1 - y) * np.log(1 - p))


def gating_gain(m: Member, Xva: np.ndarray, yva: np.ndarray) -> float:
    """Validation log-loss improvement from compiling the policy into m (positive = the gate helps)."""
    return m.val_loss - logloss(yva, p_gated(m, Xva))


Z_GAIN = 3.0   # a gating gain is material if its paired z exceeds this (r3 power check: eps-relative bars knife-edged)
MAG_FLOOR = 0.001   # ...AND its size exceeds this fraction of best loss (r4 power check: z alone flagged 2.5e-6 nats at n=78k)
MAG_SENS = (0.0001, 0.003)


def gating_z(m: Member, Xva: np.ndarray, yva: np.ndarray, rule=None) -> tuple[float, float]:
    """Paired test of the gating gain over validation rows: mean and z of per-row (loss - gated loss). Accepted rows
    inside the gate are excluded (each would cost 13.8 nats and swamp the test; adversary 3, finding 2); the construct
    check bounds how many there are."""
    keep = ~((yva == 1) & gate_mask(Xva, rule))
    Xva, yva = Xva[keep], yva[keep]
    d = row_losses(yva, p_accept(m, Xva)) - row_losses(yva, p_gated(m, Xva, rule))
    m.gain_split = {"reject_row_savings": float(d[yva == 0].sum() / len(d)),
                    "accept_row_penalty": float(-d[yva == 1].sum() / len(d))}
    sd = float(d.std(ddof=1))
    mean = float(d.mean())
    return mean, (mean / (sd / math.sqrt(len(d))) if sd > 0 else (math.inf if mean > 0 else (-math.inf if mean < 0 else 0.0)))


def heldout_leaf_stats(m: Member, Xref: np.ndarray, yref: np.ndarray) -> dict:
    """Leaf P(accept) and n estimated on held-out rows. CART chooses splits to maximise leaf differences, so training
    leaf values are selection-biased: on pure noise a depth-3 tree showed a 3.8-SE gap between leaves."""
    leaf_of = m.tree.apply(Xref[:, m.cols].astype(np.float32))
    stats = {}
    for leaf in np.unique(leaf_of):
        yy = yref[leaf_of == leaf]
        n, k = int(len(yy)), int(yy.sum())
        # (k+0.5)/(n+1): a held-out p of exactly 0 or 1 would give SE 0 (adversary 2, finding 3)
        stats[int(leaf)] = ((k + 0.5) / (n + 1), n)
    return stats


def monotone_violation(m: Member, Xref: np.ndarray = None, yref: np.ndarray = None, delta: float = DELTA) -> bool:
    """Exact over leaf boxes: a violation is a pair of leaves A, B where some point of B dominates some point of A
    (score at least as high, DTI at least as low, every other feature overlapping) and p(A) - p(B) exceeds both delta
    and Z_MONO standard errors of the difference. A fixed delta alone flags leaf noise: at min leaf 1000-3000 the SE of
    a leaf-pair difference is about 0.012 (constructed rule and flat-noise trees failed with delta = 0.02 alone)."""
    boxes = [(b, p, n) for b, p, n, _ in leaf_boxes(m, with_n=True)]
    if Xref is not None:
        st = heldout_leaf_stats(m, Xref, yref)
        # look up by node id, not by position (adversary 2, finding 4); a leaf with < 100 held-out rows says nothing
        boxes = [(b, *st[j]) for (b, _, _, j) in leaf_boxes(m, with_n=True) if j in st]
        boxes = [x for x in boxes if x[2] >= MIN_LEAF_HELDOUT]
    def iv(box, f):
        return box.get(f, (-np.inf, np.inf))
    for a, pa, na in boxes:
        for b, pb, nb in boxes:
            se = math.sqrt(pa * (1 - pa) / max(na, 1) + pb * (1 - pb) / max(nb, 1))
            if pa - pb <= max(delta, Z_MONO * se):
                continue
            ok = True
            for f in range(len(FEATURES)):
                (alo, ahi), (blo, bhi) = iv(a, f), iv(b, f)
                if f == SCORE:
                    ok &= bhi > alo                 # some score in B >= some score in A
                elif f == DTI:
                    ok &= blo < ahi                 # some DTI in B <= some DTI in A
                else:
                    ok &= (blo < ahi) and (alo < bhi)   # overlap
                if not ok:
                    break
            if ok:
                return True
    return False


def band(members: list[Member], eps: float) -> list[Member]:
    best = min(m.val_loss for m in members)
    return [m for m in members if m.val_loss <= (1 + eps) * best]


# ---------- reason fidelity (secondary) ----------

def first_reason(m: Member, x: np.ndarray) -> str | None:
    """The single feature whose change most raises P(accept) for x: each feature is moved across each of its split
    thresholds (to the float32 just above / at-or-below), others fixed. None if no single change raises it."""
    base = float(p_accept(m, x[None, :])[0])
    tr = m.tree.tree_
    best, best_gain = None, 0.0
    for local, f in enumerate(m.cols):
        ts = {float(tr.threshold[j]) for j in range(tr.node_count) if tr.feature[j] == local}
        gain = 0.0
        for t in ts:
            for v in straddle32(t):
                z = x.copy(); z[f] = v
                gain = max(gain, float(p_accept(m, z[None, :])[0]) - base)
        if gain > best_gain + 1e-12:
            best, best_gain = FEATURES[f], gain
    return best


def straddle32(t: float) -> tuple[float, float]:
    """float32 values at-or-below and just above t (sklearn compares float32 X against t in double)."""
    f = np.float32(t)
    if float(f) <= t:
        lo, hi = f, np.nextafter(f, np.float32(np.inf))
    else:
        lo, hi = np.nextafter(f, np.float32(-np.inf)), f
    return float(lo), float(hi)


def reason_fidelity(P: list[Member], Xte: np.ndarray, n_app: int = 300, seed: int = SEED) -> dict:
    """Over test applicants the written rule declines (no tolerance), for each member: the share of (applicant,
    member) pairs whose first reason (the single feature change that most raises P(accept)) is outside the rule's
    own reasons."""
    d = written_rule_declines(Xte[:, SCORE], Xte[:, DTI])
    idx = np.where(d)[0]
    if not len(idx) or not P:
        return {"pairs": 0, "outside_share": float("nan")}
    rng = np.random.RandomState(seed)
    idx = rng.choice(idx, min(n_app, len(idx)), replace=False)
    pairs = outside = none = 0
    for i in idx:
        x = Xte[i]
        truth = true_reasons(x[SCORE], x[DTI])
        for m in P:
            r = first_reason(m, x)
            pairs += 1
            if r is None:
                none += 1
            elif r not in truth:
                outside += 1
    return {"pairs": pairs, "outside_share": (outside / pairs) if pairs else float("nan"),
            "no_single_reason_share": (none / pairs) if pairs else float("nan")}


# ---------- verdict ----------

def material(gain: float, z: float, best: float) -> int:
    """+1 materially corrected, -1 materially worsened, 0 neither: paired |z| > 3 AND |gain| > 0.001 * best loss."""
    if z > Z_GAIN and gain > MAG_FLOOR * best:
        return 1
    if z < -Z_GAIN and gain < -MAG_FLOOR * best:
        return -1
    return 0


def eps_star_of(excess, mat, dominance=0.5):
    for e in EPS_GRID:
        inband = excess <= e
        n = int(inband.sum())
        if n >= MIN_G and np.mean(mat[inband] == 1) > dominance:
            return float(e)
    return float("inf")


def seed_metrics(members, Xva, yva, Xte, eps_list=EPSILONS, with_reasons=False) -> dict:
    mono = [m for m in members if not monotone_violation(m, Xva, yva)]
    if not mono:
        return {"void": True, "n_sampled": len(members), "n_monotone": 0}
    best = min(m.val_loss for m in mono)
    rows = []
    for m in mono:
        g, z = gating_z(m, Xva, yva)
        gf, zf = gating_z(m, Xva, yva, floors_declines)
        rows.append((m.val_loss / best - 1.0, g, z, material(g, z, best), material(gf, zf, best), m))
    rows.sort(key=lambda r: r[0])
    excess = np.array([r[0] for r in rows])
    mat = np.array([r[3] for r in rows])
    matf = np.array([r[4] for r in rows])
    curve = []
    for e in EPS_GRID:
        inband = excess <= e
        n = int(inband.sum())
        curve.append((float(e), n, float(np.mean(mat[inband] == 1)) if n else float("nan")))
    by_eps = {}
    for e in eps_list:
        G = [r for r in rows if r[0] <= e]
        by_eps[str(e)] = {"n_G": len(G), "share_corrected": float(np.mean([r[3] == 1 for r in G])) if G else float("nan"),
                          "gain_median": float(np.median([r[1] for r in G])) if G else float("nan")}
    best_row = rows[0]
    out = {"void": int(np.sum(excess <= 0.05)) < MIN_G, "n_sampled": len(members), "n_monotone": len(mono),
           "best_loss": best, "eps_star": eps_star_of(excess, mat), "curve": curve, "by_eps": by_eps,
           # sensitivity (adversary 3, findings 5 and 7): floors-only gate, and 25% / 75% dominance
           "eps_star_floors_only": eps_star_of(excess, matf),
           "eps_star_dominance_25": eps_star_of(excess, mat, 0.25), "eps_star_dominance_75": eps_star_of(excess, mat, 0.75),
           "gated_accepts_in_validation": int(np.sum((yva == 1) & gate_mask(Xva))),
           "best_tree": {"gain": best_row[1], "z": best_row[2], "material": best_row[3],
                         "gain_split": getattr(best_row[5], "gain_split", None)},
           "pooling_gain_median": float(np.median([r[1] for r in rows if r[3] == 1])) if (mat == 1).any() else float("nan")}
    if with_reasons:
        out["reason_fidelity"] = reason_fidelity([r[5] for r in rows if r[0] <= PRIMARY_EPS], Xte)
    return out


def region(eps_star: float) -> str:
    if eps_star > EPS_STAR_KILL:
        return "KILL"
    if eps_star < EPS_STAR_MATTERS:
        return "POLICY_MATTERS"
    return "DEPENDS_ON_EPSILON"


def seed_verdict(s: dict) -> str:
    """r5: by the region of epsilon*. (CONTRADICTS removed: it can't fire before CONSTRUCT_INVALID; adversary 3.)"""
    return "VOID" if s["void"] else region(s["eps_star"])


def overall_verdict(per_seed: list[str]) -> str:
    if sum(v == "VOID" for v in per_seed) > 1:
        return "INCONCLUSIVE"
    for v in ("KILL", "POLICY_MATTERS", "DEPENDS_ON_EPSILON"):
        if sum(x == v for x in per_seed) >= 4:
            return v
    return "INCONCLUSIVE"


def split(X, y, seed=SEED):
    rng = np.random.RandomState(seed)
    parts = {"tr": [], "va": [], "te": []}
    for c in (0, 1):
        ix = rng.permutation(np.where(y == c)[0])
        a, b = int(0.55 * len(ix)), int(0.77 * len(ix))
        parts["tr"].append(ix[:a]); parts["va"].append(ix[a:b]); parts["te"].append(ix[b:])
    return {k: np.concatenate(v) for k, v in parts.items()}


def run(X, y, seeds=SEEDS, n_trees=N_TREES, eps_list=EPSILONS, reasons=True, capacity=True) -> dict:
    sp = split(X, y)
    Xtr, ytr, Xva, yva, Xte = X[sp["tr"]], y[sp["tr"]], X[sp["va"]], y[sp["va"]], X[sp["te"]]
    cs = construct_share(X, y)
    res = {"n": int(len(y)), "accept_share": float(y.mean()), "construct_share": cs, "seeds": {}}
    if cs > CONSTRUCT_MAX_SHARE:
        res["verdict"] = "CONSTRUCT_INVALID"
        return res
    for s in seeds:
        members = sample_trees(Xtr, ytr, Xva, yva, s, n_trees)
        res["seeds"][s] = seed_metrics(members, Xva, yva, Xte, eps_list, with_reasons=reasons)
    per = [seed_verdict(res["seeds"][s]) for s in seeds]
    stars = [res["seeds"][s]["eps_star"] for s in seeds if not res["seeds"][s]["void"]]
    res["per_seed"], res["verdict"] = per, overall_verdict(per)
    res["eps_star_median"] = float(np.median(stars)) if stars else float("nan")
    res["eps_star_range"] = [float(min(stars)), float(max(stars))] if stars else None
    # capacity check: deeper trees must put epsilon* in the same region, or the verdict is about tree size
    if capacity and res["verdict"] in ("KILL", "POLICY_MATTERS", "DEPENDS_ON_EPSILON"):
        global DEPTHS
        old = DEPTHS
        DEPTHS = CAPACITY_DEPTHS
        try:
            cap = {}
            for s in seeds[:CAPACITY_SEEDS]:
                members = sample_trees(Xtr, ytr, Xva, yva, s + 1000, n_trees)
                cap[s + 1000] = seed_metrics(members, Xva, yva, Xte, eps_list)["eps_star"]
        finally:
            DEPTHS = old
        res["capacity_eps_star"] = cap
        res["capacity_regions"] = [region(v) for v in cap.values()]
        if any(r != res["verdict"] for r in res["capacity_regions"]):
            res["primary_verdict"], res["verdict"] = res["verdict"], "CAPACITY_DEPENDENT"
    return res


# ---------- data ----------

def load(root: Path):
    parts = []
    for ch in pd.read_csv(root / "data/rejected_2007_to_2018Q4.csv", chunksize=2_000_000,
                          usecols=["Application Date", "Risk_Score", "Debt-To-Income Ratio", "Amount Requested",
                                   "Employment Length", "Policy Code"]):
        d = pd.to_datetime(ch["Application Date"], errors="coerce")
        ch = ch[(d >= WINDOW[0]) & (d <= WINDOW[1]) & (pd.to_numeric(ch["Policy Code"], errors="coerce") == 0)]
        parts.append(pd.DataFrame({"score": pd.to_numeric(ch["Risk_Score"], errors="coerce"),
                                   "dti": ch["Debt-To-Income Ratio"].map(parse_pct),
                                   "amount": pd.to_numeric(ch["Amount Requested"], errors="coerce"),
                                   "emp": ch["Employment Length"].map(emp_code), "y": 0}))
    rej = pd.concat(parts, ignore_index=True)
    a = pd.read_csv(root / "data/accepted_2007_to_2018Q4.csv", low_memory=False,
                    usecols=["issue_d", "fico_range_low", "dti", "loan_amnt", "emp_length", "policy_code",
                             "application_type", "disbursement_method"])
    mth = pd.to_datetime(a["issue_d"], format="%b-%Y", errors="coerce").dt.to_period("M")
    keep = ((mth >= pd.Period(ACC_MONTHS[0], "M")) & (mth <= pd.Period(ACC_MONTHS[1], "M"))
            & (pd.to_numeric(a["policy_code"], errors="coerce") == 1)
            & (a["application_type"].fillna("Individual") == "Individual")
            & (a["disbursement_method"].fillna("Cash") == "Cash"))
    a = a[keep]
    acc = pd.DataFrame({"score": pd.to_numeric(a["fico_range_low"], errors="coerce"),
                        "dti": pd.to_numeric(a["dti"], errors="coerce"),
                        "amount": pd.to_numeric(a["loan_amnt"], errors="coerce"),
                        "emp": a["emp_length"].map(emp_code), "y": 1})
    df = pd.concat([rej, acc], ignore_index=True)
    counts = {"rejects": len(rej), "accepts": len(acc),
              # coded -1 per file: if the files code missing employment differently, emp would mark the file of origin
              "emp_minus1_share": {"rejects": float((rej["emp"] == -1).mean()), "accepts": float((acc["emp"] == -1).mean())}}
    before = len(df)
    df = df.dropna(subset=["score", "dti", "amount"])
    counts["excluded_missing_score_dti_or_amount"] = before - len(df)   # pre-reg §2 says score, DTI or amount
    df["score"] = bucket5(df["score"].to_numpy())
    return df[FEATURES].to_numpy(dtype=float), df["y"].to_numpy(dtype=int), counts


def main():
    root = Path(__file__).resolve().parents[2]
    X, y, counts = load(root)
    res = run(X, y)
    res["counts"] = counts
    print(json.dumps(res, indent=1, default=str))


if __name__ == "__main__":
    main()

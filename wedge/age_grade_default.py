"""Grade-vs-default age decomposition: does LC grade price the young-end age gradient PAST
what realized default justifies, and does the sign flip (old subsidized)?

Pure statistics, no file I/O. The runner (scripts/age_grade_default.py) handles loading.
See docs/superpowers/specs/2026-06-22-age-grade-default-design.md for the design + frozen ledger.

Lineage: descendant of wedge/age_residual.py. ~182 bps of the young-end age pricing was shown
to live inside LC grade; this module asks whether that 182 tracks realized default (grade
exonerated) or floats free of it (lawful-but-illegitimate — the empty-chair instance).

The yardstick is anchored to DEFAULT, not to LC's own price (Tony's reframe): "justified price"
is the rate that a loan's realized-default risk maps to, estimated empirically from the data. A
loan priced ABOVE its default-justified rate is being charged past what its default justifies.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from sklearn.isotonic import IsotonicRegression
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

from wedge.age_residual import AGE_BANDS, DEFAULT_CONTROLS

# Risk features for predicted default. Same lawful controls as the parent's pricing residual,
# plus C(purpose) handled separately as a categorical. Age is DELIBERATELY excluded — it is the
# thing under test; a default model that saw age would bake the age signal into the yardstick.
RISK_NUMERIC = list(DEFAULT_CONTROLS)  # fico_mid, dti, annual_inc, loan_amnt, term_months


@dataclass
class BandExcess:
    """Per-band excess of actual rate over default-justified rate, in bps, with bootstrap CI.

    band_bps[i]   = mean(actual_int_rate - justified_rate) over band i, in basis points.
                    POSITIVE = priced past default-justified (bias-against-interest at young end).
                    NEGATIVE = subsidized below default-justified (the old-end question).
    band_ci[i]    = (lo, hi) 95% bootstrap CI in bps.
    There is NO reference band: excess is absolute vs the default yardstick, by design.
    """
    band_bps: dict
    band_ci: dict
    n_per_band: dict
    map_kind: str            # "isotonic" | "decile"
    scope: str               # "corpus" | "within_grade"


@dataclass
class DefaultRateMap:
    """An empirical, monotone default->rate map: predicted-default probability -> justified rate.

    `justified_rate(p_hat)` returns the rate (percentage points) that level of predicted default
    maps to. Estimated either by isotonic regression or by decile-calibrated means. Both are
    enforced monotone non-decreasing (a non-monotone map is invalid — see assert_monotone)."""
    map_kind: str
    _x: np.ndarray = field(repr=False)   # sorted predicted-default knots
    _y: np.ndarray = field(repr=False)   # justified rate at each knot (monotone non-decreasing)

    def justified_rate(self, p_hat: np.ndarray) -> np.ndarray:
        # piecewise-linear interpolation on the monotone knots; clamp to the knot range
        return np.interp(np.asarray(p_hat, dtype=float), self._x, self._y)


def predicted_default(df: pd.DataFrame, default_col: str = "default",
                      controls: list[str] | None = None) -> np.ndarray:
    """Logistic regression of realized default on lawful risk factors (NOT age).

    Returns per-loan predicted default probability. purpose enters as one-hot. Features are
    standardized so the logistic solver is well-conditioned across income/loan_amnt scales.
    """
    controls = list(RISK_NUMERIC if controls is None else controls)
    d = df.copy()
    X_num = d[controls].astype(float).to_numpy()
    X_num = StandardScaler().fit_transform(X_num)
    if "purpose" in d.columns:
        dummies = pd.get_dummies(d["purpose"], prefix="purpose", drop_first=True)
        X = np.hstack([X_num, dummies.to_numpy(dtype=float)]) if dummies.shape[1] else X_num
    else:
        X = X_num
    y = d[default_col].astype(int).to_numpy()
    clf = LogisticRegression(max_iter=1000, C=1e6)  # near-unpenalized; we want calibration not shrinkage
    clf.fit(X, y)
    return clf.predict_proba(X)[:, 1]


def fit_default_rate_map(p_hat: np.ndarray, int_rate: np.ndarray,
                         map_kind: str = "isotonic", n_deciles: int = 10) -> DefaultRateMap:
    """Estimate the monotone default->rate map from (predicted-default, actual rate).

    isotonic: IsotonicRegression(increasing=True) — the rate as a monotone function of p_hat,
              read off as the calibrated yardstick.
    decile:   bin p_hat into quantile deciles, take mean rate per decile, then enforce
              monotone non-decreasing via a cumulative max (the spec requires monotonicity).

    Both produce knots (x sorted ascending, y non-decreasing) consumed by DefaultRateMap.interp.
    """
    p_hat = np.asarray(p_hat, dtype=float)
    int_rate = np.asarray(int_rate, dtype=float)
    if map_kind == "isotonic":
        iso = IsotonicRegression(increasing=True, out_of_bounds="clip")
        iso.fit(p_hat, int_rate)
        # np.interp needs strictly-increasing x: collapse duplicate p_hat to unique knots. Sort by
        # p_hat, then np.unique(return_index) gives the FIRST position of each unique value in the
        # sorted array; the isotonic prediction is non-decreasing along sorted x, so the fitted
        # rate at each unique knot is y_sorted[first_index]. Fully vectorized: O(n log n), no
        # per-value mask scan. (The earlier list-comprehension `[y[p_hat==xv].max() ...]` was
        # O(unique * n) — ~1e12 ops on 1.3M near-unique floats; that was the 48-hour-class wedge.)
        order = np.argsort(p_hat, kind="mergesort")
        p_sorted = p_hat[order]
        y_sorted = iso.predict(p_sorted)
        x_unique, first_idx = np.unique(p_sorted, return_index=True)
        y_at_unique = np.maximum.accumulate(y_sorted[first_idx])  # guard float jitter -> monotone
        return DefaultRateMap(map_kind="isotonic", _x=x_unique, _y=y_at_unique)
    elif map_kind == "decile":
        deciles = pd.qcut(p_hat, q=n_deciles, labels=False, duplicates="drop")
        dd = pd.DataFrame({"p": p_hat, "r": int_rate, "d": deciles})
        grp = dd.groupby("d").agg(p_mean=("p", "mean"), r_mean=("r", "mean")).sort_values("p_mean")
        x = grp["p_mean"].to_numpy()
        y = np.maximum.accumulate(grp["r_mean"].to_numpy())  # enforce monotone non-decreasing
        return DefaultRateMap(map_kind="decile", _x=x, _y=y)
    raise ValueError(f"unknown map_kind {map_kind!r}")


def assert_monotone(m: DefaultRateMap, tol: float = 1e-9) -> None:
    """Guard: the default->rate map MUST be monotone non-decreasing. If a higher realized default
    mapped to a LOWER justified rate the yardstick is meaningless. Raise loudly (spec requirement),
    never silently produce garbage downstream."""
    diffs = np.diff(m._y)
    if np.any(diffs < -tol):
        bad = int(np.argmin(diffs))
        raise ValueError(
            f"default->rate map ({m.map_kind}) is NOT monotone: y[{bad}]={m._y[bad]:.4f} -> "
            f"y[{bad+1}]={m._y[bad+1]:.4f} (drop {diffs[bad]:.4f}). Benchmark invalid."
        )


_BOOTSTRAP_MAX_N = 50_000  # above this, the percentile bootstrap of a mean is indistinguishable
                           # from the normal-theory CI; we use the closed form to stay tractable.


def _bootstrap_ci(residuals: np.ndarray, n_boot: int = 1000, seed: int = 0,
                  alpha: float = 0.05) -> tuple[float, float]:
    """95% CI for the MEAN of per-loan (actual - justified) residuals, in bps.

    For small bands: percentile bootstrap (resample with replacement, n_boot draws), looped so
    peak memory is O(n) not O(n_boot*n). For large bands (n > _BOOTSTRAP_MAX_N): the bootstrap
    distribution of a sample mean is, by the CLT, Normal(mean, SE^2) with SE = s/sqrt(n); the
    percentile bootstrap CI converges to mean +- z*SE. We use that closed form — at n in the
    hundreds of thousands the two agree to well under a basis point, and materializing a
    n_boot x n resample matrix (the original code) is ~0.5 GB per band and was the runtime wedge.
    """
    residuals = np.asarray(residuals, dtype=float)
    n = len(residuals)
    if n == 0:
        return (float("nan"), float("nan"))
    z = 1.959963984540054  # two-sided 95%
    if n > _BOOTSTRAP_MAX_N:
        mean = residuals.mean() * 100.0
        se = residuals.std(ddof=1) / np.sqrt(n) * 100.0
        return (float(mean - z * se), float(mean + z * se))
    rng = np.random.default_rng(seed)
    means = np.empty(n_boot)
    for b in range(n_boot):
        means[b] = residuals[rng.integers(0, n, size=n)].mean()
    means *= 100.0  # pp -> bps
    lo = float(np.percentile(means, 100 * alpha / 2))
    hi = float(np.percentile(means, 100 * (1 - alpha / 2)))
    return (lo, hi)


def band_excess_corpus(df: pd.DataFrame, map_kind: str = "isotonic",
                       default_col: str = "default", n_boot: int = 1000,
                       seed: int = 0, p_hat: np.ndarray | None = None) -> BandExcess:
    """CORPUS benchmark (primary): fit the default->rate map age-blind on the WHOLE population,
    apply to every loan, and measure per-band mean(actual - justified) in bps.

    The young's genuinely higher thin-file default is BUILT INTO the justified price, so a
    surviving young-end positive excess is CONSERVATIVE — it has already netted out the thin-file
    'they're just riskier' defense. That is the version a lawmaker can't unsee.

    `p_hat` (predicted default per loan) may be supplied to skip the logistic refit — it is
    deterministic given the data, so the runner computes it ONCE and threads it through every
    scope/map call (the refit on 1.34M rows was the runtime wedge).
    """
    d = df.copy()
    if p_hat is None:
        p_hat = predicted_default(d, default_col=default_col)
    p_hat = np.asarray(p_hat, dtype=float)
    m = fit_default_rate_map(p_hat, d["int_rate"].to_numpy(), map_kind=map_kind)
    assert_monotone(m)
    justified = m.justified_rate(p_hat)
    d["_excess"] = d["int_rate"].to_numpy() - justified
    return _summarize_band_excess(d, map_kind=map_kind, scope="corpus",
                                  n_boot=n_boot, seed=seed)


def band_excess_within_grade(df: pd.DataFrame, map_kind: str = "isotonic",
                             default_col: str = "default", grade_col: str = "grade",
                             n_boot: int = 1000, seed: int = 0,
                             p_hat: np.ndarray | None = None) -> BandExcess:
    """WITHIN-GRADE foil: fit the default->rate map SEPARATELY within each grade, then measure
    per-band excess pooled across grades. If young-end excess is large in CORPUS but vanishes
    here, GRADE absorbed the age pricing — the corpus-minus-within-grade gap is the laundering
    measure. Within-grade alone exonerates grade by construction, hence foil not headline.

    predicted-default is fit once on the whole population (same risk model); only the default->rate
    MAP is re-estimated within grade, so the contrast is purely 'which yardstick' not 'which risk'.
    `p_hat` may be supplied to skip the logistic refit (see band_excess_corpus).
    """
    d = df.copy()
    if p_hat is None:
        p_hat = predicted_default(d, default_col=default_col)
    d["_p_hat"] = np.asarray(p_hat, dtype=float)
    d["_excess"] = np.nan
    for g, sub in d.groupby(grade_col):
        if len(sub) < 100:  # too thin to calibrate a within-grade map; leave excess NaN, drop later
            continue
        m = fit_default_rate_map(sub["_p_hat"].to_numpy(), sub["int_rate"].to_numpy(),
                                 map_kind=map_kind)
        assert_monotone(m)
        justified = m.justified_rate(sub["_p_hat"].to_numpy())
        d.loc[sub.index, "_excess"] = sub["int_rate"].to_numpy() - justified
    d = d.dropna(subset=["_excess"]).copy()
    return _summarize_band_excess(d, map_kind=map_kind, scope="within_grade",
                                  n_boot=n_boot, seed=seed)


def _summarize_band_excess(d: pd.DataFrame, map_kind: str, scope: str,
                           n_boot: int, seed: int) -> BandExcess:
    band_bps, band_ci, n_per_band = {}, {}, {}
    for i in range(len(AGE_BANDS)):
        sub = d[d["age_band"] == i]
        n_per_band[i] = int(len(sub))
        if len(sub) == 0:
            band_bps[i] = float("nan")
            band_ci[i] = (float("nan"), float("nan"))
            continue
        resid = sub["_excess"].to_numpy()
        band_bps[i] = float(resid.mean() * 100.0)  # pp -> bps
        # vary the bootstrap seed by band so bands aren't resampled in lockstep
        band_ci[i] = _bootstrap_ci(resid, n_boot=n_boot, seed=seed + i)
    return BandExcess(band_bps=band_bps, band_ci=band_ci, n_per_band=n_per_band,
                      map_kind=map_kind, scope=scope)


def grade_vs_default_rail(df: pd.DataFrame, default_col: str = "default",
                          grade_col: str = "grade") -> dict:
    """Sanity rail (cheap, off the same age bands): does grade encode age beyond risk MORE than
    default does? Two band regressions on the same lawful controls:

      grade_numeric ~ C(age_band) + risk     (grade_numeric: A..G -> 1..7)
      default       ~ C(age_band) + risk

    Per band, compare the age coefficient in the grade regression vs the default regression, each
    rescaled to its own outcome's std (a comparable standardized age->outcome loading). If grade's
    standardized young-end age loading EXCEEDS default's, grade prices age the default data doesn't
    justify — cross-checks the benchmark. sub_grade ignored (letter granularity suffices; YAGNI).
    """
    d = df.copy()
    grade_map = {g: i + 1 for i, g in enumerate("ABCDEFG")}
    d["grade_numeric"] = d[grade_col].map(grade_map).astype(float)
    d = d.dropna(subset=["grade_numeric"]).copy()
    numeric = " + ".join(RISK_NUMERIC)
    ref = 5  # [45,50), the canonical reference band (present in full data)

    def _band_age_coefs(outcome: str) -> dict:
        d2 = d.copy()
        d2["_band"] = pd.Categorical(d2["age_band"])
        formula = (f"{outcome} ~ C(_band, Treatment(reference={ref})) + {numeric} + C(purpose)")
        m = smf.ols(formula, data=d2).fit()
        sd = float(d2[outcome].std())
        coefs = {}
        for i in range(len(AGE_BANDS)):
            if i == ref:
                coefs[i] = 0.0
                continue
            term = f"C(_band, Treatment(reference={ref}))[T.{i}]"
            coefs[i] = float(m.params[term]) / sd if term in m.params.index else float("nan")
        return coefs

    grade_coefs = _band_age_coefs("grade_numeric")
    default_coefs = _band_age_coefs(default_col)
    # grade prices age past default where the standardized grade loading exceeds the default loading
    excess_loading = {i: grade_coefs[i] - default_coefs[i] for i in range(len(AGE_BANDS))}
    return {
        "grade_age_loading_std": grade_coefs,
        "default_age_loading_std": default_coefs,
        "grade_minus_default_loading": excess_loading,
        "reference_band": ref,
        "note": "standardized age->outcome loading per band; positive grade-minus-default = grade "
                "prices age beyond what default justifies.",
    }

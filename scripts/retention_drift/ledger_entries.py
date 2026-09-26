"""Write the retention-drift observations levadura asked to cite (reply 2026-09-26) into the
governance ledger. Values are read from the installed shap sources and runs/retention_drift/results.json."""
import json, re, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "ledger"))
from ledger import append, verify

VERS = {"v2021": "0.39.0", "v2022": "0.41.0", "v2023p": "0.41.0", "v2024": "0.46.0", "v2025": "0.48.0", "v2026": "0.52.0"}
defaults, warncat = {}, {}
for v, sv in VERS.items():
    src = next((ROOT / f"envs_rd/{v}/lib").glob("python3*/site-packages/shap/explainers/_kernel.py")).read_text()
    m = re.search(r'kwargs\.get\("l1_reg", "([^"]+)"\)', src)
    defaults[f"shap {sv}"] = m.group(1) if m else None
    w = re.search(r'l1_reg=.auto. is deprecated[^\n]*\n?[^\n]*?(DeprecationWarning|FutureWarning|UserWarning)', src)
    warncat[f"shap {sv}"] = w.group(1) if w else "no l1_reg deprecation warning emitted"

append({
    "observed_at": "2025-06-12T00:00:00+00:00",
    "quantity": "shap_kernelexplainer_l1_reg_default",
    "population": {"package": "shap", "file": "shap/explainers/_kernel.py", "versions": list(defaults),
                   "envs": "governance envs_rd/<vintage>, built by scripts/retention_drift/build_envs.sh (uv --exclude-newer <year>-07-01)"},
    "instrument": {"name": "scripts/retention_drift/ledger_entries.py", "version": "1",
                   "method": "regex kwargs.get(\"l1_reg\", <default>) and the l1_reg='auto' deprecation warning class in the installed source of each version"},
    "value": {"default_by_version": defaults, "auto_deprecation_warning_class": warncat},
    "caveat": "observed_at = PyPI upload date of shap 0.48.0, the first version in this study carrying the new default; 0.47.x was not inspected, so the change happened in (0.46.0, 0.48.0]. DeprecationWarning is hidden by Python's default warning filters.",
})

res = json.load(open(ROOT / "runs/retention_drift/results.json"))
cells = {}
for key, pair in res["pairs"].items():
    if not isinstance(pair, dict) or pair["delta"] == 0:
        continue
    for meth in ("kernel_default", "kernel_pinned"):
        c = pair["cells"].get(f"xgb_{meth}", {})
        if c.get("status") == "ok":
            cells.setdefault(meth, {})[key] = {"R": c["R"], "R_ci95": c["R_ci"], "n_denied": c["n"], "arm": pair["arm"]}
append({
    "observed_at": "2026-09-25T00:00:00+00:00",
    "quantity": "reg_b_top4_reason_set_change_rate_kernelshap_default_vs_pinned",
    "population": {"substrate": "LendingClub accepted 2007-2018Q4, 24 origination features, 1000 eval rows, denied = top 20% P(default)",
                   "model": "xgboost XGBClassifier archived as native JSON at origin vintage", "prereg": "governance dc12f1a", "raw": "governance 1a9be04", "result_note": "governance 67f4e74"},
    "instrument": {"name": "scripts/retention_drift/analyze.py", "version": "1a9be04",
                   "method": "R = share of denied applicants whose unordered top-4 positive KernelSHAP attribution set differs from the origin's; bootstrap 2000; default = l1_reg omitted, pinned = l1_reg=False; np.random.seed fixed"},
    "value": cells,
    "caveat": "Nonzero default-arm R occurs only when the contest stack is shap>=0.48 and the origin's is older. Pinned arm R=0 everywhere. Same-vintage repeats are 0 by construction (seeded), so this is not drift beyond sampling noise, it is a deterministic semantic change. Omitting the argument contradicts the study's own 'store everything' premise; the blind review (REJECT as FAccT) conceded that. One substrate, one model class for this cell.",
})
print("ledger entries:", verify())

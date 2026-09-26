"""Correct obs-0001's warning-class field (regex missed a multi-line warnings.warn call in shap 0.46).
Append-only: obs-0001 stays; this entry supersedes its auto_deprecation_warning_class field."""
import re, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "ledger"))
from ledger import append, verify

VERS = {"v2021": "0.39.0", "v2022": "0.41.0", "v2024": "0.46.0", "v2025": "0.48.0", "v2026": "0.52.0"}
out = {}
for v, sv in VERS.items():
    src = next((ROOT / f"envs_rd/{v}/lib").glob("python3*/site-packages/shap/explainers/_kernel.py")).read_text()
    live = [l for l in src.splitlines() if 'if self.l1_reg == "auto":' in l and not l.strip().startswith("#")]
    if not live:
        out[f"shap {sv}"] = "none (the warning block is commented out)"
        continue
    i = src.index(live[0])
    block = src[i:i + 600]
    cat = re.search(r"(DeprecationWarning|FutureWarning|UserWarning)", block)
    out[f"shap {sv}"] = cat.group(1) if cat else "warnings.warn with default category (UserWarning)"
append({
    "observed_at": "2025-06-12T00:00:00+00:00",
    "quantity": "shap_kernelexplainer_l1_reg_auto_warning_class",
    "corrects": "obs-0001.value.auto_deprecation_warning_class",
    "population": {"package": "shap", "file": "shap/explainers/_kernel.py", "versions": list(out)},
    "instrument": {"name": "scripts/retention_drift/ledger_correction_1.py", "version": "1",
                   "method": "locate the first uncommented `if self.l1_reg == \"auto\":` and read the warning class within the next 600 characters"},
    "value": out,
    "caveat": "obs-0001's regex required the message and class on adjacent lines and missed shap 0.46's multi-line call, reporting 'no warning'. Correct reading: 0.46 announced the coming change with a DeprecationWarning (hidden by Python's default filters) that told users to pass l1_reg='num_features(10)' to opt in; 0.48 changed the default. obs-0001's default_by_version field is unaffected.",
})
print("ledger entries:", verify())

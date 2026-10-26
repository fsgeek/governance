"""POST-HOC (not pre-registered): step 1's construct check on the accepted loans it excluded as policy_code 2.

Step 1 kept policy_code == 1 (LendingClub's public program, as pre-registered). Policy Code 2 is LC's own label for
loans outside the public policy, so the 0.0% cap-violation share partly measured LC's sorting (step-2 adversary,
item 1). This reports, for policy_code 2, the same per-regime share at/above the written cap, and the count. Reuses
the frozen harness's functions unchanged."""
import json, sys
from pathlib import Path
import pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parent))
import governs as G

root = Path(__file__).resolve().parents[2]
cols = ["issue_d", "dti", "policy_code", "application_type", "disbursement_method"]
df = pd.read_csv(root / "data/accepted_2007_to_2018Q4.csv", usecols=cols, low_memory=False)
out = {}
for code in (1, 2):
    keep = ((pd.to_numeric(df["policy_code"], errors="coerce") == code)
            & (df["application_type"].fillna("Individual") == "Individual")
            & (df["disbursement_method"].fillna("Cash") == "Cash"))
    sub = df[keep]
    acc = pd.DataFrame({"month": pd.to_datetime(sub["issue_d"], format="%b-%Y", errors="coerce").dt.to_period("M"),
                        "dti": pd.to_numeric(sub["dti"], errors="coerce")}).dropna()
    by_year = acc["month"].dt.year.value_counts().sort_index().to_dict()
    out[f"policy_code_{code}"] = {"n": len(acc), "by_issue_year": {int(k): int(v) for k, v in by_year.items()},
                                  "construct_share_at_or_above_cap": G.construct_check(acc)}
print(json.dumps(out, indent=1))

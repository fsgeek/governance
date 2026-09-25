#!/usr/bin/env bash
# Build one isolated env per vintage: the stack a lender installing on July 1 of YEAR
# would have resolved (uv --exclude-newer), on the CPython minor current at that date.
set -u
cd "$(dirname "$0")/../.."
declare -A PY=( [2021]=3.9 [2022]=3.10 [2023]=3.11 [2024]=3.12 [2025]=3.13 [2026]=3.14 )
for Y in 2021 2022 2023 2024 2025 2026; do
  E=envs_rd/v$Y
  rm -rf $E
  uv venv -q --python ${PY[$Y]} $E 2>&1 | tail -2
  if uv pip install -q --python $E/bin/python --exclude-newer "$Y-07-01T00:00:00Z" \
       shap scikit-learn xgboost numpy scipy pandas pyarrow lime 2> envs_rd/v$Y.err; then
    echo "v$Y OK: $($E/bin/python -c 'import sys,shap,sklearn,xgboost,numpy,scipy,pandas;print(sys.version.split()[0],"shap",shap.__version__,"sklearn",sklearn.__version__,"xgb",xgboost.__version__,"numpy",numpy.__version__,"scipy",scipy.__version__,"pandas",pandas.__version__)' 2>&1 | tail -1)"
  else
    echo "v$Y INSTALL FAILED: $(tail -3 envs_rd/v$Y.err)"
  fi
done

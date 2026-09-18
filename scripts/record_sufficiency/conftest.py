"""Make the flat modules in this directory importable under pytest.

These are scripts, not an installed package: `run_r0_control.py` does
`from metrics import ...` when run from this directory. Adding an __init__.py
would break that; this keeps both entry points working, so tests can be run
from the repo root while the scripts stay directly executable.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

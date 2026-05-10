"""Tests for policy.encoder — policy-graph YAML to constraint object."""

from __future__ import annotations

import textwrap
from pathlib import Path

import pytest

from policy.encoder import (
    PolicyConstraints,
    PolicyValidationError,
    load_policy,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
THIN_DEMO = REPO_ROOT / "policy" / "thin_demo_hmda.yaml"


# ---------------------------------------------------------------------------
# Loading the canonical thin demo
# ---------------------------------------------------------------------------


def test_load_thin_demo_succeeds():
    pc = load_policy(THIN_DEMO)
    assert isinstance(pc, PolicyConstraints)
    assert pc.name == "thin_demo_hmda_mortgage"
    assert pc.status == "illustrative-demonstration"
    assert pc.mandatory_features == ("fico_range_low", "dti", "annual_inc")
    assert pc.prohibited_features == ()
    assert pc.monotonicity_map == {
        "fico_range_low": 1,
        "dti": -1,
        "ltv": -1,
    }
    assert pc.applicable_regime["lien_position"] == "first"


def test_load_thin_demo_str_path():
    pc = load_policy(str(THIN_DEMO))
    assert pc.name == "thin_demo_hmda_mortgage"


# ---------------------------------------------------------------------------
# monotonic_cst alignment
# ---------------------------------------------------------------------------


def test_monotonic_cst_aligned_to_features():
    pc = load_policy(THIN_DEMO)
    features = ["annual_inc", "fico_range_low", "dti", "ltv", "emp_length"]
    cst = pc.monotonic_cst(features)
    # annual_inc unconstrained, fico positive, dti negative, ltv negative, emp_length unconstrained
    assert cst == [0, 1, -1, -1, 0]


def test_monotonic_cst_different_ordering():
    pc = load_policy(THIN_DEMO)
    features = ["ltv", "dti", "fico_range_low", "annual_inc"]
    cst = pc.monotonic_cst(features)
    assert cst == [-1, -1, 1, 0]


def test_monotonic_cst_raises_when_constrained_feature_missing():
    pc = load_policy(THIN_DEMO)
    # fico_range_low is missing — silently dropping would be a real bug.
    with pytest.raises(PolicyValidationError, match="absent from feature list"):
        pc.monotonic_cst(["dti", "ltv", "annual_inc"])


# ---------------------------------------------------------------------------
# is_feature_subset_admissible
# ---------------------------------------------------------------------------


def test_admissible_subset_with_all_mandatory():
    pc = load_policy(THIN_DEMO)
    assert pc.is_feature_subset_admissible(
        ("fico_range_low", "dti", "annual_inc", "ltv")
    )


def test_admissible_minimal_mandatory_only():
    pc = load_policy(THIN_DEMO)
    assert pc.is_feature_subset_admissible(("fico_range_low", "dti", "annual_inc"))


def test_inadmissible_missing_mandatory():
    pc = load_policy(THIN_DEMO)
    # missing annual_inc
    assert not pc.is_feature_subset_admissible(("fico_range_low", "dti", "ltv"))


# ---------------------------------------------------------------------------
# Synthetic policy with prohibited features (thin demo has none)
# ---------------------------------------------------------------------------


SYNTHETIC_WITH_PROHIBITED = textwrap.dedent(
    """
    name: synthetic_with_prohibited
    version: 0.0.1
    status: test-fixture
    constraints:
      monotonicity:
        - feature: income
          direction: positive
        - feature: debt
          direction: negative
      mandatory_features:
        - income
      prohibited_features:
        - zip_code
        - applicant_race
      applicable_regime: {}
    nodes:
      - id: entry
        type: entry
    """
).strip()


def test_synthetic_prohibited_features_rejected(tmp_path: Path):
    p = tmp_path / "synthetic.yaml"
    p.write_text(SYNTHETIC_WITH_PROHIBITED)
    pc = load_policy(p)
    assert pc.prohibited_features == ("zip_code", "applicant_race")

    # Subset with prohibited feature is rejected even if mandatory is present.
    assert not pc.is_feature_subset_admissible(("income", "zip_code"))
    assert not pc.is_feature_subset_admissible(("income", "debt", "applicant_race"))
    # Subset with neither prohibited nor missing-mandatory is admissible.
    assert pc.is_feature_subset_admissible(("income", "debt"))
    # Missing mandatory still rejected.
    assert not pc.is_feature_subset_admissible(("debt",))


# ---------------------------------------------------------------------------
# Malformed YAML — informative errors
# ---------------------------------------------------------------------------


def _write(tmp_path: Path, body: str) -> Path:
    p = tmp_path / "bad.yaml"
    p.write_text(textwrap.dedent(body).strip())
    return p


def test_missing_top_level_key_raises(tmp_path: Path):
    p = _write(
        tmp_path,
        """
        name: x
        version: 0.1
        status: test
        # constraints missing
        nodes:
          - id: entry
            type: entry
        """,
    )
    with pytest.raises(PolicyValidationError, match="constraints"):
        load_policy(p)


def test_missing_constraint_key_raises(tmp_path: Path):
    p = _write(
        tmp_path,
        """
        name: x
        version: 0.1
        status: test
        constraints:
          monotonicity: []
          mandatory_features: []
          # prohibited_features missing
        nodes:
          - id: entry
            type: entry
        """,
    )
    with pytest.raises(PolicyValidationError, match="prohibited_features"):
        load_policy(p)


def test_unknown_monotonicity_direction_raises(tmp_path: Path):
    p = _write(
        tmp_path,
        """
        name: x
        version: 0.1
        status: test
        constraints:
          monotonicity:
            - feature: f
              direction: sideways
          mandatory_features: []
          prohibited_features: []
        nodes:
          - id: entry
            type: entry
        """,
    )
    with pytest.raises(PolicyValidationError, match="direction"):
        load_policy(p)


def test_node_missing_required_field_raises(tmp_path: Path):
    p = _write(
        tmp_path,
        """
        name: x
        version: 0.1
        status: test
        constraints:
          monotonicity: []
          mandatory_features: []
          prohibited_features: []
        nodes:
          - type: entry
        """,
    )
    with pytest.raises(PolicyValidationError, match="id"):
        load_policy(p)


def test_mandatory_and_prohibited_overlap_raises(tmp_path: Path):
    p = _write(
        tmp_path,
        """
        name: x
        version: 0.1
        status: test
        constraints:
          monotonicity: []
          mandatory_features: [foo]
          prohibited_features: [foo]
        nodes:
          - id: entry
            type: entry
        """,
    )
    with pytest.raises(PolicyValidationError, match="both mandatory and prohibited"):
        load_policy(p)


def test_missing_file_raises_filenotfound(tmp_path: Path):
    with pytest.raises(FileNotFoundError):
        load_policy(tmp_path / "does_not_exist.yaml")

"""Construction manifest emission per spec §3.6.

The construction manifest is the regulator-facing artifact that records
exactly what dual-set was built and under which inputs. V1 contract names
the policy (name + version), the hypothesis space, the training sample,
the cost-asymmetric loss parameters (w_T, w_F), the tolerances and
resulting set sizes for both R_T(ε_T) and R_F(ε_F), the surprise model
identifier, and the run id.

The emitter reads ε / set sizes / score labels *directly* from the
EpsilonAdmissibleSet objects returned by the pipeline so the manifest
cannot drift from what was actually constructed. Cost weights w_T and w_F
are taken from the caller (the call site that invoked `build_dual_set`
already chose them; passing them through the manifest avoids brittle
parsing of `score_label` strings).

V1.1-deferred items (OD-10 substrate-axis, OD-15 sensitivity reporting)
are named explicitly so a regulator auditor reading the manifest can see
what is *not* yet reported.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from policy.encoder import PolicyConstraints
from wedge.rashomon import EpsilonAdmissibleSet


def emit_manifest(
    *,
    R_T: EpsilonAdmissibleSet,
    R_F: EpsilonAdmissibleSet,
    policy_constraints: PolicyConstraints,
    w_T: float,
    w_F: float,
    surprise_model_metadata: dict[str, Any],
    run_id: str,
    training_sample_id: str,
    hypothesis_space: str,
) -> dict[str, Any]:
    """Build the construction-manifest dictionary per spec §3.6 V1.

    Required V1 fields:
        policy_name, policy_version, hypothesis_space, training_sample_id,
        w_T, w_F, epsilon_T, epsilon_F, n_R_T, n_R_F, surprise_model_id,
        run_id.

    Additional fields recorded for audit:
        schema_version, policy_status, mandatory_features,
        prohibited_features, score_label_T, score_label_F,
        global_best_value_T, global_best_value_F,
        surprise_model_training_sample, v1_1_deferred.
    """
    return {
        "schema_version": "v1",
        "run_id": run_id,
        "policy_name": policy_constraints.name,
        "policy_version": policy_constraints.version,
        "policy_status": policy_constraints.status,
        "mandatory_features": list(policy_constraints.mandatory_features),
        "prohibited_features": list(policy_constraints.prohibited_features),
        "hypothesis_space": hypothesis_space,
        "training_sample_id": training_sample_id,
        "w_T": w_T,
        "w_F": w_F,
        "epsilon_T": R_T.epsilon,
        "epsilon_F": R_F.epsilon,
        "n_R_T": len(R_T.within_epsilon),
        "n_R_F": len(R_F.within_epsilon),
        "score_label_T": R_T.score_label,
        "score_label_F": R_F.score_label,
        "global_best_value_T": R_T.global_best_value,
        "global_best_value_F": R_F.global_best_value,
        "surprise_model_id": surprise_model_metadata.get("model_id"),
        "surprise_model_training_sample": surprise_model_metadata.get(
            "training_sample_id"
        ),
        "v1_1_deferred": [
            "OD-10 substrate-axis",
            "OD-15 sensitivity reporting",
        ],
    }


def write_manifest(manifest_dict: dict[str, Any], output_path: Path) -> None:
    """Serialize the manifest to JSON (sorted keys, 2-space indent)."""
    output_path.write_text(
        json.dumps(manifest_dict, indent=2, sort_keys=True, default=str)
    )

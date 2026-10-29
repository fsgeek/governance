# Codebook pilot report (Phi-4; pilot codes never enter results)

Responses: 125; parsed per item: 125; failures: none.
Items with ≥1 parsed sample: 25 of 25.

## Stability of categorical fields across the 5 samples (first bet per item)

| field | items stable | values seen (count over samples) |
|---|---|---|
| bettor | 15 / 25 | `ai` 79, `pi` 25, `∅` 19, `unclaimed` 1, `undecidable` 1 |
| forecast_type | 14 / 25 | `pass_fail` 56, `multi_outcome_priced` 21, `∅` 19, `probability` 14, `point_interval` 14, `undecidable` 1 |
| register | 15 / 25 | `load-bearing` 85, `∅` 19, `exploratory` 16, `practice-grade` 5 |
| provenance_category | 3 / 25 | `author ruling` 40, `∅` 19, `ai bet` 11, `pre-registration` 9, `bet` 8, `ai` 4, `pi's decision; never an ai bet` 3, `recommendation` 3 |
| outcome_basis | 10 / 25 | `re-derivable` 61, `no_outcome_given` 25, `∅` 19, `as_reported` 16, `undecidable` 2, `unverifiable pre-registration` 1, `no outcome file given` 1 |
| record_scoring_error | 7 / 25 | `no_outcome_given` 82, `∅` 29, `no_record_scoring_error` 6, `no` 3, `no outcome file given` 2, `no outcome given` 1, `no_error` 1, `no_record_scoring_error_given` 1 |
| observed_vs_descended | 6 / 25 | `no_outcome_given` 81, `∅` 29, `no_observed_vs_descended` 5, `no` 3, `observed` 2, `undecidable` 2, `no outcome given` 1, `no outcome file given` 1 |

## Bets found per file, across samples (disagreement = the unit of analysis is ambiguous)

- `governance:docs/superpowers/specs/2026-05-09-v1-v2-predictive-test-pre-registration.md` (none): [1, 0, 0, 1, 1]
- `governance:working_notes/2026-06-08-ban-out-objective-independence-prereg.md` (none): [3, 3, 0, 3, 3]
- `governance:working_notes/2026-06-10-redundancy-mechanism-prereg.md` (none): [3, 3, 3, 3, 3]
- `hamutay:docs/ingestion-gate-preregistration-20260608.md` (none): [0, 1, 1, 0, 0]
- `hamutay:docs/preregistrations/2026-10-27-a3-loss-record-prereg.md` (none): [4, 4, 4, 4, 4]
- `hamutay:experiments/event_loop/artifact_noninferiority_20260612/PRE_REGISTRATION.md` (same_dir): [1, 1, 1, 1, 1]
- `hamutay:experiments/event_loop/audit_restart_boundary_20260612/PRE_REGISTRATION.md` (same_dir): [1, 1, 1, 1, 1]
- `hamutay:experiments/event_loop/delayed_task_terminal_surface_20260605/PRE_REGISTRATION.md` (same_dir): [1, 1, 1, 1, 1]
- `hamutay:experiments/event_loop/fork_run_identity_des_20260605/PRE_REGISTRATION.md` (same_dir): [4, 4, 4, 4, 4]
- `hamutay:experiments/event_loop/framework_field_reservation_20260605/PRE_REGISTRATION.md` (same_dir): [4, 4, 4, 4, 4]
- `hamutay:experiments/event_loop/generated_continuation_primitive_smoke_20260605/PRE_REGISTRATION.md` (same_dir): [5, 1, 6, 5, 5]
- `hamutay:experiments/event_loop/live_validation_repair_scaffold_20260605/PRE_REGISTRATION.md` (same_dir): [5, 5, 5, 5, 5]
- `hamutay:experiments/event_loop/phase_3d_richer_ipc_ingress_20260619/PRE_REGISTRATION.md` (same_dir): [1, 1, 1, 1, 1]
- `hamutay:experiments/event_loop/scheduler_reentry_diagnostic_20260605/PRE_REGISTRATION.md` (cites_bet): [4, 4, 4, 4, 4]
- `hamutay:experiments/event_loop/terminal_surface_substrate_smoke_20260605/PRE_REGISTRATION.md` (same_dir): [1, 5, 1, 5, 5]
- `hamutay:experiments/identity_claim_table_compression_20260605/PRE_REGISTRATION.md` (same_dir): [4, 4, 4, 4, 4]
- `hamutay:experiments/identity_scaffold_curator_20260604/PRE_REGISTRATION.md` (same_dir): [3, 3, 3, 3, 3]
- `levadura_salvaje:predictions/2026-09-24-fossil-turnover-claude.md` (none): [5, 5, 5, 5, 5]
- `levadura_salvaje:predictions/2026-09-28-retrospective-claude.md` (cites_bet): [8, 8, 8, 8, 8]
- `levadura_salvaje:predictions/2026-10-23-banking-parity-v3-claude.md` (cites_bet): [7, 7, 1, 1, 1]
- `quantumos:docs/superpowers/specs/2026-07-06-field-battery-prereg.md` (cites_bet): [1, 6, 6, 4, 4]
- `tessera:formal/spike/tla-probes/P9/PROBE.md` (same_dir:same_commit:exceeds_context): [0, 0, 4, 0, 0]
- `yupi:docs/d8-attribution-grid-freeze-c1-v0.3.md` (none): [0, 0, 1, 0, 0]
- `yupi:docs/three-arm-prereg-v0.2.md` (none): [0, 0, 0, 0, 0]
- `yupi:docs/w11-heldout-prereg-v0.1.md` (none): [6, 2, 6, 1, 6]

## UNDECIDABLE counts by field

- outcome_basis: 11
- observed_vs_descended: 10
- outcome_as_scored_by_record: 6
- bettor: 1
- forecast_type: 1

## UNDECIDABLE reasons, verbatim

- `hamutay:experiments/event_loop/terminal_surface_substrate_smoke_20260605/PRE_REGISTRATION.md` **outcome_basis**: UNDECIDABLE
- `tessera:formal/spike/tla-probes/P9/PROBE.md` **outcome_basis**: UNDECIDABLE
- `tessera:formal/spike/tla-probes/P9/PROBE.md` **observed_vs_descended**: UNDECIDABLE
- `tessera:formal/spike/tla-probes/P9/PROBE.md` **outcome_basis**: UNDECIDABLE
- `tessera:formal/spike/tla-probes/P9/PROBE.md` **observed_vs_descended**: UNDECIDABLE
- `tessera:formal/spike/tla-probes/P9/PROBE.md` **outcome_basis**: UNDECIDABLE
- `tessera:formal/spike/tla-probes/P9/PROBE.md` **observed_vs_descended**: UNDECIDABLE
- `tessera:formal/spike/tla-probes/P9/PROBE.md` **outcome_basis**: UNDECIDABLE
- `tessera:formal/spike/tla-probes/P9/PROBE.md` **observed_vs_descended**: UNDECIDABLE
- `yupi:docs/w11-heldout-prereg-v0.1.md` **outcome_basis**: UNDECIDABLE
- `yupi:docs/w11-heldout-prereg-v0.1.md` **observed_vs_descended**: UNDECIDABLE
- `yupi:docs/w11-heldout-prereg-v0.1.md` **outcome_as_scored_by_record**: UNDECIDABLE
- `yupi:docs/w11-heldout-prereg-v0.1.md` **outcome_basis**: UNDECIDABLE
- `yupi:docs/w11-heldout-prereg-v0.1.md` **observed_vs_descended**: UNDECIDABLE
- `yupi:docs/w11-heldout-prereg-v0.1.md` **outcome_as_scored_by_record**: UNDECIDABLE
- `yupi:docs/w11-heldout-prereg-v0.1.md` **outcome_basis**: UNDECIDABLE
- `yupi:docs/w11-heldout-prereg-v0.1.md` **observed_vs_descended**: UNDECIDABLE
- `yupi:docs/w11-heldout-prereg-v0.1.md` **outcome_as_scored_by_record**: UNDECIDABLE
- `yupi:docs/w11-heldout-prereg-v0.1.md` **outcome_basis**: UNDECIDABLE
- `yupi:docs/w11-heldout-prereg-v0.1.md` **observed_vs_descended**: UNDECIDABLE
- `yupi:docs/w11-heldout-prereg-v0.1.md` **outcome_as_scored_by_record**: UNDECIDABLE
- `yupi:docs/w11-heldout-prereg-v0.1.md` **outcome_basis**: UNDECIDABLE
- `yupi:docs/w11-heldout-prereg-v0.1.md` **observed_vs_descended**: UNDECIDABLE
- `yupi:docs/w11-heldout-prereg-v0.1.md` **outcome_as_scored_by_record**: UNDECIDABLE
- `yupi:docs/w11-heldout-prereg-v0.1.md` **outcome_basis**: UNDECIDABLE
- `yupi:docs/w11-heldout-prereg-v0.1.md` **observed_vs_descended**: UNDECIDABLE
- `yupi:docs/w11-heldout-prereg-v0.1.md` **outcome_as_scored_by_record**: UNDECIDABLE
- `yupi:docs/d8-attribution-grid-freeze-c1-v0.3.md` **bettor**: UNDECIDABLE
- `yupi:docs/d8-attribution-grid-freeze-c1-v0.3.md` **forecast_type**: UNDECIDABLE

## codebook_problems, verbatim

- `governance:working_notes/2026-06-08-ban-out-objective-independence-prereg.md` **exclusion of pre-registrations**: The content in the file is exploratory and pre-registration, excluded from Q1 but eligible for Q2 with label `prereg_unverifiable`. The file does not contain a fixed forecast with an OpenTimestamps stamp from `8c144c0` (2026-06-03) onward.
- `governance:working_notes/2026-06-08-ban-out-objective-independence-prereg.md` **bet definition**: The file does not contain a fixed forecast (bet) with a freeze commit and an OpenTimestamps stamp that predates the outcome commit. It contains predictions and exploratory notes.
- `governance:working_notes/2026-06-08-ban-out-objective-independence-prereg.md` **outcome scoring**: No outcome file is given, so the outcome as scored by the record cannot be determined.
- `governance:working_notes/2026-06-10-redundancy-mechanism-prereg.md` **outcome_as_scored_by_record**: No outcome file given, so cannot provide a verbatim outcome.
- `governance:working_notes/2026-06-10-redundancy-mechanism-prereg.md` **outcome_basis**: No outcome file given, so cannot determine the basis of scoring.
- `governance:working_notes/2026-06-10-redundancy-mechanism-prereg.md` **record_scoring_error**: No outcome file given, so cannot assess any scoring errors.
- `governance:working_notes/2026-06-10-redundancy-mechanism-prereg.md` **observed_vs_descended**: No outcome file given, so cannot determine if scores are against observed or descended.
- `governance:working_notes/2026-06-10-redundancy-mechanism-prereg.md` **outcome_as_scored_by_record**: No outcome file is given, so the outcome cannot be scored.
- `governance:working_notes/2026-06-10-redundancy-mechanism-prereg.md` **outcome_basis**: No outcome file is given, so the basis for the outcome cannot be determined.
- `governance:working_notes/2026-06-10-redundancy-mechanism-prereg.md` **record_scoring_error**: No outcome file is given, so record scoring errors cannot be identified.
- `governance:working_notes/2026-06-10-redundancy-mechanism-prereg.md` **observed_vs_descended**: No outcome file is given, so observed vs descended cannot be determined.
- `governance:docs/superpowers/specs/2026-05-09-v1-v2-predictive-test-pre-registration.md` **outcome_as_scored_by_record, outcome_basis, record_scoring_error, observed_vs_descended**: No outcome file given, so these fields cannot be coded.
- `governance:docs/superpowers/specs/2026-05-09-v1-v2-predictive-test-pre-registration.md` **Pre-registration exclusion**: The document is a pre-registration and does not contain outcomes fixed by a freeze commit, so it cannot be coded as a bet.
- `governance:docs/superpowers/specs/2026-05-09-v1-v2-predictive-test-pre-registration.md` **Outcome_as_scored_by_record**: There is no outcome file given, so this field cannot be populated.
- `governance:docs/superpowers/specs/2026-05-09-v1-v2-predictive-test-pre-registration.md` **bet definition**: The document is a pre-registration, not a bet, as it does not contain a forecast fixed by a freeze commit with an OpenTimestamps stamp.
- `governance:docs/superpowers/specs/2026-05-09-v1-v2-predictive-test-pre-registration.md` **outcome_as_scored_by_record**: No outcome file is given, so this field cannot be coded.
- `governance:docs/superpowers/specs/2026-05-09-v1-v2-predictive-test-pre-registration.md` **outcome_basis**: No outcome file is given, so this field cannot be coded.
- `governance:docs/superpowers/specs/2026-05-09-v1-v2-predictive-test-pre-registration.md` **record_scoring_error**: No outcome file is given, so this field cannot be coded.
- `governance:docs/superpowers/specs/2026-05-09-v1-v2-predictive-test-pre-registration.md` **observed_vs_descended**: No outcome file is given, so this field cannot be coded.
- `governance:docs/superpowers/specs/2026-05-09-v1-v2-predictive-test-pre-registration.md` **outcome_as_scored_by_record, outcome_basis, record_scoring_error, observed_vs_descended**: No outcome file provided, so these fields cannot be coded.
- `governance:docs/superpowers/specs/2026-05-09-v1-v2-predictive-test-pre-registration.md` **bettor**: The document is pre-registered and unverifiable, thus coded as 'unclaimed'.
- `governance:docs/superpowers/specs/2026-05-09-v1-v2-predictive-test-pre-registration.md` **outcome_as_scored_by_record**: No outcome file is provided; therefore, coded as 'NO_OUTCOME_GIVEN'.
- `governance:docs/superpowers/specs/2026-05-09-v1-v2-predictive-test-pre-registration.md` **outcome_basis**: The document is a pre-registration, not yet verified or executed; thus, 'unverifiable pre-registration'.
- `governance:docs/superpowers/specs/2026-05-09-v1-v2-predictive-test-pre-registration.md` **register**: The document is exploratory and not considered a load-bearing or practice-grade bet.
- `governance:docs/superpowers/specs/2026-05-09-v1-v2-predictive-test-pre-registration.md` **forecast_type**: The document contains multiple predictions about shifts in distributions, classified as 'multi_outcome_priced'.
- `hamutay:experiments/event_loop/fork_run_identity_des_20260605/PRE_REGISTRATION.md` **record_scoring_error**: The codebook specifies setting this field when the record itself documents a wrong score, but no such error is mentioned in the outcome file.
- `hamutay:experiments/event_loop/fork_run_identity_des_20260605/PRE_REGISTRATION.md` **observed_vs_descended**: The codebook rule specifies scoring against observed only for tessera capstone cells, but this is not relevant here.
- `hamutay:experiments/event_loop/fork_run_identity_des_20260605/PRE_REGISTRATION.md` **provenance_category**: The codebook does not specify how to determine the provenance category from the given text.
- `hamutay:experiments/event_loop/fork_run_identity_des_20260605/PRE_REGISTRATION.md` **provenance_category**: The exact provenance category (recommendation) was inferred; the document did not specify a formal marker.
- `hamutay:experiments/event_loop/audit_restart_boundary_20260612/PRE_REGISTRATION.md` **record_scoring_error**: No documented scoring error in the outcome record.
- `hamutay:experiments/event_loop/audit_restart_boundary_20260612/PRE_REGISTRATION.md` **observed_vs_descended**: No specific rule or information provided on scoring against observed vs. descended.
- `hamutay:experiments/event_loop/audit_restart_boundary_20260612/PRE_REGISTRATION.md` **record_scoring_error**: No scoring error documented in the outcome file.
- `hamutay:experiments/event_loop/audit_restart_boundary_20260612/PRE_REGISTRATION.md` **observed_vs_descended**: Not applicable to this bet as it does not involve tessera capstone cells.
- `hamutay:experiments/event_loop/audit_restart_boundary_20260612/PRE_REGISTRATION.md` **outcome_as_scored_by_record**: The outcome basis is reported as 'True', but the codebook does not specify how to handle such binary outcomes beyond 'verbatim, with the scorecard/result file'.
- `hamutay:experiments/event_loop/audit_restart_boundary_20260612/PRE_REGISTRATION.md` **record_scoring_error**: The codebook does not provide guidance on how to determine if there is a scoring error for this type of prediction.
- `hamutay:experiments/event_loop/audit_restart_boundary_20260612/PRE_REGISTRATION.md` **observed_vs_descended**: The codebook does not specify how to handle 'observed vs descended' for pass/fail forecasts like this one.
- `hamutay:experiments/event_loop/audit_restart_boundary_20260612/PRE_REGISTRATION.md` **observed_vs_descended**: Not applicable here as there is no specific instruction on how to code this for this text.
- `hamutay:experiments/event_loop/audit_restart_boundary_20260612/PRE_REGISTRATION.md` **record_scoring_error**: No evidence of scoring error in the text.
- `hamutay:experiments/event_loop/audit_restart_boundary_20260612/PRE_REGISTRATION.md` **bettor**: The codebook does not specify how to determine if a forecast is AI or PI for preregistration documents without specific provenance markers.
- `hamutay:experiments/event_loop/audit_restart_boundary_20260612/PRE_REGISTRATION.md` **register**: The codebook specifies that quantumos tool declarations affect the register, but it's unclear if this applies to other projects without similar explicit declarations.
- `hamutay:experiments/event_loop/audit_restart_boundary_20260612/PRE_REGISTRATION.md` **provenance_category**: The text does not contain explicit provenance markers such as `RULED (author)`, `CONFIRMED`, etc., making it ambiguous how to classify the provenance category.
- `hamutay:experiments/identity_claim_table_compression_20260605/PRE_REGISTRATION.md` **register**: The register was assumed as 'load-bearing' based on the description, but the specific rule for this context was not explicitly provided in the codebook.
- `hamutay:experiments/identity_claim_table_compression_20260605/PRE_REGISTRATION.md` **record_scoring_error**: The outcome files do not contain explicit records of scoring errors.
- `hamutay:experiments/identity_claim_table_compression_20260605/PRE_REGISTRATION.md` **observed_vs_descended**: The field is not applicable based on the information provided.
- `hamutay:experiments/identity_scaffold_curator_20260604/PRE_REGISTRATION.md` **record_scoring_error**: The outcome file does not provide evidence of any scoring error, so this field cannot be set.
- `hamutay:experiments/identity_scaffold_curator_20260604/PRE_REGISTRATION.md` **observed_vs_descended**: The outcome file does not provide information to code this field as it pertains to tessera capstone cells.
- `hamutay:experiments/event_loop/delayed_task_terminal_surface_20260605/PRE_REGISTRATION.md` **record_scoring_error**: No specific scoring error documented in the outcome file.
- `hamutay:experiments/event_loop/delayed_task_terminal_surface_20260605/PRE_REGISTRATION.md` **observed_vs_descended**: No specific instruction given for scoring against observed or descended outcomes.
- `hamutay:experiments/event_loop/live_validation_repair_scaffold_20260605/PRE_REGISTRATION.md` **record_scoring_error**: The codebook specifies conditions for setting this field, but no such conditions are present in the outcome file.
- `hamutay:experiments/event_loop/live_validation_repair_scaffold_20260605/PRE_REGISTRATION.md` **observed_vs_descended**: The codebook specifies this field for tessera capstone cells, but it is not applicable here.
- `hamutay:docs/preregistrations/2026-10-27-a3-loss-record-prereg.md` **outcome_as_scored_by_record**: No outcome file is given, so the outcome cannot be scored.
- `hamutay:docs/preregistrations/2026-10-27-a3-loss-record-prereg.md` **outcome_basis**: No outcome file is given, so the outcome basis cannot be determined.
- `hamutay:docs/preregistrations/2026-10-27-a3-loss-record-prereg.md` **record_scoring_error**: No outcome file is given, so scoring errors cannot be identified.
- `hamutay:docs/preregistrations/2026-10-27-a3-loss-record-prereg.md` **observed_vs_descended**: No outcome file is given, so this field cannot be evaluated.
- `hamutay:experiments/event_loop/terminal_surface_substrate_smoke_20260605/PRE_REGISTRATION.md` **outcome_as_scored_by_record**: The outcome is described textually, not as a verbatim scorecard/result file as expected.
- `hamutay:experiments/event_loop/terminal_surface_substrate_smoke_20260605/PRE_REGISTRATION.md` **record_scoring_error**: No explicit documentation of a scoring error in the outcome file.
- `hamutay:experiments/event_loop/terminal_surface_substrate_smoke_20260605/PRE_REGISTRATION.md` **observed_vs_descended**: No explicit comparison between observed and descended outcomes in the outcome file.
- `hamutay:experiments/event_loop/terminal_surface_substrate_smoke_20260605/PRE_REGISTRATION.md` **outcome_as_scored_by_record**: The analysis file does not provide explicit values for phrase recovery and intermediate-use counts.
- `hamutay:experiments/event_loop/terminal_surface_substrate_smoke_20260605/PRE_REGISTRATION.md` **H364 outcome_as_scored_by_record**: The record does not specify the outcome for this hypothesis.
- `hamutay:experiments/event_loop/terminal_surface_substrate_smoke_20260605/PRE_REGISTRATION.md` **H364 outcome basis**: Outcome basis is 'NO_OUTCOME_GIVEN' because the result for 'phrase recovery or intermediate use' is not provided in the outcome file.
- `hamutay:experiments/event_loop/generated_continuation_primitive_smoke_20260605/PRE_REGISTRATION.md` **freeze_commit**: The freeze commit hash was given, but not the outcome commit hash.
- `hamutay:experiments/event_loop/generated_continuation_primitive_smoke_20260605/PRE_REGISTRATION.md` **record_scoring_error**: No information was provided about record scoring errors.
- `hamutay:experiments/event_loop/generated_continuation_primitive_smoke_20260605/PRE_REGISTRATION.md` **observed_vs_descended**: No information was provided to determine if scoring was against observed or descended.
- `hamutay:experiments/event_loop/framework_field_reservation_20260605/PRE_REGISTRATION.md` **freeze_commit**: The exact freeze_commit hash was not specified in the outcome file.
- `hamutay:experiments/event_loop/framework_field_reservation_20260605/PRE_REGISTRATION.md` **outcome_commit**: The outcome_commit hash is not specified in the outcome file.
- `hamutay:experiments/event_loop/framework_field_reservation_20260605/PRE_REGISTRATION.md` **record_scoring_error**: No record scoring error was documented in the outcome.
- `hamutay:experiments/event_loop/framework_field_reservation_20260605/PRE_REGISTRATION.md` **observed_vs_descended**: No specific information about observed vs descended outcomes was provided.
- `hamutay:experiments/event_loop/artifact_noninferiority_20260612/PRE_REGISTRATION.md` **outcome_commit**: The codebook specifies 'outcome_commit' should be as found, but the exact commit hash for the outcome is not provided in the text; assumed based on location.
- `hamutay:experiments/event_loop/artifact_noninferiority_20260612/PRE_REGISTRATION.md` **record_scoring_error**: No explicit scoring errors documented in the outcome file.
- `hamutay:experiments/event_loop/artifact_noninferiority_20260612/PRE_REGISTRATION.md` **observed_vs_descended**: The field is not applicable as the outcome is directly re-derivable from the provided outcome file.
- `hamutay:experiments/event_loop/artifact_noninferiority_20260612/PRE_REGISTRATION.md` **record_scoring_error**: The codebook does not provide guidance on how to code this field when the outcome is simply provided without any documented scoring error.
- `hamutay:experiments/event_loop/artifact_noninferiority_20260612/PRE_REGISTRATION.md` **observed_vs_descended**: The codebook does not provide guidance on how to code this field in this context.
- `hamutay:docs/ingestion-gate-preregistration-20260608.md` **outcome_as_scored_by_record**: No outcome file is given, so this field is set to 'NO_OUTCOME_GIVEN'.
- `hamutay:docs/ingestion-gate-preregistration-20260608.md` **outcome_basis**: No outcome file is given, so this field is set to 'NO_OUTCOME_GIVEN'.
- `hamutay:docs/ingestion-gate-preregistration-20260608.md` **record_scoring_error**: No outcome file is given, so this field is set to 'NO_OUTCOME_GIVEN'.
- `hamutay:docs/ingestion-gate-preregistration-20260608.md` **observed_vs_descended**: No outcome file is given, so this field is set to 'NO_OUTCOME_GIVEN'.
- `hamutay:docs/ingestion-gate-preregistration-20260608.md` **bettor**: The pre-registration does not specify the bettor type, and it is not scored in the owner's repo before the freeze, so it cannot be classified as a bet.
- `hamutay:docs/ingestion-gate-preregistration-20260608.md` **outcome_as_scored_by_record**: No outcome file is given, so this field cannot be filled.
- `hamutay:docs/ingestion-gate-preregistration-20260608.md` **outcome_basis**: No outcome basis can be determined due to the absence of an outcome file.
- `hamutay:docs/ingestion-gate-preregistration-20260608.md` **record_scoring_error**: No outcome file is provided, so no scoring error can be assessed.
- `hamutay:docs/ingestion-gate-preregistration-20260608.md` **observed_vs_descended**: No outcome file is given, so this field cannot be determined.
- `hamutay:experiments/event_loop/scheduler_reentry_diagnostic_20260605/PRE_REGISTRATION.md` **outcome_as_scored_by_record**: Only H69 had an outcome reported, and it was not scored as pass/fail; other hypotheses' outcomes were not given.
- `hamutay:experiments/event_loop/scheduler_reentry_diagnostic_20260605/PRE_REGISTRATION.md` **outcome_basis**: The basis for outcomes (as_reported or re-derivable) is unclear for H70, H71, and H72 due to missing outcome data.
- `hamutay:experiments/event_loop/scheduler_reentry_diagnostic_20260605/PRE_REGISTRATION.md` **record_scoring_error**: No documented scoring errors are present in the outcome file.
- `hamutay:experiments/event_loop/scheduler_reentry_diagnostic_20260605/PRE_REGISTRATION.md` **observed_vs_descended**: The distinction between observed and descended is not applicable as outcomes are not scored.
- `hamutay:experiments/event_loop/scheduler_reentry_diagnostic_20260605/PRE_REGISTRATION.md` **outcome_as_scored_by_record for H70 and H72**: No outcome file given for these bets, so outcome fields are marked as NO_OUTCOME_GIVEN.
- `hamutay:experiments/event_loop/scheduler_reentry_diagnostic_20260605/PRE_REGISTRATION.md` **outcome_as_scored_by_record**: Specific outcomes for H70, H71, and H72 are not detailed in the outcome file, leading to an 'as_reported' basis.
- `hamutay:experiments/event_loop/scheduler_reentry_diagnostic_20260605/PRE_REGISTRATION.md` **record_scoring_error**: No documented scoring error for any hypothesis.
- `hamutay:experiments/event_loop/scheduler_reentry_diagnostic_20260605/PRE_REGISTRATION.md` **observed_vs_descended**: Field is not applicable as no specific outcomes are provided for H70, H71, and H72.
- `hamutay:experiments/event_loop/phase_3d_richer_ipc_ingress_20260619/PRE_REGISTRATION.md` **outcome_as_scored_by_record**: The specific verbatim outcome is not directly provided; assumed from the failure analysis.
- `hamutay:experiments/event_loop/phase_3d_richer_ipc_ingress_20260619/PRE_REGISTRATION.md` **record_scoring_error**: No explicit documented scoring error in the outcome file.
- `hamutay:experiments/event_loop/phase_3d_richer_ipc_ingress_20260619/PRE_REGISTRATION.md` **observed_vs_descended**: No specific guidance or information on scoring against observed vs. descended.
- `hamutay:experiments/event_loop/phase_3d_richer_ipc_ingress_20260619/PRE_REGISTRATION.md` **record_scoring_error**: The codebook does not provide explicit details for identifying or documenting scoring errors in the outcome analysis.
- `hamutay:experiments/event_loop/phase_3d_richer_ipc_ingress_20260619/PRE_REGISTRATION.md` **observed_vs_descended**: The codebook does not provide explicit guidance on how to differentiate observed outcomes from descended outcomes in this context.
- `levadura_salvaje:predictions/2026-10-23-banking-parity-v3-claude.md` **observed_vs_descended**: No specific guidance for scoring against observed vs. descended in the codebook.
- `levadura_salvaje:predictions/2026-10-23-banking-parity-v3-claude.md` **register determination for quantumos qsim bets**: The codebook states that every quantumos qsim bet is practice-grade, but the register is not explicitly listed for the bet in the given text.
- `levadura_salvaje:predictions/2026-10-23-banking-parity-v3-claude.md` **record_scoring_error**: The outcome file does not indicate a record scoring error.
- `levadura_salvaje:predictions/2026-10-23-banking-parity-v3-claude.md` **observed_vs_descended**: The outcome file does not specify if the scoring was against observed or descended outcomes.
- `levadura_salvaje:predictions/2026-09-24-fossil-turnover-claude.md` **outcome_as_scored_by_record, outcome_basis, record_scoring_error, observed_vs_descended**: Outcome file not provided, hence these fields coded as 'NO_OUTCOME_GIVEN'.
- `levadura_salvaje:predictions/2026-09-24-fossil-turnover-claude.md` **pre-registration verifiability**: The file is a pre-registration without a verifiable timestamp (unstamped pre-registration), which is eligible for Q2 with the label `prereg_unverifiable`, but no outcome is given to score these predictions.
- `levadura_salvaje:predictions/2026-09-24-fossil-turnover-claude.md` **outcome_as_scored_by_record, outcome_basis, record_scoring_error, observed_vs_descended**: No outcome file is given, so these fields are coded 'NO_OUTCOME_GIVEN'.
- `levadura_salvaje:predictions/2026-09-28-retrospective-claude.md` **outcome_as_scored_by_record**: Outcome basis 're-derivable' assumed, as explicit scoring data available, but needs confirmation in context
- `levadura_salvaje:predictions/2026-09-28-retrospective-claude.md` **record_scoring_error**: Rule for scoring errors not applicable; no errors reported
- `levadura_salvaje:predictions/2026-09-28-retrospective-claude.md` **observed_vs_descended**: Field not applicable to this study; no use of observed vs descended
- `levadura_salvaje:predictions/2026-09-28-retrospective-claude.md` **observed_vs_descended**: Rule does not provide guidance on how to code this field for this study.
- `levadura_salvaje:predictions/2026-09-28-retrospective-claude.md` **record_scoring_error**: No record scoring error information provided in the text.
- `quantumos:docs/superpowers/specs/2026-07-06-field-battery-prereg.md` **outcome_as_scored_by_record**: Outcome file not provided; coded as NO_OUTCOME_GIVEN.
- `quantumos:docs/superpowers/specs/2026-07-06-field-battery-prereg.md` **outcome_basis**: Specified as 'as_reported' due to absence of outcome file.
- `quantumos:docs/superpowers/specs/2026-07-06-field-battery-prereg.md` **record_scoring_error**: No outcome file to determine if the record itself documents an error.
- `quantumos:docs/superpowers/specs/2026-07-06-field-battery-prereg.md` **observed_vs_descended**: No outcome file to evaluate against observed or descended criteria.
- `quantumos:docs/superpowers/specs/2026-07-06-field-battery-prereg.md` **outcome_as_scored_by_record, outcome_basis, record_scoring_error, observed_vs_descended**: NO_OUTCOME_GIVEN as there is no outcome file provided.
- `quantumos:docs/superpowers/specs/2026-07-06-field-battery-prereg.md` **register**: The field specifies 'exploratory' based on the provided text, but the codebook indicates that it should be keyed to the instrument, not to a date. The text mentions an explicit declaration about the register, which conflicts with the rule.
- `quantumos:docs/superpowers/specs/2026-07-06-field-battery-prereg.md` **record_scoring_error**: No explicit error documentation in the outcome file.
- `quantumos:docs/superpowers/specs/2026-07-06-field-battery-prereg.md` **outcome_as_scored_by_record**: No outcome file provided to score the bet.
- `quantumos:docs/superpowers/specs/2026-07-06-field-battery-prereg.md` **observed_vs_descended**: No applicable context for 'observed_vs_descended' in the given text.
- `tessera:formal/spike/tla-probes/P9/PROBE.md` **Unit of analysis and inclusion**: The text describes a TLA+ probe which is exploratory and not a bet, as it is not a forecast about a measurement outcome fixed by a freeze commit.
- `tessera:formal/spike/tla-probes/P9/PROBE.md` **Excluded outright**: The content falls under exploratory work, which is excluded from being considered a bet.
- `tessera:formal/spike/tla-probes/P9/PROBE.md` **outcome_as_scored_by_record**: No outcome file provided for scoring
- `tessera:formal/spike/tla-probes/P9/PROBE.md` **outcome_basis**: Outcome basis cannot be determined without an outcome file
- `tessera:formal/spike/tla-probes/P9/PROBE.md` **record_scoring_error**: Cannot assess scoring errors without an outcome file
- `tessera:formal/spike/tla-probes/P9/PROBE.md` **observed_vs_descended**: Cannot determine observed vs descended without outcome details
- `tessera:formal/spike/tla-probes/P9/PROBE.md` **bet definition**: No bet is present in the provided text, as it does not contain a forecast about a measurement outcome fixed by a freeze commit with an OpenTimestamps stamp.
- `tessera:formal/spike/tla-probes/P9/PROBE.md` **bet definition**: The text describes a probe design and predictions but does not contain a forecast about a measurement outcome.
- `tessera:formal/spike/tla-probes/P9/PROBE.md` **outcome file**: No outcome file is provided, making it impossible to score outcomes.
- `tessera:formal/spike/tla-probes/P9/PROBE.md` **bet identification**: The text does not identify a specific bet as per the codebook rules.
- `yupi:docs/w11-heldout-prereg-v0.1.md` **outcome_as_scored_by_record, outcome_basis, record_scoring_error, observed_vs_descended**: NO OUTCOME FILE GIVEN, so these fields are coded as NO_OUTCOME_GIVEN
- `yupi:docs/three-arm-prereg-v0.2.md` **Pre-registration status**: The document is explicitly stated as a draft and not stamped, thus it is excluded as a bet according to the codebook.
- `yupi:docs/three-arm-prereg-v0.2.md` **Outcome basis**: The outcome basis is not applicable as there is no outcome or commit to evaluate.
- `yupi:docs/three-arm-prereg-v0.2.md` **bettor**: The document is a draft and contains no finalized forecasts or decisions that can be attributed to a specific bettor.
- `yupi:docs/three-arm-prereg-v0.2.md` **outcome_as_scored_by_record**: No outcome file is provided, so no outcome can be scored or compared.
- `yupi:docs/three-arm-prereg-v0.2.md` **register**: The document is explicitly marked as a draft and does not specify its register (load-bearing, practice-grade, exploratory), but by context, it appears to be exploratory.
- `yupi:docs/three-arm-prereg-v0.2.md` **bettor**: The document does not contain any forecasts or predictions made by the AI or PI, hence no determination of 'bettor' is possible.
- `yupi:docs/three-arm-prereg-v0.2.md` **forecast_type**: No forecast type can be identified as the document is a pre-registration draft without any finalized predictions.
- `yupi:docs/three-arm-prereg-v0.2.md` **stated_forecast**: No stated forecasts are present in the document as it is a draft and not finalized.
- `yupi:docs/three-arm-prereg-v0.2.md` **outcome_as_scored_by_record**: No outcomes are scored since the document is a draft and no results have been committed.
- `yupi:docs/three-arm-prereg-v0.2.md` **outcome_basis**: No outcome basis can be determined as there are no committed outcomes or results.
- `yupi:docs/three-arm-prereg-v0.2.md` **record_scoring_error**: No scoring errors can be identified as there are no outcomes or results to score.
- `yupi:docs/three-arm-prereg-v0.2.md` **observed_vs_descended**: No comparison between observed and descended outcomes is possible as there are no results.
- `yupi:docs/three-arm-prereg-v0.2.md` **register**: The document is a draft and not finalized, so it cannot be classified under any register.
- `yupi:docs/three-arm-prereg-v0.2.md` **project, file, freeze_commit, outcome_commit**: No outcome file is given; thus, these fields cannot be populated.
- `yupi:docs/three-arm-prereg-v0.2.md` **bettor**: No bet is present to determine the bettor category.
- `yupi:docs/three-arm-prereg-v0.2.md` **forecast_type, stated_forecast, outcome_as_scored_by_record, outcome_basis, record_scoring_error, observed_vs_descended**: No bet is present to populate these fields.
- `yupi:docs/three-arm-prereg-v0.2.md` **register**: Cannot determine the register as no bet is present.
- `yupi:docs/three-arm-prereg-v0.2.md` **outcome_commit**: NO OUTCOME FILE GIVEN; the outcome commit is not provided.
- `yupi:docs/three-arm-prereg-v0.2.md` **bettor**: The file is a draft, not a forecast, so no bettor can be assigned.
- `yupi:docs/three-arm-prereg-v0.2.md` **forecast_type**: The file is a draft, not a forecast, so no forecast type can be assigned.
- `yupi:docs/three-arm-prereg-v0.2.md` **stated_forecast**: The file is a draft, not a forecast, so no stated forecast can be assigned.
- `yupi:docs/three-arm-prereg-v0.2.md` **outcome_as_scored_by_record**: NO OUTCOME FILE GIVEN; no outcome can be scored.
- `yupi:docs/three-arm-prereg-v0.2.md` **outcome_basis**: NO OUTCOME FILE GIVEN; no basis for outcome can be determined.
- `yupi:docs/three-arm-prereg-v0.2.md` **record_scoring_error**: NO OUTCOME FILE GIVEN; no scoring errors can be identified.
- `yupi:docs/three-arm-prereg-v0.2.md` **observed_vs_descended**: NO OUTCOME FILE GIVEN; no observed vs. descended scoring can be done.
- `yupi:docs/three-arm-prereg-v0.2.md` **register**: The draft status indicates it is not a load-bearing forecast; but since it is not a forecast, register cannot be assigned.
- `yupi:docs/d8-attribution-grid-freeze-c1-v0.3.md` **outcome_commit**: No outcome file is given to determine an outcome commit.
- `yupi:docs/d8-attribution-grid-freeze-c1-v0.3.md` **outcome_as_scored_by_record**: No outcome file is given to determine the outcome as scored by the record.
- `yupi:docs/d8-attribution-grid-freeze-c1-v0.3.md` **Outcome file**: No outcome file is provided in the text, making it impossible to code the 'outcome_as_scored_by_record' field.
- `yupi:docs/d8-attribution-grid-freeze-c1-v0.3.md` **bettor**: The bettor is not explicitly stated, leading to ambiguity in categorization.
- `yupi:docs/d8-attribution-grid-freeze-c1-v0.3.md` **forecast_type**: The type of forecast (probability, point_interval, etc.) is not specified in the text.
- `yupi:docs/d8-attribution-grid-freeze-c1-v0.3.md` **outcome_as_scored_by_record**: No outcome file is provided, making it impossible to determine the scored outcome.
- `yupi:docs/d8-attribution-grid-freeze-c1-v0.3.md` **outcome_basis**: The basis for the outcome is not provided due to the lack of an outcome file.
- `yupi:docs/d8-attribution-grid-freeze-c1-v0.3.md` **record_scoring_error**: Cannot determine if there was a scoring error without an outcome file.
- `yupi:docs/d8-attribution-grid-freeze-c1-v0.3.md` **observed_vs_descended**: Cannot be determined due to missing outcome information.
- `yupi:docs/d8-attribution-grid-freeze-c1-v0.3.md` **outcome_commit**: Outcome file is not given; the codebook requires an outcome commit to determine if the forecast is a bet.
- `yupi:docs/d8-attribution-grid-freeze-c1-v0.3.md` **outcome_as_scored_by_record**: No outcome file provided to extract the outcome as scored by the record.
- `yupi:docs/d8-attribution-grid-freeze-c1-v0.3.md` **outcome_basis**: Without an outcome file, determining the basis of the outcome (re-derivable or as reported) is not possible.
- `yupi:docs/d8-attribution-grid-freeze-c1-v0.3.md` **record_scoring_error**: No outcome file to check for any documented scoring errors within the record.
- `yupi:docs/d8-attribution-grid-freeze-c1-v0.3.md` **observed_vs_descended**: No outcome file to determine if the score was against observed or descended values.

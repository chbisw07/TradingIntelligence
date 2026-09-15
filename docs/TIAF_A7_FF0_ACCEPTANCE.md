# TIAF A7 / FF-0 — Final Acceptance

## 1. Decision and accepted boundary

**FF0_ACCEPTED — 2026-09-15, Asia/Kolkata.**

**INTERNAL_ENGINEERING_CLI_ONLY**. All four FF-0 sub-milestones and all **28/28**
semantic acceptance cases are complete. This accepts a synthetic engineering
miniature, not empirical predictor quality, calibrated/advisory use, public
forecast publication, overall A7 completion or FF-1 implementation readiness.

Clean entry: `1a61cb7`, accepted FF-0.3. Frozen A6 tag still resolves to
`6dc2ff304aae0e87540260b092919bb91e4d4189`. No commit, tag or push in this pass.
FF-0.3's historical “uncommitted” record describes its own pass; that slice is
now committed at entry. The present FF-0.4 changes remain uncommitted.

| Sub-milestone | Accepted delivery |
|---|---|
| [FF-0.1](TIAF_A7_FF0_1_CONTRACTS_TARGET_CLOCK_IMPLEMENTATION.md) | Frozen contracts, exact target/schedule/price semantics, aware clocks and PIT admission |
| [FF-0.2](TIAF_A7_FF0_2_CAPTURE_STORE_TRUTH_RECORDED_REPLAY_IMPLEMENTATION.md) | Bounded capture store, independent truth revisions, exact linkage/Ledger, recorded replay |
| [FF-0.3](TIAF_A7_FF0_3_BASERATE_COLD_RUNTIME_PINNED_VERIFICATION_IMPLEMENTATION.md) | Deterministic BaseRate, static registry, frozen COLD singleton, honest ACTUAL/SIMULATED execution, pinned verifier |
| [FF-0.4](TIAF_A7_FF0_4_ENGINEERING_CLI_ACCEPTANCE_HARDENING_IMPLEMENTATION.md) | Internal command adapter, strict registered local inputs, inspect/linkage, four goldens, executable 28-case corpus, hardening and guidance |

Exact runtime: RELIANCE NSE cash, target
`equity.next_session_close.return_gt_zero@1.0`; one
`forecaster:historical-base-rate@1.0`, one BENCHMARK root, zero PRIMARY, edges or
ensembles. Frozen authored twenty-transition window with minimum twenty eligible
observations; no backfill, smoothing or request-time fit. Raw 12/20=0.6;
0/20 and 20/20 remain legitimate numeric boundaries, not scientific certainty.
Synthetic truth uses exact completed unadjusted prices and supplied qualified
session/action/source facts. Old FF-0.1–0.3 golden fixtures/fingerprints remain.

## 2. Final 28-case matrix

Before FF-0.4: **25 satisfied, 2 partial (FF0-26 and FF0-27), 1 pending (FF0-28)**.
Now: **28 satisfied, 0 partial, 0 pending**. Case IDs/names and requirements are
unchanged from [plan §17](TIAF_A7_IMPLEMENTATION_SEQUENCING_FF0_MINIATURE_PLAN.md).
The [machine-readable matrix](../tests/acceptance/ff0/corpus_manifest.csv)
and [driver](../tests/acceptance/ff0/test_ff0_acceptance_corpus.py) execute the
referenced evidence tests and check every row; this is not a checklist-only audit.
A deduplicated batch runs 229 parametrized evidence tests; the driver separately
reports 28 semantic assertions. These are overlapping evidence views, not
229 additional independent semantic cases or observations.

| Case ID | Requirement | Owning sub-milestone | Test(s) | Status | Evidence |
|---|---|---|---|---|---|
| FF0-01 | immutable-contract-roundtrip | FF-0.1 | [test_request_result_roundtrip_and_list_inputs](../tests/unit/forecasting/test_contracts.py); [test_frozen_semantic_collections_cannot_be_replaced_or_mutated](../tests/unit/forecasting/test_contracts.py) | SATISFIED | Tuple/list/JSON round-trip, frozen replacement/append rejection, strict schema/finite decimals |
| FF0-02 | target-and-subject-scope | FF-0.1 | [test_target_scope_is_closed](../tests/unit/forecasting/test_contracts.py) | SATISFIED | Exact target succeeds; unknown target/version, index and outside-universe subject do not produce estimates |
| FF0-03 | malformed-mode-and-fields | FF-0.1 | [test_request_rejects_mixed_future_clocks_and_unauthorized_fields](../tests/unit/forecasting/test_contracts.py) | SATISFIED | Unknown mode, contradictory mode-specific fields and missing required refs reject before dispatch |
| FF0-04 | timely-actual | FF-0.1/0.3/0.4 | [test_golden_command_pipeline](../tests/unit/forecasting/test_engineering_cli.py); [test_runtime_controls_original_clocks_and_unique_attempt_usage](../tests/unit/forecasting/test_baserate_runtime.py) | SATISFIED | Valid ACTUAL inequalities, artifact existence and true completion/issue preserved; synthetic basis explicit |
| FF0-05 | late-actual-no-backdating | FF-0.3/0.4 | [test_real_cli_simulates_but_cannot_backdate_and_repeated_run_is_new](../tests/unit/forecasting/test_engineering_cli.py); [test_runtime_failures_are_not_trading_nonaction](../tests/unit/forecasting/test_baserate_runtime.py) | SATISFIED | Completion or issue after open → unavailable attempt; no fake issued_at or conversion to simulation |
| FF0-06 | later-computed-simulation | FF-0.1/0.3/0.4 | [test_golden_command_pipeline](../tests/unit/forecasting/test_engineering_cli.py); [test_simulation_late_fit_and_acquisition_are_explicit_not_backdated](../tests/unit/forecasting/test_clocks_evidence.py) | SATISFIED | Historical as-of, real later compute/fit completion, no actual issue, profile pinned |
| FF0-07 | cutoff-and-fit-leakage | FF-0.1/0.3/0.4 | [test_artifact_and_label_cutoff_admission_never_reaches_primitive](../tests/unit/forecasting/test_baserate_runtime.py); [test_future_availability_is_excluded_before_forecaster](../tests/unit/forecasting/test_baserate_runtime.py); [test_simulation_rejects_fake_issue_missing_profile_and_leakage](../tests/unit/forecasting/test_clocks_evidence.py) | SATISFIED | Future feature, prior-label availability, selection/universe/action knowledge or fabricated earlier acquisition denied |
| FF0-08 | target-open-strict-boundary | FF-0.1 | [test_cutoff_and_target_open_guards](../tests/unit/forecasting/test_clocks_evidence.py) | SATISFIED | Equality at open fails ACTUAL issue and SIMULATED as-of; no one-microsecond adjustment |
| FF0-09 | timezone-and-distinct-clocks | FF-0.1 | [test_aware_zones_normalize_without_changing_identity](../tests/unit/forecasting/test_clocks_evidence.py); [test_naive_and_non_iso_clock_inputs_rejected](../tests/unit/forecasting/test_clocks_evidence.py) | SATISFIED | Naive rejects; UTC/other aware normalize to +05:30; cutoff != as-of permitted; no duplicate editable simulation clock |
| FF0-10 | qualified-calendar-and-price | FF-0.1 | [test_exact_price_format_and_bar_correspondence_preserve_zero_volume](../tests/unit/forecasting/test_clocks_evidence.py); [test_session_identity_never_guesses_or_repairs](../tests/unit/forecasting/test_contracts.py); [test_source_price_is_positive_exact_and_not_a_float_conversion](../tests/unit/forecasting/test_clocks_evidence.py) | SATISFIED | Adjacency/coverage/finality/positive exact price required; float rendering alone insufficient; no weekday/quote substitution |
| FF0-11 | deterministic-baserate | FF-0.3/0.4 | [test_exact_baserate_minimum_zero_one_and_repeatability](../tests/unit/forecasting/test_baserate_runtime.py); [test_golden_command_pipeline](../tests/unit/forecasting/test_engineering_cli.py) | SATISFIED | 12/20=0.6, stable payload/hash, prior witness matches counts, no request-time fitting |
| FF0-12 | support-and-zero-boundaries | FF-0.3/0.4 | [test_fixed_window_no_backfill_and_minimum_support](../tests/unit/forecasting/test_baserate_runtime.py); [test_count_artifact_corruption_and_unapproved_basis_reject](../tests/unit/forecasting/test_baserate_runtime.py) | SATISFIED | n<20 unavailable; no history no 0.5; k=0 and k=20 serialize 0 and 1; bool/invalid counts reject |
| FF0-13 | missing-stale-action-evidence | FF-0.1/0.3 | [test_failed_current_evidence_qualification_never_calls_forecaster](../tests/unit/forecasting/test_baserate_runtime.py); [test_action_absence_does_not_adjust_prices_or_dispatch](../tests/unit/forecasting/test_baserate_runtime.py) | SATISFIED | Missing/stale proof and unknown/affected action window produce explicit absence, no source fallback or adjustment |
| FF0-14 | status-not-qualification | FF-0.1/0.3 | [test_status_payload_and_reason_are_not_interchangeable](../tests/unit/forecasting/test_contracts.py); [test_absence_has_no_estimate_or_fake_issue](../tests/unit/forecasting/test_contracts.py) | SATISFIED | All five status contracts; RAW generated is not calibrated/advisory; ABSTAINED recorded fixture has no invented BaseRate rule |
| FF0-15 | finite-singleton-composition | FF-0.1 | [test_singleton_graph_rejects_invalid_scope](../tests/unit/forecasting/test_contracts.py) | SATISFIED | One typed primitive/root accepted; duplicate/dangling/cyclic/type-incompatible graphs reject; unsupported non-singleton config never dispatches |
| FF0-16 | cold-binding-and-absence | FF-0.3/0.4 | [test_cold_denial_precedes_any_write_or_dispatch](../tests/unit/forecasting/test_baserate_runtime.py); [test_cold_freeze_and_physical_root_not_scientific_identity](../tests/unit/forecasting/test_baserate_runtime.py); [test_trusted_input_failures_precede_any_inference_or_write](../tests/unit/forecasting/test_engineering_cli.py) | SATISFIED | Registered exact version only; immutable mapping; request cannot choose imports/artifact replacement; missing required binding fails startup |
| FF0-17 | append-idempotence-conflict | FF-0.2/0.3 | [test_append_idempotence_modes_and_multiple_simulations](../tests/unit/forecasting/test_capture_store_replay.py); [test_conflicting_run_rejects_before_any_new_bytes](../tests/unit/forecasting/test_capture_store_replay.py); [test_duplicate_injected_execution_id_cannot_reexecute](../tests/unit/forecasting/test_baserate_runtime.py) | SATISFIED | Append then identical retry idempotent; same ID/different bytes rejects; no overwrite; exact references |
| FF0-18 | mode-coexistence-new-run | FF-0.2/0.3/0.4 | [test_new_actual_and_simulations_share_independent_truth_without_extra_observations](../tests/unit/forecasting/test_pinned_runtime_replay.py); [test_real_cli_simulates_but_cannot_backdate_and_repeated_run_is_new](../tests/unit/forecasting/test_engineering_cli.py) | SATISFIED | ACTUAL/SIMULATED distinct captures coexist; repeated simulation creates fresh run; no extra independent outcome |
| FF0-19 | independent-up-down-tie-truth | FF-0.2 | [test_exact_independent_up_down_and_tie](../tests/unit/evaluation/test_forecast_truth.py) | SATISFIED | Exact completed close gives 1/0/0 without forecaster call; window/event/availability/recording distinct |
| FF0-20 | pending-missing-and-censored | FF-0.2 | [test_missing_is_pending_then_censored_without_label](../tests/unit/evaluation/test_forecast_truth.py); [test_explicit_invalidations_do_not_retarget_or_adjust_prices](../tests/unit/evaluation/test_forecast_truth.py) | SATISFIED | Missing before deadline pending; after deadline censored/ineligible; bad source/nonpositive/action conflict not zero |
| FF0-21 | journal-revision-and-time | FF-0.2 | [test_revised_truth_keeps_original_bytes_and_exact_revisions](../tests/unit/evaluation/test_forecast_truth.py); [test_material_correction_appends_explicit_invalidation_revision](../tests/unit/evaluation/test_forecast_truth.py) | SATISFIED | Revised close/source/action/schedule appends predecessor; recording can't precede availability; no fork/rewrite or S2 shift |
| FF0-22 | exact-link-and-ledger | FF-0.2 | [test_incompatible_truth_never_links](../tests/unit/evaluation/test_forecast_linkage.py); [test_missing_outcome_link_and_old_ledger_are_immutable_after_revision](../tests/unit/evaluation/test_forecast_linkage.py) | SATISFIED | Target/subject/window/version/mode/basis mismatch denied; exact journal revision joined; absent labels NOT_EVALUABLE |
| FF0-23 | recorded-replay-no-calls | FF-0.2/0.4 | [test_fresh_process_cli_replay_blocks_runtime_and_keeps_public_grammar_closed](../tests/unit/forecasting/test_engineering_cli.py); [test_replay_preserves_all_original_clocks_and_never_simulates_or_labels](../tests/unit/forecasting/test_capture_store_replay.py) | SATISFIED | Full reconstructed semantics/fingerprints equal; forecaster/registry/provider sentinels remain unused; original bytes unchanged |
| FF0-24 | pinned-verify-not-simulate | FF-0.3/0.4 | [test_golden_resealed_tamper_is_not_a_successful_verification](../tests/unit/forecasting/test_engineering_cli.py); [test_missing_pinned_verifier_has_failure_exit_without_changing_replay](../tests/unit/forecasting/test_engineering_cli.py); [test_unavailable_verifier_never_falls_back_or_mutates_history](../tests/unit/forecasting/test_pinned_runtime_replay.py) | SATISFIED | Exact recomputation, separate verifier usage; missing verifier UNVERIFIABLE; new simulation is not replay |
| FF0-25 | corrupted-partial-locked-store | FF-0.2/0.4 | [test_corrupt_persisted_history_never_repairs_or_claims_replay](../tests/unit/forecasting/test_engineering_cli.py); [test_failed_append_never_claims_transaction_success_or_repairs_history](../tests/unit/forecasting/test_capture_store_replay.py) | SATISFIED | Altered hash/missing closure/partial JSONL/writer lock/disk failure deny success; no auto repair or truncated reads |
| FF0-26 | lean-import-and-authority | FF-0.1/0.4 | [test_fresh_process_cli_runs_without_optional_dependencies_or_live_calls](../tests/unit/forecasting/test_engineering_cli.py); [test_fresh_process_cli_replay_blocks_runtime_and_keeps_public_grammar_closed](../tests/unit/forecasting/test_engineering_cli.py) | SATISFIED | No optional ML/provider/MCP import, network/model/broker call, old A2/A6 mutation or new published capability |
| FF0-27 | bounds-cost-and-private-logs | FF-0.2/0.3/0.4 | [test_persistence_failure_and_deadline_have_failure_exit](../tests/unit/forecasting/test_engineering_cli.py); [test_trusted_input_failures_precede_any_inference_or_write](../tests/unit/forecasting/test_engineering_cli.py); [test_resource_denial_is_preflight_no_truncation](../tests/unit/forecasting/test_capture_store_replay.py); [test_no_sensitive_payloads_in_structured_runtime_log](../tests/unit/forecasting/test_baserate_runtime.py) | SATISFIED | Size/count/deadline fails closed; zero model/provider calls/tokens, unpriced local cost, no sensitive logs, no double-counting |
| FF0-28 | local-engineering-end-to-end | FF-0.4 | [test_golden_command_pipeline](../tests/unit/forecasting/test_engineering_cli.py); [test_help_never_reads_config_or_dispatches](../tests/unit/forecasting/test_engineering_cli.py); [test_closed_grammar_redacts_invalid_authority_and_arguments](../tests/unit/forecasting/test_engineering_cli.py); [test_bad_logical_input_with_otherwise_complete_command](../tests/unit/forecasting/test_engineering_cli.py) | SATISFIED | CLI help safe, explicit config/IDs, simulated run→separate truth→link→replay; exit codes and unavailable paths; source fixtures untouched |

## 3. Golden and actual operator evidence

[Four golden workflows](../tests/unit/forecasting/test_engineering_cli.py)
use [pinned expected results](../tests/acceptance/ff0/golden_results.json).
Production never imports test generators or clock overrides.

| Scenario | Result | Persistence / replay / pinned verification / linkage |
|---|---|---|
| Timely ACTUAL, trusted test clock at 2026-02-04 16:06 +05:30 | GENERATED, 0.6, n=20; runtime-owned computation/issue before target open | Captured; exact recorded replay; VERIFIED; independent label 1 and engineering-eligible link |
| Later SIMULATED, test clock at 2026-02-09 | GENERATED, 0.6, n=20; historical as-of, later computation, no issue | Captured; exact recorded replay; VERIFIED; independent label 1 and engineering-eligible link |
| Insufficient support | UNAVAILABLE / HISTORY_SUPPORT_INSUFFICIENT, n=19, no probability | Captured; exact recorded replay; VERIFIED absence; label retained with NOT_EVALUABLE link |
| Re-sealed temporary tamper: probability 0.7 versus pinned 0.6 | Recorded replay faithfully reads altered capture; pinned verification MISMATCH / exit 1 | Original corpus unchanged; verifier writes no new capture; truth/linkage not needed to detect inference mismatch |

The real-clock CLI walkthrough used an explicit temporary config at
`/tmp/tiaf-ff04-acceptance-vTy2xJ/config.json` and its separate `corpus/`.
These local artifacts were retained, not committed; temporary storage is not a
durability promise. The process invocations exercised help, three runs,
independent outcome, link, inspect, replay and replay-with-verification:
**nine invocations in total** (help + 3 run + 5 other operations).

Observed SIMULATED run:
`ff-run:fffbbf3e9aaa4e0d9e1ae10bb9ace31e`.
As-of `2026-02-04T16:05:00+05:30`;
computed `2026-09-15T13:10:02.090628+05:30`; issued null.
Result fingerprint:
`90a094b70b49c2fe7adf89ffd8ab376de64aa682ca6027ced4b400cf6ee35ee5`.
Inspect, recorded replay and pinned reconstruction returned that same fingerprint.
Native inference duration was 0.0011363489320501685 seconds; verifier duration
0.000863431952893734 seconds. These are single local measurements, **not**
end-to-end latency benchmarks or guarantees.

Independent synthetic outcome label 1 linked as ENGINEERING_LINK_ELIGIBLE.
The same real-clock workflow preserved UNAVAILABLE / TEMPORAL_INELIGIBLE for the
now-past ACTUAL fixture, no issue and zero inference attempts; n=19 persisted
UNAVAILABLE with one attempt. All nine operations exited 0, including domain
absence. Negative-case tests separately establish exits 1 and 2.

## 4. Commands, failures and safety

The [operator guide](TIAF_A7_FF0_4_ENGINEERING_CLI_ACCEPTANCE_HARDENING_IMPLEMENTATION.md#3-operator-guide)
and [scripts README](../scripts/README.md#ff-0-internal-forecasting-miniature)
give exact config/ID commands, expected output and actual corpus layout.

| Command | Meaning |
|---|---|
| `run --config PATH --input ID` | Admit a registered synthetic packet; execute its explicit ACTUAL/SIMULATED mode; append fresh capture |
| `outcome --config PATH --input ID` | Independently label supplied terminal evidence; append first truth revision |
| `link --config PATH --run ID --outcome ID` | Persist exact Evaluation link plus immutable one-link Ledger snapshot |
| `inspect --config PATH --run ID` | Rights-checked immutable metadata, clocks, provenance, status, fingerprints and exact persisted links |
| `replay --config PATH --run ID` | Verify/load recorded capture; no forecaster, relabeling, new run or mutation |
| `replay --config PATH --run ID --verify` | Additionally run exact pinned verification, separate usage; original untouched |
| `--help` | Safe versioned JSON help, no config access or execution |

No REPL, NLP, mode override, arbitrary module/model loader, remote URL, credential
input, live fallback, repair/delete, broker or order authority. Reuses the
existing Shell parser/safety framework but does not alter the public grammar.
Inputs and config are trusted versioned local JSON; registries/fingerprints
admit only exact bound implementations, not whichever implementation is available.

Exit **0**: completed operation/domain absence; **2**: command/config/admission;
**1**: execution/persistence/integrity failure or requested MISMATCH/UNVERIFIABLE.
Stable structured category/messages redact private exception/argument/source
content. Corrupt run/outcome journal, absent artifact, profile mutation,
fingerprint/schema mismatch, partial write/lock, bad mode, attempted backdating,
future simulation cutoff, insufficient support and duplicate invocation all
have explicit tests. No corruption is silently repaired. Repeated valid run is
a fresh attempt; native duplicate-ID conflict remains fail-closed.

New packet contracts keep semantic collections as tuples while accepting JSON
arrays. All datetimes remain aware Asia/Kolkata with +05:30 output; UTC/other
aware zones normalize and naive values reject. Package version 0.1.0 remains
distinct from schema 1.0 and versioned target/forecaster identity.

## 5. Validation performed

| Gate | Exact result |
|---|---|
| `.venv/bin/pytest -q tests/unit/forecasting/test_engineering_cli.py` | **58 passed**; final strengthened run **27.21 s** |
| FF-0.1: test_contracts, test_clocks_evidence, test_identity_isolation, test_population_contract | **170 passed** in 2.71 s |
| FF-0.2: test_capture_store_replay, Evaluation test_forecast_truth/test_forecast_linkage | **113 passed** in 9.28 s |
| FF-0.3: test_baserate_runtime, test_pinned_runtime_replay | **75 passed** in 28.15 s |
| `.venv/bin/pytest -q -s tests/acceptance/ff0` | **28 passed** in 39.05 s; internally **229 evidence tests passed**, no failures/skips |
| Related R3 composition, R5 COLD startup, source_semantics, Evaluation, A6 | **289 passed** in 42.80 s |
| `.venv/bin/pytest -q` | **2,921 passed** in **411.95 s** on the final test state; no failures/skips |
| `.venv/bin/python -m compileall src scripts` | PASS |
| `.venv/bin/ruff check src tests scripts` | PASS |
| `.venv/bin/mypy src tests` | PASS, **600 source files** |
| CLI help/parser/import isolation | Included in 58 tests; fresh-process socket/import sentinels; real script help successful |
| Local documentation links | PASS: **15 Markdown files, 716 local links**, including unchanged handbook/reference entry points |
| `git diff --check` | PASS; new-file whitespace checked separately before handoff |

Exact regression paths:
`tests/unit/forecasting/test_contracts.py`,
`tests/unit/forecasting/test_clocks_evidence.py`,
`tests/unit/forecasting/test_identity_isolation.py`,
`tests/unit/forecasting/test_population_contract.py`;
`tests/unit/forecasting/test_capture_store_replay.py`,
`tests/unit/evaluation/test_forecast_truth.py`,
`tests/unit/evaluation/test_forecast_linkage.py`;
`tests/unit/forecasting/test_baserate_runtime.py`,
`tests/unit/forecasting/test_pinned_runtime_replay.py`.
Related command:
`.venv/bin/pytest -q tests/unit/workflows/test_r3_composition.py tests/unit/test_r5_cold_startup.py tests/unit/source_semantics tests/unit/evaluation tests/unit/a6`.
Counts overlap across gate views; do not sum them as unique tests. New tests
added to full-suite collection: 58 CLI + 28 corpus assertions = 86 above 2,835.
The initial full run also passed 2,921 tests in 338.46 s. Final review strengthened
the invalid-input tests with an explicit zero-forecaster-call assertion, so an
exception caught by the CLI cannot disguise accidental dispatch. Focused and
full suites were rerun successfully; no runtime semantics changed during review.

Fresh processes ran successfully with optional ML, provider/MCP, model and broker
imports blocked; recorded replay additionally blocks forecaster/runtime/support,
labeler and engineering input loader imports. Socket connects are denied.
No live provider/broker/LLM invocation was performed. Public catalog stays nine.
Only source edits are the internal adapter/packet modules and read-only store
inspection seam; A2/A6, public facade/Shell, old fixture goldens and policies are
unchanged. No new dependency, environment auto-discovery or learning path.

## 6. Observability, retention and carried limits

Results expose operation and request/run/result/capture identity, native
status/mode/basis/clocks, raw probability or explicit absence/support count,
source/artifact/config/composition refs, fingerprints, limitation/authority
metadata and exact replay/verification/linkage results. They do not expose
credentials, physical path dumps or raw source bodies.

Historical `original_usage` is not charged again by replay. Pinned verification
has separately identified usage and no persisted new forecast. Provider/model
calls, model tokens and model cost are zero; local work is **UNPRICED**, with
native monotonic duration and a cooperative one-second deadline. No hard timeout
or wall-clock SLA is claimed.

Existing bounded single-writer store and current access/retention checks remain:
1 MiB record, 256 journal records/closure, 32 MiB corpus; no deletion, overwrite,
truncation, automatic repair, stale-lock removal or rights inference from bytes.
CLI adds bounded regular-file reads, 64 input registrations and disjoint roots.
Link and Ledger appends are not one atomic transaction; a partial multi-command
workflow may retain valid earlier records. CLI does not auto-revise truth.
These are documented local-operational limits, not blockers to scoped FF-0.

No empirical predictor/calibration/uncertainty qualification; no training,
logistic/XGBoost/LLM/FM/LFDE/ensemble; no lifecycle registry expansion,
shadow/advisory authorization, forecasting public projection or A4/A5/A6 overlay;
no A8–A10 integration. A7 remains in progress; the complete calibrated miniature
through FF-2 is not delivered. No architecture deviation or unresolved FF-0
acceptance blocker remains. Repository clocks and implementation identity remain
pinned; incompatible environments must fail explicitly rather than regolden.

## 7. FF-1 prerequisites and Git recommendation

Next is **planning only**, requiring a separate user request. Before any fit:
qualify empirical (or explicitly synthetic plumbing) calendar/price/action/PIT
data and source/fit rights; preregister target/cohort, fixed A2 feature IDs,
availability/selection basis, chronological train/validation/test and
purge/embargo protocol, minimum support and all trials; pin solver/dependency,
regularization, scaling, seed and artifact identity; obtain bounded Learning
grants. Evaluation must specify B0 versus B2 paired common outcomes,
denominators/dispositions, uncertainty and inconclusive/zero-pair handling.
Preserve ACTUAL/SIMULATED separation. No threshold tuning to live examples,
outcome inspection before protocol approval, automatic promotion, calibration
folded into FF-1, public publication or consumer authorization.

Suggested future commit, **not executed**:
`feat(a7.ff0): complete miniature forecasting foundation`.

Tag recommendation: **yes, optionally after separate review/checkpoint
authorization**, `tiaf-a7-ff0-baseline` for the accepted synthetic miniature,
not an A7 major freeze. Do not move the A6 tag. No Git mutation in this pass.

Exact next prompt:
**TIAF A7 / FF-1 — LOGISTIC BENCHMARK AND PAIRED EVALUATION PLANNING**.

## 8. Changed files

The exact scoped inventory follows; no unrelated worktree changes were present.

```text
README.md
docs/ARCHITECTURE.md
docs/IMPLEMENTATION_ROADMAP.md
docs/MILESTONES.md
docs/TIAF_A7_DETAILED_ROADMAP.md
docs/TIAF_A7_FF0_4_ENGINEERING_CLI_ACCEPTANCE_HARDENING_IMPLEMENTATION.md
docs/TIAF_A7_FF0_ACCEPTANCE.md
docs/TIAF_CAPABILITY_MAP.md
docs/TIAF_FORECASTING_FRAMEWORK_DETAILED_ROADMAP.md
docs/TIAF_IMPLEMENTATION_TARGETS.md
scripts/README.md
scripts/forecast_miniature.py
src/tiaf/forecasting/engineering.py
src/tiaf/forecasting/engineering_inputs.py
src/tiaf/forecasting/store.py
tests/acceptance/ff0/README.md
tests/acceptance/ff0/__init__.py
tests/acceptance/ff0/_support.py
tests/acceptance/ff0/corpus_manifest.csv
tests/acceptance/ff0/golden_results.json
tests/acceptance/ff0/test_ff0_acceptance_corpus.py
tests/fixtures/forecasting/ff0/README.md
tests/fixtures/forecasting/ff0/local_config.json
tests/fixtures/forecasting/ff0/reliance-s21-actual.json
tests/fixtures/forecasting/ff0/reliance-s21-insufficient.json
tests/fixtures/forecasting/ff0/reliance-s21-simulated.json
tests/fixtures/forecasting/ff0/reliance-s21-up.json
tests/unit/forecasting/test_engineering_cli.py
```

Total: **28 repository files**. Runtime wiring: 4 files (script, two internal
modules, read-only store extension); tests/fixtures: 13 files; documentation:
11 files. The source-fixture README is counted with tests/fixtures. No existing
forecast primitive, runtime policy, serializer, schema, public grammar or A6
implementation was changed.

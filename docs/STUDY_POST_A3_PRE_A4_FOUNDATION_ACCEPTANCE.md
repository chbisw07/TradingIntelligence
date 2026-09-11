# Study — POST_A3_PRE_A4 Foundation Acceptance

**Date:** 2026-09-11 (Asia/Kolkata)
**Scope:** deterministic source semantics, A4 input projection, successor and
offline replay only. No live provider or model call was authorized or needed.

## Acceptance evidence

The accepted base was the clean post-A3 architecture consolidation commit
`dbf13ec`, with frozen A3 runtime baseline `e690da2` / `tiaf-a3-baseline`.
Implementation is additive under `tiaf.source_semantics`; frozen A2/A3 contracts
and serialized fixture schemas were not edited.

The mandatory corpus maps as follows:

| # | Case | Evidence |
| ---: | --- | --- |
| 1 | Revenue vs total income | typed predicate mismatch test |
| 2 | Standalone vs consolidated | typed scope mismatch test |
| 3 | Explicit scale transform | versioned crore-to-lakh rule test |
| 4 | Identical value, unknown basis | `UNDETERMINED` test |
| 5 | Zero vs missing | explicit missing-kind conflict test |
| 6 | Comparable incompatible values | factual-conflict test |
| 7 | Same-provider conflict | occurrence-preserving dispute test |
| 8 | Syndicated copies | `SAME_ROOT` measurement relation test |
| 9 | Independent analyses/same filing | separate analytical and measurement dimensions test |
| 10 | Hash change without correction | non-superseding version test |
| 11 | Explicit scoped correction | correction predicate/period test |
| 12 | Field leakage | assertion and authority predicate rejection tests |
| 13 | `NOT_FOUND != FALSE` | absence projection test |
| 14 | Multiple authoritative documents | binding-order invariance test |
| 15 | Equal-authority conflicts | retained multi-assertion conflict test |
| 16 | Partial confirmation | simultaneous match/conflict projection test |
| 17 | A3.9 unchanged | frozen state/reason/opinion projection assertions |
| 18 | A3.10 hashes unchanged | exact parent/child link assertions and full regressions |
| 19 | Projection-only A2 | unsupported full-assertion rejection test |
| 20 | Mandatory artifact missing/corrupt | exact four-digest fail-closed tests |
| 21 | Optional lineage absent | explicit optional gap test |
| 22 | Deterministic repeat | reordered-input fingerprint equality test |
| 23 | Policy version change | new projection/comparison record test |
| 24 | Later evidence | immutable parent and later successor test |
| 25 | Replay makes zero calls | network-blocked recorded replay test |
| 26 | Provider names not independence | missing basis-identity rejection test |
| 27 | Unknown authority | explicit `UNKNOWN` preservation test |
| 28 | No `SourceScore` | public-surface assertion and source scan |
| 29 | No A4 disposition | public-surface assertion and source scan |
| 30 | No LLM/model dependency | no-model control, source/import scan and replay test |

## Semantic observations

- Source, provider, upstream origin, document family/version and occurrence are
  distinct immutable identities.
- Authority is field/subject/time scoped and non-numeric.
- Comparison uses typed meaning before values. Unknown dimensions prevent exact
  equivalence; zero remains factual.
- Disputes preserve incompatible evidence and append history rather than voting.
- Independence requires explicit lineage/basis identities and is dimensioned.
- Confirmation is a view over an unchanged A3 result and never turns source
  lookup order into authority.
- Projection captures the unchanged A3.9/A2 view and mandatory A3.10 child
  integrity. It contains no A4 outcome.
- Successors advance time and identify new captured evidence without parent
  mutation.

## Validation results

All required gates passed:

- foundation suite: `27 passed`;
- market-intelligence suite: `149 passed`;
- opportunity-intelligence suite: `65 passed`;
- A3-hardening suite: `61 passed`;
- agents suite: `270 passed`;
- full suite: `1948 passed`;
- `python -m compileall src scripts`: pass;
- `ruff check src tests scripts`: pass;
- `mypy src tests`: success across 457 source files;
- `python -m pip check`: no broken requirements;
- documentation links: 435 local links checked, none missing;
- scoped secret scan: no credential assignment found;
- provider/model/A4-runtime surface scan: none found;
- replay with socket connection blocked: pass;
- mandatory/corrupt artifact and frozen parent regressions: pass;
- `git diff --check`: pass.

No live provider, network, model or broker call was made. Package version remains
`0.1.0`; the additive foundation contract/capture schema is separately `1.0`.

**Decision:** `READY_TO_ACCEPT_POST_A3_PRE_A4_FOUNDATION`.

## Residual boundaries

This work does not implement the selected local facade/lifecycle, A4 runtime,
A4 research loop, model integration, source citation rendering or durable
storage. Those remain governed later work. The projection contract is designed
for deterministic A4 consumption but does not authorize A4 behavior.

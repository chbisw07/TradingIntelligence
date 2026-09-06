# TIAF A1 Acceptance Report

## Scope

Engineering acceptance evidence for TIAF_A1.1 through TIAF_A1.7. This report
records the completed Data Foundation; it is not a replacement for the
architectural baseline or roadmap.

## Accepted baseline

- Decision: **A1 ACCEPTED / BASELINED FOR A2 DEPENDENCY**
- Annotated tag: `tiaf-a1.7`
- Resolved commit: `eecd7736aa939f919c0fba5b4fdbec7722179979`
- Tag date: 2026-09-06

## Verification summary

Repository closure verification:

| Gate | Result |
|---|---|
| `python -m compileall src` | Passed |
| `pytest` | **507 passed** |
| `ruff check src tests` | Passed |
| `mypy src tests` | Passed; 125 source files checked |
| `git diff --check` | Passed |

Tests are deterministic and do not require live provider credentials. Live
validation was performed separately through the documented read-only smoke
surfaces.

## Live validation matrix

The table records only observations established by the accepted milestone
documentation and user-level live acceptance. IDs are observations from the
then-current Dhan master, not constants.

| Validation | Result | Important observed evidence | Capability proven |
|---|---|---|---|
| A1.2 core quote/history | Pass | Read-only Dhan quote and OHLCV paths returned normalized facts; early ID `1333` data was later correctly attributed to HDFCBANK | Authenticated transport, parsing, time normalization, and typed factual models |
| A1.3 live option chain | Pass | Explicit-expiry option-chain transport returned normalized underlying/strike/CE/PE facts; early ID `1333` label was corrected later | Expiry discovery and factual prices, depth, OI, volume, IV, and Greeks |
| A1.4 historical expired options CE | Pass | Rolling endpoint returned normalized requested CE history with validated arrays | Historical CE acquisition, request mapping, and series normalization |
| A1.4 historical expired options PE | Pass | Rolling endpoint returned normalized requested PE history with validated arrays | Historical PE acquisition independent of CE semantics |
| A1.5 RELIANCE resolution | Pass | NSE RELIANCE resolved to observed Dhan security ID `2885` | Symbol-first canonical identity |
| A1.5 HDFCBANK resolution | Pass | NSE HDFCBANK resolved to observed Dhan security ID `1333` | Correction and prevention of earlier display-identity mismatch |
| A1.5 BSE explicit override | Pass | Explicit BSE scope overrides the configured NSE primary policy | Caller scope wins; deployment preference remains visible and deterministic |
| A1.5 canonical F&O universe | Pass | Exchange-scoped unique underlyings were derived; Dhan `DUMMYSAN` diagnostics were excluded | Deterministic eligible universe without ranking or provider-test contamination |
| A1.6 provider-to-cache reuse | Pass | Repeated identical factual request reported provider acquisition followed by cache reuse | Cache key, freshness assessment, and visible fetch disposition |
| A1.7 RELIANCE context | Pass | RELIANCE resolved as `2885`; quote and 64-bar history formed a complete factual context | End-to-end symbol → resolver → runtime → normalized `AnalysisContext` |
| A1.7 RELIANCE derivatives context | Pass | Explicit-expiry derivatives evidence was included with requirement, provenance, and quality status | Coherent optional/required derivatives integration without recommendation logic |
| A1.7 HDFCBANK context | Pass | HDFCBANK resolved as `1333`; quote was usable `PARTIAL`, history available, context complete | Independent non-RELIANCE subject assembly and partial-quality acceptance |
| A1.7 KAYNES context | Pass | KAYNES resolved as `12092`; quote was usable `PARTIAL`, history available, context complete | Independent subject identity and context assembly |
| A1.7 impossible required expiry | Pass (negative case) | An impossible explicit expiry did not fabricate an option chain; required-evidence policy remained visible | Required versus optional failure and strict/partial behavior |
| A1.7 batch deferred semantics | Pass | RELIANCE completed; immediate HDFCBANK/KAYNES work could be gate-deferred although independent builds succeeded | Scheduling deferral remains distinct from factual unavailability; order and every item are retained |

No live result in this table implies execution, a recommendation, or a fixed
provider identity for future sessions.

## Critical defects found during validation

### 1. Rolling expired-options expiry-code mismatch

- **Symptom:** `/charts/rollingoption` rejected `expiryCode=0` with Dhan
  `DH-905`, despite older/general annexure semantics describing `0/1/2`.
- **Risk:** valid-looking requests could omit zero through truthiness or use the
  wrong endpoint semantics.
- **Root cause:** the rolling endpoint uses a distinct live mapping from the
  older/general annexure.
- **Correction:** dedicated `HistoricalOptionExpiryCode` with `NEAR=1`,
  `NEXT=2`, `FAR=3`; the field is required and serialized unconditionally.
- **Regression protection:** model, CLI, builder, and HTTP-payload tests accept
  `1/2/3`, reject `0`/`None`, and verify exact integer payloads.

### 2. Security-ID / symbol-label mismatch

- **Symptom:** an early smoke command paired label RELIANCE with Dhan security
  ID `1333`; the returned facts were actually HDFCBANK.
- **Risk:** internally valid market data could be attributed to the wrong
  company and contaminate every downstream conclusion.
- **Root cause:** the diagnostic caller independently supplied a human label and
  provider ID without proving they represented one instrument.
- **Correction:** symbol-first master resolution and a hard pre-transport
  consistency check whenever both symbol and ID are supplied.
- **Regression protection:** quote, option-chain, and expired-option smoke tests
  reject mismatches before provider construction/calls.

### 3. NSE/BSE symbol ambiguity

- **Symptom:** exact human symbols such as RELIANCE can legitimately have both
  NSE and BSE cash records.
- **Risk:** an arbitrary first-row choice could change provider identity and
  market scope silently.
- **Root cause:** symbol-only identity lacks exchange scope.
- **Correction:** configurable NSE primary deployment policy, explicit BSE
  override, visible `POLICY_SELECTED` attribution, and preserved ambiguity when
  policy cannot choose uniquely.
- **Regression protection:** resolution tests cover default policy, explicit
  scope, multiple preferred-exchange candidates, and no first-row guessing.

### 4. Provider diagnostic instruments in the F&O universe

- **Symptom:** Dhan `DUMMYSAN` diagnostic underlyings appeared eligible during
  live master inspection.
- **Risk:** test/provider artifacts could enter real screening universes.
- **Root cause:** the master exposed no reliable active flag, and its generic
  buy/sell indicator also appeared on genuine derivatives.
- **Correction:** narrow filtering by identified provider ISIN markers while
  preserving legitimate names that merely contain words such as `TEST`.
- **Regression protection:** universe fixtures verify diagnostic exclusion,
  genuine derivative inclusion, uniqueness, and exchange scoping.

### 5. Retrieval freshness versus source-observation age

- **Symptom:** a newly retrieved response was labeled `FRESH` although its
  RELIANCE last trade was `2026-09-04T15:59:14+05:30` during 2026-09-06
  validation.
- **Risk:** consumers could mistake cache/API recency for current market state.
- **Root cause:** one generic freshness label described retrieval timing while
  the nested factual timestamp had different semantics.
- **Correction:** explicit retrieval freshness/age, source-observed time,
  observation age, timestamp semantics, and required-only
  `overall_retrieval_freshness`.
- **Regression protection:** old-observation/fresh-retrieval, cache-age,
  option-chain timestamp-semantics, and JSON round-trip tests.

### 6. Requested versus required evidence ambiguity

- **Symptom:** `--include-derivatives` requested an impossible chain, the chain
  failed, yet output said `Complete: YES` because it was silently optional.
- **Risk:** users could interpret completion as satisfaction of explicitly
  requested critical evidence.
- **Root cause:** inclusion and requirement were separate in the library but
  not explicit on the CLI or evidence display.
- **Correction:** `NOT_REQUESTED`, `OPTIONAL_REQUESTED`, and `REQUIRED` roles;
  requested/required flags; required CLI inclusion; separate
  `--optional-derivatives`.
- **Regression protection:** optional, required-partial, strict-required, JSON,
  and smoke-output tests.

### 7. Scheduler block misclassified as factual unavailability

- **Symptom:** an immediate RELIANCE/HDFCBANK/KAYNES batch completed RELIANCE
  but reported later symbols as incomplete/`UNAVAILABLE`; both succeeded when
  requested independently.
- **Risk:** temporary rate-gate state could become a false market-data claim.
- **Root cause:** `ProviderScheduleBlockedError` entered the generic evidence
  failure handler.
- **Correction:** typed `DEFERRED` evidence and batch status,
  `AnalysisContextDeferredError`, retained gate/retry metadata, and `UNKNOWN`
  required retrieval freshness.
- **Regression protection:** deterministic rate-gated batch tests prove one
  complete plus two deferred items, no suppressed symbols, no provider call for
  blocked work, and no hidden sleeps.

## Residual risks and deferred concerns

- Source-observation recency is not market-calendar aware.
- Dhan option chains expose acquisition time but no authoritative market-event
  timestamp.
- Cache, scheduler state, metrics, and single flight are process-local.
- Provider fallback/Zerodha and health-based degradation remain future work.
- A1.7 reports retryable deferral but does not schedule or wait for retries.
- News, filings, fundamentals, macro, sector, and peer evidence are not in A1.
- Provider identities and instrument masters can change; production must always
  resolve rather than copy acceptance examples.

These are accepted boundaries, not concealed claims of implemented behavior.

## Acceptance decision

TIAF_A1 is **accepted and baselined for A2 dependency** at tag `tiaf-a1.7`.
A2 may consume the public A1 contracts subject to the mandatory rules in
[`TIAF_A1_FOUNDATION_BASELINE.md`](TIAF_A1_FOUNDATION_BASELINE.md). No A1
contract grants recommendation or execution authority.

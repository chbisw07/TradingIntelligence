# A3.9 persisted acceptance captures

These 18 files contain **synthetic** A3.8 `OrchestrationRunRecord` captures, not
live observations. Each `.json.gz.b64` is UTF-8 capture JSON compressed with gzip,
then base64 wrapped at 88 columns. This keeps repeated original input packs,
projections, opinions and audit records intact without multi-megabyte JSON diffs.
Every decoded capture retains its original exact checksum and semantic hash.

`scripts._a3_9_cases.load_case(name)` loads the bytes without upstream execution.
`python scripts/a3_9_user_acceptance.py` exercises public A3.9 assembly/replay.

Authoring recipe: `tests.unit.opportunity_intelligence._capture_builder.build(name)`.
The 17 hypothetical cases use explicit precomputed synthetic specialist details
through the accepted A3.8 fixture pipeline. They test downstream assembly, not
specialist accuracy or whether raw market observations imply those details.
The `sparse_kaynes` case captures the existing A3.8 sparse KAYNES fixture with
unchanged accepted specialists; it is **not a recovered live historical capture**.
No persisted live KAYNES A3.8 record was present in the repository. No supportive
evidence from architecture illustrations was added to that fixture.

Fixture construction can execute A3.8 in tests; consumption, A3.9 assembly,
recorded replay and deterministic A3.9 verification cannot. Regenerating a fixture
may change operational clocks/checksums and must be reviewed as a fixture change.
Do not regenerate merely to make policy outputs more attractive.

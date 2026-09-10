# Authoritative Confirmation Gateway Live Acceptance

## Result

**Status:** `READY_TO_ACCEPT_AUTHORITATIVE_GATEWAY`

**Timestamp:** `2026-09-10T10:57:34.684093+05:30`

**Command:**

```bash
python scripts/authoritative_live_acceptance.py --live
```

The bounded read-only matrix performed exactly three official-source GETs. Two
official exchange paths returned content, passed source/final-domain validation,
were content-addressed, normalized into authoritative document evidence, and
replayed exactly without another live call. The configured Reliance IR location
returned a typed document-not-found result. No alternate domain, crawler,
browser, login, retry loop, or access-control bypass was attempted.

## Cases

| Subject | Source | Document type | Result | Authority/domain | SHA-256 | Replay |
|---|---|---|---|---|---|---|
| RELIANCE | Reliance IR | Annual report | `NOT_FOUND` / `DOCUMENT_UNAVAILABLE` | No document acquired | — | Exact |
| KAYNES | NSE | Corporate announcement | `AMBIGUOUS`; raw official response preserved, deterministic parser reported unsupported MIME | `AUTHORITATIVE` / `www.nseindia.com` | `c724d7bc3438edd66f8fc7d92b2f621afce7eb6c0f22402ae29a77b8fe27d667` | Exact |
| RELIANCE | BSE | Corporate action | `AMBIGUOUS`; document acquired but requested claim field was not explicitly present | `AUTHORITATIVE` / `www.bseindia.com` | `9a356af16e0c036e4e2b2acf67657b0e8d3fe34fb9e9130790a6feb77a066fb4` | Exact |

`AMBIGUOUS` is correct here: the live pass was designed to prove bounded
official acquisition, authority validation, document identity/fingerprinting,
normalization, and replay—not to invent a fact from an endpoint response. The
deterministic suite separately proves exact-label financial confirmation,
partial confirmation, contradiction, ambiguity, not-found, unavailable, and
out-of-coverage semantics.

## Provenance and normalization observations

- Initial and final/redirect domains were checked against the explicit source
  registry before authoritative classification.
- NSE and BSE source authority remained `AUTHORITATIVE`; canonical subjects
  remained `KAYNES` and `RELIANCE`.
- Raw response bytes were hashed before parsing. The two different responses
  produced two immutable cache entries.
- Parser limitations remained typed. Unsupported content did not become
  `fact=false`, and missing fields did not become contradiction.
- Confirmation results retained their discovery evidence IDs and linked route
  run/audit fingerprints.
- Serialized confirmation records reconstructed with identical semantic
  fingerprints after acquisition completed.
- No source observation, document version, or discovery evidence was deleted or
  overwritten.

## Failures and restrictions

- Reliance IR: configured annual-report path returned document unavailable. The
  adapter emitted `DOCUMENT_UNAVAILABLE`; the gateway emitted `NOT_FOUND` rather
  than false or contradicted.
- NSE: content acquisition succeeded; the deterministic parser did not claim to
  understand the returned MIME format and emitted
  `UNSUPPORTED_DOCUMENT_TYPE`. Raw content identity/provenance remained usable.
- BSE: content acquisition and deterministic parsing succeeded; the requested
  placeholder discovery field lacked explicit source evidence, so confirmation
  remained `AMBIGUOUS`.
- Access restrictions: none observed.
- Retries/bypasses: none.

## Security and secrets

The run was read-only and limited to three configured HTTPS URLs. It performed
no form submission, login, CAPTCHA handling, anti-bot bypass, mutation, or
broker operation. No API key, token, cookie, request headers, or secret value was
placed in evidence, output, or replay data.

## Acceptance basis

The live pass acquired two authoritative official-domain artifacts and replayed
all three outcomes exactly. Together with deterministic claim reconciliation,
deduplication, revision, parser-failure, event-cluster, evidence-graph,
provider-neutrality, and security tests, this satisfies the bounded
implementation acceptance. It does not claim complete NSE/BSE coverage,
production crawling, or live confirmation of a particular financial metric.

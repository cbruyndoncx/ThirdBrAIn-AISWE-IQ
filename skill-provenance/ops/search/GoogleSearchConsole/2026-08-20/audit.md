# Google Search Console evidence: 2026-08-20

Property: `sc-domain:skillprovenance.dev`

Canonical origin: `https://skillprovenance.dev/`

Observation date: 2026-08-20

Evidence scope: Sanitized reconciliation of the completed repository, production, and Search Console work. No fresh console inspection or mutation was performed while writing this record.

## Repository and production gates

| Lane | Result | Evidence |
|---|---|---|
| Repository and generated output | Pass | `node scripts/check-search.mjs` reported one sitemap page, zero defects, and zero infrastructure failures on 2026-08-20 |
| Production | Pass | The production validator reported one sitemap page, zero defects, and zero infrastructure failures on 2026-08-20 after deployment |

The passing contract covered the canonical homepage, robots directives, sitemap, JSON-LD, `llms.txt`, assistant-guide files, intentional host and protocol redirects, and hosted 404 behavior.

## Console observations

| Surface | Provider date | Observed state | Classification |
|---|---|---|---|
| `https://skillprovenance.dev/sitemap.xml` | Last read 2026-08-20 | `Success`; one discovered page | Accepted and provider-readable |
| `https://skillprovenance.dev/` URL Inspection | Observed 2026-08-20 | Individually reported indexed | Indexed at observation time |
| Aggregate Page indexing counts | Not captured | Unknown | Missing evidence, not zero |
| Aggregate Page indexing reason groups | Not captured | Unknown | Missing evidence, not an issue classification |
| Manual Actions | Not captured | Unknown | No conclusion supported |
| Security Issues | Not captured | Unknown | No conclusion supported |
| HTTPS report | Not captured | Unknown | No conclusion supported |
| Core Web Vitals | Not captured | Unknown | No conclusion supported; do not infer sufficient or insufficient data |
| Enhancements | Not captured | Unknown | No conclusion supported |
| Raw exports | None retained | Absent | Console evidence was observed through the authenticated UI only |
| Active validation batches | No batch observed or recorded in this property task | None recorded | Do not infer a fresh zero-count inspection |

Expected noise is limited to intentional redirects from HTTP and `www` hosts to the bare HTTPS origin, the noindex custom error page, synthetic 404 behavior, and machine-readable discovery files intentionally omitted from the HTML page sitemap.

## Action ledger

| Action | Accepted at | Confirmation | Result class | Repeat rule |
|---|---|---|---|---|
| Resubmitted `https://skillprovenance.dev/sitemap.xml` | 2026-08-20; time not recorded | Sitemap detail showed `Success`, last read 2026-08-20, one discovered page | Accepted submission; later crawling and indexing remain provider-controlled | Do not repeat while this accepted state remains current |

No separate homepage indexing request is recorded for this property task. Do not invent or repeat one based on the sitemap action.

## Current classification

- Repository defect: none supported by the 2026-08-20 gate.
- Production defect: none supported by the 2026-08-20 gate.
- Console action failure: none supported by the recorded sitemap confirmation.
- Pending state: ordinary recrawl and aggregate-report latency after later deployment.
- Unknown state: all uncaptured reports and aggregate counts listed above.

## Next review

Reopen the property only when the sitemap Last read advances beyond 2026-08-20, newer Page indexing or URL Inspection evidence appears, GSC names a failure, a material deployment remains absent after normal provider lag, or a repository or production gate fails. Re-run both gates before any new console mutation and preserve the accepted sitemap action in the do-not-repeat ledger.

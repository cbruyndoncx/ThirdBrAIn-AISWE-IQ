<!-- Upstream template: portfolio-search-indexing-audit bundle v5; repository contract v4 -->
---
title: "Search indexing"
purpose: "Property-specific index policy, validation commands, deployment gate, and console follow-up."
status: active
updated: 2026-08-28
owner: "Sam"
open_tasks: []
---
# Search indexing

## Property identity and boundaries

| Field | Value |
|---|---|
| Canonical origin | `https://skillprovenance.dev/` |
| Console property | Google Search Console `sc-domain:skillprovenance.dev` |
| Property mode | Website |
| Owning repository | `snapsynapse/skill-provenance` |
| Deployable artifact | Repository root `.` |
| Deployment | GitHub Pages legacy build from `main` `/`, custom domain, HTTPS enforced |

The repository root is both source and deployable static artifact. If that deployment configuration changes, update `search-audit.config.json` and this policy before relying on either validation lane.

## Index policy

| Surface | Policy | Reason |
|---|---|---|
| `/` | Index and include in sitemap | Canonical product and installation page |
| `/404.html` and unknown routes | `noindex` and omit from sitemap | Error handling, not a content destination |
| `/robots.txt`, `/sitemap.xml`, `/llms.txt`, `/verify.sh` | Crawlable and omitted from the page sitemap | Search, agent discovery, and pinned standalone verification surfaces |
| `/.well-known/assistant-guide.txt` and sidecar | Crawlable and omitted from the page sitemap | Bounded agent verification surfaces |
| GitHub, ClawHub, and other external copies | Omit from this sitemap | Distribution copies are not site canonical pages |

The site has one English canonical HTML page. Multilingual indexing, locale canonicals, and `hreflang` are not applicable unless additional localized pages are deliberately published.

The homepage links the deployed `llms.txt`, standalone verifier, assistant
guide, and repository-hosted agentic-surface disclosure. Bundle and GuideCheck
release tags remain separate; public installation copy uses exact bundle tags
rather than a provider's generic latest label.

## Evidence governance

- This file is the living property policy and action ledger.
- Sanitized dated observations belong under `ops/search/<provider>/YYYY-MM-DD/`.
- Raw exports, authenticated screenshots, traces, browser state, account identity, and private queries must remain outside Git or under ignored `.search-evidence-private/` and `.playwright-mcp/` directories.
- Console absence, an uninspected report, a stale report, insufficient data, and a measured zero are different states. Record the observed state without filling gaps by inference.
- New individual URL Inspection evidence overrides older aggregate evidence for that URL. An accepted action records provider receipt, not completion.

## Validation lanes

- Offline: `node scripts/check-search.mjs`
- Production after deployment: `node scripts/check-production-search.mjs`
- Machine-readable output: add `--json`
- Local HTTP test: add `--base=http://127.0.0.1:8765/` after starting the static server on port 8765

Exit code `0` is pass, `1` is a site defect, and `2` is configuration or infrastructure failure.

For a creator-profile or external-platform property, replace the website validation lanes with the reports and controls the property actually exposes. Do not invent repository, production, sitemap, or indexing work.

## Deployment and console sequence

1. Run the normal build and offline search contract.
2. If deployment copies or transforms output, stage the exact deployable artifact with the same builder used by release automation.
3. Ensure repository-wide checks include newly scaffolded files, including checks based on `git ls-files`.
4. Deploy through the repository's normal release path.
5. Wait for the deployment to complete.
6. Run the production search contract.
7. Confirm the deployed sitemap URL set matches the repository sitemap.
8. Refresh a materially changed stale sitemap at most once, using its full canonical URL for a domain property.
9. Inspect or request indexing for canonical HTML pages.
10. Start issue-group validation only when matching production behavior is live.
11. Record console state under `ops/search/<provider>/YYYY-MM-DD/`.

## Expected noise

- `http://skillprovenance.dev/`, `https://www.skillprovenance.dev/`, and `http://www.skillprovenance.dev/` intentionally redirect to `https://skillprovenance.dev/`.
- `/404.html` and synthetic unknown paths intentionally return the custom noindex error page.
- Machine-readable discovery files are intentionally not listed as canonical HTML pages in the sitemap.
- Provider crawl and indexing reports may lag accepted sitemap submissions and deployed changes.

## Current baseline

Detailed evidence: [`ops/search/GoogleSearchConsole/2026-08-20/audit.md`](search/GoogleSearchConsole/2026-08-20/audit.md)

| Lane | Evidence date | Classified state |
|---|---|---|
| Repository and generated output | 2026-08-20 | Pass: one sitemap HTML page, zero defects, zero infrastructure failures |
| Production | 2026-08-20 | Pass: canonical, robots, sitemap, JSON-LD, agent discovery files, redirects, and hosted 404 behavior matched the contract |
| Google Search Console sitemap | 2026-08-20 | `Success`; last read 2026-08-20; one discovered page |
| Google Search Console URL Inspection | 2026-08-20 | Homepage individually reported indexed |
| Aggregate Page indexing counts and reason groups | 2026-08-20 | Unknown: not captured in the available evidence |
| Other GSC reports and exports | 2026-08-20 | Not captured; do not interpret as zero or clean |
| Active validation batches | 2026-08-20 | None observed or recorded in this property task; no new inspection was performed for this reconciliation |

The repository and production evidence support a passing implementation. Later provider recrawl or aggregate-report changes remain subject to ordinary provider lag.

## Console action ledger

Read this table before opening the console. Add only observed actions and confirmations. An accepted request remains pending until a later report proves completion.

| Provider and property | Action and target | Accepted at | Confirmation | Result class | Repeat policy | Next review |
|---|---|---|---|---|---|---|
| Google Search Console, `sc-domain:skillprovenance.dev` | Resubmit `https://skillprovenance.dev/sitemap.xml` | 2026-08-20; time not recorded | Sitemap detail showed `Success`, last read 2026-08-20, one discovered page | Accepted submission, not proof of future recrawl or indexing | Do not repeat while this accepted state remains current | When the sitemap Last read advances, GSC names a sitemap failure, a materially deployed revision remains absent after normal provider lag, or a repository/production gate fails |

Keep rejected attempts and unknown outcomes distinct from accepted actions. Do not repeat an accepted action merely because the provider report remains stale.

## Do not repeat

- Do not resubmit `https://skillprovenance.dev/sitemap.xml` while the accepted 2026-08-20 state remains current.
- Do not request indexing for the already indexed homepage without newer contradictory evidence and a passing production gate.
- Do not start validation for intentional redirects, the noindex error page, machine-readable files omitted from the HTML sitemap, or a reason group that was not actually observed.
- Do not treat provider lag, missing aggregate counts, or absent exports as a repository defect.
- Do not store authenticated browser artifacts or private Search Console data in Git.

## Next review conditions

Review this property only when at least one condition is true:

- the sitemap Last read advances beyond 2026-08-20;
- Page indexing or URL Inspection produces newer evidence;
- GSC names a sitemap, indexing, security, manual-action, HTTPS, or enhancement issue;
- a material canonical HTML revision is deployed and remains absent after normal provider lag;
- the repository or production search validator fails; or
- deployment source, canonical origin, or index policy changes.

At the next authorized review, re-run repository and production gates before any console mutation, inspect only the reports needed by the trigger, update the dated evidence, and keep accepted requests out of the retry queue.

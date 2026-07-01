---
name: product-audit-pipeline
description: >
  Site-wide product-page (PDP) audit orchestrator for Shopify stores. Pulls
  ALL products via Shopify connector pagination, runs a 2-tier audit (Tier 1
  metadata-only quick-scan on all products + Tier 2 full product-analyze
  deep-scan on the prioritized subset), ranks the portfolio by opportunity
  (traffic × gap severity), and escalates any open Merchant-Center feed-risk
  gate to the top of the queue regardless of score. Produces a ranked
  portfolio report (HTML/MD + per-product scores + a prioritized action
  queue). Use when user says "audit all products", "product portfolio
  audit", "which products need optimizing", "product page audit", "find weak
  product listings", "PDP audit pipeline", or any whole-site Shopify
  product-page review.
user-invokable: true
argument-hint: "<site> [--tier ...] [--limit N] [--min-impressions N] [--strict]"
license: MIT
metadata:
  author: "Khue Tran"
  version: "0.1.0"
  category: audit
---

# Product Audit Pipeline: Site-Wide PDP Portfolio Analyzer

Sister skill to `collection-audit-pipeline` but for Shopify product pages
(PDPs). Runs a 2-tier audit across ALL products on a site (typically
200–5,000+ for mid-size to large Shopify stores), surfacing feed-risk gates,
traffic-weighted gaps, and a prioritized action queue.

Reference documents:
- `references/tier-1-quick-scan.md` — Tier 1 metadata-only checklist
  (Shopify-connector-only, no WebFetch). Scores 0–40 per product.
- `references/opportunity-scoring.md` — traffic × gap-severity ranking logic
  + feed-risk override rules
- `references/portfolio-report-template.md` — output HTML/MD structure

## Input Handling

- **Site** — e.g. `your-store.com` (resolves to Shopify connector)
- The pipeline assumes the Shopify connector is already authenticated for
  the target shop. Verify with `get-shop-info` before running.

## Flags

- `--tier <variant-rich|technical-hardware|bundles-sets|consumables-bulk|seasonal-drops|specialty-premium>` —
  restrict the run to one product-category tier (default: all tiers)
- `--limit N` (default: 30) — number of prioritized products to promote to
  full Tier-2 deep-scan via `product-analyze`
- `--min-impressions N` (default: 0) — floor on 90d GSC impressions for a
  product to qualify for the opportunity ranking (use to exclude
  zero-traffic long-tail noise from Tier 2 selection; Tier 1 still scans
  everything regardless of this flag)
- `--strict` — pass-through to `product-analyze`; N/A items earn 0 instead
  of partial credit. Recommended default for pipeline runs.
- `--no-gsc` — skip GSC pull entirely (Tier 1 falls back to inventory/price
  signals only for prioritization; Tier 2 CTR sub-checks go N/A)
- `--format html|md|json` — default html for portfolio dashboard; md for
  human-readable; json for downstream consumption

## Pipeline Phases

### Phase 0 — Connector check (10 sec)

Verify Shopify connector is authenticated and matches the site:
```
get-shop-info → confirm domain matches argv[1]
```
If mismatch, fail fast with "switch-shop required" instruction.

### Phase 1 — Bulk metadata pull (2–8 min for ≤5,000 products)

Paginate `search_products` 50/page until `hasNextPage = false`. Cache to
`output/[site]/products/_pipeline/shopify-products-all.json`.

Fields collected per product:
- `id`, `handle`, `title`, `productType`, `vendor`, `tags`, `status`,
  `updatedAt`, `publishedAt`, `createdAt`
- `descriptionHtml` (length only, not full audit at this phase)
- `seo.title`, `seo.description`
- `variants` (count, price range, `compareAtPrice`, `sku`, `barcode`,
  `inventoryQuantity`, `availableForSale`)
- `images` (count, whether any `altText` is null/empty)
- `metafields` presence flags (specs block, reviews app)

### Phase 2 — Tier detection (in-memory, fast)

For each product, apply the tier rules from `product-analyze` SKILL.md
(hero / variant-parent / technical / consumable / new / standard), mapped
onto the kit's portfolio-level category taxonomy for reporting:

| Portfolio tier | Detection |
|---|---|
| **variant-rich** | ≥5 variants across color/size/style options |
| **technical-hardware** | `productType`/title implies spec-driven durables (electronics, tools, appliances, equipment) |
| **bundles-sets** | title/tags indicate multi-item SKU (kit, set, bundle, multipack) |
| **consumables-bulk** | low differentiation, repeat-purchase, low price, high `inventoryQuantity` turnover |
| **seasonal-drops** | tags/collection membership indicate a limited-window release |
| **specialty-premium** | high price point relative to store median + low variant count |

### Phase 3 — Tier 1 quick-scan score (in-memory)

For each product, score against Shopify-metadata-only checks (no WebFetch
needed). See `references/tier-1-quick-scan.md` for full rubric:

| Check | Max | Detection |
|---|---|---|
| Description length adequacy | 6 | `descriptionHtml` word count ≥ 150 (else flag thin) |
| Image count adequacy | 5 | `images.count` ≥ 4 (else flag under-imaged) |
| Image alt-text coverage | 4 | 0 images with null/empty `altText` |
| `seo.title` present + length | 4 | 50–60 chars, non-empty |
| `seo.description` present + length | 3 | 120–160 chars, non-empty |
| Price sanity | 3 | price > 0; `compareAtPrice` (if set) > price |
| Identifiers present (GTIN/MPN/SKU) | 5 | at least `sku`; `barcode` present when vendor is a known manufacturer |
| Inventory / availability sane | 4 | `availableForSale` consistent with `inventoryQuantity` > 0 |
| Published + not orphaned | 3 | `status = ACTIVE`; not missing from every collection |
| Freshness | 3 | `updatedAt` within 180 days |

Total Tier 1 max: 40 pts. This is a cheap **proxy**, not the full 100-pt
`product-analyze` rubric — it exists purely to rank/triage before spending
WebFetch + GSC budget on Tier 2.

### Phase 4 — GSC 90-day pull (bulk, per-URL)

Pull impressions/clicks/position/CTR for each product URL (batch query,
not one-by-one). Merge into the Phase 1 cache. Skip if `--no-gsc`.

### Phase 5 — Site-wide pattern statistics

Compute and report on the full product set:
- % thin description (<150 words) by tier
- % under-imaged (<4 images) by tier
- % missing alt text
- % missing `seo.title`/`seo.description`
- % missing identifiers (`sku`/`barcode`) by vendor
- % zero-impression products (90d) — dead-weight candidates, separate from
  the optimization queue
- Tier distribution (variant-rich / technical-hardware / bundles-sets /
  consumables-bulk / seasonal-drops / specialty-premium counts)
- Stale-180d vs recently-updated split

### Phase 6 — Merchant-Center feed-risk pre-scan 🛑 (highest priority signal)

Before ranking by opportunity, run a lightweight feed-risk check against
the Phase 1+4 cache for every product (this does NOT require the full
Tier-2 WebFetch pass — enough signal exists in Shopify connector fields
alone to flag candidates for confirmation):

- `compareAtPrice` set but ≤ `price` (schema/price inconsistency risk)
- `availableForSale = true` but `inventoryQuantity = 0` and no
  backorder/pre-order tag (availability mismatch risk)
- `availableForSale = false` but still linked from active collections/nav
  (stale disapproved-looking listing)
- Missing `barcode` (GTIN/MPN) AND vendor matches a known-manufacturer
  pattern (brand-name vendor, not a private-label placeholder)
- `status = ACTIVE` with zero images (schema `image` requirement failure)

Any product matching one or more of these earns a `🛑 FEED-RISK CANDIDATE`
flag. These candidates are queued for **Tier-2 confirmation first**,
independent of their Tier 1 score or traffic — see Phase 7. A disapproved
product earns $0 regardless of how well-written its copy is, so this gate
overrides normal opportunity ranking.

### Phase 7 — Opportunity ranking + Tier 2 selection

Rank all products (excluding `--min-impressions` floor failures, if set) by:

```
opportunity_score = normalized(gsc_impressions_90d) × normalized(gap_severity)
gap_severity = (40 − tier_1_score) / 40
```

Then build the Tier-2 candidate list in this order:

1. **All `🛑 FEED-RISK CANDIDATE` products from Phase 6** — top of the
   queue unconditionally, capped only by a sane ceiling (e.g. top 50 by
   revenue/traffic if the flagged set is very large) so the pipeline
   doesn't stall auditing a long tail of zero-traffic feed risks before
   anything else.
2. **High traffic + weak page** — top `opportunity_score` products not
   already captured in (1). This is "high impressions, low Tier-1 score"
   — pages leaking the most existing demand.
3. **Bottom-quartile Tier 1 score with meaningful traffic** — fills out
   the remainder of `--limit` if (1)+(2) don't reach it.

Skip: `status != ACTIVE`, orphaned zero-collection zero-traffic products
(not real audit candidates — flag separately as "prune candidates" in the
report, don't spend Tier-2 budget on them).

### Phase 8 — Tier 2 deep-scan dispatch

For each selected product, dispatch
`product-analyze <url> --tier <auto-detected> --strict` and collect the
full 100-pt scorecard, including the `🛑 Merchant-Center feed-risk` GATE
detail from that skill's Step 3.

**Delegate Tier-2 dispatches to sub-agents at the appropriate model tier**
rather than running them serially in the main session:
- Route each `product-analyze` call through a Sonnet-tier sub-agent
  (`Agent(model: "sonnet")`) — this is a "multi-step routine: apply rubric,
  pull 3 data sources, score, write file" task, not a judgment call.
- Batch dispatches (e.g. 5–10 concurrent sub-agents) rather than one at a
  time, since each product's audit is independent of the others.
- Reserve the orchestrating session (this pipeline) for aggregation,
  ranking, and the final portfolio synthesis — not for running the
  per-product rubric itself.

If `--no-gsc` not set, mandate GSC pull for each (already cached from
Phase 4 — reuse, don't re-pull).

### Phase 9 — Portfolio report assembly

Output:
- `output/[site]/products/_portfolio/product-audit-portfolio.md` — main
  report
- `output/[site]/products/_portfolio/action-queue.md` — ranked action list
  (feed-risk first, then opportunity-ranked)
- `output/[site]/products/_portfolio/site-patterns.md` — pattern stats
- `output/[site]/products/_portfolio/prune-candidates.md` — orphaned /
  zero-traffic products not worth auditing
- `output/[site]/products/[handle]/product-quality-score.md` — per
  Tier-2-selected product (from Phase 8 dispatch)

## Phase pre-requisites (don't skip)

| Phase | Exit criterion |
|---|---|
| 0 | Connector authenticated + domain matches |
| 1 | All products in JSON cache, count ≥ 10 (else nothing to audit) |
| 2 | Every product has a portfolio tier assigned |
| 3 | Tier 1 scores in distribution |
| 4 | GSC merged (or explicitly skipped via `--no-gsc`) |
| 5 | Pattern stats computed |
| 6 | Feed-risk candidates flagged (list may be empty, but the pass must run) |
| 7 | Tier-2 candidate list built, feed-risk products first |
| 8 | Per-product full scorecards saved (for all selected candidates) |
| 9 | All report files written |

## Cost estimate (rough, per mid-size site ≈ <N> products)

- Phase 1 (pagination): scales with product count / 50 per page
- Phase 2–3, 5–7: in-memory, no API calls
- Phase 4 (GSC bulk): 1 batched pull, not per-product
- Phase 6: in-memory pass over the Phase 1+4 cache, no extra API calls
- Phase 8 Tier 2 (default 30 products): ~30 × (1 Shopify + 1 WebFetch + 1
  GSC) = ~90 API calls, dispatched via batched Sonnet sub-agents. Optional
  narrower run with `--limit` or `--tier`.
- Phase 9: file writes only

Total: scales sub-linearly with catalog size thanks to the Tier 1/Tier 2
split — Tier 1 covers the whole catalog cheaply, Tier 2 spend stays capped
by `--limit` regardless of how large the store is.

## What this skill does NOT do

- Does NOT optimize or rewrite product copy/schema, and does NOT push any
  change to Shopify (audit-only) — that's `product-optimize`
- Does NOT replace `product-analyze` for single-page deep audits — that
  skill remains the canonical "I want to deep-dive THIS product" tool
- Does NOT resolve feed-risk flags itself — it surfaces and prioritizes
  them; confirmation + fix still runs through `product-analyze` (Tier 2)
  and `product-optimize`

## Composition

- **Calls**: `product-analyze` (per prioritized product in Phase 8, via
  delegated sub-agents)
- **Feeds**: `product-optimize` — consumes the ranked queue + per-product
  reports as its work backlog
- **Reads from**: Shopify connector + GSC connector
- **Writes to**: `output/[site]/products/_portfolio/` + per-product
  artifacts under `output/[site]/products/[handle]/`

## Output convention

```
output/[site]/products/_portfolio/
├── shopify-products-all.json          (Phase 1 cache)
├── tier-1-scores.json                 (Phase 3 output, all products scored)
├── site-patterns.md                   (Phase 5 stats)
├── feed-risk-candidates.md            (Phase 6 flagged list)
├── action-queue.md                    (Phase 7 ranked list)
├── prune-candidates.md                (Phase 7 excluded orphans)
└── product-audit-portfolio.md         (Phase 9 main deliverable)

output/[site]/products/[handle]/
└── product-quality-score.md           (Phase 8, Tier-2-selected only)
```

## Re-run / re-audit

Pass `--resume` to skip Phase 1 if the JSON cache is < 24h old. Useful when
iterating on report format, re-running Tier 2 with a different `--limit`,
or re-checking feed-risk candidates after a fix has been pushed via
`product-optimize`.

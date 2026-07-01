---
name: collection-mega-hub-optimize
description: >
  End-to-end 12-step workflow to optimize a Shopify mega-hub or brand-hub
  collection page from a low baseline composite score (48-65) to 85+/100.
  Combines collection-analyze (audit) + collection-content-deep (1,500-2,000w
  content) + a hybrid template + internal linking + an optional brand-suffix
  title override. Field-tested at scale on a large multi-brand ecommerce catalog's
  mega-hubs (mean composite lift +30-35 points). Includes HARD gates: zero URL
  hallucination, zero em-dash, zero AI-trigger phrases, branded H1,
  brand-suffix opt-out, 4-schema bundle. Use when the user says "optimize
  mega-hub", "optimize brand-hub collection", "scale collection optimization",
  or any "next-hub" request.
user-invokable: true
argument-hint: "<collection-handle-or-url> [--site <domain>] [--tier mega-hub|brand-hub] [--dry-run] [--skip-template]"
license: MIT
metadata:
  author: "Khue Tran (ktbteam)"
  version: "1.6.0"
  category: optimize
  composite_baseline: "48-65 / 100"
  composite_target: "85+ / 100"
  changelog: >
    v1.6.0 — Added Step 2 workflow path selection (Path A default vs Path B
    mega-hub). Path B requires a `custom.sub_categories` metafield for the
    sub-nav chip group; documents the canonical JSON format, a pre-flight
    HEAD-check rule, and Gate 17 (sub-nav render verify).
    v1.5.2 — Added Gate 16 (custom templateSuffix pre-flight check): a non-null
    templateSuffix means deep content + FAQ accordion may not render even when
    metafields save successfully.
    v1.5.1 — Added Gate 15 (FAQ live render verify): flat `[{q,a}]` shape only,
    never a schema.org FAQPage wrapper.
    v1.5.0 — Skip hero auto-gen; flag for a human upload instead. Delegate
    simple lookups (HEAD checks, count pulls) to a cheap sub-agent to protect
    the main session's context budget.
    v1.4.0 — Added Step 13 (optional publish notification) + Gate 14.
    v1.3.0 — Gate 13 tier-aware content depth (tools template).
    v1.2.0 — Gate 0 knowledge-base-first factcheck + Gate 12 no source labels.
    v1.1.0 — Gates 7-11 (factcheck count, OG image, tagline, filter, sub-nav).
    v1.0.0 — Baseline gates 1-6.
---

# Collection Mega-Hub Optimizer: 12-Step Workflow

End-to-end workflow that takes a Shopify mega-hub or brand-hub collection from
"thin tagline + missing schema + 0 internal links" to "deep content + 4-schema
bundle + 12-20 internal links + sub-60ch keyword-dense title". Composite score
target: **≥85/100** per the `collection-analyze` rubric.

**This skill is the production playbook.** It chains `collection-analyze`
(audit), `collection-content-deep` (1,500-2,000w content), the Shopify
connector (metafield + template push), and an optional theme-level
brand-suffix opt-out (Path 2). Every step has a HARD gate that must pass
before the next step runs.

## When to invoke

- After `collection-analyze` returns composite <80 for a mega-hub or brand-hub
- When the user asks to optimize a hub to the proven pattern
- When scaling the pattern across a batch of hubs
- Pipeline mode: chained from `collection-audit-pipeline` for batch optimization

## When NOT to invoke

- Tier `sub` (productCount <100) — over-engineering, use a simpler patch
- Tier `tool` — different price-tier rules, different content depth
- Tier `new` (<30d) — wait until the tier stabilizes
- Mega-hub `all-products` (full-catalog umbrella) — different positioning

## The 12-Step Workflow

### Step 0.5 — MANDATORY: knowledge-base factcheck source pull (HARD GATE 0)

**🚨 BEFORE ANY content writing**, grep your product knowledge base at
`knowledge-base/*.md` for the collection's product line. This is the
**TIER_INTERNAL** authority — your own first-party product specs, sales data,
technique workflows, upsell pairings, target-customer profiles, positioning,
and margin signals. (The knowledge base is store-owned data you provide; it is
git-ignored and never ships with this repo. See `knowledge-base/README.md`.)

```bash
# Step 0.5a — Open the KB index
cat knowledge-base/INDEX.md

# Step 0.5b — Grep files matching the product-line keyword
grep -l -i "<product-keyword>" knowledge-base/*.md

# Step 0.5c — Read the full matched KB file(s)
# Step 0.5d — Extract the relevant facts before writing
```

**Factcheck priority order (HARD)**:

| Tier | Source | Authority | Action |
|------|--------|-----------|--------|
| **TIER_INTERNAL** | `knowledge-base/*.md` | Highest | Read silently. Extract facts. Use as the foundation. |
| **TIER_SHOPIFY** | Shopify Admin GraphQL (Step 1 pulls) | High | Verify count vs variant. HEAD-check URLs. |
| **TIER_WEBFETCH** | External WebFetch | Fallback | Only when KB + Shopify don't cover it (regulatory, third-party newer specs). |
| **TIER_GUESS** | Model estimate beyond the above | **NEVER acceptable** | Block content publish. |

**Knowledge-base structure (TIER_INTERNAL coverage)**: keep one markdown file
per product line, named `pk-<product-line>.md`, plus an `INDEX.md` that maps
each product-line keyword to its file. Each file should document positioning,
best-seller status, price tier, target customer, companion/upsell pairings, and
application technique for that line. See `knowledge-base/INDEX.example.md`.

**HARD GATE 0 (KB-first factcheck)**: you CANNOT proceed to Step 1 without
completing Step 0.5. If the KB doesn't cover the product line, document that
gap in `baseline-snapshot.json` so the coverage can be added, and note
"TIER_INTERNAL gap" before falling back to TIER_SHOPIFY + TIER_WEBFETCH.

**Field lesson**: skipping this step and writing from Shopify titles + guesses
produces hallucinated facts (wrong product structure, wrong application method,
wrong skill-level target, missed best-seller positioning, missed documented
upsell pairings). When the KB documents the line, it is the spine of the copy.

### Step 1: Baseline pull (parallel)

Pull from THREE sources in parallel:

```graphql
# 1a. Shopify Admin GraphQL
query CollectionBaseline {
  collection(id: $id) {
    id handle title description
    productsCount { count }
    sortOrder ruleSet { rules { column relation condition } }
    image { url }
    templateSuffix
    seo { title description }
    metafields(first: 20) { nodes { namespace key value type } }
  }
}
```

```javascript
// 1b. Live page extraction (Chrome MCP / WebFetch)
const data = {
  title: document.title, titleLen: document.title.length,
  metaDesc: document.querySelector('meta[name=description]')?.content,
  h1: document.querySelector('h1')?.innerText,
  schemas: [...document.querySelectorAll('script[type="application/ld+json"]')]
    .map(s => JSON.parse(s.innerHTML)),
  productCards: document.querySelectorAll('.product-card').length,
  filterSidebar: !!document.querySelector('.facets__form'),
};
```

```javascript
// 1c. GSC 90d (optional — skip with --no-gsc)
// Top queries, CTR, position distribution
```

**Output**: `output/[site]/[handle]/baseline-snapshot.json`

**🚨 HARD GATE 16 — Custom templateSuffix pre-flight check**:

After the baseline pull, check the `templateSuffix` value:

| templateSuffix value | Action |
|---|---|
| `null` / empty string | ✅ Uses the default template `collection.json` → has `collection-content` + `collection-faq` sections → deep content + FAQ accordion render. Proceed normally. |
| Any string value (e.g. `custom-template`, `new-arrivals`) | 🚨 **Custom template** assigned. Deep content (`custom.deep_content_html`) + FAQ accordion (`custom.faq_jsonld`) **MAY NOT render visibly**. FAQ JSON-LD schema typically still renders (SEO benefit retained). STOP and surface to the site owner: "Collection uses custom templateSuffix=<value>. Confirm: (a) switch to the default template, or (b) add `collection-content` + `collection-faq` sections to the custom template before pushing content." Get explicit go-ahead before proceeding. |

**Why check early**: a custom template can accept all metafields successfully
and render the FAQ JSON-LD schema (SEO/AI-citation benefit), yet NOT render the
visible deep content or FAQ accordion. Catching this early avoids a visual
content gap and wasted click-through on impressions.

**If a custom template is confirmed acceptable**: proceed with awareness that
the visible-render Gates 13 + 15 are N/A. The notification should reflect the
honest gate count (e.g. 12/15 rather than 15/15). Banner + SEO title + SEO
description + FAQ JSON-LD schema still provide ranking + SERP click-through value.

### Step 2: Tier detection + WORKFLOW PATH SELECTION

**🚨 CRITICAL DECISION** — tier-detect and choose Path A or Path B BEFORE
writing any content. The wrong path means the wrong metafields, which means a
broken layout.

**Decision tree:**

| Signal | Tier | Workflow |
|---|---|---|
| productsCount ≥ 500 SKUs **AND** cross-brand (≥3 vendor) | **MEGA-HUB** | **Path B** |
| productsCount ≥ 500 SKUs **AND** single brand (1-2 vendor) | **BRAND-HUB** | **Path B** (sub-nav showcases brand sub-lines) |
| Smart collection rule with multiple TYPE/TAG combos + a custom template with several `featured-collection-grid` blocks | **MEGA-HUB confirmed** | **Path B** |
| productsCount 100-500 SKUs **AND** a specific category | **DEFAULT (sub-collection)** | **Path A** |
| productsCount < 100 SKUs **AND** single-brand seasonal | **DEFAULT (seasonal)** | **Path A** |

**Path A — DEFAULT collection workflow** (sub-collection, seasonal, brand sub-line):
- Step 6: tier-aware deep content template (variant-rich 8-section / hardware 10-section / seasonal 7-section / bundle 7-section / specialty 9-section / sub 8-section)
- Step 8 metafields: 4 total
  - `custom.deep_content_html`
  - `custom.faq_jsonld` (flat `[{q,a},...]` format)
  - `global.title_tag`
  - `global.description_tag`
- Step 9 banner descriptionHtml (20-40 words)
- Step 10 templateSuffix=null

**Path B — MEGA-HUB collection workflow** (cross-brand category with a sub-collections nav):
- Step 6: mega-hub 8-section deep content template
- Step 7.5: determine the sub-collection list (3 sources, priority order):
  1. The site owner provides an explicit list
  2. Pull the existing custom template's `featured-collection-grid` blocks' `settings.collection`
  3. Curate from Shopify search by related vendor/type
  → Format: `[{"handle": "...", "title": "..."}, ...]`
  → PRE-FLIGHT: HEAD-check all handle URLs return 200 (404 = broken nav UX)
- Step 8 metafields: **5 total** (4 same as Path A + `custom.sub_categories`)
  - `custom.deep_content_html`
  - `custom.faq_jsonld` (flat format)
  - **`custom.sub_categories` (json, list of {handle, title}) ← MEGA-HUB ONLY**
  - `global.title_tag`
  - `global.description_tag`
- Step 9 banner descriptionHtml (20-40 words)
- Step 10 templateSuffix=null (the theme's `main-collection-banner` reads the `sub_categories` metafield + auto-renders the `sub-category-nav` chip group inline + sidebar)
- Step 11 Gate 17: verify sub-nav render — `curl -s <url> | grep -oE 'class="sub-category-nav__link"\s*>[^<]+</a>'` must return ≥3 entries with labels

Auto-detect the tier per the `collection-analyze` rules. For mega-hub and
brand-hub tiers, query the Shopify connector for ALL related sub-collections
(used in Step 7 internal linking):

```graphql
query BrandSubCollections {
  brand: collections(first: 20, query: "title:*<brand-keyword>*") {
    edges { node { handle title productsCount { count } } }
  }
}
```

**HARD GATE 1 (URL inventory)**: NEVER write an internal URL in any subsequent
step without verifying the handle exists in this query result. Do not invent
handles or slugs in long-form content — pull the inventory and link only what
exists.

### Step 3: SEO title rewrite (Path 2 — brand-suffix opt-out)

Apply the **Path 2 override pattern**:

1. Set the boolean metafield `custom.suppress_brand_suffix = true` on the collection
2. Rewrite `seo.title` to a 55-60ch full keyword + USP, with NO brand suffix
3. The theme layout liquid (`layout/theme.liquid`) must be patched once
   site-wide to honor the metafield (see `references/theme-patch-stiletto.md`)

Pattern: `{Brand or Category} {Product Lines}: {USP or Modifier}`

Examples (as reference for shape only, across different verticals):
- "Brand A Running Shoes: Trail, Road & Racing Wholesale" (~50ch)
- "Brand B Wireless Earbuds, Over-Ear & Sport Headphones" (~52ch)
- "Standing Desks: Brand A, Brand B, Brand C at Wholesale" (~53ch)

**HARD GATE 2 (title length)**: HTML title ≤60ch on live-page verify (Step 12).

### Step 4: Meta description rewrite (120-160ch)

Pattern: `Shop {N} {category} from {brand list, 3-7 items} at wholesale. Free shipping over ${threshold}.`

**HARD GATE 3 (AI-trigger phrases)**: NEVER use "Discover", "Experience",
"Elevate", "Explore", "Delve into", "Navigate the landscape", "In today's
fast-paced", "In conclusion", "It's important to note", "flawless",
"exploration". Replace with action verbs: "Shop", "Browse", "Get", "Stock",
"Find", "Compare".

### Step 5: H1 fix (if generic)

If the current `collection.title` is generic ("Brand - All products", "BRAND",
ALL CAPS shouty) and the user has cleared cascading effects (nav menu uses
linklist labels), rename `collection.title` via `collectionUpdate`.

Renaming the title cascades to:
- ✅ H1 on the collection page
- ✅ Breadcrumb
- ✅ Internal anchor text from PDPs
- ⚠️ Navigation menu — verify the theme uses `linklist.links.title` separately

Skip Step 5 if the Shopify nav can't be updated separately.

### Step 6: Deep content generation (tier-aware sections)

**🚨 PRE-WRITE CHECK**: you must have completed Step 0.5 (KB pull) and have KB
facts in working memory before invoking content gen. If Step 0.5 returned
"TIER_INTERNAL gap" for this product line, log the gap and fall back to Shopify
titles + the product-description metafield + WebFetch product spec pages. Never
guess specs.

**🚨 TIER-AWARE CONTENT DEPTH (Gate 13)**: the content section template VARIES
by product category. Pick the correct tier template before writing:

| Category tier | Example verticals | Section template | Typical word count | Visual assets |
|---|---|---|---|---|
| **variant-rich** (one line, many colors/styles/sizes) | apparel colorways, cosmetics, paint colors | 8-section template (Why stock → Lines → How to pick → Compare table → How to use → Care → Pricing → Related) | 1,500-2,000w | Hero only |
| **technical / hardware** (spec-driven durables) | electronics, tools, appliances, equipment | **10-section hardware template** (see below) | **1,800-2,500w** | **Hero + spec chart SVG + product detail callouts** |
| **bundles / sets / kits** (multi-item SKUs) | gift sets, starter kits, multipacks | 7-section bundle template (composition + value math) | 1,200-1,700w | Hero + bundle composition diagram |
| **consumables / bulk** (volume tier) | supplies, refills, wholesale volume | 6-section pricing-led template (discount math + reorder workflow) | 1,000-1,500w | Hero + pricing table |
| **seasonal / drops** (time-boxed collections) | holiday lines, seasonal apparel, limited editions | 7-section seasonal template (promotion calendar + theme story) | 1,200-1,700w | Hero + seasonal story |
| **specialty / premium** (niche or effect products) | artisan, premium, effect goods | 9-section specialty template (use-case led: workflow + companion pairings + seasonal mapping) | 1,500-2,000w | Hero + use-case callouts |

**The 10-section hardware template (REQUIRED for any spec-driven durable: electronics, tools, appliances, equipment, machines)**:

1. **Why buyers choose this category** — what the product does + scope at the site
2. **The catalog at the store** — list product types/models with a key spec one-liner per model
3. **Specs comparison table** — the parametric spine that differentiates models (power, capacity, weight, dimensions, materials, ratings, warranty, etc.)
4. **How to pick the right model** — `<ul>` with 4-6 use-case scenarios mapped to spec ranges (e.g. "High-volume / daily professional use: pick the higher-capacity model")
5. **Accessory / consumable compatibility** — which add-ons, parts, or consumables fit which model. Cross-link to the accessories collection
6. **Setup + safe-use workflow** — `<ol>` step-by-step proper use + safety callouts
7. **Maintenance + care** — cleaning, part replacement, and upkeep (per manufacturer / industry guidance where applicable)
8. **Troubleshooting** — common failure modes + fix actions
9. **Pricing at the store** — pricing model + bundle discounts
10. **Related collections at the store** + **Related reads** (accessories, companion products, buying guides)

**Mandatory visual assets for the tools tier**:
- 🟡 **Hero PNG (1200×630) — FLAGGED ONLY, SKIP auto-gen**. Auto-generated hero images are quality-rejected by default; note in the Step 13 summary "Hero pending owner upload" + suggest a pick strategy (best_seller / top_brand / product_type_diverse). Resume auto-gen only on an explicit override.
- **Inline SVG spec chart** — comparison of 1-2 key specs across 3-5 top models (a simple hand-written bar chart, fits inside the deep-content HTML)
- 3-5 product detail image callouts — reference existing Shopify product images via `<img>` tags inside the deep content. Use CDN URLs from the Shopify product `featuredMedia.preview.image.url`. Add `alt` text.

**Content voice rule (HARD GATE 12)**: write content as the store's own product
knowledge in a natural voice. NEVER expose internal source labels:
- ❌ "the KB says", "KB notes", "the knowledge base documents", "KB customer brief"
- ❌ "Pro tip from the KB", "KB sales script", "the knowledge base recommends"
- ❌ "per our internal data", "according to our database"
- ✅ "Product X is the #1 best-selling line in this category" (state the fact directly)
- ✅ "The 18 coded variants (V01 through V18) ship..." (state the structure directly)
- ✅ "Three companion products pair with Product X..." (state the recommendation directly)

Customers don't know what "KB" is. Source labels reveal internal workflow,
sound robotic, and break the voice consistency.

Invoke the `collection-content-deep` skill. The 8-section template:

1. **Category overview** — what the category does + scope at the site (2 paragraphs)
2. **Brand spotlight** — `<h3>` per brand with positioning + price tier
3. **How to pick the right brand** — `<ul>` with 4-6 use-case scenarios
4. **Comparison table** — `<table>` brand × dimension matrix
5. **How-to / usage guide** — `<ol>` step-by-step workflow + a Pro tip callout
6. **Care & maintenance for buyers** — `<ul>` 3 rules + a storage/handling paragraph
7. **Pricing at the store** — pricing model + bulk discount info
8. **Related reads** — 4 blog links

Plus 2 link layers (Step 7).

**HARD GATE 4 (em-dash)**: 0 em-dash (`—` U+2014) across the entire deep
content HTML. Use a colon, hyphen, or rephrase. Run `scripts/reduce_emdash.py`
or equivalent before push.

### Step 7: Internal linking (3 layers, 12-20 links per hub)

**Layer A — Brand H3 wraps**:
```html
<h3><a href="/collections/{verified-handle}">{Brand Name}</a></h3>
```

**Layer B — Comparison table first cell wraps**:
```html
<tr><td><a href="/collections/{verified-handle}">{Brand}</a></td>...</tr>
```

**Layer C — "Related collections" section** (a NEW H2, 5 cross-hub teasers):
```html
<h2>Related collections</h2>
<ul class="related-reads related-collections">
  <li><a href="/collections/{cross-hub-handle}">{Category Name}</a>
    <span class="teaser">{1-line USP}</span></li>
  ...
</ul>
```

Place Related Collections BEFORE Related Reads.

**HARD GATE 1 (re-applied)**: every `/collections/{handle}` MUST be verified in
the Step 2 brand mapping. Every `/blogs/articles/{slug}` MUST be verified in
the Step 11 blog inventory pull.

### Step 8: FAQ metafield (300-500w, 3-5 Q&A pairs)

**🚨 CANONICAL SHAPE — a flat `{q,a}` array, NEVER a schema.org FAQPage
wrapper.** The theme section `collection-faq.liquid` reads Liquid
`{% for item in metafield.value %}{{ item.q }}{{ item.a }}{% endfor %}` — the
wrong shape yields empty FAQ box DOM nodes with no question text.

Build the `custom.faq_jsonld` metafield (a list of `{q, a}` objects, type: `json`):

```json
[
  {"q": "What brands of {category} do you carry?", "a": "..."},
  {"q": "Is {brand} compatible with {related-brand}?", "a": "..."},
  ...3-6 items
]
```

**WRONG (do NOT use):**
```json
{"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{"@type":"Question","name":"...","acceptedAnswer":{...}}]}
```

This metafield:
- Renders via `sections/collection-faq.liquid` as an expandable accordion (consumes flat `q/a` keys)
- Is consumed by `snippets/collection-structured-data.liquid` to emit `FAQPage` JSON-LD (+1 bonus Cat 4 score) — the wrapper schema is built BY the theme; you only provide the flat data.

### Step 8.5: Update the collection description (tagline) & clean inline images

**🚨 Above-grid tagline update (Gate 9)**:
Ensure the collection's core `descriptionHtml` field is updated with a clean
20-40 word tagline summarizing the hub's USP, product count, and key brands,
rather than being left empty or containing clutter.

**🚨 Clean legacy inline images**:
Prior collection descriptions often contain legacy inline images (e.g. `<img>`
tags for old banner files). These MUST be completely removed from
`descriptionHtml` to avoid a double-banner display and layout clutter on mobile.

Use the `collectionUpdate` mutation to push this tagline directly:
```graphql
mutation collectionUpdate($input: CollectionInput!) {
  collectionUpdate(input: $input) {
    collection {
      id
      descriptionHtml
    }
    userErrors {
      field
      message
    }
  }
}
```

### Step 9: Push metafields (1 batched mutation)

```graphql
mutation PushHubMetafields($metafields: [MetafieldsSetInput!]!) {
  metafieldsSet(metafields: $metafields) {
    metafields { id key }
    userErrors { field message code }
  }
}
```

Push in a single batch:
- `custom.deep_content_html` (multi_line_text_field, the 1,500-2,000w HTML)
- `custom.faq_jsonld` (list.metaobject_reference OR list.json — depends on the metafield def)
- `custom.suppress_brand_suffix` (boolean, true)
- `custom.sub_categories` (optional list of sub-collection handles for nav rendering)

### Step 10: Apply the hybrid template

Push `templates/collection.{handle}.json` with the proven hybrid section order:

```json
{
  "sections": {
    "main_banner": {"type": "main-collection-banner", "settings": {...}},
    "sub_nav": {"type": "sub-category-nav"},
    "product_grid": {"type": "main-collection-product-grid"},
    "collection_faq": {"type": "collection-faq"},
    "collection_content": {"type": "collection-content"}
  },
  "order": ["main_banner", "sub_nav", "product_grid", "collection_faq", "collection_content"]
}
```

If theme.liquid edits are required (Path 2 brand-suffix opt-out), push to a
duplicate theme — `themeFilesUpsert` on the MAIN theme is often blocked by the
MCP safelist. The user publishes manually.

### Step 11: Pre-publish verification

Run the pre-publish gate. **DELEGATE per the model-tier rule**: the entire
link-200 sweep + sitemap pull + curl HEAD batch SHOULD be delegated to a cheap
sub-agent (`Agent(subagent_type:Explore, model:haiku, prompt:"<self-contained
verify spec>")`) — the main session reads only the 1-line-per-URL summary.

1. **Em-dash count** = 0 in deep content + tagline + FAQ + meta desc
2. **AI-trigger phrases** = 0 across the same surfaces
3. **HTML title** ≤60ch on the live page (preview theme URL)
4. **All internal `/collections/` links** return 200 (HEAD check via the sub-agent batch)
5. **All internal `/blogs/articles/` links** return 200 — pull the article list
   from `/admin/blogs/{id}/articles` first; NEVER write a slug that wasn't in
   the inventory pull
6. **FAQ quantity & length check** = must contain 3-5 Q&A pairs and total answer word count 300-500 words (Gate 18)

**HARD GATE 5 (link health)**: 0 broken internal links OR block publish.

**🚨 HARD GATE 15 (FAQ live render)**: after `metafieldsSet` + a short wait:
```bash
curl -s https://your-store.com/collections/<handle> | grep -oE 'collection-faq__question-text[^"]*">[^<]+' | head -10
```
Must return ≥3 lines WITH actual question text after the `>`. If lines show
empty content (`">` immediately followed by `<`) → the metafield shape is wrong
(probably a schema.org wrapper instead of flat `[{q,a},...]`). Block the
notification, fix the metafield, re-verify.

**Hero check (RELAXED)**: hero status should be "FLAGGED pending owner upload"
or "live real image". Do not block publish for a hero placeholder — just note
it explicitly in the Step 13 summary. Auto-gen is skipped by default.

### Step 12: Live composite re-score

After the theme publishes, run `collection-analyze` against the live URL:

- Cat 1 Copy Quality target ≥19/20
- Cat 2 SEO target ≥20/25 (lose 2-3 pts if --no-gsc)
- Cat 3 Curation target 20/20 (warning-only)
- Cat 4 Technical target ≥12.5/15 (assuming a 4-schema bundle + ItemList nested in CollectionPage.mainEntity per the `collection-structured-data` snippet)
- Cat 5 UX target ≥16/20

**HARD GATE 6 (composite floor)**: composite ≥85/100. If below, identify the
gap category, apply the fix, re-verify. NEVER ship a hub at <85.

### Step 13: Publish notification (Gate 14, optional)

If you have a notification channel configured, send a notification after a
collection content publish/optimize so the production owner has visibility
alongside other publishes. This step is **optional** — it is skipped cleanly
when no channel is configured.

Run AFTER live verification (Step 12) confirms gates 0-13 pass:

```bash
python scripts/notify_collection_publish.py \
  --site your-store.com \
  --handle <collection-handle> \
  --url https://your-store.com/collections/<handle> \
  --mode optimize \
  --tier <mega-hub|brand-hub|sub|hardware|seasonal|bundle|bulk|specialty|variant-rich> \
  --reason "<one-line why: GSC rank, content gap, refresh trigger>" \
  --baseline "<GSC 90d: imp / clicks / pos>" \
  --change "<one-line what shipped: template, sections, hero, schema>" \
  --gates "<N/N gates summary>"
```

The script reads `TELEGRAM_BOT_TOKEN` + `TELEGRAM_CHAT_ID` from a local `.env`
(path configurable via `COLLECTION_OPTIMIZER_ENV`, default `./.env`). It posts
an HTML message with a tier icon (🏛️ mega-hub, 🔧 tools, 🌸 seasonal, 🎁 bundle,
etc.) + a mode icon (⚡ optimize / ✨ new / 🔄 refresh). If the env file or
credentials are missing, the script exits without sending — no error to the run.

**The notification should include hero status**: `--change "...+ Hero FLAGGED
pending owner upload (placeholder)"` OR `"...+ Hero live"`, so the owner has
visibility on which collections still need a real hero asset.

## Hero image policy (FLAG, don't gen)

**STOP**: do NOT auto-generate a hero image (image model / staged upload /
`fileCreate` / `collectionUpdate(image.src)`) for every new collection by
default. Auto-generated hero quality is inconsistent (rigid composites,
artificial backgrounds, off-brand). Resume auto-gen ONLY on an explicit
override from the site owner.

**Do instead**: in the Step 13 notification + final summary, surface:
```
🟡 Hero pending owner upload (1200×630 PNG)
  Suggested chip strategy: <best_seller | top_brand | product_type_diverse>
  Current placeholder URL: <existing collection.image>
  Workflow: owner uploads via Shopify admin → collection page → Image
```

## Model tier routing (protect the main session's context)

**Delegate to a cheap sub-agent for simple lookups.** Each inline MCP query /
curl batch / file read in the main session consumes context budget. A cheap
sub-agent returns a 1-line summary to the main session at a fraction of the cost.

**Use `Agent(subagent_type:"Explore", model:"haiku", prompt:"...")`** for:
- Curl HEAD link batch (Step 11 verify) — give the sub-agent the exact URL list, ask "report 1 line per URL: <url>: <status>"
- Shopify `search_collections` / `get-product` / `graphql_query` simple lookups (handle resolution, count check, factcheck disambiguation)
- Sitemap scan for relevant URLs
- GSC row count pull
- Read 1 file ≤200 lines for a fact lookup

**Keep in the main session** when:
- Composing deep content (1000+ words of reasoning + memory)
- Pushing a large mutation payload with a context decision
- A decision-tree split where the output feeds the next mutation directly
- Sensitive content already in context (round-tripping through an agent doubles tokens)

## The 18 HARD Gates Summary

| Gate | Check | Pass criteria |
|------|-------|---------------|
| **0** | **KB-first factcheck (TIER_INTERNAL)** | **MUST grep `knowledge-base/*.md` for the product line BEFORE writing. Extract facts: positioning, best-seller status, discount margin, target customer, upsell pairings, technique workflow. Document the gap explicitly if the KB doesn't cover it. Skipping = block.** |
| 1 | URL inventory verify | Every internal URL is in the inventory pull |
| 2 | HTML title length | ≤60ch on the live page |
| 3 | AI-trigger phrases | 0 across title + meta + tagline + FAQ + deep |
| 4 | Em-dash compliance | 0 em-dash (`—`) anywhere in editorial copy |
| 5 | Link health | 0 broken `/collections/` or `/blogs/articles/` link |
| 6 | Composite score | ≥85/100 on the live re-score |
| 7 | Fact-check numeric claims | NEVER conflate productsCount with variant count. Pull product titles + scan for "Set/Bundle/Collection/Trio/Kit/Vol." keywords. Use "X SKUs" or "X products" if >20% of items are sets/bundles. |
| 8 | Per-collection OG image | `og:image` must be collection-specific, NOT the site-default placeholder. **RELAXED**: if the collection has an existing live image (not the site default), Gate 8 passes even if it isn't a new hero. Do not block publish for a hero placeholder; FLAG for the owner to upload a real image. Gate 8 fails ONLY when `og:image` = the site-default banner placeholder. |
| 9 | Above-grid tagline 20-40w | `collection.description` (rendered in the banner) must be a 20-40 word tagline summarizing the hub's USP + count + key brands. An empty description, or one containing raw inline images (`<img>` tags), fails. Inline images must be purged to avoid layout clutter. |
| 10 | Filter sidebar enabled | `main-collection-product-grid` must have `show_filters: true` and `disabled: false`. Browse-by-brand showcase templates that disable the grid lose filter UX and fail Cat 5. |
| 11 | Sub-collection nav present | At least one `collection-list-grid` OR `sub-category-nav` section with ≥6 sub-collection handles in the template order. Failing means clients can't navigate brand sub-lines. |
| **12** | **No source labels in content** | **0 mentions of "KB", "the knowledge base", "KB notes", "KB sales script", "per our internal data" in the published HTML. Customers cannot see internal source attribution. Write facts directly as the store's product knowledge in a natural voice.** |
| **13** | **Tier-aware content depth** | **Content sections + visual assets MUST match the product-category tier. Technical/hardware uses the 10-section template with a specs comparison table + SVG chart + product detail images. Bundles use the 7-section composition template. Variant-rich uses the 8-section template. Picking the wrong tier = re-write.** |
| **14** | **Publish notification sent (optional)** | **If a channel is configured, run `scripts/notify_collection_publish.py` AFTER live verification (Step 12) confirms gates 0-13 pass. Credentials from a local `.env`. Skipped cleanly when unconfigured.** |
| **15** | **FAQ live render verify** | **Run curl & grep to ensure `collection-faq__question-text` returns ≥3 lines with actual question text. Fails if empty (metafield shape wrong).** |
| **16** | **Custom templateSuffix check** | **`templateSuffix` must be null/empty, or if non-null, the owner must explicitly approve. Custom templates without content sections fail to render.** |
| **17** | **Sub-nav render verify (Path B)** | **Run curl & grep to verify the sub-nav chip group has ≥3 handles rendering with labels.** |
| **18** | **FAQ quantity & length check** | **The `custom.faq_jsonld` metafield must contain 3-5 Q&A pairs AND total answer word count must be 300-500 words. Under 300 words fails (thin FAQ content).** |

Failing any gate blocks the push. Re-iterate the step that owns the gate.

**Field lessons that added gates:**
- Gate 13 was added after a near-miss where a variant-rich content template was about to be cloned onto a technical hardware collection — which would have missed the specs comparison, compatibility, spec chart, and maintenance content that a hardware buyer needs.
- Gates 0 + 12 were added after a content run skipped the KB and hallucinated facts, then a rewrite fixed the facts but leaked internal "KB" source labels into client-facing copy.
- Gate 7 was added after a hub claimed "N variants" when the collection was mostly bundles and sets, not individual products.
- Gates 8-11 were added after a production audit found generic site OG images, empty taglines, disabled filter sidebars, and wrong sub-collection nav handles across a batch of hubs.

## Composition with other skills

- **Phase 0** (audit input): `collection-analyze` — provides the baseline + gaps
- **Phase 3** (content gen): `collection-content-deep` — generates 1,500-2,000w
- **Phase 6** (snippet emit): `collection-structured-data.liquid` renders CollectionPage + ItemList (nested) + BreadcrumbList + FAQPage bonus
- **Phase 12** (re-score): `collection-analyze` again — confirms the ≥85 floor
- **Pipeline mode**: `collection-audit-pipeline` batches this skill over the top-N priority list from a portfolio scan

## Reference docs

- `references/workflow-12-steps.md` — verbatim mutation queries + JS extraction
- `references/hard-gates.md` — compliance gate details + sample failure paths
- `references/brand-mapping-queries.md` — Shopify search queries for sub-collection discovery
- `references/theme-patch-stiletto.md` — example theme.liquid patch for the `suppress_brand_suffix` metafield opt-out

## Output convention

Per-hub artifact folder:
```
output/[site]/[handle]/
├── baseline-snapshot.json         # Step 1 raw pulls
├── brand-mapping.json             # Step 2 sub-collection discovery
├── seo-rewrite.json               # Step 3-4 title + meta + tagline
├── deep-content.html              # Step 6-7 final 1,500-2,000w + links
├── faq-jsonld.json                # Step 8 FAQ metafield value
├── template.json                  # Step 10 hybrid template config
├── prepush-verify.json            # Step 11 verification report
└── composite-score-final.md       # Step 12 ≥85 verified
```

## Hard rules

These rules are absolute. Violating any of them during the workflow = revert +
redo the step:

- **KB-first factcheck** (Gate 0) — the factcheck priority order is TIER_INTERNAL → TIER_SHOPIFY → TIER_WEBFETCH; a model estimate is never acceptable. MOST critical.
- **Never invent URLs** (Gate 1) — pull the inventory, link only verified handles/slugs.
- **Em-dash discipline** (Gate 4) — ≤0.3 em-dash per 100 words, hard target 0.
- **Product count vs variants** (Gate 7) — never conflate `productsCount` with variant count.
- **Same-brand-first URL discipline** — when fixing a 404, prefer a same-brand collection over a generic one.

## Factcheck priority order (cross-reference)

This is the canonical tier order any factual claim must pass through. Repeated
here from Step 0.5 because every editor of this skill MUST internalize the order
before any content writing:

1. **TIER_INTERNAL** = `knowledge-base/*.md` — your own first-party + third-party product specs/sales data — highest authority
2. **TIER_SHOPIFY** = Shopify Admin GraphQL pulls — product titles, vendor, productType, count
3. **TIER_WEBFETCH** = external WebFetch — regulatory, third-party newer specs, your own blog posts
4. **TIER_GUESS** = a model estimate — **NEVER acceptable**, blocks publish

Write content as the store's own product knowledge in a natural voice. NEVER
quote source labels ("KB", "the knowledge base", "per internal data") in the
published HTML. Customers don't know what "KB" means.

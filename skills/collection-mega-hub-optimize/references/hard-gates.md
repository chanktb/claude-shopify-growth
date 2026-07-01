# Hard Gates: Compliance Rules for Mega-Hub Optimization

These gates are non-negotiable. Failing any one blocks the push and requires
re-iterating the step that owns the gate. Gates 1-6 are the baseline; Gates
7-11 were added after a production audit found systemic gaps across a batch of
hubs; Gates 0 + 12 were added after a content run hallucinated facts (Gate 0)
and then leaked internal source labels into client-facing copy (Gate 12); Gate
13 was added after a near-miss cloned a variant-rich template onto a hardware collection.
Gates 14-18 are documented in the main `SKILL.md` gate table.

---

## Gate 0: KB-First Factcheck (Highest Authority)

**Owner**: Step 0.5 (mandatory KB pull, runs BEFORE Step 1 baseline).

**Rule**: Before writing ANY editorial copy about a product line, grep
`knowledge-base/*.md` for the keyword and read all matched files. The KB is the
**TIER_INTERNAL** source — your own first-party product specs + sales data +
technique workflows + upsell pairings + target-customer profiles. KB authority
beats Shopify titles + a model estimate.

**Factcheck priority order**:

| Tier | Source | Authority | Action |
|------|--------|-----------|--------|
| TIER_INTERNAL | `knowledge-base/*.md` | Highest | Read + extract facts as the content foundation |
| TIER_SHOPIFY | Shopify Admin GraphQL | High | Verify count vs variant. HEAD-check URLs |
| TIER_WEBFETCH | External WebFetch | Fallback | Only when KB + Shopify have gaps |
| TIER_GUESS | Model estimate | **NEVER** | Block publish |

**Knowledge-base structure**: keep one markdown file per product line, named
`pk-<product-line>.md`, plus an `INDEX.md` mapping each product-line keyword to
its file. This data is store-owned, git-ignored, and provided by you; it never
ships with the repo. See `knowledge-base/README.md` for the template.

**Pass criteria**:
1. You ran `grep -l -i "<product-keyword>" knowledge-base/*.md`
2. For each matched file, you read the relevant section fully
3. You extracted these facts where the KB documents them:
   - Positioning (best-seller rank, revenue share, brand share)
   - Discount/margin signal (low discount = high willingness-to-pay)
   - Target-customer profile (skill level, tier, segment)
   - Companion-product upsell pairings (explicit lists)
   - Application technique steps (verbatim where applicable)
   - Pricing tier vs competitors
   - Texture/formulation language (exact words)
4. You logged `tier_internal_status: covered | partial | gap` in `baseline-snapshot.json`

**Field lesson**: a content run that pulled only Shopify titles and guessed the
rest produced 7+ factual errors — wrong product structure, wrong application
method, wrong skill-level target, and missed both the best-seller positioning
and the documented upsell pairings. All of it was in the KB the entire time.
When the KB documents the line, it is the spine of the copy.

**How to apply (post-fix)**:
1. `INDEX.md` identifies which KB file covers the product line
2. Read the full matched file before opening the content-gen step
3. Write content as the store's own product knowledge using KB facts as the
   spine — the KB shapes positioning, structure, pairings, technique
4. Run the Gate 12 verify (no source labels) at the end

---

## Gate 1: URL Inventory Verify (Anti-Hallucination)

**Owner**: Steps 2 (brand mapping) + 7 (internal linking) + 11 (pre-publish).

**Rule**: NEVER write an internal URL (`/collections/{handle}` or
`/blogs/articles/{slug}`) in any editorial copy without first pulling inventory
from the Shopify connector and confirming the handle/slug exists.

**Failure mode**: Hallucinated URLs return 404 on live. Bad UX + bad SEO + lost
internal-link equity.

**Field lesson**: a batch of deep-content files once shipped with invented
`/blogs/news/{slug}` URLs — the blog handle was actually `articles` not `news`,
and most of the invented slugs didn't exist in the article catalog. Fix: pull
`blog.articles(first: 250)` first, then hand-pick semantic matches.

**How to apply**:

```graphql
# For collection links — query Shopify by title keyword
query BrandSubs { collections(first: 20, query: "title:*<keyword>*") {
  edges { node { handle title } } } }

# For blog links — pull the blog's article list
query ArticleList($cursor: String) {
  blog(id: "gid://shopify/Blog/<id>") {
    articles(first: 250, after: $cursor) {
      edges { node { handle title } }
      pageInfo { hasNextPage endCursor }
    }
  }
}
```

Keep the results in `brand-mapping.json` and `blog-inventory.json`. Every URL
written in editorial copy must reference one of these.

---

## Gate 2: HTML Title Length ≤60ch

**Owner**: Steps 3 (seo.title rewrite) + 11 (pre-publish verify).

**Rule**: the HTML `<title>` on the live page must be ≤60 characters. Google
truncates titles at roughly 580px (averages ~55-60ch). Anything longer is cut
mid-sentence in the SERP.

**Theme suffix behavior** (example: a Stiletto-style theme):
- Default: the theme appends ` – {shop.name}` if `page_title` does not already
  contain `shop.name`. This adds however many characters your shop name is.
- **Path 1 fix**: include the shop name inside `seo.title` → the theme skips
  the append. You lose that many characters of keyword budget.
- **Path 2 fix (recommended)**: patch `theme.liquid` to honor a per-collection
  metafield `custom.suppress_brand_suffix = true`. The `seo.title` becomes 100%
  keyword (55-60ch). Other collections are unaffected.

**Path 2 patch** (in `layout/theme.liquid`, replace the `unless` block):

```liquid
{%- assign escaped_page_title = page_title | escape -%}
{%- assign suppress_brand = false -%}
{%- if request.page_type == 'collection' and collection.metafields.custom.suppress_brand_suffix == true -%}
  {%- assign suppress_brand = true -%}
{%- endif -%}
{%- unless escaped_page_title contains shop.name or suppress_brand -%}
  &ndash; {{ shop.name }}
{%- endunless -%}
```

Push only to a DUPLICATE theme — `themeFilesUpsert` on the MAIN theme is often
blocked by the MCP safelist. The user publishes manually.

---

## Gate 3: AI-Trigger Phrases = 0

**Owner**: Steps 3, 4, 6, 7, 8 (anywhere user-facing editorial copy is written).

**Rule**: 0 instances of the banned phrase list across:
- `seo.title`
- `seo.description`
- Above-grid tagline (`collection.description`)
- FAQ Q&A pairs
- Deep content HTML body (Steps 6 + 7)

**Banned list**:

| Phrase | Replacement |
|---|---|
| Discover | Shop, Browse, Find |
| Experience | Get, Use, Try |
| Elevate | Improve, Upgrade, Lift |
| Explore | Browse, Compare, See |
| Delve into | Cover, Examine |
| Navigate the landscape | (cut entirely) |
| In today's fast-paced | (cut entirely) |
| In conclusion | (use a different summary line) |
| It's important to note | (state directly) |
| Flawless | Clean, Smooth |
| Exploration | Comparison, Review |
| Unleash | Use, Apply |
| Embark on | Start, Begin |
| Cutting-edge | Modern, Current |
| Game-changing | Better, New |
| Seamless | Smooth, Direct |
| Vibrant | Bright, Bold, Saturated |
| Curated | Selected, Picked |

**How to apply**: grep your draft against the banned list before push:

```bash
grep -iE "discover|experience|elevate|explore|delve into|in today's fast-paced|in conclusion|it's important to note|flawless|exploration|unleash|embark on|cutting-edge|game-changing|seamless|vibrant|curated" draft.html
```

Should return 0 matches.

---

## Gate 4: Em-dash Compliance (≤0.3 per 100w, hard target 0)

**Owner**: Step 6 (deep content generation) + Step 8 (FAQ).

**Rule**: 0 em-dashes (`—` U+2014) anywhere in editorial copy. AI-detection
heuristics flag em-dash density as a machine-generated signal.

**How to apply**: run `scripts/reduce_emdash.py <draft.html>` or grep manually:

```bash
grep -c "—" draft.html  # must return 0
```

Replace em-dash with:
- `:` (colon) for definition lists
- `,` (comma) for a parenthetical aside
- `(` `)` parentheses for true asides
- Hyphen `-` for compound modifiers
- Or rephrase the sentence

---

## Gate 5: Link Health (0 broken)

**Owner**: Step 11 (pre-publish verify).

**Rule**: every `/collections/{handle}` and `/blogs/articles/{slug}` link in
the deep content + FAQ + Related Reads sections must return HTTP 200 on a HEAD
check.

**How to apply**:

```javascript
// Run on the preview theme URL
const links = [...document.querySelectorAll('.collection-content a[href^="/"]')]
  .map(a => a.getAttribute('href'));
const results = await Promise.all(links.map(async u => {
  const r = await fetch(u, {method: 'HEAD'});
  return { url: u, status: r.status };
}));
console.log(results.filter(r => r.status !== 200));  // must be empty
```

Block publish if any URL returns 404.

---

## Gate 6: Composite Score ≥85/100

**Owner**: Step 12 (live re-score).

**Rule**: after the theme is published, run `collection-analyze` against the
live URL. Composite ≥85/100 OR the hub doesn't ship — go back and fix the gap.

**Typical score breakdown for a successful mega-hub**:

| Cat | Max | Typical |
|---|---|---|
| 1 — Copy Quality | 20 | 20 |
| 2 — SEO + Commercial Intent | 25 | 19-20 (no-gsc, 1-2 pt loss expected) |
| 3 — Curation (warning-only) | 20 | 20 |
| 4 — Technical + Schema | 15 | 12.5 (4-schema bundle + FAQPage bonus) |
| 5 — UX & Conversion | 20 | 16 |
| **Total** | **100** | **87-90** |

**Gap diagnostics**:

- Cat 1 <18: em-dash present, AI-trigger phrases, or below-grid copy too thin
- Cat 2 <18: HTML title too long, meta desc out of range, no internal inbound
- Cat 4 <11: schema bundle missing one of CollectionPage/ItemList/Breadcrumb/FAQPage
- Cat 5 <14: hero image null, filter sidebar absent, no sort dropdown

---

## Gate 7: Fact-check numeric claims (NEVER conflate productsCount with variant count)

**Owner**: Step 6 (deep content) + Step 8 (FAQ).

**Rule**: Before writing any "X variants", "X options", "X individual units",
"X colors", "X sizes" claim, pull the collection's product list and verify the
count refers to individual items, not bundles/sets.

**Failure mode**: Shopify `productsCount` returns the SKU count, not the
per-variant count. A collection with `productsCount: N` can contain:
- 1 SKU = "Set of 240" (covers 240 items inside 1 SKU)
- 1 SKU = "Collection Vol 2.1" (a themed multi-item set)
- Many "Bundle" SKUs (each contains multiple items)
- A handful of individual-item SKUs

→ Claiming "N variants" is misleading when most SKUs are sets. The true
individual-item count is unknown without summing the multi-item SKUs.

**Field lesson**: a hub once claimed an "N-item foundation library" when the
collection was mostly kits and sets, not individual items. A scan of the first
30 products showed most titles contained "Set", "Bundle", or "Collection Vol".
Fix: "N SKUs across individual items, themed bundles, and curated sets".

**How to apply**:

```graphql
query VerifyShadeCount {
  collection(id: "<gid>") {
    productsCount { count }
    products(first: 30) {
      edges { node { title productType tags } }
    }
  }
}
```

Scan product titles for these keywords (case-insensitive). If >20% of the first
30 hit, refuse the "X variants" phrasing:

| Keyword | Likely meaning |
|---|---|
| `Set` | Multi-item SKU |
| `Bundle` | Multi-item SKU |
| `Collection` (in title) | Themed multi-item |
| `Trio` / `Duo` (when in line title) | Multi-item |
| `Kit` / `Combo` / `Pack` | Multi-product |
| `Vol.` / `Volume X` | Multi-item per release |
| `X-Pack` / `X Colors` (e.g. "240 Colors") | Single SKU = X items inside |
| "Holiday" / "Spring" / "Fall" + "Collection" | Likely a themed set |

**Safe phrasings**:
- ✅ "N SKUs (individual items + curated sets)"
- ✅ "N products across individual items and bundles"
- ❌ "N variants" — when the collection has sets
- ❌ "N options" — same

**When you CAN say "X variants"**: only if the scan shows >80% of products are
single-item SKUs.

---

## Gate 8: Per-Collection OG Image

**Owner**: Step 1 (baseline) + Step 11 (pre-publish verify).

**Rule**: `og:image` on the live collection page must be a collection-specific
hero image, NOT the site-default placeholder or a random shop image.

**Failure mode**: most Shopify themes fall back to a global `og:image` (the
shop logo or a generic banner) when `collection.image` is null. Social shares
(Facebook, X, Pinterest, LinkedIn) then display this generic image, which:
- Hurts CTR on social SERP previews
- Looks unprofessional in client-facing channels
- Misleads users about the page content

**Field lesson**: a batch of hubs once shipped with a stray, unrelated social
image as their `og:image` because `collection.image` was null and the theme
fell back to a global default.

**How to apply** (Step 1 baseline check):

```javascript
const og = document.querySelector('meta[property="og:image"]')?.content;
const colImg = '<from Shopify collection.image>';
const isGeneric = !og.includes(colImg.split('/').pop());  // basename match
```

If `isGeneric`, the hub fails Gate 8. Fix path:
1. Upload a collection-specific hero image to the collection in Shopify admin
2. OR set the OG image via a theme metafield (`custom.og_image_url`)
3. OR ensure `collection.image` is set and the theme uses `{{ collection.image | img_url: '1200x630' }}`

Suggested hero card: 1200×630 showing the brand name + USP + count
(e.g. "Brand A: N Wholesale SKUs").

---

## Gate 9: Above-Grid Tagline (20-40 words)

**Owner**: Step 5 (collection.description rewrite).

**Rule**: the `collection.description` field (rendered above the product grid
in the main-collection-banner section) must be a 20-40 word tagline summarizing
the hub's USP, product count, and key brands. An empty description fails.

**Failure mode**: an empty `collection.description` means the hub banner shows
no above-grid context. Visitors landing from the SERP see a wall of product
cards with no orientation. Reduces the above-grid tagline score from 4/4 to 0/4.

**How to apply** (Step 5 patch):

```graphql
mutation SetTagline($input: CollectionInput!) {
  collectionUpdate(input: $input) {
    collection { description }
    userErrors { field message }
  }
}
```

```json
{
  "input": {
    "id": "gid://shopify/Collection/<id>",
    "descriptionHtml": "<p>Shop N SKUs of [category] at wholesale: [3-5 key brands]. Free shipping over $[threshold].</p>"
  }
}
```

Pattern: `Shop {count} {category} at wholesale: {brand 1}, {brand 2}, {brand 3}. {USP}.`

**Pass criteria**:
- 20-40 words (strict)
- 0 em-dash, 0 AI-trigger phrases
- Mentions count + ≥3 brand names + a shipping/USP hook

---

## Gate 10: Filter Sidebar Enabled

**Owner**: Step 10 (template).

**Rule**: the `main-collection-product-grid` section in the template MUST have
`show_filters: true` AND `disabled: false`. Templates that disable the grid
(showcase-only patterns) automatically fail the filter-sidebar sub-score.

**Failure mode**: brand-hub showcase templates often set the `product-grid`
section to `disabled: true` to hide the grid and show only featured sliders.
This works for a brand-showcase landing page but LOSES the filter sidebar.

**How to apply** (Step 10 template):

For mega-hubs and brand-hubs targeting commercial intent, the template MUST
include `product-grid` as enabled. For showcase brand pages, you may accept the
trade-off but log it as Cat 5 partial credit.

```json
"product-grid": {
  "type": "main-collection-product-grid",
  "disabled": false,                    // MUST be false for hub tier
  "settings": {
    "show_filters": true,               // MUST be true
    "show_sort": true,
    "enable_sticky_filter_sidebar": true
  }
}
```

**Verification (Step 11)**:

```javascript
const filterBar = document.querySelector('.facets__form, [class*="facets"]');
const productGrid = document.querySelector('.product-grid');
if (!filterBar) console.warn('Gate 10 FAIL: filter sidebar not rendered');
if (!productGrid) console.warn('Gate 10 FAIL: product grid not rendered');
```

---

## Gate 11: Sub-Collection Nav Present

**Owner**: Step 10 (template).

**Rule**: the template must include AT LEAST ONE `collection-list-grid` OR
`sub-category-nav` section that lists ≥6 sub-collection handles.

**Failure mode**: without a sub-collection nav, visitors arriving on a mega-hub
can't drill down to brand sub-lines. Lose ~2 Cat 5 points + ~3 SEO points
(sub-link internal mesh).

**Field lesson**: a hub once listed sub-collection handles that were low-priority
or deprecated, so visitors couldn't find the obvious top sub-lines. The handles
in the nav must be the top-priority sub-lines, verified live.

**How to apply**:

```json
"collection_list_grid_X": {
  "type": "collection-list-grid",
  "settings": {
    "heading": "Browse {brand} lines",
    "columns": "3",
    "mobile_columns": "2",
    "collection_list": [
      "<verified-handle-1>",
      "<verified-handle-2>",
      "<verified-handle-N>"     // 6 to 15 handles, all live (HEAD 200)
    ]
  }
}
```

**Verification (Step 11)**:
1. Every handle in `collection_list` must return HTTP 200 (HEAD check)
2. Handles must be top-priority sub-lines per the brand-mapping reference
3. ≥6 handles minimum (mega-hub) or ≥4 (smaller brand-hub)

**Live render check**:

```javascript
const subNav = document.querySelector('.collection-list, .sub-category-nav, [class*="collection-list"]');
const links = subNav?.querySelectorAll('a[href^="/collections/"]');
if (!subNav || links.length < 6) console.warn('Gate 11 FAIL: sub-collection nav missing or too few');
```

---

## Gate 12: No Source Labels in Content (Client Voice Discipline)

**Owner**: Step 6 (deep content generation) + Step 11 (pre-publish grep).

**Rule**: 0 mentions of internal source labels in the published HTML. Customers
don't know what "KB" / "knowledge base" / "internal data" means. Source labels
reveal internal workflow, sound robotic, and break the voice consistency. Write
content as the store's own product knowledge in a natural voice.

**Banned phrases (HARD)**:
- "the KB says" / "the KB notes" / "KB confirmed" / "KB-confirmed"
- "the knowledge base documents" / "the knowledge base describes"
- "Pro tip from the KB" / "KB sales script" / "KB customer brief"
- "the knowledge base recommends" / "per the knowledge base"
- "per our internal data" / "according to our database" / "from our records"
- Any sentence that names the internal source as the speaker

**Allowed phrasing (rewrite pattern)**:

| Don't write (Gate 12 fail) | Do write (Gate 12 pass) |
|----------------------------|-------------------------|
| "The knowledge base describes Product X as the #1 best seller" | "Product X is the #1 best-selling line in this category" |
| "The KB customer brief is explicit: beginner-intermediate" | "Product X fits beginner-to-intermediate technicians" |
| "Per the KB sales script, pair with the base coat" | "Pair Product X with the base coat for a softer color spread" |
| "The KB-confirmed upsell pairings" | "The Product X upsell trio" (or just list them naturally) |
| "Pro tip from the KB: the apex forms naturally" | "Pro tip: the apex of the gradient forms naturally when you pat the transition zone correctly" |

**Pass criteria**:
1. `grep -ic "knowledge base\|the KB\|KB describes\|KB notes\|KB sales\|KB recommended\|KB-confirmed" <live-html>` returns 0
2. `grep -ic "per our internal\|according to our database\|from our records" <live-html>` returns 0
3. The voice reads as the store's own product expertise, not a model reading from a doc

**Field lesson**: a rewrite once fixed all the facts (Gate 0 pass) but exposed
source labels 8+ times ("the knowledge base describes...", "the KB customer
brief is explicit", "Pro tip from the KB", "Sales script (KB)" in a table
header, etc.). Customers can't see the internal source — Gate 12 enforces
silent KB usage: extract facts, then write them as the store's own knowledge
without source attribution.

**How to apply**:
1. After content gen + before push, grep the HTML for the banned phrases
2. If any match: rewrite the sentence to state the fact directly, no source
3. Re-run the grep until 0 matches
4. Verify the rewritten sentence still carries the KB fact (Gate 0 still passes)

---

## Order of gate enforcement

```
Step 0.5 → Gate 0 (KB pull, factcheck priority order locked)
Step 1   → Gate 8 (OG image baseline check), Gate 9 (collection.description check), Gate 16 (templateSuffix)
Step 2   → Gate 1 (URL inventory locked)
Step 3   → Gate 2 (title length pre-check)
Steps 3-8 → Gate 3 (AI-trigger grep)
Step 5   → Gate 9 (collection.description rewrite)
Step 6   → Gate 4 (em-dash grep), Gate 7 (fact-check product list pull), Gate 12 (no source labels grep)
Step 10  → Gate 10 (filter enabled in template), Gate 11 (sub-nav present)
Step 11  → Gates 1, 2, 4, 5, 7, 8, 10, 11, 12, 15, 17, 18 re-applied on live HTML
Step 12  → Gate 6 (final composite verify includes Gate 7-12 deductions)
Step 13  → Gate 14 (optional publish notification)
```

A workflow run that ships without every applicable gate green is a process
failure. Log it to `CHANGELOG-live-fixes.md` with a revert plan.

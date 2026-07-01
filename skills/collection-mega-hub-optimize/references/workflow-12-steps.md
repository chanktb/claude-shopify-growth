# Workflow: 12 Steps (verbatim queries + extraction)

Companion reference to `SKILL.md`. This file collects the exact GraphQL
mutations and the JS/console extraction snippets each step uses, so you can copy
them without re-reading the narrative. All Shopify IDs are placeholders — pull
the real ones in Step 1.

---

## Step 1 — Baseline pull

```graphql
query CollectionBaseline {
  collection(id: "gid://shopify/Collection/<id>") {
    id handle title description descriptionHtml
    productsCount { count }
    sortOrder
    ruleSet { appliedDisjunctively rules { column relation condition } }
    image { url altText }
    templateSuffix
    seo { title description }
    metafields(first: 30) { nodes { namespace key value type } }
  }
}
```

Live-page extraction (run in the browser console or a headless fetch):

```javascript
const baseline = {
  title: document.title,
  titleLen: document.title.length,
  metaDesc: document.querySelector('meta[name=description]')?.content ?? null,
  ogImage: document.querySelector('meta[property="og:image"]')?.content ?? null,
  h1: document.querySelector('h1')?.innerText ?? null,
  schemas: [...document.querySelectorAll('script[type="application/ld+json"]')]
    .map(s => { try { return JSON.parse(s.innerHTML); } catch { return null; } })
    .filter(Boolean),
  productCards: document.querySelectorAll('.product-card, [class*="product-card"]').length,
  filterSidebar: !!document.querySelector('.facets__form, [class*="facets"]'),
};
console.log(JSON.stringify(baseline, null, 2));
```

Save to `output/[site]/[handle]/baseline-snapshot.json`. Then run the Gate 16
`templateSuffix` check before writing anything.

---

## Step 2 — Sub-collection discovery (for internal linking)

See `brand-mapping-queries.md` for Patterns A/B/C. Record verified handles in
`output/[site]/[handle]/brand-mapping.json`.

---

## Step 5 — Rename H1 (if generic)

```graphql
mutation RenameCollection($input: CollectionInput!) {
  collectionUpdate(input: $input) {
    collection { id title handle }
    userErrors { field message }
  }
}
```

```json
{ "input": { "id": "gid://shopify/Collection/<id>", "title": "<New Branded H1>" } }
```

---

## Step 8.5 — Tagline (collection.description) + clean inline images

```graphql
mutation SetTagline($input: CollectionInput!) {
  collectionUpdate(input: $input) {
    collection { id descriptionHtml }
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

Remove any legacy `<img>` tags from the previous `descriptionHtml` to avoid a
double-banner display.

---

## Step 9 — Push metafields (one batched mutation)

```graphql
mutation PushHubMetafields($metafields: [MetafieldsSetInput!]!) {
  metafieldsSet(metafields: $metafields) {
    metafields { id namespace key }
    userErrors { field message code }
  }
}
```

Variables (Path B example — Path A drops `sub_categories`):

```json
{
  "metafields": [
    { "ownerId": "gid://shopify/Collection/<id>", "namespace": "custom", "key": "deep_content_html", "type": "multi_line_text_field", "value": "<the 1,500-2,000w HTML>" },
    { "ownerId": "gid://shopify/Collection/<id>", "namespace": "custom", "key": "faq_jsonld", "type": "json", "value": "[{\"q\":\"...\",\"a\":\"...\"}]" },
    { "ownerId": "gid://shopify/Collection/<id>", "namespace": "custom", "key": "sub_categories", "type": "json", "value": "[{\"handle\":\"...\",\"title\":\"...\"}]" },
    { "ownerId": "gid://shopify/Collection/<id>", "namespace": "custom", "key": "suppress_brand_suffix", "type": "boolean", "value": "true" },
    { "ownerId": "gid://shopify/Collection/<id>", "namespace": "global", "key": "title_tag", "type": "single_line_text_field", "value": "<55-60ch SEO title>" },
    { "ownerId": "gid://shopify/Collection/<id>", "namespace": "global", "key": "description_tag", "type": "single_line_text_field", "value": "<120-160ch meta description>" }
  ]
}
```

> The metafield definitions (`custom.deep_content_html`, `custom.faq_jsonld`,
> `custom.sub_categories`, `custom.suppress_brand_suffix`) must exist in the
> store first, and the theme must render them (see `theme-patch-stiletto.md`).

---

## Step 10 — Hybrid template

Push `templates/collection.{handle}.json`:

```json
{
  "sections": {
    "main_banner": { "type": "main-collection-banner", "settings": {} },
    "sub_nav": { "type": "sub-category-nav" },
    "product_grid": {
      "type": "main-collection-product-grid",
      "disabled": false,
      "settings": { "show_filters": true, "show_sort": true, "enable_sticky_filter_sidebar": true }
    },
    "collection_faq": { "type": "collection-faq" },
    "collection_content": { "type": "collection-content" }
  },
  "order": ["main_banner", "sub_nav", "product_grid", "collection_faq", "collection_content"]
}
```

If a `theme.liquid` edit is needed (Path 2 brand-suffix opt-out), push to a
DUPLICATE theme — `themeFilesUpsert` on the MAIN theme is often blocked by the
MCP safelist. The user publishes manually.

---

## Step 11 — Verification snippets

```bash
# Em-dash count (must be 0)
grep -c "—" output/[site]/[handle]/deep-content.html

# AI-trigger phrases (must be 0)
grep -iE "discover|experience|elevate|explore|delve into|flawless|curated|seamless" output/[site]/[handle]/deep-content.html

# FAQ live render (must return >=3 lines with question text)
curl -s https://your-store.com/collections/<handle> \
  | grep -oE 'collection-faq__question-text[^"]*">[^<]+' | head -10

# Path B sub-nav render (must return >=3 entries)
curl -s https://your-store.com/collections/<handle> \
  | grep -oE 'class="sub-category-nav__link"\s*>[^<]+</a>'
```

Delegate the link-200 HEAD sweep to a cheap sub-agent and read only the
1-line-per-URL summary.

---

## Step 12 — Re-score

Run `collection-analyze <live-url>` and confirm composite ≥85/100.
See `../collection-analyze/references/collection-rubric-100pt.md`.

---
name: collection-content-deep
description: >
  Generate long-form below-grid editorial content for Shopify collection
  mega-hubs (1,500–2,000 words across 8 sections: Category Overview, Brand
  Spotlight, How to Pick, Comparison Table, Application Guide, Care &
  Maintenance, Wholesale Info, Related Blog Reads). Brand-specific knowledge
  prefill (fill in `references/brand-knowledge-base.md` with your own
  brands). Output HTML body suitable for Shopify metafield
  `custom.deep_content_html` rendered by the matching `collection-content`
  theme section. Pairs with collection-analyze and collection-audit-pipeline.
  Use when user says "write collection content", "deep content for
  collection", "long-form collection page", "expand collection beyond FAQ",
  "collection-content-deep".
user-invokable: true
argument-hint: "<collection-url-or-handle> [--site <domain>] [--length 1500|2000|2500] [--sections N] [--no-images] [--blog-links N] [--brand-tone wholesale|consumer|salon-pro]"
license: MIT
metadata:
  author: "Khue (ktbteam)"
  version: "0.1.0"
  last_modified: "2026-06-21"
  recent_change: "v0.1.0 — Initial release. 8-section template, brand knowledge prefill, HTML body output for metafield-driven render."
  category: content
---

# Collection Content Deep: Long-Form Below-Grid Body Generator

Generates the 1,500–2,000-word editorial body that sits BELOW the FAQ
accordion on a Shopify collection hub page. Solves the "thin content"
problem that collection-analyze v0.2.1 left unaddressed — collections were
getting a high composite score but only ~330 words of editorial content. This
skill brings collection content depth on par with a well-written blog post
while keeping the commercial-intent design (filter + grid still primary).

## When this skill applies

**Tier requirement**: mega-hub or hub. Sub-tier collections (<100 products)
do NOT need this depth — they get filtered by brand/season and serve as
landing pages for specific intent, not authority hubs.

**Tier rule check** (per collection-analyze v0.2.1):
- mega-hub (≥2000sp + OR-rule): MANDATORY apply
- hub (1000–1999sp or generic category): RECOMMENDED apply
- brand (100–999sp): OPTIONAL (apply for top-3 traffic brand collections only)
- sub / tool / new: SKIP

## Architecture

Content is stored in a **collection metafield** (`custom.deep_content_html`,
type: `multi_line_text_field` or `rich_text_field`) and rendered by a
theme section (`sections/collection-content.liquid`) placed AFTER the
FAQ section in the template JSON.

```
templates/collection.<handle>.json
  order: [banner, product-grid, collection-faq, collection-content]
                                                       │
                                                       └─ reads collection.metafields.custom.deep_content_html
```

This pattern is consistent with how `custom.sub_categories` and
`custom.faq_jsonld` work for the v0.2.1 hybrid template — metafield-driven,
section-rendered, no template rebuild needed when content changes.

## 8 Sections (default template)

Each section gets a heading + body. Total target: 1,500–2,000 words.

### Section 1: Category Overview (200–300w)

What is the category, why salons + DIY pros use it, key benefits.

**Field lesson**: wholesale-friendly + salon-pro-focused.
Address the buyer's professional decision, not just shopping inspiration.

**Required elements**:
- 1-sentence definition of the category
- 2–3 key benefits (commercial intent)
- Quick-stat callout (e.g. "<N> House Brand SKUs in stock daily")

### Section 2: Brand Spotlight (300–400w)

3–5 brands compared by personality. Each brand gets ~80w covering:
- Founding / heritage 1 sentence
- Positioning (premium / value / specialty)
- Unique value (formula / shade depth / price tier)

**Knowledge base**: see `references/brand-knowledge-base.md` — a template
for you to fill in with your own brand profiles (Brand A, Brand B, Brand C,
etc.).

### Section 3: How to Pick (200–250w)

Decision tree by buyer use-case:
- **DIY pro** — what to pick + why
- **Salon pro (low volume)** — what to pick + why
- **High-volume salon** — what to pick + why
- **Sensitive client (HEMA reactions)** — what to pick + why
- **Beginner** — what to pick + why

Format: `<dl>` definition list OR 3-column grid block.

### Section 4: Comparison Table (150–200w + HTML table)

5–6 brands × 4–5 dimensions (cure time, durability, shade range, price
tier, HEMA-free status).

Table format: semantic `<table>` with proper `<thead>` / `<tbody>` / `<th>`
scope. Styling inherits from theme.

### Section 5: Application Guide (200–300w)

Step-by-step for the category's primary use-case (manicure for gel
polish, mani for dipping powder, etc.).

Format: ordered list `<ol>` with each step containing:
- Step name (bold)
- 1–2 sentences explanation
- Optional pro-tip callout

### Section 6: Care & Maintenance (150–200w)

How to extend wear / safely remove / store properly. Reinforces
post-purchase value, drives re-purchase signal to Shopify analytics.

Topics:
- Longevity tips (avoid water, use cuticle oil, etc.)
- Removal best practice (soak-off method per category)
- Storage (temperature, light, shelf-life)

### Section 7: Wholesale Info (100–150w)

Your store's wholesale positioning + volume discount tiers + free shipping
threshold. Closes the commercial-intent loop.

**Store-specific facts** (fill in with your own policy):
- Wholesale pricing eligibility (open to everyone, or account-gated)
- Free shipping threshold
- Bulk / volume discount tiers
- Dispatch time commitment (e.g. same-day cutoff)

### Section 8: Related Blog Reads (50–100w + 3–5 link blocks)

Cross-link 3–5 of your own blog posts relevant to the hub. Increases
internal PageRank flow to blog + improves content authority signal.

Format: `<ul>` with each link wrapped in `<li>` containing:
- Article title (link)
- 1-sentence teaser

**Source**: your blog article output directory (e.g. `output/<site>/`).
Map by topic relevance.

## Scoring Process

### Step 1: Determine collection scope

Pull collection via Shopify connector:
- handle, title, productsCount
- existing descriptionHtml (tagline) — DO NOT overwrite, body content goes
  in metafield separate from tagline
- existing metafield `custom.sub_categories` (sub-collection list informs
  comparison content)
- existing metafield `custom.faq_jsonld` (FAQ themes already covered —
  don't duplicate in body)

### Step 2: Identify brands present in hub

Scan first 50–100 products for vendor / brand tag distribution. Pick top 3–5
brands by product count → these are the brands featured in Section 2 + 4.

### Step 3: Generate per-section content

For each of the 8 sections, generate text using:
- Brand knowledge base (`references/brand-knowledge-base.md`)
- Store-specific facts (wholesale policy, shipping threshold, dispatch
  commitment, etc. — see Section 7)
- Category-specific knowledge (e.g. gel polish vs dipping powder vs nail
  lacquer differences, or the equivalent distinctions for your product
  category)

### Step 4: Em-dash + AI-trigger compliance & Readability Constraints (Paragraph Limits)

Rule: keep em-dash usage very low, ≤0.3 em-dash per 100 words across ALL copy. Use colons / periods instead.

**Readability & Paragraph Rules (CRITICAL for mobile UX)**:
- **Max Paragraph Length**: Every paragraph `<p>` MUST be short (2-4 sentences max, or ≤80 words).
- **Section Subdivision**: Split each of the 8 sections (200-300 words) into 3-4 smaller paragraphs or block elements. Do NOT output a single wall-of-text paragraph.
- **Scannable Layout**: Use bullet lists (`<ul>`/`<li>`), comparison tables, or bold lead-ins for key points to break up dense descriptions.

Self-check before push:
- Count em-dashes in generated body (ratio ≤0.3/100w)
- Ensure NO paragraph exceeds 4 sentences or 80 words.
- No AI trigger phrases: "delve into", "in conclusion", "navigate the
  landscape", "in today's fast-paced", "it's important to note", "let's
  explore"

### Step 5: HTML structure

Wrap each section in:
```html
<section class="collection-content__section">
  <h2 class="collection-content__heading">{Section Title}</h2>
  <div class="collection-content__body">
    <!-- section content -->
  </div>
</section>
```

Theme section CSS handles styling.

### Step 6: Push to metafield

```graphql
mutation {
  metafieldsSet(metafields: [{
    ownerId: "gid://shopify/Collection/<id>",
    namespace: "custom",
    key: "deep_content_html",
    type: "multi_line_text_field",
    value: "<HTML body>"
  }]) { ... }
}
```

### Step 7: Verify in preview

- WebFetch the collection URL
- Check that content renders BELOW FAQ
- Validate semantic HTML (h2 hierarchy, table accessibility, no inline
  styles except for table layout)

## Compose with other skills

- **Before**: `collection-analyze` (identify which hubs need depth)
- **After**: `collection-analyze --re-audit` (verify Cat 1.2 + Cat 4 lift)
- **Sibling**: `collection-refresh` (Phase 2 — re-runs this skill for
  existing hubs with new brand data)
- **Reads from**: `brand-knowledge-base.md` (per-brand profiles)
- **Writes to**: metafield `custom.deep_content_html` per collection +
  optional theme template tweak (one-time)

## Expected lift

Per collection-analyze v0.2.1 rubric:

| Category | Before | After | Δ |
|---|---|---|---|
| 1.2 Below-grid copy | 4/4 (FAQ only) | 4/4 + bonus authority | 0 (capped) |
| 2.9 Internal links | 3/3 | 3/3 (5 new blog links) | 0 (capped) |
| 4.4 Schema bonus (HowTo) | — | +1 | +1 |
| GEO/AI passage citability | 9/10 | 10/10 | +1 |
| **Long-tail SEO surface** | low | **high** | significant |

The composite score won't change much (already high and capped). The
**long-tail keyword footprint** and **AI citation eligibility** improve
dramatically — that's the real value of deep content.

## What this skill does NOT do

- Does NOT rewrite the tagline (that's collection.descriptionHtml — stays
  20–40w per Cat 1.1)
- Does NOT generate FAQ (that's `custom.faq_jsonld` — separate metafield)
- Does NOT modify product data
- Does NOT generate images (use `blog-image` skill for that — composable)
- Does NOT pull GSC data (use Phase 4 GSC integration in collection-analyze)

## Output convention

Per collection artifact:
```
output/[site]/[handle]/
└── deep-content.md      ← markdown source (auditable)
└── deep-content.html    ← HTML body pushed to metafield
```

The markdown source is the canonical version; the HTML is generated from
it. To update, edit the markdown + re-push the HTML.

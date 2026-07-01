# claude-shopify-growth

A [Claude Code](https://claude.com/claude-code) skill kit for growing **Shopify
ecommerce stores** with Claude: SEO + GEO optimization and content generation
across collections, products, and blog.

**Available now: two modules, collections and products.** The collection module
is a four-skill workflow that audits and optimizes Shopify collection pages
(mega-hubs, brand-hubs, category pages) for
Google rankings and AI-search citations. It takes a thin collection page ("empty
tagline + missing schema + zero internal links") and turns it into a deep,
well-structured hub: 1,500-2,000 words of tier-aware content, a 4-schema
structured-data bundle, 12-20 verified internal links, a keyword-dense
sub-60-character title, and a sub-collection nav. Every step is guarded by a HARD
gate so nothing ships half-done. More modules are on the [roadmap](#roadmap).

> Field-tested at scale on a large multi-brand ecommerce catalog (mean
> composite-score lift of +30-35 points per hub). Generalized here into a
> store-agnostic, MIT-licensed kit. No store data, credentials, or business
> figures are included — your product knowledge is a private, git-ignored input.

License: MIT · Built by [Khue Tran](https://khuetran.com) · Requires: Claude Code + a Shopify MCP connector

---

## The collection module (available now)

| Skill | What it does | Invoke |
|---|---|---|
| **collection-analyze** | Scores a collection page on a 100-point composite rubric (copy quality, SEO + commercial intent, curation, technical/schema, UX). Reports gaps. | `/collection-analyze <url>` |
| **collection-content-deep** | Generates 1,500-2,000w tier-aware deep content (variant-rich / hardware / bundle / seasonal / specialty templates) with a comparison table, application guide, FAQ, and internal-link zones. | `/collection-content-deep <url>` |
| **collection-audit-pipeline** | Portfolio-wide two-tier audit: a fast metadata scan across ALL collections, then a full `collection-analyze` deep-dive on the bottom quartile. Produces a prioritized action queue. | `/collection-audit-pipeline <site>` |
| **collection-mega-hub-optimize** | The end-to-end playbook that chains the above into a 12-step / 18-gate optimization run from baseline to ≥85/100. | `/collection-mega-hub-optimize <handle>` |

They compose: `collection-mega-hub-optimize` calls `collection-analyze` for the
baseline + re-score and `collection-content-deep` for the body;
`collection-audit-pipeline` calls `collection-analyze` per collection. The kit
is self-contained — it does not depend on any other skill pack.

---

## The product module (available now)

Product pages are the money pages: they carry transactional intent and feed
Google Shopping + AI Overviews for product queries. Four skills, same discipline
as the collection module (KB-first factcheck, HARD gates, schema bundle), plus
Merchant-Center feed safety.

| Skill | What it does | Invoke |
|---|---|---|
| **product-analyze** | Scores a PDP on a 100-point rubric (copy, SEO + intent, Product schema/technical, trust & conversion, GEO/AI-citation). Flags 🛑 Merchant-Center feed risks. | `/product-analyze <url>` |
| **product-content-deep** | Generates a unique, benefits-first description (lead → benefits → specs table → how-to → best-for → comparison → FAQ). No manufacturer boilerplate. | `/product-content-deep <url>` |
| **product-audit-pipeline** | Portfolio-wide two-tier audit of ALL products; ranks by traffic × gap, floats feed-risk products to the top. | `/product-audit-pipeline <site>` |
| **product-optimize** | End-to-end PDP playbook to ≥85/100 with zero feed-risk gates: rewrite + schema + trust pass + push. | `/product-optimize <handle>` |

The standout gate: the `Product` / `Offer` schema must mirror the visible
price/availability byte-for-byte, so an optimized page never trips a
Merchant-Center disapproval.

> **Applying fixes:** content is per-product data you rewrite; schema/render is a
> one-time theme change. See [docs/how-fixes-apply.md](docs/how-fixes-apply.md).

---

## How the collection optimizer works (18 HARD gates)

The mega-hub workflow refuses to ship a page that fails any gate. Highlights:

- **Gate 0 — KB-first factcheck.** Reads your private `knowledge-base/` for the
  product line before writing a word. No knowledge = no guessing.
- **Gate 1 — URL inventory.** Every internal link is verified against live
  Shopify inventory. Zero hallucinated handles/slugs.
- **Gate 2 — Title ≤60 characters** (with an optional theme-level brand-suffix
  opt-out so the title is 100% keyword).
- **Gate 3 — Zero AI-trigger phrases** ("Discover", "Elevate", "Seamless"...).
- **Gate 4 — Zero em-dashes** in editorial copy (AI-detection hygiene).
- **Gate 6 — Composite ≥85/100** on a live re-score, or it doesn't ship.
- **Gate 7 — No conflating `productsCount` with variant count** (sets/bundles ≠ individual items).
- **Gates 8-11 — OG image, above-grid tagline, filter sidebar, sub-collection nav.**
- **Gate 12 — No internal source labels** leak into customer-facing copy.
- **Gate 13 — Tier-aware content depth** (a hardware product gets a specs table, not variant-list copy).
- **Gates 15-18 — Live FAQ render, custom-template pre-flight, sub-nav render, FAQ length.**

Full detail: [`skills/collection-mega-hub-optimize/SKILL.md`](skills/collection-mega-hub-optimize/SKILL.md)
and its [`references/hard-gates.md`](skills/collection-mega-hub-optimize/references/hard-gates.md).
The product optimizer has its own 14 gates (incl. the 🛑 feed-safety ones):
[`skills/product-optimize/SKILL.md`](skills/product-optimize/SKILL.md).

---

## Install

Clone, then run the installer for your OS. It copies the skills to
`~/.claude/skills/` and the helper scripts to `~/.claude/scripts/`.

```bash
git clone https://github.com/chanktb/claude-shopify-growth.git
cd claude-shopify-growth

# macOS / Linux
./install.sh

# Windows (PowerShell)
./install.ps1
```

Then in Claude Code run `/reload-plugins` (or restart the session) and the
`/collection-*` and `/product-*` skills are available.

---

## Quickstart

```
# 1. Audit a single collection page
/collection-analyze https://your-store.com/collections/running-shoes

# 2. Audit the whole catalog and get a prioritized queue
/collection-audit-pipeline your-store.com

# 3. Optimize one hub end-to-end
/collection-mega-hub-optimize running-shoes --site your-store.com

# 4. Audit a single product page (the money page)
/product-analyze https://your-store.com/products/your-product

# 5. Optimize a product page end-to-end (feed-safe schema + unique copy)
/product-optimize your-product --site your-store.com
```

See [`docs/QUICKSTART.md`](docs/QUICKSTART.md) for a full walkthrough. Want to see
the output first? Here's a sample report:
[`examples/product-analyze-example.md`](examples/product-analyze-example.md).

---

## Requirements

- **Claude Code** (this is a skill kit for it).
- **A Shopify MCP connector** with Admin API access — the skills pull collection
  metadata, products, and metafields, and push metafields/templates.
- **A theme that renders the metafields** (deep content, FAQ, sub-nav). A
  one-time theme patch is documented in
  [`references/theme-patch-stiletto.md`](skills/collection-mega-hub-optimize/references/theme-patch-stiletto.md).
- *Optional:* Google Search Console access (enriches the audit with query/CTR
  data; skip with `--no-gsc`).
- *Optional:* a Telegram bot for publish notifications — copy
  `config.example.env` to `.env`. Without it, the notify step just skips.

---

## Your knowledge base is private

Gate 0 reads a `knowledge-base/` folder of your own product knowledge. **This is
not shipped and not committed** — it holds pricing, positioning, and sales data
that is yours alone. The repo includes only a template and instructions; see
[`knowledge-base/README.md`](knowledge-base/README.md). Everything in that folder
except the template is git-ignored.

---

## Repo layout

```
claude-shopify-growth/
├── skills/
│   ├── collection-analyze/
│   ├── collection-content-deep/
│   ├── collection-audit-pipeline/
│   ├── collection-mega-hub-optimize/
│   ├── product-analyze/
│   ├── product-content-deep/
│   ├── product-audit-pipeline/
│   └── product-optimize/
├── scripts/
│   ├── notify_collection_publish.py   # optional Telegram notify (Gate 14)
│   └── reduce_emdash.py               # em-dash density reducer (Gate 4)
├── knowledge-base/                     # your private product KB (git-ignored)
├── examples/                           # sanitized sample outputs
├── docs/                               # QUICKSTART + how-fixes-apply (data vs theme)
├── config.example.env
├── install.sh / install.ps1
└── LICENSE  (MIT)
```

---

## Roadmap

`claude-shopify-growth` is a growing kit. The collection and product modules ship
today; the modules below are planned. Each follows the same discipline: verified
data, HARD gates, SEO **and** GEO (AI-search) targeting, no fabrication.

- **Collection content refresh** — re-optimize existing hubs on a cadence (detect decay, refresh content + schema, keep the URL).
- **Product refresh** — re-optimize existing PDPs on a cadence (price/availability drift, review growth, seasonal angle).
- **Store-wide SEO + GEO audit** — crawl the whole store, score every page type, and produce a prioritized fix queue.
- **Blog content generation for ecom** — SEO/GEO-optimized articles that link back into collections and products.
- **GEO surface optimization** — tuning for AI Overviews, ChatGPT, and Perplexity citation surfaces across page types.

Have a request or want to contribute a module? Open an issue.

## Credits

Built by **[Khue Tran](https://khuetran.com)**, a marketer and operator
building AI tools for ecommerce. More write-ups at [khuetran.com](https://khuetran.com).

The `collection-analyze` rubric was modeled on the `blog-analyze` scoring approach
by **The Minh Nguyen** ([NextGrowth.AI](https://nextgrowth.ai)) — see his kit at
[github.com/thenguyenvn90/claude-growth](https://github.com/thenguyenvn90/claude-growth).

Contributions welcome via issues and PRs.

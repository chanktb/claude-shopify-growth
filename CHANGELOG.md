# Changelog

All notable changes to this project are documented here.

## [1.1.0] — 2026-07-01

Added the **product module**: optimize Shopify product pages (PDPs) for SEO + GEO
and conversion, with Google Merchant Center feed safety.

### New skills
- `product-analyze` — 100-point PDP rubric (copy, SEO + intent, Product schema/technical, trust & conversion, GEO/AI-citation) with 🛑 feed-risk gates
- `product-content-deep` — unique, benefits-first description generator (lead → benefits → specs table → how-to → best-for → comparison → FAQ)
- `product-audit-pipeline` — portfolio-wide two-tier PDP audit; ranks by traffic × gap, floats feed-risk products to the top
- `product-optimize` — end-to-end PDP playbook to ≥85/100 with zero feed-risk gates

### Notes
- Reuses the collection module's discipline: KB-first factcheck, HARD gates, schema bundle, and the notify script.
- Standout gate: the `Offer` schema must mirror the visible price/availability byte-for-byte, so an optimized page never trips a Merchant-Center disapproval.

## [1.0.0] — 2026-07-01

First public release. Extracted and generalized from a private, battle-tested
toolkit into a standalone, store-agnostic open-source kit.

### Included skills
- `collection-analyze` — 100-point composite rubric for Shopify collection pages
- `collection-content-deep` — 1,500-2,000w tier-aware deep content generator
- `collection-audit-pipeline` — portfolio-wide two-tier audit orchestrator
- `collection-mega-hub-optimize` — the 12-step / 18-gate optimization playbook

### Included scripts
- `notify_collection_publish.py` — optional Telegram publish notification
- `reduce_emdash.py` — em-dash density reducer (AI-detection hygiene)

### Notes
- All store-specific data, credentials, internal paths, and proprietary business
  figures were removed during extraction. The knowledge base is now a
  user-provided, git-ignored input (see `knowledge-base/README.md`).

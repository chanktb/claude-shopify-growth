# knowledge-base/ — your private product knowledge (NOT committed)

This directory holds **your store's own product knowledge**: first-party
product specs, positioning, best-seller data, price tiers, target-customer
profiles, companion/upsell pairings, and application techniques.

It is the **TIER_INTERNAL** source that Gate 0 (KB-first factcheck) reads before
any content is written. When the KB documents a product line, it becomes the
spine of the collection copy — this is what prevents the model from guessing and
hallucinating product facts.

## This data is private

Everything in this folder EXCEPT `README.md` and `INDEX.example.md` is
git-ignored (see the repo `.gitignore`). **Never commit real business data** —
pricing, margins, sales figures, and sales scripts are competitively sensitive.
The repo ships only the template so you can fill it in locally.

## Structure

```
knowledge-base/
├── INDEX.md                 # maps each product-line keyword → its file (you create this)
├── pk-<product-line>.md     # one file per product line (you create these)
└── ...
```

- `INDEX.md` — a lookup table so Step 0.5 can find the right file by keyword.
  Copy `INDEX.example.md` to `INDEX.md` and edit.
- `pk-<product-line>.md` — one markdown file per product line. Each should cover:
  - **Positioning** — best-seller rank, revenue share, how it's framed
  - **Product structure** — lines, palettes, SKU families, naming scheme
  - **Price tier** — relative to competitors (keep exact numbers local)
  - **Target customer** — skill level, segment, use case
  - **Companion / upsell pairings** — what to pair it with, and why
  - **Application technique** — the correct steps, common mistakes
  - **Differentiators** — what makes this line distinct

## How it's used

```bash
# Step 0.5a — open the index
cat knowledge-base/INDEX.md

# Step 0.5b — find the file(s) for a product line
grep -l -i "<product-keyword>" knowledge-base/*.md

# Step 0.5c — read the matched file(s), extract facts, then write
```

If no file covers a product line, log a "TIER_INTERNAL gap" in the baseline and
fall back to Shopify data + WebFetch. Never guess specs.

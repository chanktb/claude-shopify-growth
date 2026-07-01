# Quickstart

A full walkthrough from install to your first optimized collection hub.

## 0. Prerequisites

- Claude Code, with a **Shopify MCP connector** connected (Admin API access).
- A Shopify **2.0 theme**. To render deep content, FAQ, and the sub-nav, apply
  the one-time theme patch in
  [`../skills/collection-mega-hub-optimize/references/theme-patch-stiletto.md`](../skills/collection-mega-hub-optimize/references/theme-patch-stiletto.md).
- *(Optional)* Google Search Console access for query/CTR enrichment.
- *(Optional)* A Telegram bot for publish notifications.

## 1. Install

```bash
git clone https://github.com/<your-org>/claude-collection-optimizer.git
cd claude-collection-optimizer
./install.sh        # or ./install.ps1 on Windows
```

In Claude Code: `/reload-plugins` (or restart). The `/collection-*` skills are
now available.

## 2. (Optional) set up the knowledge base

Gate 0 reads `knowledge-base/`. This is optional but strongly recommended — it
is what stops the model from guessing product facts.

```bash
cp knowledge-base/INDEX.example.md knowledge-base/INDEX.md
# then create one pk-<product-line>.md per product line (see knowledge-base/README.md)
```

If you skip this, the workflow logs a "TIER_INTERNAL gap" and falls back to
Shopify data + WebFetch. It never fabricates specs.

## 3. (Optional) enable publish notifications

```bash
cp config.example.env .env
# edit .env: TELEGRAM_BOT_TOKEN + TELEGRAM_CHAT_ID
```

Without this, the Step 13 notifier just prints a skip line and the run continues.

## 4. Audit first

Start read-only. Score one page:

```
/collection-analyze https://your-store.com/collections/gel-color
```

Or scan the whole catalog and get a prioritized queue of what to fix first:

```
/collection-audit-pipeline your-store.com
```

## 5. Optimize a hub

Pick a mega-hub or brand-hub from the audit and run the full playbook:

```
/collection-mega-hub-optimize gel-color --site your-store.com
```

What happens:
1. **Gate 0** reads your KB for the product line.
2. **Baseline** is pulled (Shopify + live page + optional GSC), and the custom-
   template pre-flight check runs.
3. **Tier + path** are detected (Path A default vs Path B mega-hub).
4. Title, meta, H1, and 1,500-2,000w tier-aware content are written, with
   verified internal links only.
5. FAQ, metafields, and the hybrid template are pushed.
6. **Pre-publish gates** run (em-dash, AI-phrases, title length, link health,
   FAQ live render).
7. A **live re-score** confirms composite ≥85/100.
8. An optional notification is sent.

Per-hub artifacts land in `output/[site]/[handle]/` (git-ignored).

### Useful flags

- `--dry-run` — plan and write locally, don't push.
- `--no-gsc` — skip Search Console enrichment.
- `--skip-template` — push content/metafields only, leave the template as-is.
- `--tier mega-hub|brand-hub` — force a tier instead of auto-detecting.

## 6. Theme edits

Title-suffix and template changes are pushed to a **duplicate theme** for
preview (the MCP safelist commonly blocks writes to the live theme). Preview,
then publish the theme manually from Shopify admin.

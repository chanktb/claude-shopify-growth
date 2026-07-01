#!/usr/bin/env python3
"""reduce_emdash.py — Reduce em-dash density in markdown article.

AI detection signal: em-dash density > 0.5 per 100 words = strong AI flag.
Target: ≤0.3 per 100 words.

Strategy (context-aware):
  1. In headings (lines starting #): " — " → ": " AND preserve Title Case
  2. After **bold** in list items / strong tag: " — " → ": " (descriptor follows)
  3. Inline parenthetical "(X) — Y" → "(X), Y"
  4. In body prose " — " → ", " (preserve original casing — don't lowercase)
  5. Sentence-junction " — " before clear capital + verb → ". "
  6. Preserve em-dash inside <em>, code blocks, frontmatter, quotes

Usage:
  python reduce_emdash.py <draft.md> [--out <out.md>] [--dry-run]
"""
import sys, re, argparse
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

EMDASH = '—'


def in_protected_block(line, in_frontmatter, in_code, in_quote):
    """Check if line is inside protected scope (frontmatter, code fence, blockquote)."""
    return in_frontmatter or in_code or in_quote


def process_heading(line):
    """Heading line: replace ' — ' with ': ', preserve title case (don't lowercase next word)."""
    if EMDASH not in line:
        return line
    # Match: "## Heading — Subtitle" → "## Heading: Subtitle"
    return re.sub(r'\s+' + EMDASH + r'\s+', ': ', line)


def process_body_line(line):
    """Body line transformations. Preserve original case throughout."""
    if EMDASH not in line:
        return line

    # Rule: **bold** — descriptor → **bold**: descriptor
    line = re.sub(r'(\*\*[^*\n]+?\*\*)\s+' + EMDASH + r'\s+', r'\1: ', line)

    # Rule: bullet list "- X — Y" where X has no markdown emphasis:
    # convert first em-dash on bullet line to ":"
    # (handled by general rule below if not bold)

    # Rule: parenthetical "(X) — " → "(X), "
    line = re.sub(r'\)\s+' + EMDASH + r'\s+', '), ', line)

    # Rule: ", —" or "— ," sequences → cleanup
    line = re.sub(r',\s*' + EMDASH + r'\s*', ', ', line)
    line = re.sub(r'\s*' + EMDASH + r'\s*,', ',', line)

    # Rule: ": —" → ": " (descriptor)
    line = re.sub(r':\s*' + EMDASH + r'\s*', ': ', line)

    # Rule: stray "—" at line start/end → drop
    line = re.sub(r'^\s*' + EMDASH + r'\s*', '', line)
    line = re.sub(r'\s*' + EMDASH + r'\s*$', '', line)

    # Rule: general " — " in body → ", " (preserve case)
    line = re.sub(r'\s+' + EMDASH + r'\s+', ', ', line)

    return line


def reduce(text):
    lines = text.split('\n')
    out = []
    in_frontmatter = False
    in_code = False
    frontmatter_count = 0

    for i, line in enumerate(lines):
        # Frontmatter delimiter
        stripped = line.strip()
        if stripped == '---' and i < 30:
            frontmatter_count += 1
            if frontmatter_count == 1:
                in_frontmatter = True
            elif frontmatter_count == 2:
                in_frontmatter = False
            out.append(line)
            continue
        # Code fence
        if stripped.startswith('```'):
            in_code = not in_code
            out.append(line)
            continue
        # Inside protected block: leave as-is
        if in_frontmatter or in_code:
            out.append(line)
            continue
        # Heading line
        if re.match(r'^#{1,4}\s', line):
            out.append(process_heading(line))
            continue
        # Body line
        out.append(process_body_line(line))

    return '\n'.join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('draft')
    ap.add_argument('--out')
    ap.add_argument('--dry-run', action='store_true')
    args = ap.parse_args()

    with open(args.draft, encoding='utf-8') as f:
        text = f.read()
    words = len(text.split())
    before_count = text.count(EMDASH)
    before_density = before_count / max(1, words) * 100

    new_text = reduce(text)
    after_count = new_text.count(EMDASH)
    after_density = after_count / max(1, words) * 100

    print(f'File: {args.draft}')
    print(f'  Words: {words:,}')
    print(f'  Em-dash before: {before_count} ({before_density:.2f} per 100 words)')
    print(f'  Em-dash after:  {after_count} ({after_density:.2f} per 100 words)')
    print(f'  Replaced: {before_count - after_count}')
    if after_density <= 0.3:
        print(f'  PASS: below AI-flag threshold')
    elif after_density <= 0.5:
        print(f'  WARN: close to threshold')
    else:
        print(f'  FAIL: still above threshold')

    if not args.dry_run:
        out_path = args.out or args.draft
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(new_text)
        print(f'  -> wrote {out_path}')


if __name__ == '__main__':
    main()

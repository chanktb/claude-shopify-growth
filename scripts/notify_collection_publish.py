#!/usr/bin/env python3
"""notify_collection_publish.py — Send a concise Telegram notification after a collection content publish/optimize.

Optional notifier for the collection-mega-hub-optimize workflow (Step 13 / Gate 14).
If no credentials are configured, it exits cleanly without sending — it never breaks a run.

Usage:
  python notify_collection_publish.py \
    --site your-store.com \
    --handle example-collection \
    --url https://your-store.com/collections/example-collection \
    --tier tools \
    --reason "GSC rank opportunity, tools-tier content debut" \
    --baseline "<imp> imp / <clicks> clicks / pos <n> (90d)" \
    --change "10-section tools template + specs table + SVG chart + maintenance"

Credentials: reads TELEGRAM_BOT_TOKEN + TELEGRAM_CHAT_ID from a local .env file.
The .env path is taken from the COLLECTION_OPTIMIZER_ENV environment variable,
falling back to ./.env in the current working directory. See config.example.env.

Output: posts a small HTML message to the configured Telegram chat.
"""
import argparse, os, sys, json
from urllib import request, parse, error

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# Local .env holding TELEGRAM_BOT_TOKEN + TELEGRAM_CHAT_ID. Override with the
# COLLECTION_OPTIMIZER_ENV environment variable; defaults to ./.env.
ENV_PATH = os.environ.get('COLLECTION_OPTIMIZER_ENV', os.path.join(os.getcwd(), '.env'))

TIER_ICONS = {
    'mega-hub':   '🏛️',
    'brand-hub':  '🏷️',
    'sub':        '📦',
    'tools':      '🔧',
    'seasonal':   '🌸',
    'bundle':     '🎁',
    'bulk-save':  '💰',
    'nail-art':   '🎨',
    'gel':        '💅',
}

MODE_ICONS = {
    'new':      '✨',
    'optimize': '⚡',
    'refresh':  '🔄',
}


def load_env():
    creds = {}
    if not os.path.exists(ENV_PATH):
        return creds
    with open(ENV_PATH, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line.startswith('#') or '=' not in line:
                continue
            k, v = line.split('=', 1)
            creds[k.strip()] = v.strip().strip('"').strip("'")
    return creds


def send_telegram(token, chat_id, text, parse_mode='HTML'):
    api_url = f'https://api.telegram.org/bot{token}/sendMessage'
    data = parse.urlencode({
        'chat_id': chat_id,
        'text': text,
        'parse_mode': parse_mode,
        'disable_web_page_preview': 'false',
    }).encode('utf-8')
    req = request.Request(api_url, data=data, method='POST')
    try:
        resp = request.urlopen(req, timeout=20)
        body = resp.read().decode('utf-8', errors='replace')
        result = json.loads(body)
        return result.get('ok', False), result
    except error.HTTPError as e:
        body = e.read().decode('utf-8', errors='replace')
        return False, {'error': f'HTTP {e.code}', 'body': body}
    except Exception as e:
        return False, {'error': str(e)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--site', required=True, help='e.g. your-store.com')
    ap.add_argument('--handle', required=True, help='collection handle, e.g. example-collection')
    ap.add_argument('--url', required=True, help='live URL')
    ap.add_argument('--mode', default='optimize', choices=['new', 'optimize', 'refresh'])
    ap.add_argument('--tier', default='', help='mega-hub|brand-hub|sub|tools|seasonal|bundle|bulk-save|nail-art|gel')
    ap.add_argument('--reason', required=True, help='one-line why (GSC rank, content gap, refresh trigger)')
    ap.add_argument('--baseline', default='', help='GSC baseline 90d — e.g. "33,679 imp / 155 clicks / pos 12.7"')
    ap.add_argument('--change', default='', help='one-line what changed (template, sections, hero, schema)')
    ap.add_argument('--target', default='', help='ranking/conversion target (optional)')
    ap.add_argument('--gates', default='', help='gates passed summary (optional) — e.g. "14/14 gates"')
    args = ap.parse_args()

    creds = load_env()
    token = creds.get('TELEGRAM_BOT_TOKEN')
    chat_id = creds.get('TELEGRAM_CHAT_ID')
    if not token or not chat_id:
        # No channel configured: skip cleanly so the workflow is never blocked.
        print(f'SKIP: TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID not found in {ENV_PATH}; '
              f'notification skipped (set COLLECTION_OPTIMIZER_ENV or create ./.env to enable).')
        sys.exit(0)

    mode_icon = MODE_ICONS.get(args.mode, '⚡')
    mode_label = args.mode.upper()
    tier_icon = TIER_ICONS.get(args.tier, '🛍️') if args.tier else '🛍️'

    def esc(s):
        return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

    lines = [
        f'{mode_icon} <b>Collection {mode_label}</b> {tier_icon} — <code>{esc(args.site)}</code>',
        '',
        f'🏷️ <b>{esc(args.handle)}</b>',
        f'🔗 {esc(args.url)}',
        '',
        f'<b>Why</b>: {esc(args.reason)}',
    ]
    if args.tier:
        lines.append(f'<b>Tier</b>: {esc(args.tier)}')
    if args.baseline:
        lines.append(f'<b>Baseline</b>: {esc(args.baseline)}')
    if args.change:
        lines.append(f'<b>Change</b>: {esc(args.change)}')
    if args.target:
        lines.append(f'<b>Target</b>: {esc(args.target)}')
    if args.gates:
        lines.append(f'<b>Gates</b>: {esc(args.gates)}')

    text = '\n'.join(lines)

    ok, result = send_telegram(token, chat_id, text)
    if ok:
        print(f'OK Telegram notification sent (message_id={result["result"]["message_id"]})')
    else:
        print(f'FAIL Telegram send: {result}')
        sys.exit(2)


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""Turn a downloaded copy of the WordPress site into Astro source files.

Usage: python3 scripts/import-wordpress.py <html-dir>
  <html-dir> holds one index.html per page, in the same folders as the live URLs
  (html/index.html, html/over/index.html, ...).

Writes:
  src/partials/header.html, src/partials/footer.html   shared site header and footer
  src/wp/<path>/content.html                            the page body between header and footer
  src/wp/<path>/meta.json                               title, <head> extras, body class, scripts
Absolute links to dansblok.com become {{BASE}}/... so the site works on any host or sub-path.
"""
import json, os, re, sys, glob, shutil

SRC = sys.argv[1]
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'src', 'wp')
PARTIALS = os.path.join(ROOT, 'src', 'partials')

ACTIVE_RE = re.compile(r'\s(current[-_][a-z_-]+|active|page_item|page-item-\d+)(?=[\s"])')

HEAD_DROP = [
    re.compile(r'<link[^>]+rel=["\'](EditURI|wlwmanifest|shortlink|pingback|https://api\.w\.org/)["\'][^>]*>\s*', re.I),
    re.compile(r'<link[^>]+rel=["\']alternate["\'][^>]*>\s*', re.I),
    re.compile(r'<link[^>]+rel=["\']profile["\'][^>]*>\s*', re.I),
    re.compile(r'<meta[^>]+name=["\']generator["\'][^>]*>\s*', re.I),
]
# Google Analytics (MonsterInsights). Left out of the copy; see GO-LIVE.md.
SCRIPT_RE = re.compile(r'<script\b[^>]*>.*?</script>\s*', re.S | re.I)
def drop_script(tag):
    return ('googletagmanager.com' in tag or 'monsterinsights' in tag.lower()
            or '__gtagTracker' in tag or 'frontend-gtag' in tag)

def rewrite(s):
    # Keep canonical links and structured data pointing at the real domain.
    keep = []
    def stash(m):
        keep.append(m.group(0)); return f'\x00{len(keep)-1}\x00'
    s = re.sub(r'<link[^>]+rel=["\']canonical["\'][^>]*>', stash, s)
    s = re.sub(r'<script[^>]+application/ld\+json[^>]*>.*?</script>', stash, s, flags=re.S)
    s = re.sub(r'<meta[^>]+(property|name)=["\'](og:|twitter:)[^>]*>', stash, s)
    s = re.sub(r'https?://(www\.)?dansblok\.com(?=[/"\'?#\s<]|$)', '{{BASE}}', s)
    s = re.sub(r'https?:\\/\\/(www\.)?dansblok\.com(?=\\/|["\'])', '{{BASE_JSON}}', s)
    s = re.sub(r'(?<=["\'(])//(www\.)?dansblok\.com(?=/)', '{{BASE}}', s)
    # Protocol-relative third-party URLs (Google Fonts etc.) fail on plain http previews.
    s = re.sub(r'(["\'(])//(?=[a-z0-9.-]+\.[a-z]{2,}/)', r'\1https://', s)
    # A bare home link ("{{BASE}}") must still point somewhere when BASE is empty.
    s = re.sub(r'(href|action)="\{\{BASE\}\}"', r'\1="{{BASE}}/"', s)
    return re.sub(r'\x00(\d+)\x00', lambda m: keep[int(m.group(1))], s)

def menu_state(hdr):
    """Which menu items are marked current on this page, with their full class lists."""
    state = {}
    for m in re.finditer(r'<li id="(menu-item-\d+)" class="([^"]*)"', hdr):
        if ACTIVE_RE.search(' ' + m.group(2) + '"'):
            state[m.group(1)] = m.group(2)
    current = sorted(set(re.findall(r'href="([^"]+)" aria-current="page"', hdr)))
    return state, current

def neutral(part):
    part = re.sub(r'(<li id="menu-item-\d+" class=")([^"]*)(")',
                  lambda m: m.group(1) + ACTIVE_RE.sub('', ' ' + m.group(2) + '"')[1:-1] + m.group(3), part)
    return part.replace(' aria-current="page"', '')

def convert(path, rel):
    s = open(path, encoding='utf-8').read()
    html_tag = re.search(r'<html([^>]*)>', s).group(1)
    head = s[s.find('<head>') + 6:s.find('</head>')]
    body_open = re.search(r'<body([^>]*)>', s)
    body_class = re.search(r'class="([^"]*)"', body_open.group(1)).group(1)
    b = body_open.end()
    h1 = s.find('<header class="header'); h2 = s.find('</header>', h1) + len('</header>')
    f1 = s.find('<footer'); f2 = s.find('</footer>', f1) + len('</footer>')
    end = s.rfind('</body>')
    before_header = s[b:h1]           # opening <div class="wrapper ...">
    header = s[h1:h2]; content = s[h2:f1]; footer = s[f1:f2]; after = s[f2:end]

    title = re.search(r'<title>(.*?)</title>', head, re.S)
    head = re.sub(r'<title>.*?</title>\s*', '', head, flags=re.S)
    head = re.sub(r'<meta charset[^>]*>\s*|<meta name="viewport"[^>]*>\s*', '', head)
    for r in HEAD_DROP: head = r.sub('', head)
    head = SCRIPT_RE.sub(lambda m: '' if drop_script(m.group(0)) else m.group(0), head)
    after = SCRIPT_RE.sub(lambda m: '' if drop_script(m.group(0)) else m.group(0), after)

    hstate, hcur = menu_state(header)
    fstate, fcur = menu_state(footer)
    meta = {
        'path': '/' + rel + ('/' if rel else ''),
        'title': title.group(1).strip() if title else '',
        'htmlAttrs': html_tag.strip(),
        'bodyClass': body_class,
        'wrapperOpen': rewrite(before_header).strip(),
        'head': rewrite(head).strip(),
        'afterFooter': rewrite(after).strip(),
        'headerActive': hstate, 'headerCurrent': [rewrite(x) for x in hcur],
        'footerActive': fstate, 'footerCurrent': [rewrite(x) for x in fcur],
    }
    d = os.path.join(OUT, rel)
    os.makedirs(d, exist_ok=True)
    open(os.path.join(d, 'content.html'), 'w', encoding='utf-8').write(rewrite(content).strip() + '\n')
    json.dump(meta, open(os.path.join(d, 'meta.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    return neutral(rewrite(header)), neutral(rewrite(footer))

if os.path.isdir(OUT): shutil.rmtree(OUT)
os.makedirs(PARTIALS, exist_ok=True)
headers, footers = {}, {}
for f in sorted(glob.glob(os.path.join(SRC, '**', 'index.html'), recursive=True)):
    rel = os.path.relpath(os.path.dirname(f), SRC)
    rel = '' if rel == '.' else rel
    h, ft = convert(f, rel)
    headers.setdefault(h, []).append(rel); footers.setdefault(ft, []).append(rel)
for name, variants in (('header', headers), ('footer', footers)):
    best = max(variants, key=lambda k: len(variants[k]))
    open(os.path.join(PARTIALS, name + '.html'), 'w', encoding='utf-8').write(best + '\n')
    if len(variants) > 1:
        print(f'warning: {name} differs on', [v for k, v in variants.items() if k != best])
print('pages:', sum(len(v) for v in headers.values()))

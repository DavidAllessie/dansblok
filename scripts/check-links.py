#!/usr/bin/env python3
"""List internal links in dist/ that point to pages or files that don't exist."""
import os, re, glob, sys, urllib.parse, collections
DIST = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'dist')
missing = collections.Counter()
for f in glob.glob(DIST + '/**/*.html', recursive=True):
    s = open(f, encoding='utf-8').read()
    for m in re.finditer(r'(?:href|src)="(/[^"#?]*)', s):
        u = urllib.parse.unquote(m.group(1))
        if u.startswith('//'): continue
        t = os.path.join(DIST, u.lstrip('/'))
        if not (os.path.isfile(t) or os.path.isfile(os.path.join(t, 'index.html'))):
            missing[m.group(1)] += 1
for u, n in missing.most_common(): print(n, u)

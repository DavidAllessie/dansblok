#!/usr/bin/env python3
"""Make absolute https://dansblok.com/... links inside copied CSS files relative,
so styles and fonts load on any host or sub-path (e.g. GitHub Pages)."""
import os, re, glob, posixpath
ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'public')
for f in glob.glob(os.path.join(ROOT, '**', '*.css'), recursive=True):
    s = open(f, encoding='utf-8', errors='surrogateescape').read()
    d = '/' + posixpath.relpath(os.path.dirname(f), ROOT).replace(os.sep, '/')
    n = re.sub(r'https?://(?:www\.)?dansblok\.com(/[^)\'"\s]*)',
               lambda m: posixpath.relpath(m.group(1), d), s)
    if n != s:
        open(f, 'w', encoding='utf-8', errors='surrogateescape').write(n); print('fixed', f)

// @ts-check
import { defineConfig } from 'astro/config';
import { readFileSync } from 'node:fs';

// Old WordPress URLs that redirect elsewhere (taken from the live site).
const redirects = JSON.parse(readFileSync(new URL('./src/redirects.json', import.meta.url), 'utf8'));

// SITE_BASE lets the same build run on GitHub Pages (/dansblok/) and later on dansblok.com (/).
export default defineConfig({
  site: process.env.SITE_URL ?? 'https://dansblok.com',
  base: process.env.SITE_BASE ?? '/',
  trailingSlash: 'ignore',
  build: { format: 'directory' },
  compressHTML: false,
  redirects,
});

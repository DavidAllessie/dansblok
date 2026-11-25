# DansBlok website

A static copy of [dansblok.com](https://dansblok.com) (WordPress) rebuilt with [Astro](https://astro.build).
It looks and behaves like the live site, but needs no WordPress, database or PHP.

## How it is put together

| Folder | What is in it |
| --- | --- |
| `src/wp/<page>/content.html` | The content of each page (one folder per URL, e.g. `src/wp/over/`) |
| `src/wp/<page>/meta.json` | Page title, SEO tags, page-specific styles and scripts |
| `src/partials/header.html`, `footer.html` | The menu and footer shared by every page |
| `src/redirects.json` | Old URLs that forward to new ones |
| `public/wp-content/…` | Images, PDFs, theme styles and scripts, at the same paths as on the live site |
| `scripts/` | The import tools used to make this copy from the live site |

To change text on a page, edit its `content.html`. To change the menu, edit `src/partials/header.html`.

## Commands

```sh
npm install
npm run dev      # local preview at http://localhost:4321
npm run build    # static site in dist/
```

Every push to `main` publishes a preview to GitHub Pages at https://davidallessie.github.io/dansblok/ (see `.github/workflows/deploy.yml`).

## Re-importing from WordPress

`python3 scripts/import-wordpress.py <folder with downloaded pages>` regenerates `src/wp/` and the partials.
`python3 scripts/fix-asset-urls.py` makes links inside copied CSS files relative.
`python3 scripts/check-links.py` lists internal links that point nowhere after a build.

## Not working yet in the static copy

- Contact form (WPForms) and donation form (Mollie) need a replacement service.
- Site search and the agenda's month/week view switcher relied on WordPress.
- Google Analytics is left out of the preview.

// Loads the pages imported from WordPress (src/wp/**) and fills in the shared header/footer.
import headerHtml from '../partials/header.html?raw';
import footerHtml from '../partials/footer.html?raw';

export interface WpMeta {
  path: string;
  title: string;
  htmlAttrs: string;
  bodyClass: string;
  wrapperOpen: string;
  head: string;
  afterFooter: string;
  headerActive: Record<string, string>;
  headerCurrent: string[];
  footerActive: Record<string, string>;
  footerCurrent: string[];
}

const metas = import.meta.glob<WpMeta>('../wp/**/meta.json', { eager: true, import: 'default' });
const contents = import.meta.glob<string>('../wp/**/content.html', { eager: true, query: '?raw', import: 'default' });

export function allPages() {
  return Object.entries(metas).map(([file, meta]) => ({
    meta,
    content: contents[file.replace('meta.json', 'content.html')] ?? '',
  }));
}

// Site base without trailing slash: '' on dansblok.com, '/dansblok' on GitHub Pages.
const BASE = import.meta.env.BASE_URL.replace(/\/$/, '');

export function withBase(html: string): string {
  return html
    .replaceAll('{{BASE_JSON}}', BASE.replaceAll('/', '\\/'))
    .replaceAll('{{BASE}}', BASE);
}

function markMenu(html: string, active: Record<string, string>, current: string[]): string {
  let out = html;
  for (const [id, cls] of Object.entries(active)) {
    out = out.replace(new RegExp(`(<li id="${id}" class=")[^"]*(")`), `$1${cls}$2`);
  }
  for (const href of current) {
    out = out.replaceAll(`href="${href}">`, `href="${href}" aria-current="page">`);
  }
  return out;
}

export const header = (m: WpMeta) => markMenu(headerHtml, m.headerActive, m.headerCurrent);
export const footer = (m: WpMeta) => markMenu(footerHtml, m.footerActive, m.footerCurrent);

import { readFileSync } from 'node:fs';
import vm from 'node:vm';

export const SCIEZKA_HTML = new URL('../cwiczenia-pakiet-analityczny.html', import.meta.url);

export function wczytajHtml() {
  return readFileSync(SCIEZKA_HTML, 'utf8');
}

export function blok(html, id) {
  const m = html.match(new RegExp(`<script id="${id}">([\\s\\S]*?)</script>`));
  if (!m) throw new Error(`Brak bloku <script id="${id}"> w cwiczenia-pakiet-analityczny.html`);
  return m[1];
}

export function zaladuj({ zrzuty = false } = {}) {
  const html = wczytajHtml();
  const kod = [
    blok(html, 'dane'),
    zrzuty ? blok(html, 'zrzuty') : '',
    `globalThis.__api = { ...DANE${zrzuty ? ', ZRZUTY' : ''} };`,
  ].join('\n;\n');
  const kontekst = vm.createContext({});
  vm.runInContext(kod, kontekst, { filename: 'cwiczenia-pakiet-analityczny.html' });
  return kontekst.__api;
}

// Obiekty z innego realmu vm mają inne prototypy - przed deepEqual kopiujemy je przez JSON.
export const j = (x) => JSON.parse(JSON.stringify(x));

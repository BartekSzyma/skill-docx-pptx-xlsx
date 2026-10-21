import { readFileSync } from 'node:fs';
import vm from 'node:vm';

export const PLIK_GLOWNY = 'cwiczenia-pakiet-analityczny.html';
export const PLIK_HOOKI = 'cwiczenia-hooki.html';
export const SCIEZKA_HTML = new URL(`../${PLIK_GLOWNY}`, import.meta.url);

export function wczytajHtml(plik = PLIK_GLOWNY) {
  return readFileSync(new URL(`../${plik}`, import.meta.url), 'utf8');
}

export function blok(html, id, plik = PLIK_GLOWNY) {
  const m = html.match(new RegExp(`<script id="${id}">([\\s\\S]*?)</script>`));
  if (!m) throw new Error(`Brak bloku <script id="${id}"> w ${plik}`);
  return m[1];
}

export function zaladuj({ zrzuty = false, plik = PLIK_GLOWNY } = {}) {
  const html = wczytajHtml(plik);
  const kod = [
    blok(html, 'dane', plik),
    zrzuty ? blok(html, 'zrzuty', plik) : '',
    `globalThis.__api = { ...DANE${zrzuty ? ', ZRZUTY' : ''} };`,
  ].join('\n;\n');
  const kontekst = vm.createContext({});
  vm.runInContext(kod, kontekst, { filename: plik });
  return kontekst.__api;
}

// Obiekty z innego realmu vm mają inne prototypy - przed deepEqual kopiujemy je przez JSON.
export const j = (x) => JSON.parse(JSON.stringify(x));

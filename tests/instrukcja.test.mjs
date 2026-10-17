import { test } from 'node:test';
import assert from 'node:assert/strict';
import { zaladuj, j } from './zaladuj.mjs';
import { wypiszPrompt } from '../tools/wypisz-prompt.mjs';
import { existsSync } from 'node:fs';
import { fileURLToPath } from 'node:url';

const A = zaladuj();
const elementy = () => A.INSTRUKCJA.flatMap((s) => s.elementy);
const TYPY = new Set(['tekst', 'komenda', 'sprawdz', 'uwaga', 'wazne', 'mac', 'zrzut', 'prompt', 'plik', 'dlaczego', 'schemat', 'animacja']);

test('sekcje mają unikalne ASCII id i tytuły numerowane od 0 po kolei', () => {
  assert.ok(A.INSTRUKCJA.length > 0);
  A.INSTRUKCJA.forEach((s, i) => {
    assert.match(s.id, /^[a-z0-9-]+$/, s.id);
    assert.ok(s.tytul.startsWith(`${i}. `), s.tytul);
  });
  assert.equal(new Set(A.INSTRUKCJA.map((s) => s.id)).size, A.INSTRUKCJA.length);
});

test('każdy element ma znany typ i niepustą treść; html bez <script', () => {
  for (const e of elementy()) {
    assert.ok(TYPY.has(e.typ), e.typ);
    if (['tekst', 'sprawdz', 'uwaga', 'wazne', 'mac', 'dlaczego'].includes(e.typ)) assert.ok(e.html.length > 0);
    if (e.typ === 'komenda') assert.ok(e.tekst.length > 0);
    if (e.typ === 'prompt') assert.ok(e.tytul.length > 0 && e.tekst.length > 0, e.id);
    if (e.typ === 'plik') assert.ok(e.nazwa.length > 0 && e.linie.length > 0);
    if ('html' in e) assert.doesNotMatch(e.html, /<script/i);
  }
});

test('prompty P1..Pn występują dokładnie raz i po kolei', () => {
  const ids = elementy().filter((e) => e.typ === 'prompt').map((e) => e.id);
  assert.ok(ids.length >= 4, `za mało promptów: ${ids.length}`);
  assert.deepEqual(j(ids), Array.from({ length: ids.length }, (_, i) => `P${i + 1}`));
});

test('prompty nie zawierają ścieżek ani nazw autora', () => {
  for (const e of elementy().filter((x) => x.typ === 'prompt')) {
    assert.doesNotMatch(e.tekst, /C:\\Programowanie|Bartek|auto mode|herdr|CLAUDE_CONFIG_DIR/i, e.id);
  }
});

test('każdy zrzut z LISTA_ZRZUTOW użyty dokładnie raz', () => {
  const uzyte = elementy().filter((e) => e.typ === 'zrzut').map((e) => e.klucz).sort();
  assert.deepEqual(j(uzyte), j(A.LISTA_ZRZUTOW.map((z) => z.klucz).sort()));
  for (const z of A.LISTA_ZRZUTOW) {
    assert.match(z.klucz, /^[0-9]{2}-[a-z0-9-]+$/);
    assert.ok(z.podpis.length > 0, z.klucz);
  }
});

test('wypiszPrompt zwraca tekst promptu i rzuca dla nieznanego id', () => {
  const html = `<script id="dane">
const DANE = { INSTRUKCJA: [{ id: 'x', tytul: '0. X', elementy: [{ typ: 'prompt', id: 'P1', tytul: 'T', tekst: 'Zrób coś.\\nDruga linia z ąę.' }] }] };
</script>`;
  assert.equal(wypiszPrompt(html, 'P1'), 'Zrób coś.\nDruga linia z ąę.');
  assert.throws(() => wypiszPrompt(html, 'P9'), /P9/);
});

test('ścieżki Windows w treści nie zgubiły ukośników (np. C:Program Files, .claudeskills)', () => {
  for (const e of elementy()) {
    const tresc = `${e.html || ''}${e.tekst || ''}`;
    assert.doesNotMatch(tresc, /[A-Z]:Program|\.claudeskills|META(zrodla|wyniki|weryfikacja)|Dokumentyanalizy/, tresc.slice(0, 80));
  }
});

test('każdy krok z promptem ma ramkę „Co się dzieje i po co” i punkt „Sprawdź”', () => {
  for (const s of A.INSTRUKCJA.filter((x) => x.elementy.some((e) => e.typ === 'prompt'))) {
    assert.ok(s.elementy.some((e) => e.typ === 'dlaczego'), `${s.id}: brak ramki dlaczego`);
    assert.ok(s.elementy.some((e) => e.typ === 'sprawdz'), `${s.id}: brak Sprawdź`);
  }
});

test('wymagania systemowe wymieniają Python, LibreOffice i MS Office', () => {
  const zanim = A.INSTRUKCJA[0].elementy.map((e) => e.html || '').join(' ');
  for (const w of ['Python 3.11', 'LibreOffice', 'MS Office']) assert.ok(zanim.includes(w), w);
});

test('każda animacja z ANIMACJE użyta dokładnie raz i ma podpis', () => {
  const uzyte = elementy().filter((e) => e.typ === 'animacja').map((e) => e.klucz).sort();
  assert.deepEqual(j(uzyte), Object.keys(A.ANIMACJE).sort());
  for (const [klucz, a] of Object.entries(A.ANIMACJE)) {
    assert.ok(a.podpis.length > 0, klucz);
    assert.ok(a.rodzaj === 'eksplorator' || Array.isArray(a.kroki), klucz);
  }
});

test('konstruktor pytania pomija puste pola i zawsze dodaje kontekst oraz zadanie', () => {
  const pytanie = A.zlozPytanie('Krok 2: ledger', { zrobilem: 'Wkleiłem P2.', widze: '  ', oczekiwalem: '' });
  assert.match(pytanie, /^\[KONTEKST\]\n.*Krok 2: ledger/);
  assert.match(pytanie, /\[CO ZROBIŁEM\]\nWkleiłem P2\./);
  assert.doesNotMatch(pytanie, /CO WIDZĘ|CZEGO SIĘ/);
  assert.match(pytanie, /\[ZADANIE\]\n.*Nie łagodź/);
});

test('linki do dokumentów z budowy wzorcowej prowadzą do istniejących plików Office', () => {
  const html = elementy().map((e) => e.html || '').join(' ');
  const linki = [...html.matchAll(/href="(budowa-wzorcowa\/[^"]+)"/g)].map((m) => m[1]);
  assert.ok(new Set(linki).size >= 6, `za mało linków: ${new Set(linki).size}`);
  for (const l of linki) {
    assert.match(l, /\.(xlsx|pptx|docx)$/, l);
    assert.ok(existsSync(fileURLToPath(new URL(`../${l}`, import.meta.url))), l);
  }
});

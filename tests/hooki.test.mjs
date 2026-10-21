import { test } from 'node:test';
import assert from 'node:assert/strict';
import vm from 'node:vm';
import { zaladuj, wczytajHtml, blok, j, PLIK_HOOKI, PLIK_GLOWNY } from './zaladuj.mjs';

const A = zaladuj({ plik: PLIK_HOOKI });
const elementy = () => A.INSTRUKCJA.flatMap((s) => s.elementy);
const TYPY = new Set(['tekst', 'komenda', 'sprawdz', 'uwaga', 'wazne', 'mac', 'zrzut', 'prompt', 'plik', 'dlaczego', 'schemat', 'animacja']);
const prompty = () => elementy().filter((e) => e.typ === 'prompt');

test('hooki: sekcje mają unikalne ASCII id i tytuły numerowane od 0 po kolei', () => {
  A.INSTRUKCJA.forEach((s, i) => {
    assert.match(s.id, /^[a-z0-9-]+$/, s.id);
    assert.ok(s.tytul.startsWith(`${i}. `), s.tytul);
  });
  assert.equal(new Set(A.INSTRUKCJA.map((s) => s.id)).size, A.INSTRUKCJA.length);
});

test('hooki: każdy element ma znany typ i niepustą treść; html bez <script', () => {
  for (const e of elementy()) {
    assert.ok(TYPY.has(e.typ), e.typ);
    if (['tekst', 'sprawdz', 'uwaga', 'wazne', 'mac', 'dlaczego'].includes(e.typ)) assert.ok(e.html.length > 0);
    if (e.typ === 'komenda') assert.ok(e.tekst.length > 0);
    if (e.typ === 'prompt') assert.ok(e.tytul.length > 0 && e.tekst.length > 0, e.id);
    if ('html' in e) assert.doesNotMatch(e.html, /<script/i);
  }
});

test('hooki: prompty K1..K11 po kolei, potem poglądowe Z1..Z4', () => {
  const ids = prompty().map((e) => e.id);
  const oczekiwane = [...Array.from({ length: 11 }, (_, i) => `K${i + 1}`), 'Z1', 'Z2', 'Z3', 'Z4'];
  assert.deepEqual(j(ids), oczekiwane);
  for (const e of prompty()) assert.equal(Boolean(e.poglad), e.id.startsWith('Z'), e.id);
});

test('hooki: prompty nie zawierają ścieżek ani nazw autora', () => {
  for (const e of prompty()) {
    assert.doesNotMatch(e.tekst, /C:\\Programowanie|Bartek|auto mode|herdr|CLAUDE_CONFIG_DIR/i, e.id);
  }
});

test('hooki: ścieżki Windows w treści nie zgubiły ukośników', () => {
  for (const e of elementy()) {
    const tresc = `${e.html || ''}${e.tekst || ''}`;
    assert.doesNotMatch(tresc, /[A-Z]:Program|\.claudeskills|\.claudehooks|Dokumentyhooki/, tresc.slice(0, 80));
  }
});

test('hooki: każdy krok z promptem (poza poglądowymi) ma ramkę „Co się dzieje i po co” i punkt „Sprawdź”', () => {
  for (const s of A.INSTRUKCJA.filter((x) => x.elementy.some((e) => e.typ === 'prompt' && !e.poglad))) {
    assert.ok(s.elementy.some((e) => e.typ === 'dlaczego'), `${s.id}: brak ramki dlaczego`);
    assert.ok(s.elementy.some((e) => e.typ === 'sprawdz'), `${s.id}: brak Sprawdź`);
  }
});

test('hooki: każdy zrzut z LISTA_ZRZUTOW użyty dokładnie raz, a każde id jest unikalne', () => {
  const uzyte = elementy().filter((e) => e.typ === 'zrzut').map((e) => e.klucz).sort();
  assert.deepEqual(j(uzyte), j(A.LISTA_ZRZUTOW.map((z) => z.klucz).sort()));
  assert.equal(new Set(uzyte).size, uzyte.length);
});

test('hooki: zrzuty z tej strony nie powtarzają się na stronie głównej', () => {
  const glowna = zaladuj({ plik: PLIK_GLOWNY }).LISTA_ZRZUTOW.map((z) => z.klucz);
  for (const z of A.LISTA_ZRZUTOW) assert.ok(!glowna.includes(z.klucz), z.klucz);
});

test('hooki: skrypty hooków w promptach zapisują UTF-8 z BOM i nie używają ~ ani %USERPROFILE% w poleceniu', () => {
  for (const e of prompty().filter((p) => ['K1', 'K2', 'K3', 'K5', 'K6', 'K7', 'K11'].includes(p.id))) {
    assert.match(e.tekst, /UTF-8 z BOM/, e.id);
  }
  const k4 = prompty().find((p) => p.id === 'K4').tekst;
  assert.match(k4, /\$HOME\/\.claude\/hooks\/dzwiek\.ps1/);
});

test('hooki: K5 obejmuje narzędzia plikowe i powłoki (w tym PowerShell)', () => {
  const k5 = prompty().find((p) => p.id === 'K5').tekst;
  assert.match(k5, /Write\|Edit\|MultiEdit\|Bash\|PowerShell/);
});

test('hooki: konstruktor pytania składa kontekst i zadanie, pomija puste pola', () => {
  const pytanie = A.zlozPytanie('K1: hook na starcie (tekst)', { zrobilem: 'Wkleiłem K1.', widze: ' ' });
  assert.match(pytanie, /^\[KONTEKST\]\n.*K1: hook na starcie/);
  assert.match(pytanie, /\[CO ZROBIŁEM\]\nWkleiłem K1\./);
  assert.doesNotMatch(pytanie, /CO WIDZĘ/);
  assert.match(pytanie, /\[ZADANIE\]/);
});

test('hooki: bloki skryptu się kompilują, a HTML deklaruje UTF-8 i polski', () => {
  const html = wczytajHtml(PLIK_HOOKI);
  assert.match(html, /<meta charset="utf-8">/);
  assert.match(html, /<html lang="pl">/);
  for (const id of ['dane', 'widok', 'zrzuty']) assert.doesNotThrow(() => new vm.Script(blok(html, id, PLIK_HOOKI)), id);
});

test('hooki: strona zawiera sekcję o konfiguracji lokalnej i globalnej', () => {
  const sekcja = A.INSTRUKCJA.find((s) => s.id === 'gdzie-hooki');
  assert.ok(sekcja, 'brak sekcji gdzie-hooki');
  const tekst = sekcja.elementy.map((e) => e.html || '').join(' ');
  for (const w of ['settings.local.json', 'settings.json', 'globalnie', 'lokalnie', '$HOME']) assert.ok(tekst.includes(w), w);
});

test('główna instrukcja linkuje do ćwiczenia o hookach, a ono wraca do głównej', () => {
  const glowna = wczytajHtml(PLIK_GLOWNY);
  assert.ok(glowna.includes('href="cwiczenia-hooki.html"'));
  assert.ok(wczytajHtml(PLIK_HOOKI).includes('href="cwiczenia-pakiet-analityczny.html"'));
});

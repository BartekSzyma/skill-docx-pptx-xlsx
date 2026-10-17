// Wypisuje dokładny tekst promptu z instrukcji (jedno źródło prawdy dla budowy na żywo).
// Użycie: node tools/wypisz-prompt.mjs P2
import { readFileSync } from 'node:fs';
import vm from 'node:vm';
import { pathToFileURL, fileURLToPath } from 'node:url';

export function wypiszPrompt(html, id) {
  const m = html.match(/<script id="dane">([\s\S]*?)<\/script>/);
  if (!m) throw new Error('Brak bloku <script id="dane"> w HTML');
  const kontekst = vm.createContext({});
  vm.runInContext(`${m[1]}\n;globalThis.__dane = DANE;`, kontekst);
  const prompt = kontekst.__dane.INSTRUKCJA.flatMap((s) => s.elementy).find((e) => e.typ === 'prompt' && e.id === id);
  if (!prompt) throw new Error(`Brak promptu ${id} w instrukcji`);
  return prompt.tekst;
}

function main() {
  const html = readFileSync(fileURLToPath(new URL('../cwiczenia-pakiet-analityczny.html', import.meta.url)), 'utf8');
  process.stdout.write(wypiszPrompt(html, process.argv[2]));
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) main();

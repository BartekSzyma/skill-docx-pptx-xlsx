"""Bramka 2: niezależny model sprawdza, czy cytat naprawdę potwierdza wpis ledgera.

Użycie: python .claude/skills/pakiet-analityczny/scripts/weryfikuj_modelem.py TICKER

Bierze fakty i dane rynkowe, które przeszły bramkę 1 (TICKER/weryfikacja/bramka1.json),
i wysyła je partiami po 6 do osobnego procesu `claude -p --model sonnet` bez narzędzi.
Model dostaje tylko wpisy i pełny tekst ich stron źródłowych (z długiego pliku CSV -
ostatnie wiersze), nie zna naszej rozmowy ani plików projektu.

Wynik: TICKER/weryfikacja/bramka2.json.
"""

import json
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from sprawdz_cytaty import KATALOG_GLOWNY, plik_strony

MODEL = "sonnet"
PARTIA = 6
LIMIT_CZASU = 600  # sekund na jedną partię
WIERSZE_CSV = 40
WERDYKTY = {"potwierdza", "nie potwierdza", "niejasne"}
POLA_WPISU = ["id", "klasa", "klucz", "opis", "wartosc", "jednostka", "okres", "zrodlo", "cytat", "data_pobrania"]

INSTRUKCJA = """Jesteś niezależnym kontrolerem faktów. Sprawdzasz wpisy rejestru danych o spółce.
Każdy wpis ma cytat ze źródła. Poniżej są wpisy i pełny tekst ich źródeł.

Dla każdego wpisu sprawdź, czy cytat i tekst źródła naprawdę potwierdzają wpis:
- liczba w polu "wartosc" jest taka jak w źródle (uwaga na kolumny tabel: która liczba należy do którego roku),
- okres (rok, data) się zgadza,
- jednostka się zgadza (np. mln czy mld USD, %, sztuki),
- zakres się zgadza (cała spółka czy segment),
- opis wpisu (po polsku) zgodnie oddaje to, co mówi cytat.
Wartość zaokrąglona w opisie jako zaokrąglona jest dopuszczalna. Nie korzystaj z wiedzy spoza podanych źródeł.

Werdykt: "potwierdza", "nie potwierdza" albo "niejasne".
Odpowiedz WYŁĄCZNIE tablicą JSON, bez żadnego innego tekstu i bez bloków kodu, w formacie:
[{"id": "F-01", "werdykt": "potwierdza", "uzasadnienie": "Jedno zdanie po polsku."}]
"""


def tekst_zrodla(wpis, katalog_spolki):
    zrodlo = wpis["zrodlo"]
    if wpis["klasa"] == "fakt":
        plik = plik_strony(katalog_spolki / "zrodla" / "10k", zrodlo["strona"], zrodlo.get("plik"))
        return f"Raport 10-K, strona {zrodlo['strona']} ({plik.name})", plik.read_text(encoding="utf-8")
    plik = KATALOG_GLOWNY / zrodlo["plik"]
    tekst = plik.read_text(encoding="utf-8")
    if plik.suffix == ".csv":
        wiersze = tekst.splitlines()
        if len(wiersze) > WIERSZE_CSV + 1:
            tekst = "\n".join([wiersze[0], f"... (pominięto {len(wiersze) - WIERSZE_CSV - 1} starszych wierszy) ..."]
                              + wiersze[-WIERSZE_CSV:])
    return f"Plik {zrodlo['plik']} (pobrany {wpis.get('data_pobrania', '?')}, adres {zrodlo.get('url', '')})", tekst


def zbuduj_prompt(partia, katalog_spolki):
    zrodla = {}
    for w in partia:
        nazwa, tekst = tekst_zrodla(w, katalog_spolki)
        zrodla.setdefault(nazwa, tekst)
    wpisy = [{k: w[k] for k in POLA_WPISU if k in w} for w in partia]
    czesci = [INSTRUKCJA, "=== WPISY ===", json.dumps(wpisy, ensure_ascii=False, indent=2), "=== ŹRÓDŁA ==="]
    for nazwa, tekst in zrodla.items():
        czesci += [f"--- {nazwa} ---", tekst, f"--- koniec: {nazwa} ---"]
    czesci.append(f"Odpowiedz tablicą JSON z {len(partia)} elementami (id: {', '.join(w['id'] for w in partia)}).")
    return "\n\n".join(czesci)


def zapytaj_model(prompt):
    claude = shutil.which("claude")
    if claude is None:
        raise SystemExit("Nie znaleziono programu claude (Claude Code) w PATH.")
    polecenie = [claude, "-p", "--model", MODEL, "--tools", "", "--strict-mcp-config",
                 "--no-session-persistence", "--output-format", "text"]
    # Katalog tymczasowy jako katalog roboczy: model nie wczytuje CLAUDE.md ani plików projektu.
    with tempfile.TemporaryDirectory() as pusty:
        wynik = subprocess.run(polecenie, input=prompt, capture_output=True, text=True, encoding="utf-8",
                               errors="replace", timeout=LIMIT_CZASU, cwd=pusty)
    if wynik.returncode != 0:
        raise RuntimeError(f"claude zakończył się kodem {wynik.returncode}: {wynik.stderr.strip()[:300]}")
    return wynik.stdout


def odczytaj_json(odpowiedz):
    poczatek, koniec = odpowiedz.find("["), odpowiedz.rfind("]")
    if poczatek < 0 or koniec < poczatek:
        raise ValueError("w odpowiedzi modelu nie ma tablicy JSON")
    return json.loads(odpowiedz[poczatek:koniec + 1])


def sprawdz_partie(partia, katalog_spolki):
    prompt = zbuduj_prompt(partia, katalog_spolki)
    ostatni_blad = None
    for _ in range(2):  # jedna ponowna próba przy błędzie procesu albo nieczytelnej odpowiedzi
        try:
            odpowiedz = odczytaj_json(zapytaj_model(prompt))
            break
        except (RuntimeError, ValueError, json.JSONDecodeError, subprocess.TimeoutExpired) as e:
            ostatni_blad = e
    else:
        return [{"id": w["id"], "werdykt": "niejasne", "uzasadnienie": f"Brak odpowiedzi modelu: {ostatni_blad}"}
                for w in partia]

    po_id = {str(o.get("id")): o for o in odpowiedz if isinstance(o, dict)}
    wyniki = []
    for w in partia:
        o = po_id.get(w["id"])
        if o is None or o.get("werdykt") not in WERDYKTY:
            wyniki.append({"id": w["id"], "werdykt": "niejasne",
                           "uzasadnienie": "Model nie zwrócił poprawnego werdyktu dla tego wpisu."})
        else:
            wyniki.append({"id": w["id"], "werdykt": o["werdykt"], "uzasadnienie": str(o.get("uzasadnienie", ""))})
    return wyniki


def weryfikuj(ticker):
    katalog_spolki = KATALOG_GLOWNY / ticker
    katalog = katalog_spolki / "weryfikacja"
    bramka1 = json.loads((katalog / "bramka1.json").read_text(encoding="utf-8"))
    przeszly = {b["id"] for b in bramka1 if b["wynik"] == "ok"}
    wpisy = json.loads((katalog_spolki / "ledger.json").read_text(encoding="utf-8"))
    do_sprawdzenia = [w for w in wpisy if w["klasa"] in ("fakt", "dana_rynkowa") and w["id"] in przeszly]

    wyniki = []
    for i in range(0, len(do_sprawdzenia), PARTIA):
        partia = do_sprawdzenia[i:i + PARTIA]
        print(f"Partia {i // PARTIA + 1}: {', '.join(w['id'] for w in partia)}", flush=True)
        wyniki += sprawdz_partie(partia, katalog_spolki)

    raport = {"model": MODEL, "data": datetime.now(timezone.utc).isoformat(timespec="seconds"),
              "wyniki": wyniki}
    (katalog / "bramka2.json").write_text(json.dumps(raport, ensure_ascii=False, indent=2), encoding="utf-8")
    return wyniki


def main():
    if len(sys.argv) != 2:
        raise SystemExit("Użycie: python .claude/skills/pakiet-analityczny/scripts/weryfikuj_modelem.py TICKER")
    wyniki = weryfikuj(sys.argv[1].upper())
    zle = [w for w in wyniki if w["werdykt"] != "potwierdza"]
    for w in zle:
        print(f"{w['id']}: {w['werdykt']} - {w['uzasadnienie']}")
    print(f"Bramka 2: {len(wyniki) - len(zle)}/{len(wyniki)} wpisów potwierdzonych")
    sys.exit(1 if zle else 0)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()

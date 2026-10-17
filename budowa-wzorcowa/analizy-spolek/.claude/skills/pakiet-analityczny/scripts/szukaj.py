"""Szuka frazy w stronach raportu 10-K (bez względu na wielkość liter).

Użycie: python .claude/skills/pakiet-analityczny/scripts/szukaj.py TICKER "fraza"
"""

import json
import re
import sys
from pathlib import Path

# Wyniki trafiają do katalogu, z którego uruchomiono skrypt (katalog projektu): TICKER/...
KATALOG_GLOWNY = Path.cwd()
KONTEKST = 60


def main():
    if len(sys.argv) != 3:
        raise SystemExit('Użycie: python .claude/skills/pakiet-analityczny/scripts/szukaj.py TICKER "fraza"')
    ticker, fraza = sys.argv[1].upper(), sys.argv[2]

    katalog = KATALOG_GLOWNY / ticker / "zrodla" / "10k"
    spis = json.loads((katalog / "spis.json").read_text(encoding="utf-8"))
    wzor = re.compile(re.escape(" ".join(fraza.split())), re.IGNORECASE)

    trafienia = 0
    for wpis in spis:
        tekst = " ".join((katalog / "strony" / wpis["plik"]).read_text(encoding="utf-8").split())
        dopasowania = list(wzor.finditer(tekst))
        if not dopasowania:
            continue
        trafienia += len(dopasowania)
        numer = wpis["strona"] or f"bez numeru, plik {wpis['plik']}"
        print(f"Strona {numer} ({len(dopasowania)}x):")
        for m in dopasowania[:3]:
            poczatek = max(0, m.start() - KONTEKST)
            fragment = tekst[poczatek:m.end() + KONTEKST]
            print(f"  ...{fragment}...")
        if len(dopasowania) > 3:
            print(f"  (i jeszcze {len(dopasowania) - 3})")

    print(f"\nRazem trafień: {trafienia}")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()

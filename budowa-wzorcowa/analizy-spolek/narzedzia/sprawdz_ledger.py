"""Sprawdza ledger spółki i wypisuje tabelę wpisów.

Użycie: python narzedzia/sprawdz_ledger.py TICKER

Kontrole:
  - wymagane pola dla każdej klasy, unikalne id i klucze,
  - cytat jest dosłownym fragmentem pliku źródłowego (porównanie po scaleniu białych znaków),
  - liczba z pola wartosc występuje w cytacie (np. 200966 jako "200,966", -19193 jako "(19,193)"),
  - uzasadnienie założenia odwołuje się do istniejących id,
  - grafika: plik istnieje, projekt to id istniejącego faktu, licencja jest dozwolona.
"""

import json
import re
import sys
from collections import Counter
from pathlib import Path

KATALOG_GLOWNY = Path(__file__).resolve().parent.parent
POLA = {
    "fakt": ["id", "klasa", "klucz", "opis", "wartosc", "jednostka", "okres", "zrodlo", "cytat"],
    "dana_rynkowa": ["id", "klasa", "klucz", "opis", "wartosc", "jednostka", "okres", "zrodlo", "cytat", "data_pobrania"],
    "zalozenie": ["id", "klasa", "klucz", "opis", "wartosc", "jednostka", "okres", "uzasadnienie"],
    "grafika": ["id", "klasa", "klucz", "plik", "opis", "projekt", "autor", "licencja", "zrodlo"],
}
PREFIKS = {"fakt": "F", "dana_rynkowa": "R", "zalozenie": "Z", "grafika": "G"}
LICENCJE = re.compile(r"^(CC0|Public domain|PD\b|CC BY(-SA)? \d(\.\d)?$)", re.IGNORECASE)


def scal(tekst):
    return " ".join(tekst.split())


def zapisy_liczby(wartosc):
    a = abs(wartosc)
    if float(a).is_integer():
        a = int(a)
        return [f"{a:,}", str(a)]
    return [str(a), f"{a:,}"]


def main():
    if len(sys.argv) != 2:
        raise SystemExit("Użycie: python narzedzia/sprawdz_ledger.py TICKER")
    ticker = sys.argv[1].upper()
    wpisy = json.loads((KATALOG_GLOWNY / ticker / "ledger.json").read_text(encoding="utf-8"))

    bledy = []
    ids = Counter(w.get("id") for w in wpisy)
    klucze = Counter(w.get("klucz") for w in wpisy)
    bledy += [f"powtórzone id {i}" for i, n in ids.items() if n > 1]
    bledy += [f"powtórzony klucz {k}" for k, n in klucze.items() if n > 1]

    for w in wpisy:
        wid, klasa = w.get("id"), w.get("klasa")
        if klasa not in POLA:
            bledy.append(f"{wid}: nieznana klasa {klasa}")
            continue
        brak = [p for p in POLA[klasa] if p not in w]
        if brak:
            bledy.append(f"{wid}: brak pól {brak}")
        if not str(wid).startswith(PREFIKS[klasa] + "-"):
            bledy.append(f"{wid}: id nie pasuje do klasy {klasa}")
        if " " in w.get("klucz", " "):
            bledy.append(f"{wid}: klucz ze spacją")

        if klasa == "grafika":
            if not (KATALOG_GLOWNY / w["plik"]).exists():
                bledy.append(f"{wid}: brak pliku {w['plik']}")
            if not str(w["projekt"]).startswith("F-") or w["projekt"] not in ids:
                bledy.append(f"{wid}: projekt {w['projekt']} nie jest istniejącym faktem")
            if not LICENCJE.match(w["licencja"]):
                bledy.append(f"{wid}: niedozwolona licencja {w['licencja']}")
            if not w["zrodlo"].get("url", "").startswith("https://commons.wikimedia.org/"):
                bledy.append(f"{wid}: zrodlo.url nie wskazuje strony pliku na Commons")
            continue

        if klasa == "zalozenie":
            for odw in re.findall(r"\b[FRZ]-\d{2}\b", w.get("uzasadnienie", "")):
                if odw not in ids:
                    bledy.append(f"{wid}: odwołanie do nieistniejącego {odw}")
            continue

        plik = KATALOG_GLOWNY / w["zrodlo"]["plik"]
        if not plik.exists():
            bledy.append(f"{wid}: brak pliku {plik}")
            continue
        tekst = scal(plik.read_text(encoding="utf-8"))
        cytat = scal(w["cytat"])
        if cytat not in tekst:
            bledy.append(f"{wid}: cytat nie jest dosłownym fragmentem {w['zrodlo']['plik']}")
        wartosc = w["wartosc"]
        if isinstance(wartosc, (int, float)) and not any(z in cytat for z in zapisy_liczby(wartosc)):
            bledy.append(f"{wid}: wartości {wartosc} nie ma w cytacie")
        if isinstance(wartosc, (int, float)) and wartosc < 0 and f"({zapisy_liczby(wartosc)[0]})" not in cytat:
            bledy.append(f"{wid}: ujemna wartość {wartosc}, a w cytacie brak liczby w nawiasie")

    print(f"{'id':<5} | {'opis':<70} | {'wartość':>16} | strona")
    print("-" * 110)
    for w in wpisy:
        if w["klasa"] == "grafika":
            print(f"{w['id']:<5} | {w['opis'][:70]:<70} | {'projekt ' + w['projekt']:>16} | {w['licencja']}")
            continue
        wart = w["wartosc"]
        wart = f"{wart:,}".replace(",", " ") if isinstance(wart, (int, float)) else str(wart)
        strona = w["zrodlo"]["strona"] if "zrodlo" in w else "-"
        print(f"{w['id']:<5} | {w['opis'][:70]:<70} | {wart + ' ' + w['jednostka']:>16} | {strona}")

    liczby = Counter(w["klasa"] for w in wpisy)
    print("\nWpisów: " + ", ".join(f"{k}: {n}" for k, n in liczby.items()) + f", razem: {len(wpisy)}")
    if bledy:
        print(f"\nBŁĘDY ({len(bledy)}):")
        for b in bledy:
            print("  " + b)
        sys.exit(1)
    print("Kontrola ledgera: OK")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()

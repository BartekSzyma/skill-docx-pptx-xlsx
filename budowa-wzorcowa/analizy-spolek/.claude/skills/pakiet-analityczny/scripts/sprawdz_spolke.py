"""Sprawdza, czy spółka pasuje do pakietu: składa raport 10-K w SEC i nie jest bankiem ani ubezpieczycielem.

Użycie: python .claude/skills/pakiet-analityczny/scripts/sprawdz_spolke.py TICKER

Kod wyjścia 0 = spółka pasuje, 1 = nie pasuje (z wyjaśnieniem po polsku).
Model DCF z pakietu liczy wolne przepływy z działalności operacyjnej (zysk operacyjny, amortyzacja,
nakłady inwestycyjne). U banków i ubezpieczycieli dług i inwestycje są częścią działalności, więc
taki model daje bezsensowne wyniki; do nich stosuje się inne metody (np. model dywidend, P/BV).
"""

import sys

import requests

USER_AGENT = "pakiet-analityczny kurs.alx@example.com"
NAGLOWKI = {"User-Agent": USER_AGENT}

# Kody SIC (Standard Industrial Classification) wykluczone z modelu DCF.
WYKLUCZONE_SIC = [
    (6000, 6199, "bank albo instytucja kredytowa"),
    (6300, 6411, "ubezpieczyciel"),
]


def pobierz_json(url):
    odp = requests.get(url, headers=NAGLOWKI, timeout=60)
    odp.raise_for_status()
    return odp.json()


def sprawdz(ticker):
    """Zwraca (ok, komunikat)."""
    tickery = pobierz_json("https://www.sec.gov/files/company_tickers.json")
    wpis = next((w for w in tickery.values() if w["ticker"].upper() == ticker.upper()), None)
    if wpis is None:
        return False, (f"Ticker {ticker} nie występuje w wykazie spółek SEC. Pakiet działa tylko dla spółek "
                       "notowanych w USA, które składają raporty w SEC (sprawdź pisownię tickera).")
    cik = int(wpis["cik_str"])
    dane = pobierz_json(f"https://data.sec.gov/submissions/CIK{cik:010d}.json")
    nazwa = dane.get("name", wpis["title"])
    formularze = set(dane["filings"]["recent"]["form"])

    if "10-K" not in formularze:
        inne = sorted(formularze & {"20-F", "40-F", "10-KT"})
        powod = (f" Spółka składa zamiast niego {', '.join(inne)} (spółka zagraniczna albo zmiana roku obrotowego)."
                 if inne else "")
        return False, f"{nazwa} ({ticker}) nie złożyła raportu 10-K wśród ostatnich zgłoszeń w SEC.{powod} Pakiet wymaga 10-K."

    try:
        sic = int(dane.get("sic") or 0)
    except ValueError:
        sic = 0
    for od, do, rodzaj in WYKLUCZONE_SIC:
        if od <= sic <= do:
            return False, (f"{nazwa} ({ticker}) to {rodzaj} (kod SIC {sic}: {dane.get('sicDescription', '')}). "
                           "Model DCF z tego pakietu nie pasuje do banków i ubezpieczycieli, bo dług i inwestycje są "
                           "u nich częścią działalności operacyjnej. Pakiet kończy pracę.")
    return True, f"{nazwa} ({ticker}), CIK {cik:010d}, SIC {sic} ({dane.get('sicDescription', 'brak opisu')}): spółka pasuje do pakietu."


def main():
    if len(sys.argv) != 2:
        raise SystemExit("Użycie: python .claude/skills/pakiet-analityczny/scripts/sprawdz_spolke.py TICKER")
    ok, komunikat = sprawdz(sys.argv[1].upper())
    print(("OK: " if ok else "STOP: ") + komunikat)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()

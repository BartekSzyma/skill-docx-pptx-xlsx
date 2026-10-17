"""Pobiera dane rynkowe: kurs akcji (Yahoo Finance) i rentowność 10-letnich obligacji USA (FRED).

Użycie: python narzedzia/pobierz_rynek.py TICKER

Wynik w TICKER/zrodla/rynek/ (data pobrania w nazwie pliku i w info):
  kurs-RRRR-MM-DD.json   - pełna odpowiedź Yahoo z dopisanym polem "pobrano"
  dgs10-RRRR-MM-DD.csv   - plik CSV z FRED (seria DGS10)
  pobranie-RRRR-MM-DD.json - podsumowanie: adresy, data pobrania, ostatnie wartości
"""

import csv
import io
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import requests

USER_AGENT = "pakiet-analityczny kurs.alx@example.com"
KATALOG_GLOWNY = Path(__file__).resolve().parent.parent


def pobierz(url):
    odp = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=60)
    odp.raise_for_status()
    return odp


def main():
    if len(sys.argv) != 2:
        raise SystemExit("Użycie: python narzedzia/pobierz_rynek.py TICKER")
    ticker = sys.argv[1].upper()

    katalog = KATALOG_GLOWNY / ticker / "zrodla" / "rynek"
    katalog.mkdir(parents=True, exist_ok=True)
    teraz = datetime.now(timezone.utc)
    pobrano = teraz.isoformat(timespec="seconds")
    dzien = teraz.strftime("%Y-%m-%d")

    url_kurs = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?range=5d&interval=1d"
    kurs = pobierz(url_kurs).json()
    kurs["pobrano"] = pobrano
    kurs["adres"] = url_kurs
    (katalog / f"kurs-{dzien}.json").write_text(json.dumps(kurs, ensure_ascii=False, indent=2), encoding="utf-8")

    wynik = kurs["chart"]["result"][0]
    zamkniecia = wynik["indicators"]["quote"][0]["close"]
    daty = wynik["timestamp"]
    ostatni = max(i for i, c in enumerate(zamkniecia) if c is not None)
    data_kursu = datetime.fromtimestamp(daty[ostatni], timezone.utc).strftime("%Y-%m-%d")

    url_fred = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=DGS10"
    csv_tekst = pobierz(url_fred).text
    (katalog / f"dgs10-{dzien}.csv").write_text(csv_tekst, encoding="utf-8")

    wiersze = [w for w in csv.reader(io.StringIO(csv_tekst))][1:]
    wiersze = [w for w in wiersze if len(w) == 2 and w[1] not in ("", ".")]
    data_dgs10, dgs10 = wiersze[-1]

    podsumowanie = {
        "ticker": ticker,
        "pobrano": pobrano,
        "kurs": {
            "adres": url_kurs,
            "plik": f"kurs-{dzien}.json",
            "waluta": wynik["meta"].get("currency"),
            "data": data_kursu,
            "zamkniecie": zamkniecia[ostatni],
        },
        "dgs10": {
            "adres": url_fred,
            "plik": f"dgs10-{dzien}.csv",
            "data": data_dgs10,
            "rentownosc_proc": float(dgs10),
        },
    }
    (katalog / f"pobranie-{dzien}.json").write_text(
        json.dumps(podsumowanie, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"{ticker}: zamknięcie {zamkniecia[ostatni]:.2f} {podsumowanie['kurs']['waluta']} ({data_kursu})")
    print(f"DGS10: {dgs10}% ({data_dgs10})")
    print(f"Zapisano w {katalog}")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()

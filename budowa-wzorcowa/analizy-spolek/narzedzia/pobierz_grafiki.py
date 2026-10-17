"""Szuka i pobiera zdjęcia z Wikimedia Commons razem z autorem i licencją.

Użycie: python narzedzia/pobierz_grafiki.py TICKER "zapytanie" [--projekt F-30] [--limit 5]

Zdjęcia trafiają do TICKER/zrodla/grafiki/, a ich metadane (autor, licencja, strona pliku,
zapytanie, id projektu) do TICKER/zrodla/grafiki/kandydaci.json. Akceptowane licencje:
CC0, domena publiczna, CC BY, CC BY-SA. Pomijane: SVG, logotypy, zrzuty ekranu.
"""

import argparse
import json
import re
import sys
from datetime import date
from html import unescape
from pathlib import Path

import requests
from PIL import Image

USER_AGENT = "pakiet-analityczny kurs.alx@example.com"
NAGLOWKI = {"User-Agent": USER_AGENT}
API = "https://commons.wikimedia.org/w/api.php"
# Commons wydaje miniatury w standardowych szerokościach, dla 1200 dostajemy zwykle 1280 px.
SZEROKOSC = 1200
KATALOG_GLOWNY = Path(__file__).resolve().parent.parent

LICENCJE = [
    re.compile(r"^CC0"),
    re.compile(r"^Public domain", re.IGNORECASE),
    re.compile(r"^PD\b"),
    re.compile(r"^CC BY(-SA)? \d(\.\d)?"),
]
MIME = {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp"}
ZAKAZANE = re.compile(r"logo|screenshot|screen shot|zrzut ekranu|wordmark|icon", re.IGNORECASE)


def bez_html(tekst):
    return " ".join(unescape(re.sub(r"<[^>]+>", " ", tekst or "")).split())


def licencja_ok(nazwa):
    if re.search(r"\bNC\b|\bND\b", nazwa):
        return False
    return any(w.search(nazwa) for w in LICENCJE)


def nazwa_pliku(tytul, rozszerzenie):
    rdzen = tytul.removeprefix("File:").rsplit(".", 1)[0]
    rdzen = re.sub(r"[^A-Za-z0-9]+", "-", rdzen).strip("-").lower()[:80]
    return rdzen + rozszerzenie


def szukaj(zapytanie, limit):
    parametry = {
        "action": "query", "format": "json", "generator": "search",
        "gsrsearch": f"{zapytanie} filetype:bitmap", "gsrnamespace": 6, "gsrlimit": limit,
        "prop": "imageinfo", "iiprop": "url|mime|size|extmetadata", "iiurlwidth": SZEROKOSC,
    }
    odp = requests.get(API, params=parametry, headers=NAGLOWKI, timeout=60)
    odp.raise_for_status()
    strony = odp.json().get("query", {}).get("pages", {}).values()
    return sorted(strony, key=lambda s: s.get("index", 0))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("ticker")
    parser.add_argument("zapytanie")
    parser.add_argument("--projekt", default=None, help="id faktu z ledgera, którego dotyczy zdjęcie")
    parser.add_argument("--limit", type=int, default=5)
    arg = parser.parse_args()

    katalog = KATALOG_GLOWNY / arg.ticker.upper() / "zrodla" / "grafiki"
    katalog.mkdir(parents=True, exist_ok=True)
    plik_kandydatow = katalog / "kandydaci.json"
    kandydaci = json.loads(plik_kandydatow.read_text(encoding="utf-8")) if plik_kandydatow.exists() else []
    znane = {k["tytul"] for k in kandydaci}

    for strona in szukaj(arg.zapytanie, arg.limit):
        tytul = strona["title"]
        info = strona["imageinfo"][0]
        meta = {k: v.get("value", "") for k, v in info.get("extmetadata", {}).items()}
        licencja = bez_html(meta.get("LicenseShortName"))
        kategorie = meta.get("Categories", "")

        powod = None
        if info["mime"] not in MIME:
            powod = f"format {info['mime']}"
        elif ZAKAZANE.search(tytul) or ZAKAZANE.search(kategorie):
            powod = "logo lub zrzut ekranu"
        elif not licencja_ok(licencja):
            powod = f"licencja {licencja or 'nieznana'}"
        elif tytul in znane:
            powod = "już pobrany"
        if powod:
            print(f"pomijam: {tytul} ({powod})")
            continue

        plik = nazwa_pliku(tytul, MIME[info["mime"]])
        adres = info.get("thumburl") or info["url"]
        obraz = requests.get(adres, headers=NAGLOWKI, timeout=120)
        if obraz.status_code != 200:
            # Np. 403: Commons nie wydaje oryginałów (plików węższych niż SZEROKOSC) każdemu klientowi.
            print(f"pomijam: {tytul} (HTTP {obraz.status_code} przy pobieraniu)")
            continue
        (katalog / plik).write_bytes(obraz.content)

        kandydaci.append({
            "plik": plik,
            "tytul": tytul,
            "opis_commons": bez_html(meta.get("ImageDescription"))[:300],
            "autor": bez_html(meta.get("Artist")) or bez_html(meta.get("Credit")),
            "licencja": licencja,
            "licencja_url": meta.get("LicenseUrl", ""),
            "url_strony": info["descriptionurl"],
            "url_obrazu": adres,
            "rozmiar_px": list(Image.open(katalog / plik).size),
            "zapytanie": arg.zapytanie,
            "projekt": arg.projekt,
            "data_pobrania": date.today().isoformat(),
        })
        znane.add(tytul)
        plik_kandydatow.write_text(json.dumps(kandydaci, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"pobrano: {plik} | {licencja} | {kandydaci[-1]['autor'][:60]}")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()

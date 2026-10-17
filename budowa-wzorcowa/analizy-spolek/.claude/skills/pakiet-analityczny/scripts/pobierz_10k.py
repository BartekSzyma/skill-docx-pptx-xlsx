"""Pobiera najnowszy raport 10-K spółki z SEC EDGAR i dzieli go na strony.

Użycie: python .claude/skills/pakiet-analityczny/scripts/pobierz_10k.py TICKER

Wynik w TICKER/zrodla/10k/:
  oryginal.htm          - główny dokument HTML raportu
  info.json             - nazwa spółki, CIK, okres raportu, data złożenia, adres
  strony/strona-NNN.txt - tekst stron; NNN to numer z stopki strony
  spis.json             - numer strony i jej początek (ok. 100 znaków)
"""

import json
import re
import sys
import warnings
from pathlib import Path

import requests
from bs4 import BeautifulSoup, NavigableString, XMLParsedAsHTMLWarning

# Dokument iXBRL jest XHTML-em; parser HTML radzi sobie z nim dobrze.
warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)

USER_AGENT = "pakiet-analityczny kurs.alx@example.com"
NAGLOWKI = {"User-Agent": USER_AGENT}
# Wyniki trafiają do katalogu, z którego uruchomiono skrypt (katalog projektu): TICKER/...
KATALOG_GLOWNY = Path.cwd()

ZNACZNIK = "\n@@@PODZIAL_STRONY@@@\n"
BLOKOWE = {"div", "p", "tr", "br", "table", "li", "h1", "h2", "h3", "h4", "h5", "h6", "hr"}
# Numer w stopce: arabski ("45"), rzymski ("ii") albo z prefiksem ("F-3"). Spółki różnie drukują stopkę,
# np. "45", "Page 45", "Alphabet Inc. | 2025 Form 10-K | 45", "45 | Company"; wzory sprawdzamy po kolei.
NUMER = r"((?:[A-Z]{1,2}-)?\d{1,3}|[ivxlc]{1,6})"
WZORY_STOPKI = [
    re.compile(rf"^{NUMER}$", re.IGNORECASE),
    re.compile(rf"^{NUMER}\.$", re.IGNORECASE),  # np. "17." (Alphabet)
    re.compile(rf"^(?:page|p\.)\s*{NUMER}(?:\s+of\s+\d+)?$", re.IGNORECASE),
    re.compile(rf"\|\s*{NUMER}$", re.IGNORECASE),
    re.compile(rf"^{NUMER}\s*\|", re.IGNORECASE),
]
PROG_OSTRZEZENIA = 0.8  # jeśli numer ma mniej stron, numeracja wymaga sprawdzenia


def pobierz(url):
    odp = requests.get(url, headers=NAGLOWKI, timeout=60)
    odp.raise_for_status()
    return odp


def znajdz_cik(ticker):
    dane = pobierz("https://www.sec.gov/files/company_tickers.json").json()
    for wpis in dane.values():
        if wpis["ticker"].upper() == ticker.upper():
            return int(wpis["cik_str"]), wpis["title"]
    raise SystemExit(f"Nie znaleziono tickera {ticker} w SEC.")


def znajdz_10k(cik):
    url = f"https://data.sec.gov/submissions/CIK{cik:010d}.json"
    dane = pobierz(url).json()
    ostatnie = dane["filings"]["recent"]
    for i, formularz in enumerate(ostatnie["form"]):
        if formularz == "10-K":
            numer = ostatnie["accessionNumber"][i]
            dokument = ostatnie["primaryDocument"][i]
            adres = (
                f"https://www.sec.gov/Archives/edgar/data/{cik}/"
                f"{numer.replace('-', '')}/{dokument}"
            )
            return {
                "nazwa_spolki": dane["name"],
                "cik": f"{cik:010d}",
                "formularz": formularz,
                "okres_raportu": ostatnie["reportDate"][i],
                "data_zlozenia": ostatnie["filingDate"][i],
                "numer_zgloszenia": numer,
                "adres_dokumentu": adres,
            }
    raise SystemExit("Nie znaleziono raportu 10-K wśród ostatnich zgłoszeń.")


def styl(tag):
    return (tag.get("style") or "").replace(" ", "").lower()


def podziel_na_strony(html):
    soup = BeautifulSoup(html, "lxml")

    # Ukryte elementy (np. nagłówek ix:header z danymi XBRL) nie są częścią strony.
    for tag in soup.find_all(style=True):
        if "display:none" in styl(tag):
            tag.decompose()

    for tag in soup.find_all(style=True):
        s = styl(tag)
        if "page-break-before:always" in s or "break-before:page" in s:
            tag.insert_before(NavigableString(ZNACZNIK))
        if "page-break-after:always" in s or "break-after:page" in s:
            tag.insert_after(NavigableString(ZNACZNIK))

    for tag in soup.find_all(BLOKOWE):
        tag.insert_after(NavigableString("\n"))
    for tag in soup.find_all(["td", "th"]):
        tag.insert_after(NavigableString(" "))

    tekst = (soup.body or soup).get_text("")
    strony = []
    for kawalek in tekst.split(ZNACZNIK.strip()):
        linie = []
        for linia in kawalek.replace("\xa0", " ").splitlines():
            linia = re.sub(r"[ \t]+", " ", linia).strip()
            if linia:
                linie.append(linia)
        if linie:
            strony.append("\n".join(linie))
    return strony


def numer_ze_stopki(tekst):
    linie = tekst.splitlines()
    # Numer jest zwykle w ostatniej linii; czasem po nim stoi jeszcze krótki dopisek.
    for linia in reversed(linie[-3:]):
        for wzor in WZORY_STOPKI:
            m = wzor.search(linia.strip())
            if m:
                return m.group(1)
    return None


def nazwa_pliku(numer, indeks):
    if numer is None:
        # Strona bez numeru w stopce (np. okładka) - kolejny numer w dokumencie.
        return f"strona-bez-numeru-{indeks:03d}.txt"
    if numer.isdigit():
        return f"strona-{int(numer):03d}.txt"
    return f"strona-{numer}.txt"


def main():
    if len(sys.argv) != 2:
        raise SystemExit("Użycie: python .claude/skills/pakiet-analityczny/scripts/pobierz_10k.py TICKER")
    ticker = sys.argv[1].upper()

    cik, _ = znajdz_cik(ticker)
    info = znajdz_10k(cik)
    info["ticker"] = ticker

    katalog = KATALOG_GLOWNY / ticker / "zrodla" / "10k"
    katalog_stron = katalog / "strony"
    katalog_stron.mkdir(parents=True, exist_ok=True)
    for stary in katalog_stron.glob("*.txt"):
        stary.unlink()

    odp = pobierz(info["adres_dokumentu"])
    (katalog / "oryginal.htm").write_bytes(odp.content)
    html = odp.content.decode("utf-8", errors="replace")

    strony = podziel_na_strony(html)
    spis = []
    uzyte = set()
    for indeks, tekst in enumerate(strony, start=1):
        numer = numer_ze_stopki(tekst)
        plik = nazwa_pliku(numer, indeks)
        if plik in uzyte:
            plik = plik.replace(".txt", f"-{indeks:03d}.txt")
        uzyte.add(plik)
        (katalog_stron / plik).write_text(tekst, encoding="utf-8")
        poczatek = " ".join(tekst.split())[:100]
        spis.append({"strona": numer, "kolejnosc": indeks, "plik": plik, "poczatek": poczatek})

    info["liczba_stron"] = len(strony)
    info["liczba_stron_z_numerem"] = sum(1 for s in spis if s["strona"] is not None)
    (katalog / "info.json").write_text(json.dumps(info, ensure_ascii=False, indent=2), encoding="utf-8")
    (katalog / "spis.json").write_text(json.dumps(spis, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"{info['nazwa_spolki']} (CIK {info['cik']}), 10-K za okres do {info['okres_raportu']}, "
          f"złożony {info['data_zlozenia']}")
    print(f"Stron: {len(strony)} (z numerem w stopce: {info['liczba_stron_z_numerem']})")
    if info["liczba_stron_z_numerem"] < PROG_OSTRZEZENIA * len(strony):
        print("UWAGA: numer w stopce znaleziono na mniej niż 80% stron. Obejrzyj końcówki kilku plików w "
              "strony/ i w razie potrzeby dopisz wzór stopki w WZORY_STOPKI. Pliki bez numeru mają nazwę "
              "strona-bez-numeru-NNN.txt (NNN = kolejność w dokumencie).")
    print(f"Zapisano w {katalog}")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()

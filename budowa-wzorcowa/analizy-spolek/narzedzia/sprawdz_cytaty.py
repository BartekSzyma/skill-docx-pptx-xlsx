"""Bramka 1: deterministyczna kontrola ledgera (bez AI).

Użycie: python narzedzia/sprawdz_cytaty.py TICKER

Kontrole:
  - fakt: cytat występuje na podanej stronie raportu (po ujednoliceniu spacji, cudzysłowów
    i myślników), a wartość wpisu występuje w cytacie (także z separatorem tysięcy;
    liczba ujemna jako "(1,234)" albo "-1,234"; liczba dodatnia nie może stać w nawiasie),
  - dana_rynkowa: cytat występuje w zapisanym pliku źródłowym,
  - grafika: plik istnieje, autor, licencja i adres są wypełnione,
  - zalozenie: ma uzasadnienie (a odwołania do id w uzasadnieniu istnieją).

Wynik: TICKER/weryfikacja/bramka1.json - lista {id, wynik: "ok"|"błąd", powod}.
"""

import json
import re
import sys
from pathlib import Path

KATALOG_GLOWNY = Path(__file__).resolve().parent.parent

ZAMIANY = {
    " ": " ", " ": " ", " ": " ",
    "‘": "'", "’": "'", "‚": "'", "′": "'",
    "“": '"', "”": '"', "„": '"', "″": '"',
    "‐": "-", "‑": "-", "‒": "-", "–": "-", "—": "-", "−": "-",
}


def ujednolic(tekst):
    for znak, zamiennik in ZAMIANY.items():
        tekst = tekst.replace(znak, zamiennik)
    return " ".join(tekst.split())


def wzory_liczby(wartosc):
    """Wyrażenia regularne, które znajdują liczbę w tekście jako osobny zapis (nie fragment innej liczby)."""
    a = abs(wartosc)
    if float(a).is_integer():
        a = int(a)
        zapisy = {f"{a:,}", str(a)}
    else:
        zapisy = {repr(a), f"{a:,}"}
        # 5.1 może być zapisane jako 5.10
        zapisy |= {z + "0" for z in list(zapisy)}
    granica_l, granica_p = r"(?<![\d.,])", r"(?![\d]|[.,]\d)"
    wzory = []
    for z in zapisy:
        z = re.escape(z)
        if wartosc < 0:
            wzory.append(re.compile(rf"\(\s*\$?\s*{z}\s*\)"))
            wzory.append(re.compile(rf"(?<!\d)-\s*\$?\s*{granica_l}{z}{granica_p}"))
        else:
            # Liczba dodatnia nie może stać w nawiasie ani po minusie (nawias w raporcie oznacza wartość ujemną).
            # Dywiz po cyfrze to zakres ("13-16%"), a nie minus.
            wzory.append(re.compile(rf"(?<!\()(?<!\(\$)(?<!\(\$ )(?<![^\d]-)(?<!^-){granica_l}{z}{granica_p}(?!\s*\))"))
    return wzory


def plik_strony(katalog_10k, strona):
    """Plik z tekstem strony o danym numerze ze stopki (okładka nie ma numeru)."""
    spis = json.loads((katalog_10k / "spis.json").read_text(encoding="utf-8"))
    if isinstance(strona, int):
        trafienia = [s for s in spis if s["strona"] == str(strona)]
    elif isinstance(strona, str) and strona.startswith("okładka"):
        trafienia = [s for s in spis if s["strona"] is None and s["kolejnosc"] == 1]
    else:
        return None
    return katalog_10k / "strony" / trafienia[0]["plik"] if trafienia else None


def sprawdz_wpis(w, ids, katalog_spolki):
    klasa = w.get("klasa")
    if klasa == "zalozenie":
        if not str(w.get("uzasadnienie", "")).strip():
            return "brak uzasadnienia"
        brakujace = [i for i in re.findall(r"\b[FRZG]-\d{2}\b", w["uzasadnienie"]) if i not in ids]
        if brakujace:
            return f"uzasadnienie odwołuje się do nieistniejących wpisów: {', '.join(brakujace)}"
        return None

    if klasa == "grafika":
        if not (KATALOG_GLOWNY / str(w.get("plik", ""))).is_file():
            return f"brak pliku {w.get('plik')}"
        puste = [p for p in ("autor", "licencja") if not str(w.get(p, "")).strip()]
        if not str(w.get("zrodlo", {}).get("url", "")).strip():
            puste.append("zrodlo.url")
        return f"puste pola: {', '.join(puste)}" if puste else None

    if klasa not in ("fakt", "dana_rynkowa"):
        return f"nieznana klasa {klasa}"

    zrodlo, cytat = w.get("zrodlo", {}), str(w.get("cytat", ""))
    if not cytat.strip():
        return "brak cytatu"

    if klasa == "fakt":
        plik = plik_strony(katalog_spolki / "zrodla" / "10k", zrodlo.get("strona"))
        if plik is None:
            return f"nie ma strony {zrodlo.get('strona')!r} w spisie raportu"
        if zrodlo.get("plik") and Path(zrodlo["plik"]).name != plik.name:
            return f"pole zrodlo.plik ({zrodlo['plik']}) nie odpowiada stronie {zrodlo.get('strona')} ({plik.name})"
        gdzie = f"na stronie {zrodlo.get('strona')}"
    else:
        plik = KATALOG_GLOWNY / str(zrodlo.get("plik", ""))
        if not plik.is_file():
            return f"brak pliku źródłowego {zrodlo.get('plik')}"
        gdzie = f"w pliku {zrodlo.get('plik')}"

    if ujednolic(cytat) not in ujednolic(plik.read_text(encoding="utf-8")):
        return f"cytat nie występuje {gdzie}"

    wartosc = w.get("wartosc")
    if klasa == "fakt" and isinstance(wartosc, (int, float)) and not isinstance(wartosc, bool):
        if not any(wz.search(ujednolic(cytat)) for wz in wzory_liczby(wartosc)):
            return f"wartość {wartosc} nie występuje w cytacie"
    return None


def sprawdz(ticker):
    katalog_spolki = KATALOG_GLOWNY / ticker
    wpisy = json.loads((katalog_spolki / "ledger.json").read_text(encoding="utf-8"))
    ids = {w.get("id") for w in wpisy}
    wyniki = []
    for w in wpisy:
        powod = sprawdz_wpis(w, ids, katalog_spolki)
        wyniki.append({"id": w.get("id"), "klasa": w.get("klasa"),
                       "wynik": "ok" if powod is None else "błąd", "powod": powod or ""})
    duplikaty = sorted({w["id"] for w in wpisy if [x["id"] for x in wpisy].count(w["id"]) > 1})
    for wynik in wyniki:
        if wynik["id"] in duplikaty:
            wynik.update(wynik="błąd", powod="powtórzone id")

    katalog = katalog_spolki / "weryfikacja"
    katalog.mkdir(exist_ok=True)
    (katalog / "bramka1.json").write_text(json.dumps(wyniki, ensure_ascii=False, indent=2), encoding="utf-8")
    return wyniki


def main():
    if len(sys.argv) != 2:
        raise SystemExit("Użycie: python narzedzia/sprawdz_cytaty.py TICKER")
    wyniki = sprawdz(sys.argv[1].upper())
    bledy = [w for w in wyniki if w["wynik"] != "ok"]
    for b in bledy:
        print(f"{b['id']}: {b['powod']}")
    print(f"Bramka 1: {len(wyniki) - len(bledy)}/{len(wyniki)} wpisów ok")
    sys.exit(1 if bledy else 0)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()

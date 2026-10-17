"""Wspólne formatowanie liczb (zapis polski) i wypełnianie pól {ID} w tekstach z tresc.json."""

import re
import sys

NBSP = " "  # twarda spacja: liczba nie rozdziela się z jednostką ani na tysiącach

JEDNOSTKI = {"mln USD": "mln USD", "mld USD": "mld USD", "%": "%", "szt.": "", "mln szt.": "mln", "mld osób": "mld"}

# Pole w tekście: {F-07}, {F-09|abs}, {Z-01|bez_jedn}, {wycena.roznica_proc|1}, {F-28|2|bez_jedn}
POLE = re.compile(r"\{([FRZG]-\d{2}|wycena\.[a-z0-9_]+)((?:\|[a-z0-9_]+)*)\}")


def liczba(v, miejsca=0):
    """Spacja (twarda) tysięcy, przecinek dziesiętny, minus jako dywiz."""
    tekst = f"{abs(v):,.{miejsca}f}".replace(",", NBSP).replace(".", ",")
    return ("-" if round(v, miejsca) < 0 else "") + tekst


def wartosc_z_jedn(w, miejsca=None):
    """Wartość wpisu ledgera z jednostką, np. '60 458 mln USD', '41%'."""
    v = w["wartosc"]
    if miejsca is None:
        miejsca = 0 if float(v).is_integer() else 2
    j = JEDNOSTKI.get(w["jednostka"], w["jednostka"])
    return f"{liczba(v, miejsca)}{'' if j == '%' else NBSP}{j}".rstrip(NBSP)


def wypelnij(tekst, po_id, wycena):
    """Zamienia pola {ID|opcje} na wartości. Zwraca (tekst, lista użytych id).

    Opcje: abs (bez znaku, np. nakłady zapisane jako wypływ), bez_jedn (sama liczba),
    cyfra (liczba miejsc po przecinku). Wartości z wycena.json nie mają jednostki - dopisz ją w tekście.
    Wpis tekstowy (np. ryzyko) wstawia się jako tekst.
    """
    uzyte = []

    def zamien(m):
        ident, opcje = m.group(1), [o for o in m.group(2).split("|") if o]
        miejsca = next((int(o) for o in opcje if o.isdigit()), None)
        if ident.startswith("wycena."):
            klucz = ident.removeprefix("wycena.")
            if klucz not in wycena or not isinstance(wycena[klucz], (int, float)):
                sys.exit(f"STOP: w wycena.json nie ma liczby '{klucz}' (pole {m.group(0)}).")
            v = abs(wycena[klucz]) if "abs" in opcje else wycena[klucz]
            uzyte.append("wycena")
            return liczba(v, miejsca if miejsca is not None else (0 if float(v).is_integer() else 2))
        if ident not in po_id:
            sys.exit(f"STOP: pole {m.group(0)} odwołuje się do wpisu, którego nie ma w ledgerze.")
        w = dict(po_id[ident])
        uzyte.append(ident)
        if not isinstance(w.get("wartosc"), (int, float)):
            return str(w.get("wartosc"))
        if "abs" in opcje:
            w["wartosc"] = abs(w["wartosc"])
        if "bez_jedn" in opcje:
            v = w["wartosc"]
            return liczba(v, miejsca if miejsca is not None else (0 if float(v).is_integer() else 2))
        return wartosc_z_jedn(w, miejsca)

    wynik = POLE.sub(zamien, tekst)
    if "{" in wynik or "}" in wynik:
        sys.exit(f"STOP: niepoprawne pole w tekście: {tekst!r}")
    return wynik, list(dict.fromkeys(uzyte))

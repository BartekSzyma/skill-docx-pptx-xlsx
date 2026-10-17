"""Wspólne formatowanie liczb w dokumentach dla ludzi (zapis polski)."""

NBSP = " "  # twarda spacja: liczba nie rozdziela się z jednostką ani na tysiącach

JEDNOSTKI = {"mln USD": "mln USD", "mld USD": "mld USD", "%": "%", "szt.": "", "mld osób": "mld"}


def liczba(v, miejsca=0):
    """Spacja (twarda) tysięcy, przecinek dziesiętny, minus jako dywiz."""
    tekst = f"{abs(v):,.{miejsca}f}".replace(",", NBSP).replace(".", ",")
    return ("-" if v < 0 else "") + tekst


def wartosc_z_jedn(w, miejsca=None):
    """Wartość wpisu ledgera z jednostką, np. '60 458 mln USD', '41%'."""
    v = w["wartosc"]
    if miejsca is None:
        miejsca = 0 if float(v).is_integer() else 2
    j = JEDNOSTKI.get(w["jednostka"], w["jednostka"])
    return f"{liczba(v, miejsca)}{'' if j == '%' else NBSP}{j}".rstrip(NBSP)

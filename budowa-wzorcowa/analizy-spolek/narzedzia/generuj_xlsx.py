"""Model DCF spółki w Excelu, zbudowany wyłącznie z ledgera.

Użycie: python narzedzia/generuj_xlsx.py TICKER

Kroki:
  1. sprawdza weryfikację ledgera (bramka.wymagaj_weryfikacji),
  2. zapisuje TICKER/wyniki/TICKER_DCF.xlsx: dane wejściowe z ledgera (niebieska czcionka,
     id wpisu obok, cytat w komentarzu), cały model liczony formułami Excela,
  3. przelicza plik w LibreOffice (bez okna) i sprawdza, że żadna komórka nie ma błędu,
  4. zapisuje wynik wyceny w TICKER/wyniki/wycena.json,
  5. robi podgląd arkuszy do PNG w TICKER/wyniki/podglad/.

W skrypcie nie ma żadnych liczb o spółce. Stałe poniżej to parametry budowy modelu
(kroki tabeli wrażliwości, próg istotności długu), opisane w arkuszu.
"""

import json
import shutil
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from openpyxl import Workbook, load_workbook
from openpyxl.chart import BarChart, LineChart, Reference
from openpyxl.chart.label import DataLabelList
from openpyxl.comments import Comment
from openpyxl.formatting.rule import ColorScaleRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

from bramka import KATALOG_GLOWNY, wymagaj_weryfikacji
from libreoffice import konwertuj, podglad_png

# Parametry modelu (nie są danymi o spółce)
KROK_WACC = 0.01          # krok WACC w tabeli wrażliwości
KROK_G = 0.005            # krok wzrostu rezydualnego w tabeli wrażliwości
PROG_DLUGU = 0.10         # udział długu w finansowaniu, powyżej którego dług trzeba ująć w WACC
LATA_HIST = ["2023", "2024", "2025"]
LATA_PROG = ["2026", "2027", "2028", "2029", "2030"]
BLEDY_EXCELA = ("#REF!", "#DIV/0!", "#VALUE!", "#NAME?", "#N/A", "#NUM!", "#NULL!", "Err:")

FONT = "Arial"
NIEBIESKI = Font(name=FONT, color="0000FF")
ZIELONY = Font(name=FONT, color="008000")
CZARNY = Font(name=FONT)
POGRUB = Font(name=FONT, bold=True)
SZARY = Font(name=FONT, color="808080", size=9)
TYTUL = Font(name=FONT, bold=True, size=14)
NAGLOWEK = Font(name=FONT, bold=True, color="FFFFFF")
TLO_NAGL = PatternFill("solid", fgColor="1F3864")
TLO_KLUCZ = PatternFill("solid", fgColor="FFFF00")
TLO_WYNIK = PatternFill("solid", fgColor="E2EFDA")
CIENKA = Side(style="thin", color="BFBFBF")
RAMKA = Border(top=CIENKA, bottom=CIENKA, left=CIENKA, right=CIENKA)

F_MLN = '#,##0;(#,##0);"-"'
F_PROC = '0.0%;(0.0%);"-"'
F_USD = '$#,##0.00;($#,##0.00);"-"'
F_SZT = '#,##0'
F_ULAM = '0.000'


# ---------------------------------------------------------------- ledger


class Ledger:
    def __init__(self, ticker):
        self.ticker = ticker
        self.wpisy = json.loads((KATALOG_GLOWNY / ticker / "ledger.json").read_text(encoding="utf-8"))
        self.po_kluczu = {w["klucz"]: w for w in self.wpisy}

    def __getitem__(self, klucz):
        if klucz not in self.po_kluczu:
            sys.exit(f"STOP: w ledgerze {self.ticker} brakuje wpisu o kluczu '{klucz}'. Dodaj go i zweryfikuj ledger.")
        return self.po_kluczu[klucz]


def komentarz(w):
    if w["klasa"] == "zalozenie":
        tekst = f"{w['id']} (założenie)\n{w['opis']}\n\nUzasadnienie: {w['uzasadnienie']}"
    else:
        zr = w["zrodlo"]
        gdzie = f"strona {zr['strona']}" if w["klasa"] == "fakt" else f"plik {zr.get('plik')}, pobrano {w.get('data_pobrania')}"
        tekst = f"{w['id']} - {zr['dokument']}, {gdzie}\n\nCytat: \"{w['cytat']}\""
        if w["jednostka"] == "%":
            tekst += f"\n\nW ledgerze: {w['wartosc']} % (w arkuszu jako ułamek)."
    k = Comment(tekst, "ledger")
    k.width, k.height = 420, min(60 + len(tekst) // 2, 420)
    return k


def wartosc_do_arkusza(w):
    """Wartość z ledgera w jednostce arkusza: procenty jako ułamki, reszta bez zmian."""
    v = w["wartosc"]
    return v / 100 if w["jednostka"] == "%" else v


def wejscie(ws, adres, w, fmt):
    """Komórka danych wejściowych: wartość z ledgera, niebieska czcionka, komentarz ze źródłem."""
    c = ws[adres]
    c.value = wartosc_do_arkusza(w)
    c.font = NIEBIESKI
    c.number_format = fmt
    c.comment = komentarz(w)
    c.border = RAMKA
    return c


def formula(ws, adres, tekst, fmt=None, font=CZARNY, fill=None):
    c = ws[adres]
    c.value = tekst
    c.font = font
    if fmt:
        c.number_format = fmt
    if fill:
        c.fill = fill
    c.border = RAMKA
    return c


def etykieta(ws, adres, tekst, font=CZARNY):
    ws[adres] = tekst
    ws[adres].font = font
    return ws[adres]


def naglowki(ws, wiersz, teksty, kol=1):
    for i, t in enumerate(teksty):
        c = ws.cell(row=wiersz, column=kol + i, value=t)
        c.font, c.fill = NAGLOWEK, TLO_NAGL
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)


def id_obok(ws, adres, w):
    ws[adres] = w["id"]
    ws[adres].font = SZARY
    ws[adres].alignment = Alignment(horizontal="center")


def linie(tekst, szerokosc):
    """Przybliżona liczba linii zawiniętego tekstu w kolumnie o danej szerokości."""
    return max(1, -(-len(str(tekst)) // max(1, int(szerokosc * 1.05))))


def etykiety_danych():
    d = DataLabelList()
    d.showVal = True
    d.showSerName = d.showCatName = d.showLegendKey = d.showPercent = False
    d.numFmt = '#,##0'
    return d


def strona_wydruku(ws, poziomo=True):
    ws.page_setup.orientation = "landscape" if poziomo else "portrait"
    ws.page_setup.paperSize = ws.PAPERSIZE_A4
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 0
    ws.sheet_properties.pageSetUpPr.fitToPage = True
    ws.page_margins.left = ws.page_margins.right = 0.4
    ws.page_margins.top = ws.page_margins.bottom = 0.5


# ---------------------------------------------------------------- arkusze


def arkusz_dane(wb, L, A):
    ws = wb.create_sheet("Dane historyczne")
    etykieta(ws, "A1", f"{L.ticker} - dane historyczne z raportu 10-K (mln USD, jeśli nie podano inaczej)", TYTUL)
    etykieta(ws, "A2", "Niebieskie liczby pochodzą z ledgera; obok id wpisu, w komentarzu komórki cytat i strona źródła.", SZARY)

    naglowki(ws, 4, ["Pozycja"] + LATA_HIST + [f"id {r}" for r in LATA_HIST])
    for wiersz, (nazwa, prefiks) in enumerate([("Przychody", "revenue"), ("Zysk operacyjny", "operating_income")], start=5):
        etykieta(ws, f"A{wiersz}", nazwa)
        for i, rok in enumerate(LATA_HIST):
            w = L[f"{prefiks}_{rok}"]
            wejscie(ws, f"{get_column_letter(2 + i)}{wiersz}", w, F_MLN)
            id_obok(ws, f"{get_column_letter(5 + i)}{wiersz}", w)
    etykieta(ws, "A7", "Marża operacyjna")
    for i in range(3):
        k = get_column_letter(2 + i)
        formula(ws, f"{k}7", f"=IF({k}5=0,0,{k}6/{k}5)", F_PROC)
    etykieta(ws, "A8", "Wzrost przychodów r/r")
    for i in range(1, 3):
        k, kp = get_column_letter(2 + i), get_column_letter(1 + i)
        formula(ws, f"{k}8", f"=IF({kp}5=0,0,{k}5/{kp}5-1)", F_PROC)
    A["rev_2025"] = "'Dane historyczne'!$D$5"
    A["hist_rev"] = ("'Dane historyczne'", "B5", "D5")
    A["hist_marza"] = ("'Dane historyczne'", "B7", "D7")

    naglowki(ws, 10, ["Pozostałe fakty", "Wartość", "Jednostka", "Okres", "id"])
    pozycje = [
        ("net_income_2025", F_MLN), ("depreciation_amortization_2025", F_MLN), ("capex_2025", F_MLN),
        ("income_before_tax_2025", F_MLN), ("income_tax_2025", F_MLN),
        ("cash_and_equivalents_2025", F_MLN), ("marketable_securities_2025", F_MLN),
        ("long_term_debt_2025", F_MLN), ("ppe_net_2025", F_MLN), ("ppe_net_2024", F_MLN),
        ("foa_revenue_2025", F_MLN), ("foa_operating_income_2025", F_MLN),
        ("rl_revenue_2025", F_MLN), ("rl_operating_income_2025", F_MLN),
        ("shares_class_a", F_SZT), ("shares_class_b", F_SZT),
        ("effective_tax_rate_2025", F_PROC), ("effective_tax_rate_guidance_2026_low", F_PROC),
        ("effective_tax_rate_guidance_2026_high", F_PROC),
        ("capex_guidance_2026_low", '#,##0'), ("capex_guidance_2026_high", '#,##0'),
        ("cash_and_marketable_securities_2025", '#,##0.00'),
    ]
    wiersz = 11
    for klucz, fmt in pozycje:
        w = L[klucz]
        etykieta(ws, f"A{wiersz}", w["opis"])
        wejscie(ws, f"B{wiersz}", w, fmt)
        etykieta(ws, f"C{wiersz}", "ułamek (%)" if w["jednostka"] == "%" else w["jednostka"])
        etykieta(ws, f"D{wiersz}", w["okres"])
        id_obok(ws, f"E{wiersz}", w)
        A[klucz] = f"'Dane historyczne'!$B${wiersz}"
        wiersz += 1

    wiersz += 1
    naglowki(ws, wiersz, ["Wielkości wyliczone", "Wartość", "Jednostka", "Okres", "Formuła"])
    wyliczone = [
        ("Gotówka i papiery wartościowe", f"={A['cash_and_equivalents_2025']}+{A['marketable_securities_2025']}",
         F_MLN, "mln USD", "gotowka", "F-12 + F-13"),
        ("Liczba akcji wszystkich klas", f"={A['shares_class_a']}+{A['shares_class_b']}", F_SZT, "szt.", "akcje", "F-22 + F-23"),
        ("Liczba akcji wszystkich klas", f"=({A['shares_class_a']}+{A['shares_class_b']})/10^6", '#,##0.0', "mln szt.",
         "akcje_mln", "(F-22 + F-23) / 1 mln"),
        ("Nakłady inwestycyjne / przychody", f"=-{A['capex_2025']}/{A['rev_2025']}", F_PROC, "%", "capex_proc", "-F-09 / F-01"),
        ("Amortyzacja / przychody", f"={A['depreciation_amortization_2025']}/{A['rev_2025']}", F_PROC, "%", "da_proc", "F-08 / F-01"),
        ("Efektywna stopa podatkowa (wyliczona)", f"={A['income_tax_2025']}/{A['income_before_tax_2025']}", F_PROC, "%",
         "etr", "F-11 / F-10"),
    ]
    for opis, f, fmt, jedn, nazwa, skad in wyliczone:
        wiersz += 1
        etykieta(ws, f"A{wiersz}", opis)
        formula(ws, f"B{wiersz}", f, fmt)
        etykieta(ws, f"C{wiersz}", jedn)
        etykieta(ws, f"D{wiersz}", "2025-12-31" if nazwa in ("gotowka",) else ("2026-01-23" if "akcje" in nazwa else "2025"))
        etykieta(ws, f"E{wiersz}", skad, SZARY)
        A[nazwa] = f"'Dane historyczne'!$B${wiersz}"

    ws.column_dimensions["A"].width = 100
    ws.column_dimensions["B"].width = 17
    for k in "CDEFG":
        ws.column_dimensions[k].width = 14
    ws.freeze_panes = "B5"
    strona_wydruku(ws)


def arkusz_zalozenia(wb, L, A):
    ws = wb.create_sheet("Założenia")
    etykieta(ws, "A1", f"{L.ticker} - założenia modelu DCF", TYTUL)
    etykieta(ws, "A2", "Niebieskie komórki to założenia z ledgera (Z-..) i dane rynkowe (R-..). Zmiana wartości przelicza cały model. "
             "Uzasadnienie w komentarzu komórki i w tabeli poniżej.", SZARY)

    naglowki(ws, 4, ["Prognoza"] + LATA_PROG + ["Po 2030"])
    wiersze = [("Wzrost przychodów r/r", "revenue_growth_{}", None, "wzrost"),
               ("Marża operacyjna", "operating_margin_{}", "operating_margin_terminal", "marza"),
               ("Nakłady inwestycyjne / przychody", "capex_pct_revenue_{}", "capex_pct_revenue_terminal", "capex"),
               ("Amortyzacja / przychody", "da_pct_revenue_{}", "da_pct_revenue_terminal", "da")]
    wiersz = 5
    for opis, wzor, rezyd, nazwa in wiersze:
        etykieta(ws, f"A{wiersz}", opis)
        etykieta(ws, f"A{wiersz + 1}", "   id wpisu", SZARY)
        for i, rok in enumerate(LATA_PROG):
            k = get_column_letter(2 + i)
            w = L[wzor.format(rok)]
            wejscie(ws, f"{k}{wiersz}", w, F_PROC).fill = TLO_KLUCZ
            id_obok(ws, f"{k}{wiersz + 1}", w)
        if rezyd:
            w = L[rezyd]
            wejscie(ws, f"G{wiersz}", w, F_PROC).fill = TLO_KLUCZ
            id_obok(ws, f"G{wiersz + 1}", w)
        A[nazwa] = (wiersz, rezyd is not None)
        wiersz += 2

    wiersz += 1
    naglowki(ws, wiersz, ["Pozostałe założenia i dane rynkowe", "Wartość", "id", "Uwagi"])
    pojedyncze = [("tax_rate", F_PROC, "podatek"), ("beta", '0.00', "beta"), ("equity_risk_premium", F_PROC, "erp"),
                  ("terminal_growth", F_PROC, "g"), ("us_treasury_10y_yield", '0.00%', "rf"), ("share_price", F_USD, "kurs")]
    for klucz, fmt, nazwa in pojedyncze:
        wiersz += 1
        w = L[klucz]
        etykieta(ws, f"A{wiersz}", w["opis"])
        c = wejscie(ws, f"B{wiersz}", w, fmt)
        if w["klasa"] == "zalozenie":
            c.fill = TLO_KLUCZ
        id_obok(ws, f"C{wiersz}", w)
        uwaga = f"stan na {w['okres']}, pobrano {w.get('data_pobrania')}" if w["klasa"] == "dana_rynkowa" else "założenie"
        etykieta(ws, f"D{wiersz}", uwaga, SZARY)
        A[nazwa] = f"'Założenia'!$B${wiersz}"

    wiersz += 2
    naglowki(ws, wiersz, ["Koszt kapitału (WACC)", "Wartość", "", "Formuła"])
    wacc_wiersze = [
        ("Koszt kapitału własnego (CAPM)", f"={A['rf']}+{A['beta']}*{A['erp']}", F_PROC, "ke", "stopa wolna od ryzyka + beta × premia za ryzyko"),
        ("Dług długoterminowy (mln USD)", f"={A['long_term_debt_2025']}", F_MLN, "dlug", "F-15"),
        ("Kapitalizacja rynkowa (mln USD)", f"={A['kurs']}*{A['akcje_mln']}", F_MLN, "kapitalizacja", "kurs × liczba akcji"),
        ("Udział długu w finansowaniu D/(D+E)", None, F_PROC, "udzial_dlugu", "dług / (dług + kapitalizacja)"),
        ("Próg istotności długu (parametr modelu)", PROG_DLUGU, F_PROC, "prog", "powyżej progu dług trzeba ująć w WACC"),
        ("Czy dług jest istotny?", None, None, "flaga", ""),
        ("WACC", None, F_PROC, "wacc", "równy kosztowi kapitału własnego, bo dług jest poniżej progu istotności"),
    ]
    for opis, f, fmt, nazwa, skad in wacc_wiersze:
        wiersz += 1
        A[nazwa] = f"'Założenia'!$B${wiersz}"
        etykieta(ws, f"A{wiersz}", opis, POGRUB if nazwa == "wacc" else CZARNY)
        if nazwa == "udzial_dlugu":
            f = f"={A['dlug']}/({A['dlug']}+{A['kapitalizacja']})"
        elif nazwa == "flaga":
            f = (f'=IF({A["udzial_dlugu"]}>{A["prog"]},"TAK - dodaj koszt długu do WACC",'
                 f'"NIE - WACC = koszt kapitału własnego")')
        elif nazwa == "wacc":
            f = f"={A['ke']}"
        c = formula(ws, f"B{wiersz}", f, fmt, POGRUB if nazwa == "wacc" else CZARNY,
                    TLO_WYNIK if nazwa == "wacc" else None)
        if nazwa == "prog":
            c.font = NIEBIESKI
        etykieta(ws, f"D{wiersz}", skad, SZARY)

    wiersz += 2
    naglowki(ws, wiersz, ["Założenie", "id", "Uzasadnienie"])
    ws.merge_cells(start_row=wiersz, start_column=3, end_row=wiersz, end_column=7)
    for w in L.wpisy:
        if w["klasa"] != "zalozenie":
            continue
        wiersz += 1
        etykieta(ws, f"A{wiersz}", w["opis"])
        id_obok(ws, f"B{wiersz}", w)
        ws.merge_cells(start_row=wiersz, start_column=3, end_row=wiersz, end_column=7)
        etykieta(ws, f"C{wiersz}", w["uzasadnienie"])
        ws[f"A{wiersz}"].alignment = Alignment(wrap_text=True, vertical="top")
        ws[f"B{wiersz}"].alignment = Alignment(horizontal="center", vertical="top")
        ws[f"C{wiersz}"].alignment = Alignment(wrap_text=True, vertical="top")
        ws.row_dimensions[wiersz].height = 14 * max(linie(w["opis"], 44), linie(w["uzasadnienie"], 5 * 22)) + 4

    ws.column_dimensions["A"].width = 44
    ws.column_dimensions["B"].width = 26
    for k in "CDEFG":
        ws.column_dimensions[k].width = 22
    strona_wydruku(ws)


def arkusz_dcf(wb, L, A):
    ws = wb.create_sheet("DCF")
    etykieta(ws, "A1", f"{L.ticker} - model DCF (mln USD)", TYTUL)
    etykieta(ws, "A2", "Wszystkie komórki to formuły. Dane wejściowe są w arkuszach 'Założenia' i 'Dane historyczne'. "
             "Przepływy dyskontowane na koniec każdego roku od końca 2025 r.", SZARY)
    naglowki(ws, 4, ["Pozycja", "2025 (raport)"] + [f"{r} P" for r in LATA_PROG] + ["Rezydualny (2031)"])

    zal = "'Założenia'"
    kol = {r: get_column_letter(3 + i) for i, r in enumerate(LATA_PROG)}  # C..G
    H = "H"

    def wiersz_zal(nazwa, k_idx, rezydualny=False):
        w, _ = A[nazwa]
        return f"{zal}!${'G' if rezydualny else get_column_letter(2 + k_idx)}${w}"

    etykiety = {5: "Okres dyskontowy t (lata)", 6: "Przychody", 7: "Wzrost r/r", 8: "Marża operacyjna", 9: "Zysk operacyjny (EBIT)",
                10: "Stopa podatkowa", 11: "Podatek", 12: "NOPAT", 13: "Amortyzacja / przychody", 14: "Amortyzacja",
                15: "Nakłady inwestycyjne / przychody", 16: "Nakłady inwestycyjne", 17: "Wolne przepływy pieniężne (FCF)",
                18: "Czynnik dyskontowy", 19: "Wartość bieżąca FCF"}
    for w, t in etykiety.items():
        etykieta(ws, f"A{w}", t, POGRUB if w in (6, 12, 17, 19) else CZARNY)

    formula(ws, "B6", f"={A['rev_2025']}", F_MLN, ZIELONY)
    for i, r in enumerate(LATA_PROG):
        k = kol[r]
        poprz = "B" if i == 0 else kol[LATA_PROG[i - 1]]
        formula(ws, f"{k}5", "=1" if i == 0 else f"={poprz}5+1", '0')
        formula(ws, f"{k}7", f"={wiersz_zal('wzrost', i)}", F_PROC, ZIELONY)
        formula(ws, f"{k}6", f"={poprz}6*(1+{k}7)", F_MLN)
        formula(ws, f"{k}8", f"={wiersz_zal('marza', i)}", F_PROC, ZIELONY)
        formula(ws, f"{k}13", f"={wiersz_zal('da', i)}", F_PROC, ZIELONY)
        formula(ws, f"{k}15", f"={wiersz_zal('capex', i)}", F_PROC, ZIELONY)
    formula(ws, "H7", f"={A['g']}", F_PROC, ZIELONY)
    formula(ws, "H6", "=G6*(1+H7)", F_MLN)
    formula(ws, "H8", f"={wiersz_zal('marza', 0, True)}", F_PROC, ZIELONY)
    formula(ws, "H13", f"={wiersz_zal('da', 0, True)}", F_PROC, ZIELONY)
    formula(ws, "H15", f"={wiersz_zal('capex', 0, True)}", F_PROC, ZIELONY)
    for k in list(kol.values()) + [H]:
        formula(ws, f"{k}9", f"={k}6*{k}8", F_MLN)
        formula(ws, f"{k}10", f"={A['podatek']}", F_PROC, ZIELONY)
        formula(ws, f"{k}11", f"=-{k}9*{k}10", F_MLN)
        formula(ws, f"{k}12", f"={k}9+{k}11", F_MLN)
        formula(ws, f"{k}14", f"={k}6*{k}13", F_MLN)
        formula(ws, f"{k}16", f"=-{k}6*{k}15", F_MLN)
        formula(ws, f"{k}17", f"={k}12+{k}14+{k}16", F_MLN, POGRUB)
    for k in kol.values():
        formula(ws, f"{k}18", f"=1/(1+$B$24)^{k}5", '0.0000')
        formula(ws, f"{k}19", f"={k}17*{k}18", F_MLN, POGRUB)

    wynik = [
        (22, "Suma wartości bieżących FCF 2026-2030", "=SUM(C19:G19)", F_MLN),
        (23, "FCF okresu rezydualnego (rok 2031)", "=H17", F_MLN),
        (24, "WACC", f"={A['wacc']}", F_PROC),
        (25, "Wzrost w okresie rezydualnym (g)", f"={A['g']}", F_PROC),
        (26, "Wartość rezydualna na koniec 2030 (Gordon: FCF 2031 / (WACC - g))",
         '=IF(B24>B25,B23/(B24-B25),"WACC musi być większy od g")', F_MLN),
        (27, "Wartość bieżąca wartości rezydualnej", "=B26*G18", F_MLN),
        (28, "Wartość firmy (EV)", "=B22+B27", F_MLN),
        (29, "+ Gotówka i papiery wartościowe", f"={A['gotowka']}", F_MLN),
        (30, "- Dług długoterminowy", f"=-{A['long_term_debt_2025']}", F_MLN),
        (31, "Wartość kapitału własnego", "=B28+B29+B30", F_MLN),
        (32, "Liczba akcji wszystkich klas (mln)", f"={A['akcje_mln']}", '#,##0.0'),
        (33, "Wartość jednej akcji (USD)", "=B31/B32", F_USD),
        (34, "Udział wartości rezydualnej w wartości firmy", "=B27/B28", F_PROC),
    ]
    naglowki(ws, 21, ["Wycena", "Wartość"])
    for w, opis, f, fmt in wynik:
        etykieta(ws, f"A{w}", opis, POGRUB if w in (28, 31, 33) else CZARNY)
        zielony = f.startswith("='") or f.startswith("=-'")
        formula(ws, f"B{w}", f, fmt, ZIELONY if zielony else (POGRUB if w in (28, 31, 33) else CZARNY),
                TLO_WYNIK if w == 33 else None)
    A.update(dcf_ev="DCF!$B$28", dcf_eq="DCF!$B$31", dcf_akcja="DCF!$B$33", dcf_pvfcf="DCF!$B$22",
             dcf_pvtv="DCF!$B$27", dcf_gotowka="DCF!$B$29", dcf_dlug="DCF!$B$30", dcf_udzial_tv="DCF!$B$34")

    ws.column_dimensions["A"].width = 62
    for k in "BCDEFGH":
        ws.column_dimensions[k].width = 16
    ws.freeze_panes = "B5"
    strona_wydruku(ws)


def arkusz_wrazliwosc(wb, L, A):
    ws = wb.create_sheet("Wrażliwość")
    etykieta(ws, "A1", f"{L.ticker} - wartość jednej akcji (USD) przy różnych WACC i wzroście rezydualnym", TYTUL)
    etykieta(ws, "A2", "Każda komórka liczy pełną wycenę formułą: przepływy 2026-2030 z arkusza DCF, wartość rezydualna "
             "dla danego g i WACC, gotówka, dług, liczba akcji. Środek tabeli = wariant bazowy.", SZARY)
    etykieta(ws, "A4", "Krok WACC (parametr)")
    formula(ws, "B4", KROK_WACC, F_PROC, NIEBIESKI)
    etykieta(ws, "A5", "Krok g (parametr)")
    formula(ws, "B5", KROK_G, F_PROC, NIEBIESKI)
    etykieta(ws, "C7", "WACC →", POGRUB)
    etykieta(ws, "A8", "g ↓", POGRUB)
    for j in range(5):
        k = get_column_letter(3 + j)  # C..G
        formula(ws, f"{k}8", f"={A['wacc']}+({j - 2})*$B$4", F_PROC, POGRUB, PatternFill("solid", fgColor="D9E1F2"))
    for i in range(5):
        r = 9 + i
        formula(ws, f"B{r}", f"={A['g']}+({i - 2})*$B$5", F_PROC, POGRUB, PatternFill("solid", fgColor="D9E1F2"))
        for j in range(5):
            k = get_column_letter(3 + j)
            w, g = f"{k}$8", f"$B{r}"
            rezyd = f"DCF!$G$6*(1+{g})*(DCF!$H$8*(1-DCF!$H$10)+DCF!$H$13-DCF!$H$15)"
            f = (f"=IF({w}>{g},(SUMPRODUCT(DCF!$C$17:$G$17/(1+{w})^DCF!$C$5:$G$5)"
                 f"+{rezyd}/({w}-{g})/(1+{w})^DCF!$G$5+{A['dcf_gotowka']}+{A['dcf_dlug']})/{A['akcje_mln']},\"-\")")
            formula(ws, f"{k}{r}", f, F_USD, fill=TLO_KLUCZ if (i, j) == (2, 2) else None)
    ws.conditional_formatting.add("C9:G13", ColorScaleRule(start_type="min", start_color="F8696B", mid_type="percentile",
                                                           mid_value=50, mid_color="FFEB84", end_type="max", end_color="63BE7B"))
    ws["C9"].fill = PatternFill()  # skala kolorów ma pierwszeństwo; brak stałego tła poza środkiem
    etykieta(ws, "A15", "Aktualny kurs (USD)")
    formula(ws, "B15", f"={A['kurs']}", F_USD, ZIELONY)
    etykieta(ws, "A16", "Wartość bazowa (USD)")
    formula(ws, "B16", f"={A['dcf_akcja']}", F_USD, ZIELONY)
    etykieta(ws, "A17", "Kontrola: środek tabeli = wartość bazowa")
    formula(ws, "B17", '=IF(ABS(E11-B16)<0.01,"OK","BŁĄD")')
    ws.column_dimensions["A"].width = 40
    for k in "BCDEFG":
        ws.column_dimensions[k].width = 14
    strona_wydruku(ws)


SZER = [6, 12, 40, 34, 14, 10, 12, 24, 12, 48, 70]
ZAWIJANE = (4, 8, 9, 10, 11)


def arkusz_ledger(wb, L):
    ws = wb.create_sheet("Ledger")
    etykieta(ws, "A1", f"{L.ticker} - ledger: wszystkie wpisy ze źródłem i cytatem", TYTUL)
    kolumny = ["id", "klasa", "klucz", "opis", "wartość", "jednostka", "okres", "źródło", "strona", "adres", "cytat / uzasadnienie"]
    naglowki(ws, 3, kolumny)
    for r, w in enumerate(L.wpisy, start=4):
        zr = w.get("zrodlo", {})
        wartosc = w.get("wartosc", w.get("plik", ""))
        tekst = w.get("cytat") or w.get("uzasadnienie") or f"autor: {w.get('autor')}; licencja: {w.get('licencja')}"
        wiersz = [w["id"], w["klasa"], w["klucz"], w["opis"], wartosc, w.get("jednostka", ""), w.get("okres", ""),
                  zr.get("dokument", ""), str(zr.get("strona", "")), zr.get("url", ""), tekst]
        for c, v in enumerate(wiersz, start=1):
            komorka = ws.cell(row=r, column=c, value=v)
            komorka.font = CZARNY
            komorka.alignment = Alignment(wrap_text=c in ZAWIJANE, vertical="top")
            if c == 5 and isinstance(v, (int, float)):
                komorka.number_format = '#,##0.##'
        # Adres zawija się tylko na ukośnikach, więc liczymy dla niego krótsze linie.
        ws.row_dimensions[r].height = 13 * max(linie(v, SZER[c - 1] * (0.7 if c == 10 else 1))
                                               for c, v in enumerate(wiersz, start=1) if c in ZAWIJANE) + 4
    for k, s in zip("ABCDEFGHIJK", SZER):
        ws.column_dimensions[k].width = s
    ws.freeze_panes = "A4"
    strona_wydruku(ws)


def arkusz_podsumowanie(wb, L, A):
    ws = wb["Podsumowanie"]
    etykieta(ws, "A1", f"{L.ticker} - wycena metodą DCF", TYTUL)
    etykieta(ws, "A2", "Wszystkie liczby w tym arkuszu to formuły odwołujące się do pozostałych arkuszy.", SZARY)
    naglowki(ws, 4, ["Wynik", "Wartość"])
    rzad = [("Wartość jednej akcji z DCF (USD)", f"={A['dcf_akcja']}", F_USD),
            ("Aktualny kurs (USD)", f"={A['kurs']}", F_USD),
            ("Różnica: wartość z DCF wobec kursu", "=B5/B6-1", F_PROC),
            ("WACC", f"={A['wacc']}", F_PROC),
            ("Wzrost w okresie rezydualnym", f"={A['g']}", F_PROC),
            ("Wartość firmy (mln USD)", f"={A['dcf_ev']}", F_MLN),
            ("Wartość kapitału własnego (mln USD)", f"={A['dcf_eq']}", F_MLN),
            ("Udział wartości rezydualnej w wartości firmy", f"={A['dcf_udzial_tv']}", F_PROC)]
    for i, (opis, f, fmt) in enumerate(rzad, start=5):
        etykieta(ws, f"A{i}", opis, POGRUB if i <= 7 else CZARNY)
        formula(ws, f"B{i}", f, fmt, POGRUB if i in (5, 7) else ZIELONY, TLO_WYNIK if i == 5 else None)

    naglowki(ws, 14, ["Kluczowe założenia", "Wartość"])
    zal = "'Założenia'"
    w_wzrost, w_marza, w_capex, w_da = (A[n][0] for n in ("wzrost", "marza", "capex", "da"))
    kluczowe = [("Wzrost przychodów 2026", f"={zal}!$B${w_wzrost}"), ("Wzrost przychodów 2030", f"={zal}!$F${w_wzrost}"),
                ("Marża operacyjna 2026", f"={zal}!$B${w_marza}"), ("Marża operacyjna po 2030", f"={zal}!$G${w_marza}"),
                ("Nakłady inwestycyjne / przychody 2026", f"={zal}!$B${w_capex}"),
                ("Nakłady inwestycyjne / przychody po 2030", f"={zal}!$G${w_capex}"),
                ("Amortyzacja / przychody po 2030", f"={zal}!$G${w_da}"),
                ("Stopa podatkowa", f"={A['podatek']}"), ("Stopa wolna od ryzyka (10Y UST)", f"={A['rf']}"),
                ("Beta", f"={A['beta']}"), ("Premia za ryzyko rynkowe", f"={A['erp']}")]
    for i, (opis, f) in enumerate(kluczowe, start=15):
        etykieta(ws, f"A{i}", opis)
        formula(ws, f"B{i}", f, '0.00' if opis == "Beta" else F_PROC, ZIELONY)

    # Dane do wykresów (formuły)
    etykieta(ws, "D27", "Dane do wykresów", POGRUB)
    naglowki(ws, 28, ["Rok", "Przychody (mln USD)", "Marża operacyjna", "FCF (mln USD)"], kol=4)
    ws.row_dimensions[28].height = 30
    hist_ark = A["hist_rev"][0]
    for i, rok in enumerate(LATA_HIST + LATA_PROG):
        r = 29 + i
        ws[f"D{r}"] = rok
        if rok in LATA_HIST:
            k = get_column_letter(2 + i)
            formula(ws, f"E{r}", f"={hist_ark}!${k}$5", F_MLN, ZIELONY)
            formula(ws, f"F{r}", f"={hist_ark}!${k}$7", F_PROC, ZIELONY)
            ws[f"G{r}"] = None
        else:
            k = get_column_letter(3 + i - len(LATA_HIST))
            formula(ws, f"E{r}", f"=DCF!${k}$6", F_MLN, ZIELONY)
            formula(ws, f"F{r}", f"=DCF!${k}$8", F_PROC, ZIELONY)
            formula(ws, f"G{r}", f"=DCF!${k}$17", F_MLN, ZIELONY)

    naglowki(ws, 39, ["Od wartości firmy do kapitału", "Podstawa (pomocnicza)", "Wartość (mln USD)"], kol=4)
    ws.row_dimensions[39].height = 30
    mostek = [("PV FCF 2026-2030", "0", f"={A['dcf_pvfcf']}"),
              ("PV wartości rezydualnej", f"=MIN(0,{A['dcf_pvfcf']})+MAX(0,{A['dcf_pvfcf']})", f"={A['dcf_pvtv']}"),
              ("Wartość firmy", "0", f"={A['dcf_ev']}"),
              ("+ Gotówka i papiery", f"={A['dcf_ev']}", f"={A['dcf_gotowka']}"),
              ("- Dług", f"={A['dcf_ev']}+{A['dcf_gotowka']}+{A['dcf_dlug']}", f"=-{A['dcf_dlug']}"),
              ("Kapitał własny", "0", f"={A['dcf_eq']}")]
    for i, (opis, baza, wart) in enumerate(mostek, start=40):
        ws[f"D{i}"] = opis
        formula(ws, f"E{i}", f"={baza}" if baza == "0" else baza, F_MLN)
        formula(ws, f"F{i}", wart, F_MLN, ZIELONY)
    etykieta(ws, "D47", "Kapitał własny / liczba akcji (mln) = wartość jednej akcji (USD):")
    formula(ws, "G47", f"={A['dcf_akcja']}", F_USD, POGRUB)

    # Wykres 1: przychody (słupki) + marża (linia, oś prawa)
    lata = Reference(ws, min_col=4, min_row=29, max_row=36)
    w1 = BarChart()
    w1.title = "Przychody 2023-2025 i prognoza 2026-2030 (mln USD) oraz marża operacyjna"
    w1.add_data(Reference(ws, min_col=5, min_row=28, max_row=36), titles_from_data=True)
    w1.set_categories(lata)
    w1.y_axis.title = "mln USD"
    w1.y_axis.majorGridlines = None
    w1.y_axis.number_format = '#,##0'
    l1 = LineChart()
    l1.add_data(Reference(ws, min_col=6, min_row=28, max_row=36), titles_from_data=True)
    l1.y_axis.axId = 200
    l1.y_axis.title = "Marża operacyjna"
    l1.y_axis.number_format = '0%'
    l1.y_axis.crosses = "max"
    l1.series[0].marker.symbol = "circle"
    for os_ in (w1.x_axis, w1.y_axis, l1.y_axis):
        os_.delete = False
    w1 += l1
    w1.legend.position = "b"
    w1.width, w1.height = 18, 8.5
    ws.add_chart(w1, "D4")

    # Wykres 2: FCF w prognozie
    w2 = BarChart()
    w2.title = "Wolne przepływy pieniężne (FCF) w prognozie, mln USD"
    w2.add_data(Reference(ws, min_col=7, min_row=29 + len(LATA_HIST), max_row=36), titles_from_data=False)
    w2.set_categories(Reference(ws, min_col=4, min_row=29 + len(LATA_HIST), max_row=36))
    w2.legend = None
    w2.y_axis.number_format = '#,##0'
    w2.y_axis.majorGridlines = None
    w2.series[0].dLbls = etykiety_danych()
    w2.series[0].graphicalProperties.solidFill = "1F3864"
    w2.x_axis.tickLblPos = "low"
    for os_ in (w2.x_axis, w2.y_axis):
        os_.delete = False
    w2.width, w2.height = 13, 8.5
    ws.add_chart(w2, "A49")

    # Wykres 3: mostek od wartości firmy do kapitału własnego (słupki skumulowane z niewidoczną podstawą)
    w3 = BarChart()
    w3.type, w3.grouping, w3.overlap = "col", "stacked", 100
    w3.title = "Od wartości firmy do wartości kapitału własnego (mln USD)"
    w3.add_data(Reference(ws, min_col=5, min_row=40, max_row=45), titles_from_data=False)
    w3.add_data(Reference(ws, min_col=6, min_row=40, max_row=45), titles_from_data=False)
    w3.set_categories(Reference(ws, min_col=4, min_row=40, max_row=45))
    baza = w3.series[0]
    baza.graphicalProperties.noFill = True
    baza.graphicalProperties.line.noFill = True
    w3.series[1].graphicalProperties.solidFill = "8EA9DB"
    w3.series[1].dLbls = etykiety_danych()
    w3.legend = None
    w3.y_axis.number_format = '#,##0'
    w3.y_axis.majorGridlines = None
    for os_ in (w3.x_axis, w3.y_axis):
        os_.delete = False
    w3.width, w3.height = 18, 8.5
    ws.add_chart(w3, "E49")

    ws.column_dimensions["A"].width = 44
    ws.column_dimensions["B"].width = 16
    ws.column_dimensions["C"].width = 3
    ws.column_dimensions["D"].width = 30
    for k in "EFG":
        ws.column_dimensions[k].width = 18
    strona_wydruku(ws, poziomo=False)


# ---------------------------------------------------------------- kontrola


def sprawdz_bledy(plik):
    wb = load_workbook(plik, data_only=True)
    bledy, puste = [], []
    wzory = load_workbook(plik)
    for ws in wb.worksheets:
        for wiersz in ws.iter_rows():
            for c in wiersz:
                if isinstance(c.value, str) and c.value.startswith(BLEDY_EXCELA):
                    bledy.append(f"{ws.title}!{c.coordinate}: {c.value}")
                f = wzory[ws.title][c.coordinate].value
                if isinstance(f, str) and f.startswith("=") and c.value is None:
                    puste.append(f"{ws.title}!{c.coordinate}")
    return bledy, puste


# ---------------------------------------------------------------- main


def main():
    if len(sys.argv) != 2:
        raise SystemExit("Użycie: python narzedzia/generuj_xlsx.py TICKER")
    ticker = sys.argv[1].upper()
    wymagaj_weryfikacji(ticker)
    L = Ledger(ticker)

    katalog = KATALOG_GLOWNY / ticker / "wyniki"
    katalog.mkdir(parents=True, exist_ok=True)
    plik = katalog / f"{ticker}_DCF.xlsx"

    wb = Workbook()
    wb.active.title = "Podsumowanie"
    A = {}
    arkusz_dane(wb, L, A)
    arkusz_zalozenia(wb, L, A)
    arkusz_dcf(wb, L, A)
    arkusz_wrazliwosc(wb, L, A)
    arkusz_ledger(wb, L)
    arkusz_podsumowanie(wb, L, A)
    for ws in wb.worksheets:
        ws.sheet_view.showGridLines = False
    wb.calculation.fullCalcOnLoad = True

    with tempfile.TemporaryDirectory() as tmp:
        surowy = Path(tmp) / plik.name
        wb.save(surowy)
        # LibreOffice przelicza formuły przy wczytaniu i zapisuje plik z wartościami (cache), żeby każdy
        # podgląd i skrypt widział liczby. Tę przeliczoną wersję zapisujemy jako wynik.
        przeliczony = konwertuj(surowy, "xlsx:Calc Office Open XML", Path(tmp) / "przeliczony")
        bledy, puste = sprawdz_bledy(przeliczony)
        if bledy or puste:
            print("Błędy w formułach:" if bledy else "", *bledy[:30], sep="\n")
            print("Formuły bez wartości po przeliczeniu:" if puste else "", *puste[:30], sep="\n")
            sys.exit("STOP: model ma błędy po przeliczeniu w LibreOffice.")
        shutil.copy(przeliczony, plik)

    # Wynik wyceny z przeliczonego pliku
    wb_v = load_workbook(plik, data_only=True)
    pods = wb_v["Podsumowanie"]
    wycena = {
        "ticker": ticker,
        "plik_modelu": str(plik.relative_to(KATALOG_GLOWNY)).replace("\\", "/"),
        "data_wyceny": datetime.now(timezone.utc).date().isoformat(),
        "wartosc_jednej_akcji_usd": pods["B5"].value,
        "kurs_usd": pods["B6"].value,
        "roznica_proc": pods["B7"].value * 100,
        "wacc_proc": pods["B8"].value * 100,
        "wzrost_rezydualny_proc": pods["B9"].value * 100,
        "wartosc_firmy_mln_usd": pods["B10"].value,
        "wartosc_kapitalu_mln_usd": pods["B11"].value,
        "udzial_wartosci_rezydualnej_proc": pods["B12"].value * 100,
        "kontrola_wrazliwosci": wb_v["Wrażliwość"]["B17"].value,
        "sha256_ledgera": json.loads((KATALOG_GLOWNY / ticker / "weryfikacja" / "status.json").read_text(encoding="utf-8"))["sha256_ledgera"],
    }
    (katalog / "wycena.json").write_text(json.dumps(wycena, ensure_ascii=False, indent=2), encoding="utf-8")

    # Podgląd: PDF z LibreOffice -> PNG każdej strony
    podglad = katalog / "podglad"
    liczba_stron = podglad_png(plik, podglad, "xlsx-strona")

    print(f"Model: {plik}")
    print(f"Wartość jednej akcji: {wycena['wartosc_jednej_akcji_usd']:.2f} USD, kurs {wycena['kurs_usd']:.2f} USD, "
          f"różnica {wycena['roznica_proc']:+.1f}%")
    print(f"WACC {wycena['wacc_proc']:.2f}%, g {wycena['wzrost_rezydualny_proc']:.2f}%, "
          f"EV {wycena['wartosc_firmy_mln_usd']:,.0f} mln USD, kapitał {wycena['wartosc_kapitalu_mln_usd']:,.0f} mln USD")
    print(f"Kontrola wrażliwości: {wycena['kontrola_wrazliwosci']}; podgląd: {liczba_stron} stron w {podglad}")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    main()

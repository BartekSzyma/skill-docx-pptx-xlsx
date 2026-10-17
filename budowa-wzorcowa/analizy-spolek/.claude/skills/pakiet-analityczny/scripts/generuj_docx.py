"""Jednostronicowa notatka dla zarządu, zbudowana z ledgera, wyniku wyceny i planu treści.

Użycie: python .claude/skills/pakiet-analityczny/scripts/generuj_docx.py TICKER

Wejście: TICKER/ledger.json, TICKER/wyniki/wycena.json, TICKER/tresc.json (sekcja "notatka").
Kroki:
  1. sprawdza weryfikację ledgera i to, że wycena.json powstała z tego samego ledgera,
  2. zapisuje TICKER/wyniki/TICKER_notatka_zarzad.docx (A4); przy każdej liczbie id wpisu,
  3. zamienia plik na PDF w LibreOffice i sprawdza, że ma dokładnie 1 stronę (kod wyjścia 1, jeśli więcej),
  4. zapisuje podgląd w TICKER/wyniki/podglad/docx-strona-NN.png.
"""

import sys
import tempfile

import pymupdf
from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

from bramka import KATALOG_GLOWNY, wymagaj_weryfikacji
from formaty import NBSP, liczba, wartosc_z_jedn
from generuj_pptx import Dane
from libreoffice import konwertuj, podglad_png

SKRYPTY = ".claude/skills/pakiet-analityczny/scripts"
FONT = "Calibri"
CIEMNY = RGBColor(0x1E, 0x2A, 0x36)
AKCENT = RGBColor(0x0F, 0x7C, 0x80)
SZARY = RGBColor(0x6B, 0x77, 0x85)
CZERWONY = RGBColor(0xB0, 0x3A, 0x2E)
BIALY = RGBColor(0xFF, 0xFF, 0xFF)
TLO_NAGLOWKA_TABELI = "1E2A36"
TLO_WIERSZA = "F1F4F6"
ROZMIAR = 10        # tekst główny, pt
ROZMIAR_DROBNY = 9  # źródła i id wpisów; mniej nie schodzimy
ZASTRZEZENIE = "Materiał edukacyjny, nie stanowi rekomendacji inwestycyjnej."


# ---------------------------------------------------------------- elementy


def run(p, tekst, rozmiar=ROZMIAR, pogrub=False, kolor=None):
    r = p.add_run(tekst)
    r.font.name = FONT
    r.font.size = Pt(rozmiar)
    r.font.bold = pogrub
    if kolor is not None:
        r.font.color.rgb = kolor
    return r


def ids(p, identyfikatory):
    if identyfikatory:
        run(p, f" [{', '.join(identyfikatory)}]", ROZMIAR_DROBNY, kolor=SZARY)


def akapit(doc, odstep_po=3, styl=None):
    p = doc.add_paragraph(style=styl)
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(odstep_po)
    p.paragraph_format.line_spacing = 1.05
    return p


def naglowek_sekcji(doc, tekst):
    p = akapit(doc, odstep_po=2)
    p.paragraph_format.space_before = Pt(7)
    run(p, tekst, 11.5, pogrub=True, kolor=AKCENT)


def punkt(doc, naglowek, tekst, identyfikatory):
    """Punkt listy (styl 'List Bullet' z numeracją Worda): pogrubiony nagłówek, tekst, id wpisów."""
    p = akapit(doc, odstep_po=2, styl="List Bullet")
    if naglowek:
        run(p, naglowek.rstrip(": ") + ": ", pogrub=True)
    run(p, tekst)
    ids(p, identyfikatory)


def punkt_z_tresci(doc, D, element):
    tekst, uzyte = D.wypelnij(element["tekst"], element.get("id", []))
    punkt(doc, element.get("naglowek", ""), tekst, uzyte)


def cieniowanie(komorka, kolor):
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), kolor)
    komorka._tc.get_or_add_tcPr().append(shd)


def linia_pod(p, kolor="0F7C80"):
    granice = OxmlElement("w:pBdr")
    dol = OxmlElement("w:bottom")
    for k, v in (("w:val", "single"), ("w:sz", "8"), ("w:space", "4"), ("w:color", kolor)):
        dol.set(qn(k), v)
    granice.append(dol)
    p._p.get_or_add_pPr().append(granice)


def tabela_liczb(doc, wiersze):
    tabela = doc.add_table(rows=1 + len(wiersze), cols=4)
    tabela.alignment = WD_TABLE_ALIGNMENT.CENTER
    szerokosci = [Cm(8.6), Cm(2.9), Cm(3.6), Cm(2.1)]
    for i, tekst in enumerate(["Pozycja", "Okres / data", "Wartość", "id"]):
        k = tabela.rows[0].cells[i]
        cieniowanie(k, TLO_NAGLOWKA_TABELI)
        k.paragraphs[0].paragraph_format.space_after = Pt(0)
        run(k.paragraphs[0], tekst, 9.5, pogrub=True, kolor=BIALY)
    for r, wiersz in enumerate(wiersze, start=1):
        for c, tekst in enumerate(wiersz):
            k = tabela.rows[r].cells[c]
            if r % 2 == 0:
                cieniowanie(k, TLO_WIERSZA)
            p = k.paragraphs[0]
            p.paragraph_format.space_after = Pt(0)
            if c == 2:
                p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
            kolor = SZARY if c == 3 else (CZERWONY if c == 2 and tekst.startswith("-") else None)
            run(p, tekst, ROZMIAR_DROBNY if c == 3 else ROZMIAR, pogrub=(c == 2), kolor=kolor)
    # Szerokości kolumn: siatka tabeli (czyta ją LibreOffice) i szerokość każdej komórki (czyta ją Word).
    tabela.autofit = False
    for kolumna, s_ in zip(tabela._tbl.tblGrid.findall(qn("w:gridCol")), szerokosci):
        kolumna.set(qn("w:w"), str(int(s_.twips)))
    for wiersz in tabela.rows:
        for k, s_ in zip(wiersz.cells, szerokosci):
            k.width = s_


# ---------------------------------------------------------------- treść


def zbuduj(D):
    W, R = D.wycena, D.rok
    cfg = D.tresc["notatka"]
    rev, kurs = D[f"revenue_{R}"], D["share_price"]

    doc = Document()
    sekcja = doc.sections[0]
    sekcja.page_width, sekcja.page_height = Cm(21.0), Cm(29.7)
    sekcja.left_margin = sekcja.right_margin = Cm(1.9)
    sekcja.top_margin, sekcja.bottom_margin = Cm(1.5), Cm(1.4)
    styl = doc.styles["Normal"]
    styl.font.name = FONT
    styl.font.size = Pt(ROZMIAR)
    styl.element.rPr.rFonts.set(qn("w:eastAsia"), FONT)

    p = akapit(doc, odstep_po=0)
    run(p, "Notatka dla zarządu", 10, pogrub=True, kolor=AKCENT)
    p = akapit(doc, odstep_po=1)
    run(p, f"{D.spolka()} ({D.ticker})", 20, pogrub=True, kolor=CIEMNY)
    p = akapit(doc, odstep_po=6)
    run(p, f"Data: {W['data_wyceny']}  |  dane finansowe: raport 10-K za {rev['okres']} r., kurs z {kurs['okres']}",
        9.5, kolor=SZARY)
    linia_pod(p)

    naglowek_sekcji(doc, "Najważniejsze wnioski")
    for element in cfg["wnioski"][:3]:
        punkt_z_tresci(doc, D, element)

    naglowek_sekcji(doc, "Kluczowe liczby")
    tabela_liczb(doc, [
        ("Przychody", rev["okres"], wartosc_z_jedn(rev), rev["id"]),
        ("Marża operacyjna (zysk operacyjny / przychody)", str(R), f"{liczba(W[f'marza_operacyjna_{R}_proc'], 1)}%", "wycena"),
        ("Gotówka i papiery wartościowe", D[f"cash_and_equivalents_{R}"]["okres"],
         f"{liczba(W['gotowka_i_papiery_mln_usd'])}{NBSP}mln USD", "wycena"),
        ("Wartość jednej akcji z DCF (założenia, nie fakt)", W["data_wyceny"],
         f"{liczba(W['wartosc_jednej_akcji_usd'], 2)}{NBSP}USD", "wycena"),
        ("Kurs akcji", kurs["okres"], f"{liczba(kurs['wartosc'], 2)}{NBSP}USD", kurs["id"]),
        ("Różnica: wartość z DCF wobec kursu", W["data_wyceny"], f"{liczba(W['roznica_proc'], 1)}%", "wycena"),
    ])

    naglowek_sekcji(doc, "Projekty")
    for element in cfg["projekty"][:3]:
        punkt_z_tresci(doc, D, element)

    naglowek_sekcji(doc, "Ryzyka")
    for w in [w for w in D.wpisy if w["klasa"] == "fakt" and w["klucz"].startswith("risk_")][:3]:
        opis = w["opis"].removeprefix("Ryzyko: ")
        punkt(doc, str(w["wartosc"])[0].upper() + str(w["wartosc"])[1:], opis + ".", [w["id"]])

    # Źródła: strony 10-K wszystkich faktów, do których odwołuje się notatka
    uzyte = {rev["id"]}
    for element in cfg["wnioski"][:3] + cfg["projekty"][:3]:
        uzyte.update(D.wypelnij(element["tekst"], element.get("id", []))[1])
    uzyte.update(w["id"] for w in D.wpisy if w["klasa"] == "fakt" and w["klucz"].startswith("risk_"))
    strony = {}
    for w in D.wpisy:
        if w["klasa"] == "fakt" and w["id"] in uzyte:
            strony.setdefault(str(w["zrodlo"]["strona"]), []).append(w["id"])
    opis_stron = "; ".join(f"{'okładka' if s.startswith('okładka') else 's. ' + s}: {', '.join(v)}"
                           for s, v in sorted(strony.items(), key=lambda x: (not x[0].isdigit(), int(x[0]) if x[0].isdigit() else 0, x[0])))
    naglowek_sekcji(doc, "Źródła")
    p = akapit(doc, odstep_po=2)
    run(p, f"{rev['zrodlo']['dokument']} (SEC EDGAR), strony i wpisy ledgera: {opis_stron}. "
           f"{kurs['zrodlo']['dokument']} [{kurs['id']}], pobrano {kurs['data_pobrania']}. "
           f"Wycena i wielkości wyliczone: model {W['plik_modelu']} [wycena], założenia w ledgerze (wpisy Z). "
           "Wszystkie wpisy ledgera mają dosłowny cytat ze źródła i zostały sprawdzone dwiema bramkami.",
        ROZMIAR_DROBNY, kolor=SZARY)
    p = akapit(doc, odstep_po=0)
    run(p, ZASTRZEZENIE, ROZMIAR_DROBNY, pogrub=True, kolor=CIEMNY)
    return doc


def main():
    if len(sys.argv) != 2:
        raise SystemExit(f"Użycie: python {SKRYPTY}/generuj_docx.py TICKER")
    ticker = sys.argv[1].upper()
    wymagaj_weryfikacji(ticker)
    D = Dane(ticker)
    doc = zbuduj(D)
    doc.core_properties.title = f"{ticker} - notatka dla zarządu"
    doc.core_properties.language = "pl-PL"

    katalog = KATALOG_GLOWNY / ticker / "wyniki"
    plik = katalog / f"{ticker}_notatka_zarzad.docx"
    doc.save(plik)
    with tempfile.TemporaryDirectory() as tmp:
        with pymupdf.open(konwertuj(plik, "pdf", tmp)) as d:
            stron = len(d)
    podglad_png(plik, katalog / "podglad", "docx-strona", dpi=110)
    print(f"Notatka: {plik}; PDF ma {stron} stron(y)")
    if stron != 1:
        sys.exit(f"STOP: notatka ma {stron} strony zamiast 1. Skróć teksty w {ticker}/tresc.json (sekcja 'notatka'); "
                 "czcionki nie zmniejszamy poniżej 9 pt.")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    main()

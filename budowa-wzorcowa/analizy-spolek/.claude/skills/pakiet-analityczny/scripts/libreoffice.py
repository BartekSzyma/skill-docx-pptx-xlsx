"""Wspólne funkcje: konwersja plików przez LibreOffice (bez okna) i podgląd PDF do PNG."""

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import pymupdf

SOFFICE_KANDYDACI = [
    shutil.which("soffice"),
    r"C:\Program Files\LibreOffice\program\soffice.exe",
    r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
]


def soffice():
    for k in SOFFICE_KANDYDACI:
        if k and Path(k).exists():
            return k
    sys.exit("STOP: nie znaleziono LibreOffice (soffice). Zainstaluj go albo dodaj do PATH.")


def konwertuj(plik, format_, katalog):
    """Konwertuje plik (np. do 'pdf' albo 'xlsx:Calc Office Open XML'); xlsx jest przy tym przeliczany."""
    with tempfile.TemporaryDirectory() as profil:
        polecenie = [soffice(), f"-env:UserInstallation={Path(profil).as_uri()}", "--headless",
                     "--convert-to", format_, "--outdir", str(katalog), str(plik)]
        wynik = subprocess.run(polecenie, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=240)
    wyjscie = Path(katalog) / f"{Path(plik).stem}.{format_.split(':')[0]}"
    if wynik.returncode != 0 or not wyjscie.exists():
        sys.exit(f"STOP: LibreOffice nie przekonwertował pliku {Path(plik).name} ({wynik.stderr.strip()[:300]})")
    return wyjscie


def podglad_png(plik, katalog, prefiks, dpi=110):
    """Zapisuje każdą stronę pliku (przez PDF) jako katalog/prefiks-NN.png; usuwa stare pliki z tym prefiksem."""
    katalog = Path(katalog)
    katalog.mkdir(parents=True, exist_ok=True)
    for stary in katalog.glob(f"{prefiks}-*.png"):
        stary.unlink()
    with tempfile.TemporaryDirectory() as tmp:
        pdf = konwertuj(plik, "pdf", tmp)
        with pymupdf.open(pdf) as dok:
            for i, strona in enumerate(dok, start=1):
                strona.get_pixmap(dpi=dpi).save(katalog / f"{prefiks}-{i:02d}.png")
            return len(dok)

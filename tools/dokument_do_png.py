# Render dokumentu Office (xlsx/pptx/docx) do PNG: LibreOffice -> PDF -> PNG (PyMuPDF).
# Użycie: PYTHONUTF8=1 python tools/dokument_do_png.py <plik> <katalog_wyjscia> [--strony 1,2] [--dpi 110]
# Wynik: <katalog>/<nazwa>-NN.png dla każdej (wybranej) strony PDF.
import argparse
import shutil
import subprocess
import tempfile
from pathlib import Path

import fitz

SOFFICE = shutil.which("soffice") or r"C:\Program Files\LibreOffice\program\soffice.exe"


def do_pdf(plik: Path, katalog: Path) -> Path:
    # Osobny profil LibreOffice, żeby nie kolidować z otwartym oknem LibreOffice użytkownika.
    profil = Path(tempfile.mkdtemp(prefix="lo-profil-"))
    subprocess.run([SOFFICE, f"-env:UserInstallation={profil.as_uri()}", "--headless", "--convert-to", "pdf",
                    "--outdir", str(katalog), str(plik)], check=True, capture_output=True, timeout=180)
    shutil.rmtree(profil, ignore_errors=True)
    return katalog / (plik.stem + ".pdf")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("plik")
    p.add_argument("wyjscie")
    p.add_argument("--strony", default="")
    p.add_argument("--dpi", type=int, default=110)
    a = p.parse_args()
    plik, wyj = Path(a.plik).resolve(), Path(a.wyjscie)
    wyj.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        pdf = do_pdf(plik, Path(tmp))
        dok = fitz.open(pdf)
        wybrane = [int(s) for s in a.strony.split(",") if s] or range(1, dok.page_count + 1)
        for n in wybrane:
            cel = wyj / f"{plik.stem}-{n:02d}.png"
            dok[n - 1].get_pixmap(dpi=a.dpi).save(cel)
            print(cel)
        print(f"stron w PDF: {dok.page_count}")
        dok.close()


if __name__ == "__main__":
    main()

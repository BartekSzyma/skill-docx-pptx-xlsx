# Przygotowuje zrzuty do instrukcji: kadry terminala (PNG) i strony dokumentów (JPG, przycięte białe marginesy).
# Źródła: zrzuty/oryginaly/kadr-*.png (tools/przebieg.sh) oraz render dokumentów (tools/dokument_do_png.py).
# Użycie: PYTHONUTF8=1 python tools/przygotuj-zrzuty.py <katalog_renderow>
import sys
from pathlib import Path

from PIL import Image, ImageChops

KORZEN = Path(__file__).resolve().parent.parent
ORYGINALY = KORZEN / "zrzuty" / "oryginaly"
CEL = KORZEN / "zrzuty"
MAKS_SZEROKOSC = 1400

# klucz w instrukcji -> (plik źródłowy, czy dokument)
ZRZUTY = {
    "01-konsola-wersje": ("konsola-wersje.png", False),
    "02-konsola-winget-python": ("konsola-winget-python.png", False),
    "03-konsola-winget-libreoffice": ("konsola-winget-libreoffice.png", False),
    "04-konsola-claude": ("konsola-claude.png", False),
    "05-zaufanie": ("kadr-zaufanie.png", False),
    "06-p1-start": ("kadr-P1-start.png", False),
    "07-p1-zrodla": ("kadr-P1.png", False),
    "08-p2-start": ("kadr-P2-start.png", False),
    "09-p2-ledger": ("kadr-P2.png", False),
    "10-p3-start": ("kadr-P3-start.png", False),
    "11-p3-grafiki": ("kadr-P3.png", False),
    "12-p4-start": ("kadr-P4-start.png", False),
    "13-p4-weryfikacja": ("kadr-P4.png", False),
    "14-p5-start": ("kadr-P5-start.png", False),
    "15-p5-pulapki": ("kadr-P5.png", False),
    "16-p6-start": ("kadr-P6-start.png", False),
    "17-p6-wynik": ("kadr-P6.png", False),
    "18-xlsx-podsumowanie": ("META_DCF-01.png", True),
    "19-xlsx-wrazliwosc": ("META_DCF-07.png", True),
    "20-p7-start": ("kadr-P7-start.png", False),
    "21-p7-slajdy": ("kadr-P7.png", False),
    "22-pptx-liczby": ("META_prezentacja-02.png", True),
    "23-pptx-projekt": ("META_prezentacja-06.png", True),
    "24-pptx-wycena": ("META_prezentacja-07.png", True),
    "25-p8-start": ("kadr-P8-start.png", False),
    "26-p8-kontrola": ("kadr-P8.png", False),
    "27-docx-notatka": ("META_notatka_zarzad-01.png", True),
    "28-p9-start": ("kadr-P9-start.png", False),
    "29-p9-skill": ("kadr-P9.png", False),
    "30-exit-start": ("kadr-exit-start.png", False),
    "31-p10-start": ("kadr-P10-start.png", False),
    "32-p10-goog": ("kadr-P10.png", False),
    "33-goog-notatka": ("GOOG_notatka_zarzad-01.png", True),
}


def przytnij(obraz, margines=12):
    tlo = Image.new(obraz.mode, obraz.size, (255, 255, 255))
    ramka = ImageChops.difference(obraz, tlo).getbbox()
    if not ramka:
        return obraz
    x0, y0, x1, y1 = ramka
    return obraz.crop((max(0, x0 - margines), max(0, y0 - margines),
                       min(obraz.width, x1 + margines), min(obraz.height, y1 + margines)))


def main(rendery):
    for stary in CEL.glob("[0-9][0-9]-*"):
        stary.unlink()
    for klucz, (plik, dokument) in ZRZUTY.items():
        zrodlo = (Path(rendery) if dokument else ORYGINALY) / plik
        if not zrodlo.exists():
            print(f"BRAK: {zrodlo}")
            continue
        obraz = Image.open(zrodlo).convert("RGB")
        if dokument:
            obraz = przytnij(obraz)
        if obraz.width > MAKS_SZEROKOSC:
            obraz = obraz.resize((MAKS_SZEROKOSC, round(obraz.height * MAKS_SZEROKOSC / obraz.width)), Image.LANCZOS)
        cel = CEL / (klucz + (".jpg" if dokument else ".png"))
        if dokument:
            obraz.save(cel, quality=85, optimize=True)
        else:
            # Kadry terminala mają mało kolorów - paleta 64 barw zmniejsza plik kilkukrotnie bez utraty czytelności.
            obraz.quantize(colors=64, method=Image.Quantize.MEDIANCUT).save(cel, optimize=True)
        print(f"{cel.name}: {obraz.width}x{obraz.height}, {cel.stat().st_size // 1024} KB")


if __name__ == "__main__":
    main(sys.argv[1])

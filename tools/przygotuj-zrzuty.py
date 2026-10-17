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
    "01-zaufanie": ("kadr-zaufanie.png", False),
    "02-p1-zrodla": ("kadr-P1.png", False),
    "03-p2-ledger": ("kadr-P2.png", False),
    "04-p3-grafiki": ("kadr-P3.png", False),
    "05-p4-weryfikacja": ("kadr-P4.png", False),
    "06-p5-pulapki": ("kadr-P5.png", False),
    "07-p6-wynik": ("kadr-P6.png", False),
    "08-xlsx-podsumowanie": ("META_DCF-01.png", True),
    "09-xlsx-wrazliwosc": ("META_DCF-07.png", True),
    "10-pptx-liczby": ("META_prezentacja-02.png", True),
    "11-pptx-projekt": ("META_prezentacja-06.png", True),
    "12-pptx-wycena": ("META_prezentacja-07.png", True),
    "13-p8-kontrola": ("kadr-P8.png", False),
    "14-docx-notatka": ("META_notatka_zarzad-01.png", True),
    "15-p9-skill": ("kadr-P9.png", False),
    "16-p10-goog": ("kadr-P10.png", False),
    "17-goog-notatka": ("GOOG_notatka_zarzad-01.png", True),
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

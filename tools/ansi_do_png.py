# Render wyjścia terminala z herdr (ANSI truecolor) do PNG przez HTML + Playwright.
# Użycie: herdr agent read <agent> --source visible --format ansi > x.ansi
#         PYTHONUTF8=1 python tools/ansi_do_png.py x.ansi x.png [--z-polem] [--terminal]
#   --z-polem     zostawia dolne pole wpisywania Claude Code (kadry „początek kroku” z wklejonym promptem)
#   --terminal    wygląd okna Windows Terminal z kartą PowerShell (kadry konsoli)
import html, re, sys
from pathlib import Path

SGR = re.compile(r"\x1b\[([0-9;]*)m")
INNE = re.compile(r"\x1b\[[0-9;?]*[A-Za-ln-z]")
ZNACZNIK = re.compile(r"<[^>]+>")
KONTO = re.compile(r"(\\Users\\)[^\\\s]+(\\)")


def scal_puste_wiersze(linie, maks=2):
    """Skraca każdą serię pustych wierszy (po zdjęciu znaczników same białe znaki) do najwyżej `maks`."""
    wynik, puste = [], 0
    for linia in linie:
        puste = puste + 1 if not ZNACZNIK.sub("", linia).strip() else 0
        if puste <= maks:
            wynik.append(linia)
    return wynik


def utnij_pole_wpisywania(tekst):
    """Usuwa dolny pasek Claude Code (pole wpisywania z podpowiedzią i linię trybu) - od przedostatniej linii z samych ─."""
    linie = tekst.replace("\r", "").split("\n")
    gole = [INNE.sub("", SGR.sub("", l)).strip() for l in linie]
    ramki = [i for i, l in enumerate(gole) if l and set(l) == {"─"}]
    return "\n".join(linie[:ramki[-2]]) if len(ramki) >= 2 else tekst


def skroc_ramki(tekst, szerokosc=104):
    """Skraca linie z samych ─ (ramka pola wpisywania na całą szerokość terminala) i usuwa spacje na końcu linii,
    żeby kadr z krótką treścią nie był szeroki i pomniejszany w instrukcji."""
    wynik = []
    for linia in tekst.replace("\r", "").split("\n"):
        gola = INNE.sub("", SGR.sub("", linia)).strip()
        if gola and set(gola) == {"─"}:
            linia = linia.replace("─" * len(gola), "─" * szerokosc)
        wynik.append(linia.rstrip())
    return "\n".join(wynik)


def anonimizuj(tekst):
    """Zamienia nazwę konta Windows w ścieżkach (C:\\Users\\<konto>\\...) na „kursant”."""
    return KONTO.sub(r"\1kursant\2", tekst)


def ansi_do_html(tekst):
    stan = {"fg": None, "bg": None, "b": False}
    wynik = []
    for linia in tekst.replace("\r", "").split("\n"):
        linia = INNE.sub("", linia)
        poz = 0
        czesci = []
        for m in SGR.finditer(linia + "\x1b[m"):
            fragment = linia[poz:m.start()] if m.start() <= len(linia) else linia[poz:]
            if fragment:
                styl = []
                if stan["fg"]: styl.append(f"color:rgb({stan['fg']})")
                if stan["bg"]: styl.append(f"background:rgb({stan['bg']})")
                if stan["b"]: styl.append("font-weight:bold")
                czesci.append(f'<span style="{";".join(styl)}">{html.escape(fragment)}</span>')
            poz = m.end()
            kody = [int(k) if k else 0 for k in m.group(1).split(";")]
            i = 0
            while i < len(kody):
                k = kody[i]
                if k == 0: stan.update(fg=None, bg=None, b=False)
                elif k == 1: stan["b"] = True
                elif k == 22: stan["b"] = False
                elif k in (38, 48) and i + 4 < len(kody) + 0 and kody[i + 1] == 2:
                    stan["fg" if k == 38 else "bg"] = ",".join(map(str, kody[i + 2:i + 5])); i += 4
                elif k == 39: stan["fg"] = None
                elif k == 49: stan["bg"] = None
                i += 1
        wynik.append("".join(czesci))
    while wynik and not ZNACZNIK.sub("", wynik[-1]).strip(): wynik.pop()
    while wynik and not ZNACZNIK.sub("", wynik[0]).strip(): wynik.pop(0)
    return "\n".join(scal_puste_wiersze(wynik))


SZEROKOSC_MIN = 920  # szerokość kolumny instrukcji: kadry węższe od niej nie są ani rozciągane, ani pomniejszane


def strona_html(tresc, terminal=False):
    if terminal:
        return f"""<!doctype html><meta charset="utf-8"><body style="margin:0;background:#fff">
<div id="t" style="display:inline-block;box-sizing:border-box;min-width:{SZEROKOSC_MIN}px;border:1px solid #3a3a3a;
background:#0c0c0c;font-family:'Segoe UI',sans-serif">
<div style="display:flex;align-items:flex-end;height:36px;background:#202020;padding-left:8px;font-size:12px">
<div style="display:flex;align-items:center;gap:8px;min-width:200px;padding:9px 12px;background:#0c0c0c;color:#fff;border-radius:6px 6px 0 0">
<span style="background:#2b5797;color:#fff;font:bold 9px Consolas,monospace;padding:1px 3px;border-radius:2px">&gt;_</span>
<span style="flex:1">Windows PowerShell</span><span style="color:#aaa">✕</span></div>
<div style="color:#ccc;padding:9px 12px">+&nbsp;&nbsp;⌄</div>
<div style="margin-left:auto;color:#ccc;padding:9px 16px;word-spacing:22px">_ ☐ ✕</div></div>
<pre style="margin:0;padding:10px 14px 14px;color:#cccccc;background:#0c0c0c;
font:15px/1.35 'Cascadia Mono','Consolas',monospace">{tresc}</pre></div>"""
    return f"""<!doctype html><meta charset="utf-8"><body style="margin:0;background:#0c0c0c">
<pre id="t" style="display:inline-block;box-sizing:border-box;min-width:{SZEROKOSC_MIN}px;margin:0;padding:16px 20px;
color:#cccccc;background:#0c0c0c;font:15px/1.35 'Cascadia Mono','Consolas',monospace">{tresc}</pre>"""


def main(wej, wyj, z_polem=False, terminal=False):
    from playwright.sync_api import sync_playwright

    tekst = anonimizuj(Path(wej).read_text(encoding="utf-8", errors="replace"))
    if z_polem:
        tekst = skroc_ramki(tekst)
    elif not terminal:
        tekst = utnij_pole_wpisywania(tekst)
    strona = strona_html(ansi_do_html(tekst), terminal)
    with sync_playwright() as p:
        b = p.chromium.launch()
        s = b.new_page(viewport={"width": 1600, "height": 800}, device_scale_factor=1)
        s.set_content(strona)
        s.locator("#t").screenshot(path=wyj)
        b.close()


if __name__ == "__main__":
    argumenty = [a for a in sys.argv[1:] if not a.startswith("--")]
    main(argumenty[0], argumenty[1], z_polem="--z-polem" in sys.argv, terminal="--terminal" in sys.argv)

# Render wyjścia terminala z herdr (ANSI truecolor) do PNG przez HTML + Playwright.
# Użycie: herdr agent read <agent> --source visible --format ansi > x.ansi
#         PYTHONUTF8=1 python tools/ansi_do_png.py x.ansi x.png
import html, re, sys
from pathlib import Path

SGR = re.compile(r"\x1b\[([0-9;]*)m")
INNE = re.compile(r"\x1b\[[0-9;?]*[A-Za-ln-z]")
ZNACZNIK = re.compile(r"<[^>]+>")


def scal_puste_wiersze(linie, maks=2):
    """Skraca każdą serię pustych wierszy (po zdjęciu znaczników same białe znaki) do najwyżej `maks`."""
    wynik, puste = [], 0
    for linia in linie:
        puste = puste + 1 if not ZNACZNIK.sub("", linia).strip() else 0
        if puste <= maks:
            wynik.append(linia)
    return wynik


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

def main(wej, wyj):
    from playwright.sync_api import sync_playwright

    tresc = ansi_do_html(Path(wej).read_text(encoding="utf-8", errors="replace"))
    strona = f"""<!doctype html><meta charset="utf-8"><body style="margin:0;background:#0c0c0c">
<pre id="t" style="display:inline-block;margin:0;padding:16px 20px;color:#cccccc;background:#0c0c0c;
font:15px/1.35 'Cascadia Mono','Consolas',monospace">{tresc}</pre>"""
    with sync_playwright() as p:
        b = p.chromium.launch()
        s = b.new_page(viewport={"width": 1600, "height": 800}, device_scale_factor=1)
        s.set_content(strona)
        s.locator("#t").screenshot(path=wyj)
        b.close()

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])

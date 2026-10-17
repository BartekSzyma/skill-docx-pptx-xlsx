from ansi_do_png import scal_puste_wiersze


def test_scal_puste_wiersze_zostawia_najwyzej_dwa():
    assert scal_puste_wiersze(["a", "", "", "", "", "b"]) == ["a", "", "", "b"]


def test_scal_puste_wiersze_traktuje_spacje_i_znaczniki_jako_puste():
    assert scal_puste_wiersze(["a", "<span> </span>", "   ", "", "b"], maks=1) == ["a", "<span> </span>", "b"]


def test_utnij_pole_wpisywania_usuwa_dolny_pasek():
    from ansi_do_png import utnij_pole_wpisywania
    tekst = "odpowiedź\n" + "─" * 10 + "\n❯ podpowiedź\n" + "─" * 10 + "\n  auto mode on"
    assert utnij_pole_wpisywania(tekst) == "odpowiedź"


def test_skroc_ramki_skraca_tylko_linie_z_samych_kresek():
    from ansi_do_png import skroc_ramki
    tekst = "\x1b[38;2;136;136;136m" + "─" * 168 + "\x1b[0m\n❯ wpis   \n─ a ─"
    assert skroc_ramki(tekst, 10) == "\x1b[38;2;136;136;136m" + "─" * 10 + "\x1b[0m\n❯ wpis\n─ a ─"


def test_anonimizuj_zamienia_nazwe_konta_w_sciezce():
    from ansi_do_png import anonimizuj
    assert anonimizuj(r"plik C:\Users\Jan.Kowalski\AppData\x.py") == r"plik C:\Users\kursant\AppData\x.py"
    assert anonimizuj(r"C:\Programowanie\x") == r"C:\Programowanie\x"


def test_anonimizuj_zamienia_folder_budowy_na_folder_kursanta():
    from ansi_do_png import anonimizuj
    assert anonimizuj(r"▝▝   C:\Programowanie\ALX vibecoding\pakiet-budowa\analizy-spolek") == \
        r"▝▝   C:\Users\kursant\Documents\analizy-spolek"
    assert anonimizuj(r"PS C:\tmp\demo\analizy-spolek> claude") == r"PS C:\Users\kursant\Documents\analizy-spolek> claude"
    assert anonimizuj(r"C:\Users\Bartek\AppData\Local\Temp\claude\C--Programowanie-ALX-vibecoding-pakiet-budowa-analizy-spolek\a") == \
        r"C:\Users\kursant\AppData\Local\Temp\claude\C--Users-kursant-Documents-analizy-spolek\a"

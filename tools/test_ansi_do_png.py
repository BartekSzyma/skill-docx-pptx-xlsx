from ansi_do_png import scal_puste_wiersze


def test_scal_puste_wiersze_zostawia_najwyzej_dwa():
    assert scal_puste_wiersze(["a", "", "", "", "", "b"]) == ["a", "", "", "b"]


def test_scal_puste_wiersze_traktuje_spacje_i_znaczniki_jako_puste():
    assert scal_puste_wiersze(["a", "<span> </span>", "   ", "", "b"], maks=1) == ["a", "<span> </span>", "b"]


def test_utnij_pole_wpisywania_usuwa_dolny_pasek():
    from ansi_do_png import utnij_pole_wpisywania
    tekst = "odpowiedź\n" + "─" * 10 + "\n❯ podpowiedź\n" + "─" * 10 + "\n  auto mode on"
    assert utnij_pole_wpisywania(tekst) == "odpowiedź"

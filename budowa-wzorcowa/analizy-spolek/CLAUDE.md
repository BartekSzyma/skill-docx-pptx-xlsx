# Analizy spółek - zasady projektu

Te zasady obowiązują w każdej rozmowie w tym projekcie.

## Fakty i ledger

- Każda informacja o spółce (liczba, data, nazwa projektu, produktu itp.) trafia najpierw do ledgera, czyli pliku `TICKER/ledger.json` w folderze spółki, razem ze źródłem (dokument, strona) i dosłownym cytatem.
- Do dokumentów wolno wpisać tylko to, co jest w ledgerze.
- Liczby do dokumentów wstawiają skrypty z ledgera. Nie przepisuj liczb ręcznie.
- Założenia (np. tempo wzrostu, koszt kapitału) to nie fakty: zapisuj je jako założenia z uzasadnieniem, oddzielnie od faktów.

## Weryfikacja ledgera (bramki)

- Po każdej zmianie ledgera uruchom `narzedzia/weryfikuj.py TICKER`: bramka 1 (skrypt: cytaty, strony, wartości) i bramka 2 (niezależny model sonnet: czy cytat potwierdza wpis). Wynik w `TICKER/weryfikacja/` (raport.md, status.json).
- Każdy skrypt tworzący dokumenty na początku wywołuje `bramka.wymagaj_weryfikacji(TICKER)`; nie omijaj tego.
- Błędy poprawiamy w ledgerze na podstawie źródła, nigdy przez osłabianie bramek.
- Znak liczby jak w raporcie: kwota w nawiasie (wypływ, strata) to wartość ujemna w ledgerze.

## Praca z raportem 10-K

- Nigdy nie czytaj całego raportu 10-K naraz.
- Wyszukuj frazy skryptem `narzedzia/szukaj.py TICKER "fraza"` i czytaj tylko potrzebne strony z `TICKER/zrodla/10k/strony/strona-NNN.txt` (NNN = numer wydrukowany w stopce strony).

## Język i pliki

- Teksty dla ludzi piszemy po polsku z polskimi znakami.
- Bez długich myślników (— ani –), zamiast nich krótki dywiz -.
- Pliki zapisujemy w UTF-8.
- Nazwy plików bez polskich znaków.

## Skill dla innych spółek

`/pakiet-analityczny TICKER` (`.claude/skills/pakiet-analityczny/`) - uogólniona wersja całego procesu z META, z własnymi kopiami skryptów w `scripts/`. Folder `narzedzia/` to pierwotna wersja zbudowana dla META; zmiany w procesie wprowadzaj w skillu.

## Narzędzia

Python z `.venv` (`.venv\Scripts\python.exe`), zależności w `requirements.txt`.

- `narzedzia/pobierz_10k.py TICKER` - pobiera najnowszy 10-K z SEC i dzieli go na strony.
- `narzedzia/szukaj.py TICKER "fraza"` - szuka frazy w stronach raportu.
- `narzedzia/pobierz_rynek.py TICKER` - pobiera kurs akcji (Yahoo) i rentowność 10-letnich obligacji USA (FRED).
- `narzedzia/pobierz_grafiki.py TICKER "zapytanie" --projekt F-NN` - pobiera zdjęcia z Wikimedia Commons (tylko CC0, domena publiczna, CC BY, CC BY-SA) z autorem i licencją do `TICKER/zrodla/grafiki/`. Zdjęcia do dokumentów bierzemy tylko z wpisów klasy "grafika" w ledgerze.
- `narzedzia/generuj_xlsx.py TICKER` - model DCF w Excelu (`TICKER/wyniki/TICKER_DCF.xlsx`) z ledgera, przeliczony w LibreOffice, wynik w `TICKER/wyniki/wycena.json`, podgląd PNG w `TICKER/wyniki/podglad/`. Liczby wyceny do prezentacji i notatki bierzemy tylko z `wycena.json`.
- `narzedzia/generuj_pptx.py TICKER` - prezentacja `TICKER/wyniki/TICKER_prezentacja.pptx` z ledgera i `wycena.json` (id wpisu przy każdej liczbie), podgląd `podglad/slajd-NN.png`. Uwaga: LibreOffice rysuje ujemne słupki z python-pptx jako dodatnie, więc wartości ujemnych nie pokazujemy na wykresach słupkowych w prezentacji.
- `narzedzia/generuj_docx.py TICKER` - notatka dla zarządu `TICKER/wyniki/TICKER_notatka_zarzad.docx`, dokładnie 1 strona A4 (skrypt sprawdza przez PDF), czcionka min. 9 pt.
- `narzedzia/sprawdz_liczby.py TICKER` - każda liczba w pptx i docx musi mieć pokrycie w ledgerze albo `wycena.json`; uruchamiaj po każdej zmianie generatorów. Liczb policzonych przez nas (sumy, zmiany %) nie wpisujemy do dokumentów, dopóki nie trafią do ledgera.
- `narzedzia/libreoffice.py`, `narzedzia/formaty.py` - wspólne funkcje: konwersja przez LibreOffice, podgląd PNG, polski zapis liczb.
- `narzedzia/sprawdz_ledger.py TICKER` - sprawdza ledger (cytaty dosłowne, liczby w cytatach, odwołania założeń) i wypisuje tabelę. Uruchamiaj po każdej zmianie ledgera.

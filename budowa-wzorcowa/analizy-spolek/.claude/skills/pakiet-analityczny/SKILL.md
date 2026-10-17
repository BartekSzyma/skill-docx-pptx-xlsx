---
name: pakiet-analityczny
description: Pakiet analityczny spółki giełdowej z USA na podstawie raportu rocznego 10-K - ledger faktów z cytatami, weryfikacja dwiema bramkami, model DCF w Excelu, prezentacja PowerPoint i jednostronicowa notatka dla zarządu, wszystko po polsku. Użyj zawsze, gdy użytkownik wpisze /pakiet-analityczny TICKER albo poprosi o analizę, wycenę DCF, prezentację lub notatkę o spółce notowanej w USA (np. "zrób pakiet dla GOOGL", "przeanalizuj Apple z raportu 10-K", "wycena Microsoftu i notatka dla zarządu"), nawet jeśli nie użyje słowa "pakiet".
argument-hint: TICKER
---

# Pakiet analityczny spółki (10-K -> ledger -> DCF -> prezentacja i notatka)

Ticker spółki: **$ARGUMENTS** (dalej TICKER; zamień na wielkie litery). Jeśli argument jest pusty, zapytaj użytkownika o ticker i nie zaczynaj pracy.

Ten skill odtwarza sprawdzony proces zbudowany dla Meta Platforms (META). Wszystkie pliki spółki trafiają do folderu `TICKER/` w katalogu projektu (katalog, w którym pracujesz):

```
TICKER/
  zrodla/10k/      oryginal.htm, info.json, spis.json, strony/strona-NNN.txt
  zrodla/rynek/    kurs-RRRR-MM-DD.json, dgs10-RRRR-MM-DD.csv, pobranie-RRRR-MM-DD.json
  zrodla/grafiki/  wybrane zdjęcia i kandydaci.json
  ledger.json      jedyne źródło faktów i liczb
  weryfikacja/     bramka1.json, bramka2.json, raport.md, status.json
  tresc.json       plan treści prezentacji i notatki (teksty z polami {ID})
  wyniki/          TICKER_DCF.xlsx, wycena.json, TICKER_prezentacja.pptx, TICKER_notatka_zarzad.docx, podglad/
```

## Zasady (obowiązują przez cały proces)

Pakiet ma być wiarygodny: każdą liczbę da się prześledzić do strony raportu albo do jawnego założenia. Dlatego:

- **Ledger najpierw.** Każda informacja o spółce (liczba, data, nazwa projektu) trafia najpierw do `TICKER/ledger.json` razem ze źródłem i dosłownym cytatem. Do dokumentów wolno wpisać tylko to, co jest w ledgerze (albo w `wyniki/wycena.json`, który model liczy z ledgera).
- **Liczby wstawiają skrypty.** W dokumentach nie przepisujesz liczb ręcznie: w `tresc.json` piszesz pola `{F-07}`, a skrypty wstawiają wartości. Ledger to jedyne miejsce, gdzie liczby przepisujesz z raportu, i dlatego pilnują go bramki.
- **Założenia to nie fakty.** Tempo wzrostu, koszt kapitału itp. zapisujesz jako klasę `zalozenie` z uzasadnieniem odwołującym się do id faktów.
- **Nie czytaj całego 10-K naraz** (to 100-300 stron). Wyszukuj frazy skryptem `szukaj.py` i czytaj tylko potrzebne pliki stron.
- **Język:** teksty dla ludzi po polsku z polskimi znakami, bez długich myślników (zamiast nich krótki dywiz -). Pliki w UTF-8, nazwy plików bez polskich znaków.
- **Nie omijaj kontroli.** Gdy bramka albo kontrola zgłasza błąd, poprawiasz dane na podstawie źródła; nigdy nie osłabiasz skryptów, żeby błąd przeszedł.

## Przygotowanie

Polecenia uruchamiasz z katalogu projektu. Skróty używane niżej:

- `S` = `.claude/skills/pakiet-analityczny/scripts`
- `PY` = Python z wirtualnego środowiska: `.venv/Scripts/python.exe` (Windows) albo `.venv/bin/python` (Linux/macOS).

1. Jeśli nie ma `.venv`, utwórz je i zainstaluj zależności: `python -m venv .venv`, potem `PY -m pip install -r S/requirements.txt`.
2. Sprawdź, że są: LibreOffice (`soffice`; na Windowsie zwykle `C:\Program Files\LibreOffice\program\soffice.exe`) i program `claude` w PATH (bramka 2). Jeśli czegoś brakuje, powiedz użytkownikowi, czego brakuje, i zatrzymaj się.
3. Jeśli `TICKER/` już istnieje, zapytaj, czy budować od nowa, czy kontynuować od ostatniego kroku.

## Krok 1. Czy spółka pasuje do pakietu

```
PY S/sprawdz_spolke.py TICKER
```

Skrypt sprawdza, czy spółka składa raport 10-K w SEC i czy nie jest bankiem ani ubezpieczycielem (kody SIC 6000-6199 i 6300-6411). Przy kodzie wyjścia 1 przekaż użytkownikowi komunikat skryptu (jest po polsku) i **zakończ pracę**. Wyjaśnienie dla użytkownika: model DCF liczy przepływy z działalności operacyjnej, a u banków i ubezpieczycieli dług i inwestycje są częścią działalności, więc taka wycena nie ma sensu. Spółki zagraniczne składają 20-F zamiast 10-K i też nie pasują.

## Krok 2. Źródła

```
PY S/pobierz_10k.py TICKER
PY S/pobierz_rynek.py TICKER
```

`pobierz_10k.py` pobiera najnowszy 10-K, dzieli go na strony w miejscach page-break i nazywa pliki numerem ze stopki (`strona-089.txt`). Sprawdź numerację, zanim zaczniesz z niej korzystać:

- Przeczytaj spis treści (zwykle `strona-002.txt`) i porównaj 3-4 pozycje (np. Item 1A, Item 7, Item 8) z pierwszą linią odpowiednich plików stron.
- Jeśli skrypt ostrzega, że numer znalazł na mniej niż 80% stron, obejrzyj ostatnie linie kilku plików i dopisz wzór stopki w `WZORY_STOPKI` w `pobierz_10k.py` (to poprawka pobierania, nie osłabianie kontroli).
- Strony bez numeru mają nazwę `strona-bez-numeru-NNN.txt`; w ledgerze podaj wtedy `strona` jako `"okładka (bez numeru)"` dla pierwszej strony albo opis typu `"bez numeru"` i dokładny `plik`.

Znajdź strony sprawozdań: `PY S/szukaj.py TICKER "Consolidated Statements of"` i indeks sprawozdań w Item 8. Uwaga: wyciągnięty tekst bywa sklejony bez spacji w miejscach znaczników (np. `Item 1B.Unresolved`), więc szukaj krótszych fraz.

## Krok 3. Ledger

Przeczytaj `references/ledger.md`: format wpisu, klasy, stałe klucze (z nich korzystają skrypty) i zasady cytatów. Najważniejsze:

- **Fakty z 10-K** (kwoty w mln USD jak w raporcie, rok bazowy R = ostatni rok obrotowy): przychody i zysk operacyjny za 3 lata, za rok R zysk netto, amortyzacja, nakłady inwestycyjne, zysk przed opodatkowaniem, podatek; na koniec roku R gotówka, papiery wartościowe (jeśli są), dług długoterminowy (i krótkoterminowy, jeśli jest); przychody i wynik segmentów, jeśli spółka je raportuje.
- **Liczba akcji z pierwszej strony** raportu: osobny wpis na każdą klasę akcji (np. Alphabet: A, B i C), z datą, której dotyczy. Model sumuje wszystkie wpisy `shares_...`.
- **4-6 faktów o najważniejszych projektach** spółki i plan nakładów inwestycyjnych na kolejny rok, jeśli raport go podaje.
- **2-3 najważniejsze ryzyka** z Item 1A, każde z cytatem nazywającym ryzyko (nagłówek ryzyka, a nie tylko zdanie o działalności).
- **Dane rynkowe** z plików w `zrodla/rynek/` (kurs, rentowność 10-letnich obligacji USA).
- **Założenia DCF** według `references/zalozenia.md`, spójne ze sobą (nakłady a amortyzacja, okres rezydualny).

Nazwy pozycji różnią się między spółkami (np. "Revenues", "Total net sales", "Net revenues"; "Income from operations" albo "Operating income"; "Purchases of property and equipment" albo "Capital expenditures"). Klucz w ledgerze jest zawsze ten sam, a cytat i opis zawierają nazwę pozycji dokładnie tak, jak w raporcie. Jeśli czegoś nie ma w raporcie, nie zgaduj: pomiń wpis albo (dla wymaganych pozycji) powiedz o tym użytkownikowi.

Zapisz ledger jako `TICKER/ledger.json` (lista wpisów, UTF-8).

## Krok 4. Zdjęcia projektów

Dla 3-4 projektów z ledgera szukaj zdjęć tylko na Wikimedia Commons:

```
PY S/pobierz_grafiki.py TICKER "zapytanie po angielsku" --projekt F-NN --limit 5
```

Skrypt przyjmuje tylko CC0, domenę publiczną, CC BY i CC BY-SA, pomija logotypy, zrzuty ekranu i SVG, a pliki, których Commons nie wydaje (HTTP 403), pomija z komunikatem. Potem:

1. Obejrzyj pobrane zdjęcia (narzędziem do czytania obrazów) i wybierz po jednym, które naprawdę pokazuje dany projekt (produkt, obiekt). Nie wybieraj zdjęć, na których projektu prawie nie widać, ani portretów przypadkowych osób, jeśli jest zdjęcie samego produktu.
2. Usuń pozostałe pliki i ich wpisy z `kandydaci.json`.
3. Dopisz wybrane do ledgera jako klasa `grafika` (format w `references/ledger.md`). Przypisz zdjęcie do faktu, który rzeczywiście pokazuje (np. zdjęcie zwykłych okularów nie ilustruje faktu o innym modelu okularów).
4. Jeśli do projektu nie ma dobrego zdjęcia, zapisz to i powiedz użytkownikowi na końcu.

## Krok 5. Weryfikacja dwiema bramkami (do zielonego statusu)

```
PY S/weryfikuj.py TICKER
```

- **Bramka 1** (skrypt, bez AI): cytat występuje na podanej stronie, wartość jest w cytacie (dodatnia nie w nawiasie, ujemna jako "(1,234)"), grafika ma plik, autora, licencję i adres, założenie ma uzasadnienie.
- **Bramka 2** (osobny proces `claude -p --model sonnet` bez narzędzi, partie po 6): czy cytat naprawdę potwierdza wpis (liczba, rok, jednostka, zakres, opis).

Czytaj `TICKER/weryfikacja/raport.md`, poprawiaj wpisy w ledgerze **na podstawie źródła** (sprawdź stronę skryptem i przeczytaj ją) i uruchamiaj weryfikację ponownie, aż `status.json` ma `"ok": true`. Typowe poprawki: liczba z sąsiedniej kolumny (inny rok), znak (kwota w nawiasie to wartość ujemna), cytat, który nie nazywa ryzyka. Jeśli wpisu nie da się potwierdzić, usuń go i powiedz o tym użytkownikowi. Każda zmiana ledgera unieważnia status, więc po zmianach zawsze weryfikuj ponownie.

## Krok 6. Model DCF w Excelu

```
PY S/generuj_xlsx.py TICKER
```

Skrypt sam sprawdza status weryfikacji i skrót ledgera, buduje model wyłącznie z formuł (dane wejściowe niebieskie, z id i cytatem w komentarzu), przelicza go w LibreOffice, sprawdza, że nie ma błędów, zapisuje `wyniki/wycena.json` i podgląd `wyniki/podglad/xlsx-strona-NN.png`. Obejrzyj podgląd (wykresy czytelne, nic się nie ucina). Jeśli wynik różni się od kursu o więcej niż 50%, wskaż użytkownikowi założenia, które za to najbardziej odpowiadają (tabela wrażliwości pomaga); założeń sam nie zmieniaj.

## Krok 7. Plan treści `tresc.json`

Przeczytaj `references/tresc.md` i napisz `TICKER/tresc.json`: karty z liczbami, opcjonalny slajd o projekcie bez zdjęcia, slajdy projektów ze zdjęciami (2-3 punkty każdy) oraz 3 wnioski i 3 projekty do notatki. Każda liczba w tekście to pole `{ID}` (np. `{F-01}`, `{F-09|abs}`, `{wycena.roznica_proc|1}`); fakty bez liczby podpinasz polem `"id"`. Lata i daty możesz pisać zwykłym tekstem. Pisz tylko to, co mówią cytaty w ledgerze; nie dopisuj wniosków, których źródło nie potwierdza (np. "większość nakładów trafia do X", jeśli żaden cytat tego nie mówi).

## Krok 8. Prezentacja i notatka

```
PY S/generuj_pptx.py TICKER
PY S/generuj_docx.py TICKER
```

- Prezentacja (16:9, ok. 8 slajdów): tytuł, spółka w liczbach, opcjonalny slajd dodatkowy, slajdy projektów ze zdjęciami, wycena DCF (z wyraźnym "To są ZAŁOŻENIA, nie fakty"), ryzyka i źródła.
- Notatka: dokładnie 1 strona A4 (skrypt sprawdza przez PDF i kończy pracę, jeśli stron jest więcej; wtedy skróć teksty w `tresc.json`, nie zmniejszaj czcionki poniżej 9 pt).
- Obejrzyj **każdy** podgląd `wyniki/podglad/slajd-NN.png` i `docx-strona-01.png`: tekst ucięty, nachodzący na siebie, liczba rozbita między wiersze. Poprawiaj przez skrócenie tekstów w `tresc.json` i generuj ponownie.
- Wykresy słupkowe pokazują tylko wartości dodatnie: LibreOffice rysuje ujemne słupki z python-pptx jako dodatnie, więc skrypt odmawia takiego wykresu. Stratę opisz w punktach.

## Krok 9. Kontrola liczb

```
PY S/sprawdz_liczby.py TICKER
```

Każda liczba w pptx i docx musi mieć pokrycie w ledgerze albo w `wycena.json` (z zaokrągleniem i zamianą mln/mld). Liczba bez pokrycia to zwykle liczba policzona ręcznie albo wpisana w `tresc.json` zamiast pola `{ID}`: popraw `tresc.json` (albo, jeśli to nowy fakt, dodaj go do ledgera i przejdź znów przez weryfikację), wygeneruj dokumenty i uruchom kontrolę ponownie.

## Na koniec

Napisz użytkownikowi krótko, po polsku:
- za jaki rok jest raport i ile wpisów każdej klasy ma ledger,
- wynik weryfikacji (ile poprawek było potrzebnych i jakich),
- wynik wyceny w 3-4 zdaniach prostym językiem (wartość jednej akcji wobec kursu) i, przy różnicy ponad 50%, które założenia najbardziej za nią odpowiadają,
- listę slajdów i ścieżki plików w `TICKER/wyniki/`,
- czego nie udało się znaleźć (brakujące fakty, projekty bez zdjęć) i jakie były ograniczenia.

Przypomnij, że materiał jest edukacyjny i nie stanowi rekomendacji inwestycyjnej.

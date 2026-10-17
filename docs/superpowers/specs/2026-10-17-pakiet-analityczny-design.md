# Instrukcja: pakiet analityczny spółki (DCF xlsx + pptx + docx) z ledgerem źródeł i skillem - projekt

Data: 2026-10-17. Autor ustaleń: Bartek (kurs ALX vibecoding). Spisane przez Claude.

Legenda: **[ustalone]** - decyzja użytkownika; **[decyzja Claude]** - wybór Claude, do zmiany przez użytkownika;
**[wykonawca]** - zostawione wykonawcy. Użytkownik zrezygnował z dalszych pytań („pomiń dalsze pytania, decyzje
wypisz w raporcie”), więc wszystkie [decyzja Claude] trafiają też do `docs/raport-koncowy.md`.

## 1. Po co to jest

Projekt analogiczny do instrukcji bota Discord (`C:\Programowanie\ALX vibecoding\discord-instrukcja`) [ustalone].
Pokazuje uczestnikom kursu, jak Claude Code na bazie sprawozdań spółki **Meta Platforms** generuje [ustalone]:

1. model **DCF w xlsx** z kluczowymi wykresami;
2. prezentację **pptx** z 3-4 grafikami lub zdjęciami najważniejszych projektów spółki;
3. **jednostronicowy docx** z podsumowaniem dla zarządu;

a na koniec, jak spiąć to w **skill**, któremu podaje się tylko ticker, np. `pakiet-analityczny goog`, i dostaje
się tę samą paletę dokumentów [ustalone].

Wymagania jakościowe [ustalone]:
- **ledger**: każdy fakt o spółce ma źródło (dokument lub strona www + numer strony) i cytat;
- po zbudowaniu ledgera **nowy model** sprawdza poprawność każdego cytatu;
- materiał dla uczestnika wyjaśnia **dokładnie i prostym językiem**, co się dzieje i dlaczego (po co ledger, po co
  weryfikacja itd.).

Forma zajęć [ustalone]: **prowadzący robi pokaz**, a uczestnicy dostają materiał do **odtworzenia krok po kroku
w domu**. External review pomijamy [ustalone], tak jak przy bocie Discord. Miarą sukcesu jest pakiet wygenerowany
od zera wyłącznie promptami z instrukcji oraz działający skill (przebieg dla GOOG) [decyzja Claude, analogicznie
do Discorda].

## 2. Produkty (w `C:\Programowanie\ALX vibecoding\skill-docx-pptx-xlsx\`)

1. **`cwiczenia-pakiet-analityczny.html`** - jedna strona HTML offline (wzorzec i silnik z `cwiczenia-discord.html`):
   treść jako dane (`INSTRUKCJA`), bloki `tekst | komenda | sprawdz | uwaga | wazne | mac | zrzut | prompt | plik`
   plus nowe [decyzja Claude]:
   - **`dlaczego`** - ramka „Co się dzieje i po co” prostym językiem przy każdym kroku;
   - **`schemat`** - wbudowany diagram SVG przepływu: źródła -> ledger -> bramka 1 (skrypt) -> bramka 2 (nowy model)
     -> generatory -> xlsx/pptx/docx -> skill.
   HTML nadaje się też do wyświetlenia na pokazie (duże nagłówki, schemat) [decyzja Claude: jeden materiał zamiast
   osobnej prezentacji dla prowadzącego].
2. **Budowa wzorcowa** w `budowa-wzorcowa\` - pliki wygenerowane przez Claude Code z promptów instrukcji (dowód, że
   prompty działają, i punkt odniesienia „jeśli utkniesz”): ledger, raporty weryfikacji, `META_DCF.xlsx`,
   `META_prezentacja.pptx`, `META_notatka_zarzad.docx`, skill i przebieg GOOG.
3. **Narzędzia** `tools\` (z projektu Discord): `ansi_do_png.py`, `osadz-zrzuty.mjs`, `wypisz-prompt.mjs`,
   `zaznacz-zrzuty.py`; nowe: render dokumentów do PNG przez LibreOffice (xlsx/pptx/docx -> PDF -> PNG).
4. **Testy** `npm test` (node --test): typografia (brak U+2014/U+2013 i encji), struktura instrukcji, prompty bez
   ścieżek autora, każdy zrzut użyty raz, obecność kluczowych ramek („dlaczego” przy każdym prompcie).
5. **`docs\raport-koncowy.md`** - raport dla użytkownika: co powstało, decyzje, czasy i liczba wywołań, problemy.

## 3. Co buduje uczestnik (projekt w folderze `analizy-spolek\`)

Wszystko w **Pythonie** [decyzja Claude: jeden język, biblioteki openpyxl, python-pptx, python-docx; skille
Anthropic xlsx/pptx/docx są dostępne w Claude Code na koncie Pro i Claude może z nich korzystać, ale wynik
ma być powtarzalny, więc dokumenty powstają ze skryptów]. Układ: `analizy-spolek\CLAUDE.md` (zasady),
`analizy-spolek\narzedzia\` (skrypty), `analizy-spolek\META\` (źródła, ledger, weryfikacja, wyniki). Później skill w
`analizy-spolek\.claude\skills\pakiet-analityczny\` i `analizy-spolek\GOOG\`.

### 3.1 Źródła [decyzja Claude]
- **Raport roczny 10-K za 2025** z SEC EDGAR (Meta: CIK 1326801, złożony 2026-01-29, `meta-20251231.htm`).
  Ticker -> CIK przez `https://www.sec.gov/files/company_tickers.json` (sprawdzone, działa także dla GOOG).
  SEC wymaga nagłówka User-Agent z kontaktem - uczestnik podaje **własny e-mail** (w prompcie pole do uzupełnienia).
- **Numer strony = numer drukowany w stopce 10-K.** Dokument HTML ma znaczniki `page-break-after:always`
  (sprawdzone: 134 podziały), a każda strona kończy się numerem. Skrypt dzieli dokument na pliki
  `strona-NNN.txt` z numerem ze stopki. Claude **nigdy nie czyta całego 10-K** (2,3 MB), tylko wyszukuje frazy
  skryptem i czyta wybrane strony.
- **Dane rynkowe**: kurs akcji z Yahoo Finance (chart API, sprawdzone), rentowność 10-letnich obligacji USA z FRED
  (`DGS10`, sprawdzone). Kopia odpowiedzi zapisana w `zrodla\` z datą pobrania; „strona” = n/d (www).
- **Grafiki**: zdjęcia z **Wikimedia Commons** (API sprawdzone; np. Ray-Ban Meta), z autorem, licencją i adresem
  w ledgerze oraz podpisem na slajdzie. Brak sensownego zdjęcia -> grafika wygenerowana z danych (wykres).
  Zdjęcia prasowe Meta i grafiki z wyszukiwarki - zakazane (licencje).
- Zakres: **tylko 10-K** + dane rynkowe [decyzja Claude: najprostszy łańcuch dowodowy; liczba akcji z okładki 10-K].

### 3.2 Ledger (`META\ledger.json`) [decyzja Claude]
Cztery klasy wpisów, bo nie wszystko w DCF jest faktem:
- **fakt** - z 10-K: `zrodlo.dokument`, `zrodlo.url`, `zrodlo.strona` (numer ze stopki), **dosłowny cytat**,
  wartość, jednostka, okres, `klucz` (stała nazwa używana przez generatory, np. `przychody_2025`);
- **dana_rynkowa** - www: adres, data pobrania, cytat z zapisanej kopii (np. wiersz CSV), „strona”: `n/d (www)`;
- **zalozenie** - WACC, wzrost, marża, stopa terminalna: **bez cytatu**, z uzasadnieniem prostym językiem;
- **grafika** - plik, adres strony pliku na Commons, autor, licencja.
Rozmiar: ok. 20-30 faktów, kilka danych rynkowych, 6-8 założeń, 3-4 grafiki (koszt i czas na planie Pro).
Liczba akcji = **suma wszystkich klas** z okładki 10-K (Meta: A + B; Alphabet: A + B + C) - jawny fakt w ledgerze.

### 3.3 Weryfikacja: dwie bramki [decyzja Claude]
- **Bramka 1 (skrypt, deterministyczna)**: czy cytat występuje na podanej stronie (po normalizacji spacji,
  cudzysłowów i myślników); czy w cytacie występuje wartość (z tolerancją formatu: 200,966 / 200966); dla danych
  rynkowych - czy cytat jest w zapisanej kopii. Wynik: `META\weryfikacja\bramka1.json`.
- **Bramka 2 (nowy model)**: osobny proces `claude -p --model sonnet` **bez narzędzi i bez naszej rozmowy**
  (świeży kontekst + inny model niż domyślny Opus), partiami po kilka wpisów: dostaje wpis i tekst strony,
  odpowiada JSON-em, czy cytat potwierdza wartość, jednostkę, okres i zakres (cała spółka vs segment, GAAP).
  Wynik: `bramka2.json` + raport po polsku `raport.md`.
- **Bramka jest bramką**: `weryfikacja\status.json` zawiera skrót SHA-256 ledgera; generatory odmawiają pracy,
  gdy status nie jest „ok” albo ledger zmieniono po weryfikacji.
- **Test pułapek** (osobny prompt): kopia ledgera z dwoma podrzuconymi błędami (zmieniony cytat; poprawny cytat,
  zła wartość) - pierwszy łapie skrypt, drugi tylko model. To pokazuje, po co są obie bramki.

### 3.4 Dokumenty [decyzja Claude]
- **`META_DCF.xlsx`**: arkusze Podsumowanie, Dane historyczne, Założenia, DCF (prognoza 5 lat na formułach),
  Wrażliwość (WACC x wzrost terminalny, formuły), Ledger (wszystkie wpisy ze źródłami i cytatami). Komórki wejściowe
  niebieskie, z identyfikatorem wpisu ledgera obok i komentarzem z cytatem. Wykresy natywne Excela: przychody
  i marża operacyjna, FCF w prognozie, mostek wartość firmy -> wartość na akcję, wrażliwość (formatowanie
  warunkowe). Po zapisie **przeliczenie LibreOffice** i kontrola braku błędów (#REF!, #DIV/0! itd.); wynik
  wyceny odczytany z przeliczonego pliku do `wyniki\wycena.json` - pptx i docx biorą liczby wyceny stąd
  (jedno źródło prawdy: formuły Excela, bez drugiej implementacji DCF w Pythonie).
- **`META_prezentacja.pptx`** (ok. 8 slajdów): tytuł, spółka w liczbach (wykres), 3-4 slajdy projektów ze
  zdjęciem (podpis: autor, licencja), wycena, ryzyka, źródła. Liczby z ledgera z identyfikatorem (np. [F-07]).
  Render do PNG przez LibreOffice i przegląd slajdów przez Claude.
- **`META_notatka_zarzad.docx`**: dokładnie **jedna strona** (kontrola: konwersja do PDF = 1 strona),
  wnioski, kluczowe liczby, wycena vs kurs, projekty, ryzyka, przypisy z identyfikatorami ledgera, dopisek
  „materiał edukacyjny, nie rekomendacja inwestycyjna”.
- **Kontrola liczb**: skrypt wyciąga wszystkie liczby z tekstu pptx i docx i sprawdza, że każda pochodzi z ledgera
  lub `wycena.json` (z wyjątkiem lat i numeracji). Liczba spoza ledgera = błąd.

### 3.5 Skill [decyzja Claude]
- **Skill projektowy** `analizy-spolek\.claude\skills\pakiet-analityczny\` (SKILL.md + `scripts\` przeniesione
  z `narzedzia\` i uogólnione na dowolny ticker). Wywołanie: `/pakiet-analityczny GOOG` w folderze
  `analizy-spolek`. Wynik w `analizy-spolek\GOOG\`. Powód: nie dotyka globalnej konfiguracji Claude Code
  uczestnika, da się go skopiować do `~/.claude/skills`, żeby działał wszędzie (wskazówka w instrukcji).
- Zakres: **niefinansowe spółki z USA składające 10-K**; bank, ubezpieczyciel, spółka spoza EDGAR -> jasny
  komunikat zamiast złej wyceny.
- Skill wykonuje te same kroki i te same bramki; założenia dobiera model z uzasadnieniem (klasa `zalozenie`).

## 4. Struktura instrukcji [decyzja Claude]

0. **Zanim zaczniesz** - wymagania systemowe [ustalone przez użytkownika w trakcie]: Claude Code (plan Pro,
   `claude update`), **Python 3.11+**, **LibreOffice** (darmowy; Claude przelicza nim formuły i robi podglądy, żeby
   sam sprawdzić swoją pracę), **MS Office opcjonalnie** (bez licencji otwiera pliki tylko do odczytu - wystarczy do
   obejrzenia wyników); folder, PowerShell z paska Eksploratora; czas i koszt limitu (zmierzone w budowie).
1. **Jak to działa** - schemat, słowa-klucze prostym językiem: 10-K, ledger, cytat, bramka, DCF, WACC.
2. Kroki z promptami P1..Pn, każdy: „Co się dzieje i po co” -> prompt -> „Sprawdź:” -> zrzut wyniku.
   P1 zasady + źródła; P2 ledger; P3 weryfikacja; P4 test pułapek; P5 xlsx; P6 pptx; P7 docx + kontrola liczb;
   P8 skill; P9 `/pakiet-analityczny GOOG`.
3. **Dla prowadzącego** - przebieg pokazu z czasami z budowy wzorcowej.
4. **Typowe problemy** - SEC 403 (brak User-Agent), LibreOffice nie w PATH, plik otwarty w Excelu (blokada zapisu),
   krzaki w polskich znakach (`PYTHONUTF8=1`), bramka czerwona (co zrobić), limit Pro.
5. Ramka „Gdy coś pójdzie nie tak” (szablon pytania do Claude Code).

## 5. Jak powstaje instrukcja (proces budowy)

Jak przy Discordzie: nowa zakładka herdr, `CLAUDE_CONFIG_DIR=C:\Users\Bartek\.claude-kurs` (czysty profil bez
globalnego `CLAUDE.md` i wtyczek, zalogowany), model domyślny (Opus 5.5), tryb domyślny (auto mode), `cwd` =
`budowa-wzorcowa\analizy-spolek`. Prompty wysyłane **dokładnie w brzmieniu z HTML** (`wypisz-prompt.mjs`).
Pytanie kontrolne na starcie: czy sesja nie widzi globalnego `CLAUDE.md`. Gdy prompt nie daje dobrego wyniku -
poprawka promptu, nie kodu; po poprawkach pełny przebieg od zera. Pomiar czasu i liczby wywołań. Zrzuty:
dokumenty przez LibreOffice -> PNG, terminal 2-4 kadry przez `ansi_do_png.py`. Nie ruszamy innych zakładek herdr.
Bezpiecznik: prompt, który nie przechodzi po 3 poprawkach, opisuję w raporcie zamiast kręcić się w kółko.

## 6. Cele, nie-cele, anty-cele
- Cel: uczestnik w domu odtwarza pakiet dla Meta i uruchamia skill dla innej spółki; rozumie, po co ledger i bramki.
- Nie-cel: profesjonalna wycena, rekomendacja inwestycyjna, obsługa banków i spółek spoza USA, symulator.
- Anty-cele: liczba w dokumencie bez pokrycia w ledgerze; „cytat” wymyślony przez model; zdjęcie bez licencji;
  instrukcja, która działa tylko w środowisku autora.

## 7. Ograniczenia
Polszczyzna z diakrytykami, bez długich myślników; nazwy generowanych plików ASCII; UTF-8; Windows (wstawki
„Na Macu:” bez testu); plan Pro uczestników; dane na dzień budowy (kurs i rentowność się zmienią - instrukcja
mówi, że wyniki uczestnika będą inne).

## 8. Zostawione wykonawcy
Dokładny dobór faktów, układ arkuszy i slajdów, styl wizualny, treść założeń (z uzasadnieniem), dobór zdjęć.

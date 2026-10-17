# Raport końcowy: instrukcja „Pakiet analityczny spółki” (DCF xlsx + pptx + docx, ledger, skill)

Data: 2026-10-17 (praca w nocy, bez pytań do użytkownika - zgodnie z prośbą decyzje są wypisane niżej).

## 1. Co powstało

| Plik / folder | Co to jest |
|---|---|
| `C:\Programowanie\ALX vibecoding\skill-docx-pptx-xlsx\cwiczenia-pakiet-analityczny.html` | **Instrukcja dla uczestników** (offline, dwuklik, 3,1 MB): wymagania systemowe, schemat przepływu, słowniczek, 10 kroków z promptami (P1-P10), przy każdym ramka „Co się dzieje i po co”, punkt „Sprawdź”, 17 zrzutów z budowy wzorcowej, sekcja dla prowadzącego z czasami i scenariuszem pokazu, typowe problemy. |
| `C:\Programowanie\ALX vibecoding\skill-docx-pptx-xlsx\budowa-wzorcowa\analizy-spolek\` | Kopia wyniku budowy wzorcowej (przebieg 2): `CLAUDE.md`, `narzedzia\`, skill `.claude\skills\pakiet-analityczny\`, `META\` i `GOOG\` (ledger, weryfikacja, wyniki). |
| `C:\Programowanie\ALX vibecoding\skill-docx-pptx-xlsx\budowa-wzorcowa\analizy-spolek\META\wyniki\META_DCF.xlsx` | Model DCF Meta (formuły, 3 wykresy, wrażliwość, arkusz Ledger, komentarze z cytatami). |
| `C:\Programowanie\ALX vibecoding\skill-docx-pptx-xlsx\budowa-wzorcowa\analizy-spolek\META\wyniki\META_prezentacja.pptx` | Prezentacja Meta (8 slajdów, 3 zdjęcia z Wikimedia Commons z autorem i licencją). |
| `C:\Programowanie\ALX vibecoding\skill-docx-pptx-xlsx\budowa-wzorcowa\analizy-spolek\META\wyniki\META_notatka_zarzad.docx` | Notatka dla zarządu, 1 strona. |
| `C:\Programowanie\ALX vibecoding\skill-docx-pptx-xlsx\budowa-wzorcowa\analizy-spolek\GOOG\wyniki\` | Ten sam komplet dla Alphabet, zrobiony samym `/pakiet-analityczny GOOG`. |
| `C:\Programowanie\ALX vibecoding\pakiet-budowa\analizy-spolek\` | **Działający folder z budowy** (z `.venv`): gotowy do pokazu „z gotowego folderu” na zajęciach. |
| `C:\Programowanie\ALX vibecoding\pakiet-budowa\przebieg1\` | Przebieg 1 (przed poprawką założeń) - do usunięcia, jeśli niepotrzebny. |
| `C:\Programowanie\ALX vibecoding\skill-docx-pptx-xlsx\docs\superpowers\specs\2026-10-17-pakiet-analityczny-design.md` | Projekt (spec). |
| `C:\Programowanie\ALX vibecoding\skill-docx-pptx-xlsx\docs\superpowers\plans\2026-10-17-pakiet-analityczny.md` | Plan. |

Repo git: `C:\Programowanie\ALX vibecoding\skill-docx-pptx-xlsx` (gałąź `main`, lokalnie; nic nie publikowałem). Testy: `npm test` - 16/16.

## 2. Jak to sprawdziłem

- Wzorem projektu Discord: nowa zakładka herdr, **czysty profil** Claude Code (`C:\Users\Bartek\.claude-kurs`, bez
  Twojego `CLAUDE.md` i wtyczek; sprawdzone pytaniem kontrolnym), model domyślny (Opus 5.5), auto mode, folder poza
  repo. Prompty wysyłane dokładnie w brzmieniu z HTML (jedyna podmiana: `[TWÓJ E-MAIL]` -> `kurs.alx@example.com`).
- **Przebieg 1** (P1-P10) wykazał jeden problem merytoryczny (niżej), poprawiłem prompty P2 i P6.
- **Przebieg 2 od zera** z finalnymi promptami: wszystko przeszło bez ręcznych poprawek kodu i bez zatrzymań.
- Obejrzałem dokumenty (render LibreOffice -> PNG), HTML w Chromium (0 błędów konsoli, „Kopiuj” działa, 17/17 zrzutów).

### Czasy przebiegu 2 (praca Claude)

| Krok | Czas |
|---|---|
| P1 źródła | 2 min 23 s |
| P2 ledger | 4 min 0 s |
| P3 zdjęcia | 3 min 1 s |
| P4 weryfikacja | 4 min 38 s |
| P5 pułapki | 1 min 19 s |
| P6 Excel | 6 min 31 s |
| P7 prezentacja | 6 min 23 s |
| P8 notatka + kontrola liczb | 4 min 1 s |
| P9 skill | 11 min 27 s |
| P10 `/pakiet-analityczny GOOG` | 8 min 13 s |
| **Razem** | **ok. 52 min** (Meta P1-P8: ok. 32 min) |

Bramka 2 (`claude -p --model sonnet`): Meta 7 wywołań (partie po 6), test pułapek 1, GOOG ok. 8. Budowa szła na Twoim
koncie Max przez profil kursowy; uczestnicy mają Pro - czasy będą podobne, limit to osobna sprawa (ostrzeżenie w instrukcji).

### Wyniki merytoryczne

- **Meta:** 69 wpisów ledgera (37 faktów, 2 dane rynkowe, 27 założeń, 3 grafiki), obie bramki 69/69 i 39/39. Bramki
  złapały prawdziwe błędy w P4 (znak nakładów inwestycyjnych; zbyt ogólny cytat ryzyka) - pokazane na zrzucie.
  Wycena: **345 USD/akcję wobec kursu 709 USD (-51%)**, WACC 11,1%.
- **Test pułapek:** zmieniony cytat złapał skrypt, liczbę z sąsiedniej kolumny tylko model, blokada zatrzymała dokumenty.
- **Alphabet (GOOG):** 72 wpisy, bramki 72/72 i 43/43, akcje A+B+C = 12 097 mln, notatka 1 strona.
  Wycena **111 USD wobec 337 USD (-67%)**. Tylko 2 zdjęcia (Commons nie ma zdjęcia TPU Ironwood) - skill to zgłosił
  zamiast wstawiać nietrafione zdjęcie. Skill sam poprawił po drodze swoje skrypty (numery stron z kropką,
  zapis „$16.0 billion”), bez łagodzenia kontroli - zostawiłem to celowo jako element pokazu.

## 3. Decyzje podjęte bez Ciebie (do weryfikacji)

1. **Forma:** jedna instrukcja HTML (wzorzec `cwiczenia-discord`) zamiast osobnej prezentacji dla prowadzącego; nadaje
   się do wyświetlania na pokazie (schemat, duże nagłówki). Dodałem bloki „Co się dzieje i po co” i schemat SVG.
2. **Źródło:** tylko raport 10-K z SEC EDGAR + kurs (Yahoo chart API) + rentowność 10Y (FRED DGS10). „Numer strony” =
   numer drukowany w stopce 10-K (dokument dzielony po znacznikach page-break); dla www „n/d (www)” + kopia pliku z datą.
3. **Ledger w 4 klasach:** fakt / dana rynkowa / założenie (bez cytatu, z uzasadnieniem) / grafika.
4. **„Nowy model sprawdza cytaty” rozbite na dwie bramki:** skrypt (czy cytat jest na stronie, czy liczba w cytacie)
   + osobny proces `claude -p --model sonnet` bez narzędzi i bez naszej rozmowy (czy cytat potwierdza wpis). Status ze
   skrótem SHA-256 ledgera blokuje generatory po zmianie ledgera.
5. **Dodatkowy krok „test pułapek” (P5)** - pokazuje, po co są obie bramki.
6. **Zdjęcia tylko z Wikimedia Commons** (CC0/PD/CC BY/CC BY-SA), autor i licencja w ledgerze i pod zdjęciem.
7. **Python wszędzie** (openpyxl, python-pptx, python-docx); dokumenty generowane skryptami z ledgera, a Claude korzysta
   ze skilli Anthropic xlsx/pptx/docx jako wiedzy. Model DCF liczy się **formułami Excela**; LibreOffice przelicza plik,
   wynik trafia do `wycena.json` (jedno źródło liczb wyceny dla pptx i docx).
8. **Kontrola liczb** (`sprawdz_liczby.py`) jako ostatnia bramka: każda liczba w pptx/docx musi mieć pokrycie w ledgerze
   i id wpisu obok.
9. **Skill projektowy** (`analizy-spolek\.claude\skills\pakiet-analityczny`), nie globalny - nie rusza konfiguracji
   uczestnika; w instrukcji wskazówka, jak go skopiować do `~\.claude\skills`. Zakres: niefinansowe spółki z USA
   składające 10-K (banki, ubezpieczyciele, 20-F -> komunikat i stop).
10. **Wymagania systemowe** (Twoja uwaga w trakcie): Python 3.11+, LibreOffice wymagany (Claude sam przelicza formuły
    i ogląda podglądy), MS Office opcjonalny (bez licencji tylko odczyt; do zmiany założeń LibreOffice Calc). Komendy
    `winget` i wstawka dla Maca (Homebrew) - **wstawki dla Maca nie testowałem**.
11. **E-mail do SEC:** w prompcie P1 pole `[TWÓJ E-MAIL]` do uzupełnienia przez uczestnika (bez niego SEC daje 403).
12. **Zrzuty:** kadry terminala z przebiegu 2 (bez dolnego paska Claude Code) i strony dokumentów z LibreOffice.

## 4. Słabe punkty i ryzyka (bez upiększania)

- **Wycena wychodzi wyraźnie poniżej kursu** (Meta -51%, Alphabet -67%). To nie błąd modelu, tylko założenia:
  rentowność 10Y 5,1% + premia 5% daje WACC 10-11%, a nakłady na AI zjadają FCF w latach 2026-2027. W przebiegu 1
  (Meta -83%) był to **rzeczywisty błąd założeń** (nakłady 35% wobec amortyzacji 12% ciągnięte w nieskończoność) -
  poprawiłem P2 (spójność nakładów i amortyzacji, osobne założenia dla okresu rezydualnego) i P6 (wskazanie założeń,
  gdy różnica > 50%). Instrukcja mówi wprost, że celem nie jest trafienie w kurs. Jeśli wolisz wyniki bliższe rynkowi,
  trzeba świadomie zmienić założenia (np. premia 4%, beta z danych) - nie zrobiłem tego, żeby nie stroić modelu pod kurs.
- **Długość:** ok. 52 min pracy Claude na całość - na żywo trzeba pokazywać wybrane kroki (scenariusz w sekcji 12).
- **Limit Pro:** nie zmierzyłem zużycia limitu na planie Pro (budowa na Max). Ostrzeżenie jest w instrukcji.
- **Wyniki uczestników będą inne** (kurs, rentowność, wybór założeń i zdjęć przez model) - instrukcja to mówi.
- **Zdjęcia:** dla części projektów Commons nie ma zdjęć (GOOG: 2 zamiast 3-4); skill to uczciwie raportuje.
- **Zrzut z pytaniem o zaufanie** pokazuje ścieżkę `C:\tmp\demo\analizy-spolek`, a jeden kadr (P2) ścieżkę tymczasową
  z nazwą Twojego konta Windows. Nazwa konta: naprawione w rundzie 2 (renderer wstawia `kursant`, p. 7).
- **Typografia:** test zakazu długich myślników pomija `budowa-wzorcowa\` - są tam dosłowne cytaty z raportów SEC
  (z długimi myślnikami) i pliki napisane przez Claude w budowie; reszta repo jest sprawdzana.

## 5. Problemy techniczne po drodze (rozwiązane)

- Pierwsza budowa w folderze wewnątrz repo widziała status git repo autora - przeniosłem budowę poza repo.
- Git Bash zamienia argumenty zaczynające się od `/` na ścieżki (`/exit`, `/pakiet-analityczny`) - `MSYS_NO_PATHCONV=1`.
- Narzędzie Bash psuło ukośniki odwrotne w edycjach - poprawki robione przez pliki; dodałem test, który wyłapuje
  zgubione ukośniki w ścieżkach w instrukcji.

## 6. Do decyzji użytkownika

- Publikacja (publiczne repo + GitHub Pages jak przy gicie) - nic nie publikowałem.
- Czy zostawić `C:\Programowanie\ALX vibecoding\pakiet-budowa\przebieg1\`.
- Czy dostroić założenia DCF (premia za ryzyko, beta) - patrz p. 4.

## 7. Runda 2 (2026-10-17): zrzuty początku kroków, animacje, schemat bramek, konstruktor pytania

Co doszło:
- **Zrzuty „początek kroku”** dla P1-P10 i `/exit`: prawdziwy Claude Code (ten sam czysty profil), prompt wklejony
  w pole wpisywania **bez Enter** (`tools/kadry-startowe.sh`), więc nic nie poszło do modelu. Długie prompty Claude Code
  zwija do `[Pasted text #N +M lines]` - zostawiłem to tak, jak jest, bo to zobaczy uczestnik, i opisałem w podpisie.
  P5 (krótki) widać w całości, `/pakiet-analityczny GOOG` i `/exit` są wpisane znak po znaku.
- **Zrzuty konsoli** pod poleceniami: `python --version` i `claude --version` wykonane naprawdę; `winget install ...`
  i `claude` pokazane jako wklejone, przed Enter.
- Dodatkowy zrzut końca kroku 7 (`kadr-P7`, wcześniej nieużyty). Razem 33 zrzuty, HTML 3,47 MB. Na zrzutach
  startowych ramka pola jest skrócona do 100 kolumn, żeby obraz nie był pomniejszany (bez tego tekst miał ok. 9 px).
- **Animacje (HTML/CSS, nie GIF):** otwieranie PowerShella z paska adresu Eksploratora; wklejenie P1 i pierwsze sekundy
  pracy; `/exit`, `claude`, podpowiedź skilla i `/pakiet-analityczny GOOG`. Startują, gdy są widoczne na ekranie.
- **Schemat bramek** w sekcji 5 (`tools/schemat-bramki.svg`, osadzony w HTML).
- **Linki do 6 dokumentów Office** (xlsx, pptx, docx dla META i GOOG): tabela w sekcji 0 oraz w punktach „Sprawdź”.
- **„Lub poproś Claude”** w punktach „Sprawdź” kroków 1-10 i w tabeli typowych problemów.
- **Sekcja 12** przemianowana na orientacyjny czas trwania zadań: zakres ±50% i lista czynników.
- **Konstruktor pytania** w „Gdy coś pójdzie nie tak” (krok + 4 pola, podgląd na żywo, Kopiuj). Zastąpił stały szablon.
- Testy: `npm test` 19/19 (było 16; doszły: animacje, konstruktor, istnienie plików z linków) i `pytest` dla
  renderera 5/5 (było 3; doszły: anonimizacja ścieżek, skracanie ramek).

Decyzje:
1. **Prawdziwe zrzuty zamiast makiety** tam, gdzie się dało (prompt wklejony bez wysyłania). Makieta jest tylko w
   animacjach: kolory i logo skopiowane z prawdziwego zrzutu, ścieżka `C:\Users\kursant\Documents\analizy-spolek`.
2. **Animacje w HTML/CSS zamiast GIF**: ostre na każdym ekranie, zero bajtów obrazów, tekst do zaznaczenia.
   GIF-y z kilkunastu klatek dodałyby ok. 1-3 MB.
3. **Eksplorator jako makieta**, a nie zrzuty mojego pulpitu: zrzuty pokazałyby Twoje foldery w panelu nawigacji,
   a wpisywanie w pasek adresu wymagałoby sterowania Twoim pulpitem.
4. **winget nie uruchomiony naprawdę**: na tym komputerze zainstalowane programy mogłyby się zaktualizować. Podpis mówi,
   co pojawi się po Enter (pobieranie, pytanie o zgodę na warunki: Y).
5. **Gdzie nie dodałem „poproś Claude”**: tworzenie folderu i instalacja przed pierwszym uruchomieniem (Claude jeszcze
   nie działa - zamiast tego ramka „jeśli masz już Claude Code, zleć mu instalację”), `/exit` i ponowne uruchomienie
   w kroku 10 (Claude nie uruchomi sam siebie). W kroku 2 dopisek jest, ale z prośbą, żeby raz sprawdzić cytat samemu:
   to jedyny moment, w którym człowiek sprawdza źródło bez pośrednictwa AI.
6. Anonimizacja: renderer zamienia nazwę konta w ścieżkach `C:\Users\<konto>\` na `kursant` (dotyczyło zrzutu kroku 2).

Słabe punkty tej rundy:
- Zrzuty „początek” dla P1-P4 i P6-P9 wyglądają prawie tak samo (zwinięty prompt). Są, bo o to prosiłeś, ale
  niosą mało informacji; jeśli chcesz krótszą instrukcję, można zostawić tylko P1, P5 i P10.
- Zrzuty startowe pochodzą z nowej sesji, więc nad polem nie ma odpowiedzi z poprzedniego kroku (w prawdziwej
  rozmowie będzie).
- Zrzuty konsoli pokazują folder `C:\tmp\demo\analizy-spolek`, a animacje `C:\Users\kursant\Documents\analizy-spolek`.
- Mac: nadal nietestowany (dopisałem sposób otwarcia terminala w folderze, bez sprawdzenia).

## 8. Runda 3 (2026-10-17): Windows Terminal, rozwinięte prompty, LibreOffice

- **Jedna szerokość:** wszystkie zrzuty mają w instrukcji 920 px (kolumna tekstu). Kadry konsoli renderowane w tej
  szerokości, kadry startowe z węższego okna terminala (104 kolumny), więc nie są pomniejszane.
- **Windows Terminal zamiast PowerShella:** zrzuty konsoli w wyglądzie Windows Terminal; animacja: prawy przycisk
  w folderze, „Otwórz w terminalu”, Windows Terminal w tym folderze. W wymaganiach doszedł Windows Terminal
  (`winget install Microsoft.WindowsTerminal` dla Windows 10); pasek adresu + `powershell` został jako zapasowa droga.
- **Rozwinięte prompty:** zrzuty początku kroków P1-P4 i P6-P9 zrobione z dwukrotnym wklejeniem (drugie wklejenie
  rozwija `[Pasted text]`). Długie prompty Claude Code pokazuje od końca (ok. 20 ostatnich linii) - napisane w podpisie.
  P5 wklejony raz (krótki prompt po drugim wklejeniu byłby wstawiony dwa razy). Każdy podpis przypomina o podwójnym
  wklejeniu i o tym, że ścieżki u uczestnika będą inne.
- **Animacja P1:** Ctrl+V (zwinięty), Ctrl+V drugi raz (rozwinięty, „ctrl+g to edit in Notepad”), Enter, praca.
  Nazwy klawiszy widać 2,4 s.
- **Ctrl+G:** w kroku 1 dopisana wskazówka, jak poprawić `[TWÓJ E-MAIL]` po wklejeniu (Claude Code otwiera prompt
  w Notatniku). Podpowiedź pochodzi z interfejsu Claude Code; samego edytowania w Notatniku nie testowałem.
- **LibreOffice zostaje wymagany także przy MS Office** (decyzja użytkownika po teście: Office z licencją przez COM
  przeliczył Excela, policzył strony Worda i wyeksportował slajd w 13 s, ale prompty i skill używają LibreOffice,
  a Office bez licencji i na Macu tego nie zastąpi). Wymagania mówią to wprost.
- **winget:** identyfikatory `TheDocumentFoundation.LibreOffice` (26.8.1.1), `Python.Python.3.12` (3.12.10)
  i `Microsoft.WindowsTerminal` (1.25) sprawdzone przez `winget show` (bez instalacji). Dopisane: zgoda administratora
  przy LibreOffice, pytanie o warunki źródła przy pierwszym użyciu, ponowne otwarcie terminala po instalacji.

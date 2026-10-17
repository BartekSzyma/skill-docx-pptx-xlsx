# Ledger: format, klasy, klucze, cytaty

`TICKER/ledger.json` to lista wpisów (JSON, UTF-8). Każdy wpis ma stałe pola; skrypty korzystają z pól `klucz`, `wartosc`, `jednostka`, `zrodlo`.

## Klasy i id

| klasa | id | do czego |
|---|---|---|
| `fakt` | F-01, F-02, ... | informacja z raportu 10-K (liczba albo krótki tekst) |
| `dana_rynkowa` | R-01, ... | kurs akcji, rentowność obligacji (pliki w `zrodla/rynek/`) |
| `zalozenie` | Z-01, ... | założenia modelu DCF z uzasadnieniem |
| `grafika` | G-01, ... | zdjęcie projektu z Wikimedia Commons |

Id nadawaj kolejno w obrębie klasy, bez luk. Nie zmieniaj id istniejących wpisów, gdy dopisujesz nowe (dopisuj na końcu klasy), bo uzasadnienia założeń i `tresc.json` odwołują się do id.

## Pola wpisu

- `id`, `klasa`, `klucz` - klucz to stała nazwa po angielsku bez spacji (tabela niżej),
- `opis` - po polsku, co dokładnie to jest (np. "Przychody ogółem", "Liczba akcji klasy C w obrocie"),
- `wartosc` - liczba (bez separatorów tysięcy) albo krótki tekst; `jednostka` - "mln USD", "mld USD", "%", "szt.", "mln szt."...; `okres` - rok ("2025"), data ("2025-12-31") albo opis okresu,
- `zrodlo` - `{"dokument", "plik", "url", "strona"}`:
  - `dokument`: dla 10-K zawsze w formacie **`"<Nazwa spółki z okładki> - raport roczny 10-K za <rok> r."`** (skrypty biorą nazwę spółki z części przed " - "),
  - `plik`: ścieżka pliku strony względem katalogu projektu, np. `"GOOGL/zrodla/10k/strony/strona-052.txt"`,
  - `url`: adres dokumentu z `zrodla/10k/info.json`,
  - `strona`: numer ze stopki jako liczba (np. `52`), numer z prefiksem jako tekst (`"F-3"`), dla okładki `"okładka (bez numeru)"`; dla danych z internetu `"n/d (www)"`,
- `cytat` - dosłowny fragment tekstu źródła (fakt, dana rynkowa),
- `data_pobrania` - tylko dane rynkowe,
- `uzasadnienie` - tylko założenia: 1-3 zdania prostym językiem z odwołaniem do id faktów (np. "(F-01, F-02)").

Grafika: `id`, `klasa: "grafika"`, `klucz` (`photo_<slug>`), `plik` (np. `"GOOGL/zrodla/grafiki/waymo.jpg"`), `opis` (co przedstawia), `projekt` (id faktu, którego dotyczy), `autor`, `licencja`, `zrodlo: {"dokument": "Wikimedia Commons", "url": <strona pliku na Commons>, "licencja_url": ...}`, `data_pobrania`. Dane bierz z `zrodla/grafiki/kandydaci.json`.

## Zasady cytatu

- Cytat to **dokładny fragment** pliku strony (bramka porównuje po ujednoliceniu spacji, cudzysłowów i myślników), bez poprawiania, bez tłumaczenia i bez skracania w środku.
- Cytat zawiera **nazwę pozycji i liczbę**, żeby było jasne, czego liczba dotyczy. Dla tabel najlepiej cała linia wiersza, np. `"Revenue $ 200,966 $ 164,501 $ 134,902"`; ta sama linia może służyć trzem wpisom (różne lata). Bramka 2 sprawdza, czy rok pasuje do właściwej kolumny, więc ustal kolejność kolumn z nagłówka tabeli.
- **Znak jak w raporcie:** kwota w nawiasie (wypływ gotówki, strata) to wartość ujemna w ledgerze (np. nakłady inwestycyjne `-69691`). Bramka 1 odrzuca liczbę dodatnią, która w cytacie stoi w nawiasie.
- Kwoty w mln USD, tak jak w tabelach raportu. Jeśli raport podaje jakąś sumę tylko w mld (np. w omówieniu), zapisz ją w mld z jednostką "mld USD"; nie przeliczaj i nie sumuj sam (sumy liczy model).
- Ryzyko: cytuj nagłówek ryzyka albo zdanie, które nazywa zagrożenie i jego skutek, a nie samo zdanie o działalności (bramka 2 odrzuca takie cytaty jako "niejasne").
- Dane rynkowe: cytat to fragment zapisanego pliku, np. tablica `"close": [ ... ]` z pliku kursu albo wiersz `"2026-10-15,5.10"` z pliku DGS10. Kurs możesz zaokrąglić do centów i napisać to w opisie.

## Stałe klucze (R = rok bazowy, czyli ostatni rok obrotowy w raporcie)

Skrypty wymagają kluczy oznaczonych "tak". Rok w kluczu to rok obrotowy z raportu (dla roku kończącego się np. we wrześniu - rok "fiscal" z raportu; datę końca roku zapisz w `okres` albo w opisie).

| klucz | wymagany | uwagi |
|---|---|---|
| `revenue_{R-2}`, `revenue_{R-1}`, `revenue_{R}` | tak | przychody ogółem (Revenue / Total revenues / Net sales) |
| `operating_income_{R-2..R}` | tak | zysk (wynik) operacyjny; strata jako wartość ujemna |
| `net_income_{R}` | tak | zysk netto |
| `depreciation_amortization_{R}` | tak* | z rachunku przepływów; *jeśli raport podaje osobno: `depreciation_{R}` i `amortization_{R}` (model zsumuje) |
| `capex_{R}` | tak | zakupy rzeczowych aktywów trwałych, wartość ujemna jak w raporcie |
| `income_before_tax_{R}`, `income_tax_{R}` | tak | zysk przed opodatkowaniem, podatek dochodowy |
| `cash_and_equivalents_{R}` | tak | gotówka i ekwiwalenty na koniec roku |
| `marketable_securities_{R}` | nie | papiery wartościowe, jeśli spółka je ma (model doda do gotówki) |
| `long_term_debt_{R}` | tak | dług długoterminowy (jeśli spółka nie ma długu, wpisz 0 tylko wtedy, gdy raport to mówi, z cytatem) |
| `current_debt_{R}` albo `short_term_debt_{R}` | nie | krótkoterminowa część długu (model doda do długu) |
| `shares_<klasa>` | tak (min. 1) | z okładki, każda klasa osobno: `shares_class_a`, `shares_class_b`, `shares_class_c` albo `shares_common`; jednostka "szt." (albo "mln szt."), okres = data z okładki |
| `operating_margin_{R}` | nie | jeśli raport podaje marżę wprost |
| `ppe_net_{R}`, `ppe_net_{R-1}` | nie | przydatne do uzasadnienia amortyzacji |
| `segment_revenue_<slug>_{R}`, `segment_operating_income_<slug>_{R}` | nie | dla każdego segmentu; brak segmentów = brak wpisów |
| `capex_guidance_{R+1}_low` / `_high` | nie | plan nakładów na kolejny rok, jeśli raport go podaje (zwykle w mld USD) |
| `effective_tax_rate_{R}`, `effective_tax_rate_guidance_{R+1}_low/_high` | nie | do uzasadnienia stopy podatkowej |
| `risk_<slug>` | tak (2-3) | `wartosc` = krótka polska nazwa ryzyka (np. "zależność od reklam"), `opis` zaczyna się od "Ryzyko: ..." |
| projekty: dowolne opisowe klucze | 4-6 | np. `data_center_locations`, `daily_active_users_<miesiąc>`, `ai_strategy` |
| `share_price` | tak | klasa `dana_rynkowa`, USD |
| `us_treasury_10y_yield` | tak | klasa `dana_rynkowa`, "%" |
| założenia | tak | lista w `zalozenia.md` |

Wszystkie pozostałe fakty liczbowe model pokaże w arkuszu "Dane historyczne" automatycznie (w kolejności ledgera).

## Przykład (META, fragment)

```json
{
  "id": "F-01", "klasa": "fakt", "klucz": "revenue_2025",
  "opis": "Przychody ogółem", "wartosc": 200966, "jednostka": "mln USD", "okres": "2025",
  "zrodlo": {"dokument": "Meta Platforms, Inc. - raport roczny 10-K za 2025 r.",
             "plik": "META/zrodla/10k/strony/strona-089.txt",
             "url": "https://www.sec.gov/Archives/edgar/data/1326801/000162828026003942/meta-20251231.htm",
             "strona": 89},
  "cytat": "Revenue $ 200,966 $ 164,501 $ 134,902"
}
```

# Weryfikacja ledgera GOOG

- Data: 2026-10-17T02:32:18+00:00
- SHA-256 ledgera: `869309793930eab69ad481f5494590ebc4e896d8cdcfe93a3277458c3d83a78a`
- Wynik: **OK - ledger można używać**

## Podsumowanie

- Wpisów w ledgerze: 72 (fakt: 41, dana_rynkowa: 2, zalozenie: 27, grafika: 2)
- Bramka 1 (skrypt, cytaty i wartości): 72/72 ok
- Bramka 2 (model sonnet, fakty i dane rynkowe): 43/43 potwierdzonych
- Przeszło obie wymagane bramki: 72/72

## Problemy

Brak.

## Werdykty bramki 2

| id | werdykt | uzasadnienie |
|---|---|---|
| F-01 | potwierdza | Tabela ma kolumny 2023, 2024, 2025, a ostatnia liczba w wierszu Revenues (402,836 mln USD) należy do 2025, co zgadza się z wpisem. |
| F-02 | potwierdza | Środkowa kolumna (2024) w wierszu Revenues to 350,018 mln USD, zgodnie z wpisem. |
| F-03 | potwierdza | Pierwsza kolumna (2023) w wierszu Revenues to 307,394 mln USD, zgodnie z wpisem. |
| F-04 | potwierdza | Ostatnia kolumna (2025) w wierszu Income from operations to 129,039 mln USD, zgodnie z wpisem. |
| F-05 | potwierdza | Środkowa kolumna (2024) w wierszu Income from operations to 112,390 mln USD, zgodnie z wpisem. |
| F-06 | potwierdza | Pierwsza kolumna (2023) w wierszu Income from operations to 84,293 mln USD, zgodnie z wpisem. |
| F-07 | potwierdza | Zysk netto za 2025 (ostatnia kolumna) wynosi 132 170 mln USD, zgodnie z wpisem i rachunkiem zysków i strat. |
| F-08 | potwierdza | Amortyzacja rzeczowych aktywów trwałych w kolumnie 2025 to 21 136 mln USD, zgodnie z rachunkiem przepływów. |
| F-09 | potwierdza | Zakupy rzeczowych aktywów trwałych w 2025 to (91 447) mln USD, czyli wypływ gotówki, więc wartość ujemna jest poprawna. |
| F-10 | potwierdza | Zysk przed opodatkowaniem za 2025 wynosi 158 826 mln USD, zgodnie z kolumną 2025. |
| F-11 | potwierdza | Podatek dochodowy za 2025 wynosi 26 656 mln USD, zgodnie z ostatnią kolumną tabeli. |
| F-12 | potwierdza | Gotówka i ekwiwalenty na 31.12.2025 to 30 708 mln USD (kolumna 2025 bilansu, potwierdzone też w rachunku przepływów). |
| F-13 | potwierdza | W bilansie kolumna 2025 dla Marketable securities wynosi 96 135 mln USD (2024: 72 191), co zgadza się z wpisem na 31.12.2025. |
| F-14 | potwierdza | Long-term debt na 31.12.2025 to 46 547 mln USD (kolumna 2025; 2024: 10 883), zgodnie z wpisem. |
| F-15 | potwierdza | Property and equipment, net w kolumnie 2025 wynosi 246 597 mln USD, co odpowiada wpisowi na 31.12.2025. |
| F-16 | potwierdza | Property and equipment, net w kolumnie 2024 wynosi 171 036 mln USD, co odpowiada wpisowi na 31.12.2024. |
| F-17 | potwierdza | Effective tax rate za 2025 to 16,8% (druga kolumna), a tekst potwierdza wzrost z 2024 do 2025. |
| F-18 | potwierdza | Effective tax rate za 2024 to 16,4% (pierwsza kolumna), zgodnie z wpisem. |
| F-19 | potwierdza | Cytat i źródło podają 5 822 mln akcji klasy A na dzień 28 stycznia 2026, co zgadza się z wartością, jednostką i datą wpisu. |
| F-20 | potwierdza | Cytat i źródło podają 837 mln akcji klasy B na dzień 28 stycznia 2026, co zgadza się z wpisem. |
| F-21 | potwierdza | Cytat i źródło podają 5 438 mln akcji klasy C na dzień 28 stycznia 2026, co zgadza się z wpisem. |
| F-22 | potwierdza | W tabeli przychodów Google Services total wynosi 304 930 mln USD za 2024 i 342 721 mln USD za 2025, więc wartość odpowiada kolumnie 2025. |
| F-23 | potwierdza | Google Cloud ma 43 229 mln USD za 2024 i 58 705 mln USD za 2025, więc wartość odpowiada kolumnie 2025. |
| F-24 | potwierdza | Other Bets ma 1 648 mln USD za 2024 i 1 537 mln USD za 2025, więc wartość 1537 odpowiada właściwej kolumnie 2025. |
| F-25 | potwierdza | Tabela na stronie 36 podaje dla Google Services zysk operacyjny 139 404 mln USD w kolumnie 2025 (121 263 to 2024), zakres segmentu i jednostka się zgadzają. |
| F-26 | potwierdza | Dla Google Cloud źródło podaje 6 112 mln USD za 2024 i 13 910 mln USD za 2025, więc wartość 13 910 odpowiada właściwemu rokowi i segmentowi. |
| F-27 | potwierdza | Other Bets ma stratę operacyjną (7 515) mln USD w 2025 (w 2024: (4 444)), co zgadza się z wartością -7515 i z opisem jako strata; potwierdza to też tekst o 7,5 mld USD straty. |
| F-28 | potwierdza | Tabela przychodów na stronie 33 podaje dla Google Cloud 43 229 mln USD w kolumnie 2024 (58 705 to 2025), więc okres, segment i jednostka są poprawne. |
| F-29 | potwierdza | Cytat ze strony 4 mówi dosłownie, że Gemini 3 to najbardziej inteligentny model AI spółki, co zgadza się z opisem wpisu. |
| F-30 | potwierdza | Cytat mówi, że wszystkie 15 produktów z ponad pół miliardem użytkowników korzysta z modeli Gemini, co zgadza się z wartością 15 i opisem. |
| F-31 | potwierdza | Strona 4 wprost wymienia Ironwood jako własny układ TPU siódmej generacji, co zgadza się z opisem i wartością. |
| F-32 | potwierdza | Strona 60 podaje 242,8 mld USD portfela zamówień (remaining performance obligations) na 31 grudnia 2025, głównie Google Cloud, zgodnie z wpisem. |
| F-33 | potwierdza | Cytat ze strony 4 mówi, że Waymo świadczy w pełni autonomiczne, płatne usługi przewozowe w wielu miastach, co odpowiada opisowi. |
| F-34 | potwierdza | Strona 33 podaje rundę inwestycyjną Waymo na 16,0 mld USD ogłoszoną w lutym 2026, w znacznej większości sfinansowaną przez Alphabet. |
| F-35 | potwierdza | Strona 33 podaje umowy z 2025 r. o przejęciu Wiz za 32,0 mld USD, co zgadza się z wartością, jednostką i okresem. |
| F-36 | potwierdza | Strona 38 mówi, że w 2026 r. spółka spodziewa się znacząco zwiększyć inwestycje w infrastrukturę techniczną względem 2025 r., bez podania kwoty, jak w opisie. |
| F-37 | potwierdza | Źródło na stronie 9 stwierdza dosłownie, że w 2025 r. ponad 70% łącznych przychodów pochodziło z reklamy online, co zgadza się z wartością 70% i opisem "ponad 70%". |
| F-38 | potwierdza | Strona 33 podaje, że na 31 grudnia 2025 r. spółka miała 190 820 pracowników, czyli tyle, ile wpisano. |
| F-39 | potwierdza | Cytat ze strony 9 w pełni oddaje opis ryzyka związanego z zależnością od przychodów z reklam: niższe wydatki reklamodawców, utrata partnerów, zmiany w reklamie online i blokowanie reklam. |
| F-40 | potwierdza | Cytat ze strony 9 mówi, że rosnące inwestycje w nowe biznesy, produkty i technologie są z natury ryzykowne i mogą zaszkodzić wynikom, a tekst źródła wprost wymienia infrastrukturę i możliwości AI jako przykład tych inwestycji. |
| F-41 | potwierdza | Strona 18 zawiera cytowane zdanie o pozwach, postępowaniach regulacyjnych i sprawach dotyczących konkurencji, które mogą zaszkodzić biznesowi, reputacji i wynikom, a dalej opisuje pozwy antymonopolowe. |
| R-01 | potwierdza | Ostatni element tablicy zamknięć w pliku JSON to 336,91, zgodny z regularMarketPrice, a ostatni znacznik czasu odpowiada sesji z 16 października 2026 r. (piątek) na Nasdaq w USD. |
| R-02 | potwierdza | W źródle wiersz 2026-10-15 ma wartość 5.10 (% rentowności DGS10), co zgadza się z wartością 5,1%, okresem, jednostką i opisem wpisu. |

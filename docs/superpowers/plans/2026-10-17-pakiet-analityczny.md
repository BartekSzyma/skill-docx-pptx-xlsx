# Plan wykonania: instrukcja „pakiet analityczny spółki”

Spec: `docs/superpowers/specs/2026-10-17-pakiet-analityczny-design.md`. Wykonanie w tej sesji (budowa na żywo
w herdr wymaga sterowania zakładką; podagent tego nie zrobi). Użytkownik śpi - decyzje do raportu końcowego.

| # | Zadanie | Gotowe, gdy |
|---|---|---|
| 1 | Szkielet repo: narzędzia z projektu Discord, silnik HTML (`dlaczego`, `schemat`), testy, `package.json` | `npm test` zielony |
| 2 | Prompty P1-P9 w HTML (pierwsza wersja) | `node tools/wypisz-prompt.mjs P1` działa |
| 3 | Zakładka herdr na czystym profilu, pytanie kontrolne (brak globalnego CLAUDE.md) | odpowiedź potwierdza czysty profil |
| 4 | Budowa na żywo P1-P4 (źródła, ledger, bramki, test pułapek); poprawki promptów | bramki zielone, pułapki złapane |
| 5 | Budowa na żywo P5-P7 (xlsx, pptx, docx, kontrola liczb) | pliki otwierają się, 1 strona docx, brak błędów formuł |
| 6 | P8 skill, P9 `/pakiet-analityczny GOOG` w nowej sesji | komplet dla GOOG, bramki zielone |
| 7 | Pełny przebieg od zera (jeśli prompty były poprawiane), pomiar czasu i wywołań | przebieg bez ręcznych poprawek |
| 8 | Zrzuty (LibreOffice -> PNG, terminal), treść instrukcji, sekcja dla prowadzącego, typowe problemy | testy zielone, HTML przejrzany w Chromium |
| 9 | Raport końcowy `docs/raport-koncowy.md` | decyzje, czasy, ścieżki bezwzględne |

Bezpiecznik: prompt nieprzechodzący po 3 poprawkach -> opis w raporcie.

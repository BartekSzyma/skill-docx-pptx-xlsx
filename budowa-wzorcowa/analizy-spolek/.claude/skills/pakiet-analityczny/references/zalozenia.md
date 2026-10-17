# Założenia do modelu DCF

Założenia to klasa `zalozenie` w ledgerze: wartość, jednostka, okres i **uzasadnienie** (1-3 zdania prostym językiem z odwołaniem do id faktów). Procenty zapisuj jako liczby w procentach (18 = 18%, jednostka "%"). P1..P5 to pięć lat prognozy po roku bazowym R (np. R = 2025, prognoza 2026-2030).

## Lista (klucze stałe, z nich korzysta model)

| klucz | co | wskazówki |
|---|---|---|
| `revenue_growth_{P1..P5}` | wzrost przychodów r/r | punkt wyjścia: wzrost w dwóch ostatnich latach (F przychodów); zwykle stopniowe spowolnienie do poziomu bliskiego wzrostowi rezydualnemu |
| `operating_margin_{P1..P5}`, `operating_margin_terminal` | marża operacyjna | punkt wyjścia: marża z ostatnich lat; uwzględnij, że rosnąca amortyzacja obniża zysk operacyjny |
| `capex_pct_revenue_{P1..P5}`, `capex_pct_revenue_terminal` | nakłady inwestycyjne / przychody | punkt wyjścia: \|capex\| / przychody w roku R; jeśli raport podaje plan nakładów na P1, użyj go (środek przedziału / prognozowane przychody) |
| `da_pct_revenue_{P1..P5}`, `da_pct_revenue_terminal` | amortyzacja / przychody | punkt wyjścia: amortyzacja / przychody w roku R |
| `tax_rate` | stopa podatkowa | prognoza spółki, jeśli jest w raporcie; inaczej efektywna stopa z ostatnich lat bez jednorazowych zdarzeń (ustawowa stawka federalna w USA to 21%) |
| `beta` | beta akcji | w źródłach zwykle jej nie ma: napisz to wprost w uzasadnieniu i przyjmij rozsądną wartość dla branży |
| `equity_risk_premium` | premia za ryzyko rynkowe | typowo 4-6% dla USA; napisz, skąd wartość |
| `terminal_growth` | wzrost po P5 | 2-3%; musi być niższy niż WACC i niż rentowność obligacji (R-..) |

## Spójność (najważniejsze)

- **Nakłady a amortyzacja.** Jeśli nakłady są dużo wyższe niż amortyzacja, majątek trwały rośnie, więc amortyzacja w kolejnych latach też rośnie (nowe inwestycje zaczynają się amortyzować). Prosty sposób: policz stawkę amortyzacji z roku R (amortyzacja / średni majątek trwały netto, jeśli masz `ppe_net`) i przenieś majątek rok po roku: majątek + nakłady - amortyzacja.
- **Okres rezydualny.** Po P5 spółka rośnie już wolno, więc nakłady są tylko trochę wyższe niż amortyzacja: różnica mniej więcej równa wzrostowi rezydualnemu razy (majątek trwały netto / przychody).
- **Marża a amortyzacja.** Marża operacyjna jest po amortyzacji: jeśli amortyzacja rośnie o kilka punktów procentowych przychodów, marża operacyjna zwykle spada o podobną wielkość, chyba że uzasadnisz wzrost marży przed amortyzacją.
- **Strata operacyjna.** Dla spółki ze stratą zaplanuj ścieżkę dojścia do zysku i opisz ją w uzasadnieniach; jeśli to niewiarygodne, powiedz użytkownikowi, że DCF jest tu bardzo niepewny.
- WACC liczy model: stopa wolna od ryzyka (R-.. DGS10) + beta × premia. Dług uwzględnia tylko wtedy, gdy przekracza 10% finansowania (wtedy arkusz pokazuje ostrzeżenie: dopisz wtedy w uzasadnieniu, że WACC trzeba uzupełnić o koszt długu, i powiedz o tym użytkownikowi).

## Przykład uzasadnienia (META)

> "Spółka planuje 115-135 mld USD nakładów w 2026 r. (F-33, F-34); 52% prognozowanych przychodów to ok. 123 mld USD, czyli środek tego przedziału. W 2025 r. nakłady wyniosły ok. 35% przychodów (F-09, F-01)."

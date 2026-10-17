# Plan treści: TICKER/tresc.json

Prezentacja i notatka składają się z części stałej (budują ją skrypty ze standardowych kluczy: tytuł, wykres przychodów, wycena, ryzyka, źródła, tabela liczb) i z tekstów zależnych od spółki, które piszesz w `tresc.json`. Piszesz go po kroku 6 (potrzebne są pola z `wycena.json`).

## Pola {ID}: liczby wstawia skrypt

W tekście nie wpisujesz liczb o spółce. Wstawiasz pole, a skrypt podstawia sformatowaną wartość i dopisuje id wpisu drobnym drukiem:

| pole | wynik (przykład META) |
|---|---|
| `{F-01}` | `200 966 mln USD` (wartość z jednostką z ledgera) |
| `{F-27}` | `41%` |
| `{F-09\|abs}` | `69 691 mln USD` (bez znaku: nakłady zapisane w ledgerze jako wypływ) |
| `{F-33\|bez_jedn}` | `115` (sama liczba; jednostkę dopisz sam albo przez kolejne pole) |
| `{F-28\|2\|bez_jedn}` | `3,58` (2 miejsca po przecinku) |
| `{wycena.roznica_proc\|1}` | `-51,4` (pola z wycena.json nie mają jednostki: dopisz "%" albo "USD" w tekście) |
| `{F-35}` (wpis tekstowy) | `zależność od reklam` |

Przydatne pola z `wycena.json`: `wartosc_jednej_akcji_usd`, `kurs_usd`, `roznica_proc`, `wacc_proc`, `wzrost_rezydualny_proc`, `wartosc_firmy_mln_usd`, `wartosc_kapitalu_mln_usd`, `udzial_wartosci_rezydualnej_proc`, `gotowka_i_papiery_mln_usd`, `dlug_mln_usd`, `liczba_akcji_mln`, `marza_operacyjna_<rok>_proc`, `wzrost_przychodow_<rok>_proc`.

Lata i daty piszesz zwykłym tekstem ("w 2025 r."). Fakt bez liczby (np. nazwę produktu z cytatu) podpinasz polem `"id": ["F-30"]`, żeby trafił do podpisu. Dopisuj tylko to, co mówią cytaty w ledgerze.

## Struktura

```json
{
  "prezentacja": {
    "karty": [
      {"wartosc": "{F-07}", "opis": "zysk netto w 2025 r."},
      {"wartosc": "{F-27}", "opis": "marża operacyjna w 2025 r."},
      {"wartosc": "{F-14}", "opis": "gotówka i papiery wartościowe na koniec 2025 r."}
    ],
    "slajd_dodatkowy": {
      "tytul": "AI i aplikacje: źródło zysków",
      "podtytul": "Family of Apps zarabia, Reality Labs inwestuje",
      "punkty": [
        {"tekst": "Cel spółki w AI: budowa superinteligencji", "id": ["F-29"]},
        {"tekst": "Zysk operacyjny Family of Apps: {F-19}; strata Reality Labs: {F-21}"}
      ],
      "wykres": {"tytul": "Przychody segmentów w 2025 r., mln USD", "kategorie": ["Family of Apps", "Reality Labs"],
                 "wartosci": ["F-18", "F-20"], "zrodlo": "nota 15, raport 10-K, s. 126"}
    },
    "projekty": [
      {"grafika": "G-01", "tytul": "Okulary AI", "podtytul": "Urządzenia noszone to główny kierunek Reality Labs",
       "punkty": [{"tekst": "W 2026 r. ok. {F-31} kosztów Reality Labs ma trafić na urządzenia noszone"}]}
    ]
  },
  "notatka": {
    "wnioski": [
      {"naglowek": "Silny, rentowny biznes", "tekst": "przychody wzrosły z {F-02} do {F-01} przy marży {F-27}."}
    ],
    "projekty": [
      {"naglowek": "Centra danych", "tekst": "spółka ma {F-32|bez_jedn} własnych lokalizacji centrów danych na świecie."}
    ]
  }
}
```

- `karty`: dokładnie 3 kluczowe liczby obok wykresu przychodów (krótkie opisy, do ok. 60 znaków).
- `slajd_dodatkowy`: opcjonalny (pomiń klucz, jeśli nie potrzeba), np. dla projektu bez zdjęcia albo segmentów; `wykres` opcjonalny, tylko wartości dodatnie (np. przychody segmentów; stratę opisz w punktach).
- `projekty`: po jednym na każde zdjęcie z ledgera (3-4), 2-3 punkty po ok. 60-110 znaków; tytuł do ok. 30 znaków.
- `notatka.wnioski` i `notatka.projekty`: dokładnie po 3, każdy w jednym zdaniu (nagłówek do ok. 40 znaków, tekst do ok. 200 znaków), żeby notatka zmieściła się na 1 stronie.

Ryzyka (3 pierwsze wpisy `risk_...`), tabela kluczowych liczb, wycena i źródła powstają automatycznie.

Po wygenerowaniu obejrzyj podglądy PNG: jeśli tekst się ucina albo notatka ma więcej niż 1 stronę, skróć teksty tutaj i wygeneruj ponownie.

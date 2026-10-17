"""Weryfikacja ledgera: bramka 1 (skrypt) i bramka 2 (niezależny model).

Użycie: python .claude/skills/pakiet-analityczny/scripts/weryfikuj.py TICKER

Zapisuje w TICKER/weryfikacja/:
  bramka1.json, bramka2.json - wyniki bramek,
  raport.md                  - raport po polsku,
  status.json                - ok (true tylko gdy wszystkie wpisy przeszły obie bramki) i SHA-256 ledgera.
Skrypty tworzące dokumenty sprawdzają status funkcją bramka.wymagaj_weryfikacji.
"""

import json
import sys
from collections import Counter
from datetime import datetime, timezone

from bramka import KATALOG_GLOWNY, skrot_ledgera
from sprawdz_cytaty import sprawdz
from weryfikuj_modelem import MODEL, weryfikuj


def main():
    if len(sys.argv) != 2:
        raise SystemExit("Użycie: python .claude/skills/pakiet-analityczny/scripts/weryfikuj.py TICKER")
    ticker = sys.argv[1].upper()
    katalog = KATALOG_GLOWNY / ticker / "weryfikacja"
    # Skrót liczymy przed bramkami: jeśli ledger zmieni się w trakcie, status i tak go nie uzna.
    skrot = skrot_ledgera(ticker)
    teraz = datetime.now(timezone.utc).isoformat(timespec="seconds")

    print("Bramka 1 (skrypt)...", flush=True)
    b1 = sprawdz(ticker)
    print("Bramka 2 (model)...", flush=True)
    b2 = weryfikuj(ticker)

    wpisy = json.loads((KATALOG_GLOWNY / ticker / "ledger.json").read_text(encoding="utf-8"))
    opisy = {w["id"]: w.get("opis", "") for w in wpisy}
    b1_bledy = [b for b in b1 if b["wynik"] != "ok"]
    b2_po_id = {w["id"]: w for w in b2}
    b2_zle = [w for w in b2 if w["werdykt"] != "potwierdza"]
    wymagaja_b2 = [b for b in b1 if b["klasa"] in ("fakt", "dana_rynkowa")]
    pominiete_b2 = [b["id"] for b in wymagaja_b2 if b["id"] not in b2_po_id]
    ok = not b1_bledy and not b2_zle and not pominiete_b2

    klasy = Counter(b["klasa"] for b in b1)
    przeszly = sum(1 for b in b1 if b["wynik"] == "ok"
                   and (b["klasa"] not in ("fakt", "dana_rynkowa") or b2_po_id.get(b["id"], {}).get("werdykt") == "potwierdza"))

    linie = [
        f"# Weryfikacja ledgera {ticker}",
        "",
        f"- Data: {teraz}",
        f"- SHA-256 ledgera: `{skrot}`",
        f"- Wynik: **{'OK - ledger można używać' if ok else 'BŁĘDY - ledgera nie wolno używać, dopóki ich nie poprawimy'}**",
        "",
        "## Podsumowanie",
        "",
        f"- Wpisów w ledgerze: {len(b1)} (" + ", ".join(f"{k}: {n}" for k, n in klasy.items()) + ")",
        f"- Bramka 1 (skrypt, cytaty i wartości): {len(b1) - len(b1_bledy)}/{len(b1)} ok",
        f"- Bramka 2 (model {MODEL}, fakty i dane rynkowe): {len(b2) - len(b2_zle)}/{len(b2)} potwierdzonych"
        + (f"; nie sprawdzono {len(pominiete_b2)} wpisów, bo nie przeszły bramki 1" if pominiete_b2 else ""),
        f"- Przeszło obie wymagane bramki: {przeszly}/{len(b1)}",
        "",
        "## Problemy",
        "",
    ]
    if ok:
        linie.append("Brak.")
    for b in b1_bledy:
        linie.append(f"- **{b['id']}** ({opisy.get(b['id'], '')}) - bramka 1: {b['powod']}")
    for w in b2_zle:
        linie.append(f"- **{w['id']}** ({opisy.get(w['id'], '')}) - bramka 2: {w['werdykt']}. {w['uzasadnienie']}")
    linie += ["", "## Werdykty bramki 2", "", "| id | werdykt | uzasadnienie |", "|---|---|---|"]
    linie += [f"| {w['id']} | {w['werdykt']} | {w['uzasadnienie'].replace('|', '/')} |" for w in b2]

    (katalog / "raport.md").write_text("\n".join(linie) + "\n", encoding="utf-8")
    status = {"ok": ok, "sha256_ledgera": skrot, "data": teraz,
              "bramka1_bledy": len(b1_bledy), "bramka2_niepotwierdzone": len(b2_zle)}
    (katalog / "status.json").write_text(json.dumps(status, ensure_ascii=False, indent=2), encoding="utf-8")

    print("\n".join(linie[:20]))
    print(f"\nRaport: {katalog / 'raport.md'}")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()

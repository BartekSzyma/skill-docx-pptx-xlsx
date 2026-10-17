"""Blokada dla skryptów tworzących dokumenty: pracujemy tylko na zweryfikowanym ledgerze.

Użycie w skrypcie:
    from bramka import wymagaj_weryfikacji
    wymagaj_weryfikacji("META")
"""

import hashlib
import json
import sys
from pathlib import Path

KATALOG_GLOWNY = Path(__file__).resolve().parent.parent


def skrot_ledgera(ticker):
    return hashlib.sha256((KATALOG_GLOWNY / ticker / "ledger.json").read_bytes()).hexdigest()


def wymagaj_weryfikacji(ticker):
    """Kończy program z wyjaśnieniem, jeśli ledger nie przeszedł weryfikacji albo zmienił się po niej."""
    ticker = ticker.upper()
    status_plik = KATALOG_GLOWNY / ticker / "weryfikacja" / "status.json"
    polecenie = f"python narzedzia/weryfikuj.py {ticker}"
    if not status_plik.exists():
        sys.exit(f"STOP: ledger {ticker} nie był jeszcze weryfikowany. Uruchom: {polecenie}")
    status = json.loads(status_plik.read_text(encoding="utf-8"))
    if not status.get("ok"):
        sys.exit(f"STOP: ledger {ticker} nie przeszedł weryfikacji. "
                 f"Szczegóły w {ticker}/weryfikacja/raport.md. Popraw wpisy i uruchom: {polecenie}")
    if status.get("sha256_ledgera") != skrot_ledgera(ticker):
        sys.exit(f"STOP: ledger {ticker} zmieniono po ostatniej weryfikacji "
                 f"({status.get('data', 'nieznana data')}). Uruchom ponownie: {polecenie}")

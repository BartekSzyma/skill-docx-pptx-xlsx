#!/usr/bin/env bash
# Wysyła prompt z instrukcji (dokładnie w brzmieniu z HTML) do agenta herdr i mierzy czas.
# Użycie: tools/wyslij-prompt.sh <agent> <P1..Pn>
# Jedyna podmiana: pole [TWÓJ E-MAIL] -> adres testowy budowy wzorcowej.
set -euo pipefail
cd "$(dirname "$0")/.."
agent="$1"; id="$2"
tekst=$(node tools/wypisz-prompt.mjs "$id" | sed 's/\[TWÓJ E-MAIL\]/kurs.alx@example.com/g')
start=$(date +%s)
herdr agent prompt "$agent" "$tekst" --wait --timeout 3600000 > /dev/null || true
koniec=$(date +%s)
stan=$(herdr agent get "$agent" | sed -n 's/.*"agent_status":"\([a-z]*\)".*/\1/p')
echo "$(date '+%F %T') $id ${agent} czas_s=$((koniec - start)) stan=${stan}" | tee -a budowa-wzorcowa/czasy.log

#!/usr/bin/env bash
# Kadry „początek kroku”: wkleja prompt z instrukcji do pola wpisywania Claude Code BEZ Enter,
# zapisuje widok terminala (ANSI) i czyści pole (Ctrl+C). Nie zużywa limitu: nic nie jest wysyłane do modelu.
# Z --rozwin wkleja dwa razy: drugie wklejenie rozwija zwinięty „[Pasted text #N +M lines]” do pełnego tekstu.
# Użycie: tools/kadry-startowe.sh [--rozwin] <agent> <pane> P1 P2 ... [exit]
set -euo pipefail
export MSYS_NO_PATHCONV=1  # Git Bash zamienia argumenty od / na ścieżki Windows
cd "$(dirname "$0")/.."
rozwin=0
if [ "${1:-}" = "--rozwin" ]; then rozwin=1; shift; fi
agent="$1"; pane="$2"; shift 2
for id in "$@"; do
  if [ "$id" = "exit" ]; then tekst="/exit"; else tekst=$(node tools/wypisz-prompt.mjs "$id"); fi
  herdr pane send-text "$pane" "$tekst" > /dev/null
  sleep 1.5
  if [ "$rozwin" = 1 ]; then herdr pane send-text "$pane" "$tekst" > /dev/null; sleep 2; fi
  stan=$(herdr agent get "$agent" | sed -n 's/.*"agent_status":"\([a-z]*\)".*/\1/p')
  if [ "$stan" != "idle" ] && [ "$stan" != "done" ]; then echo "STOP: $id zmienił stan na $stan"; exit 1; fi
  herdr agent read "$agent" --source visible --format ansi > "zrzuty/kadr-$id-start.ansi"
  herdr agent send-keys "$agent" ctrl+c > /dev/null
  sleep 1
  echo "$id: zapisano zrzuty/kadr-$id-start.ansi"
done

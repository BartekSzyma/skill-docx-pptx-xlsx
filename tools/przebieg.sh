#!/usr/bin/env bash
# Przebieg budowy wzorcowej: wysyła po kolei prompty z instrukcji, po każdym zapisuje kadr terminala (ANSI -> PNG).
# Zatrzymuje się, gdy agent nie skończył normalnie (np. czeka na zgodę).
# Użycie: tools/przebieg.sh <agent> P1 P2 ...
set -uo pipefail
export MSYS_NO_PATHCONV=1
cd "$(dirname "$0")/.."
agent="$1"; shift
for id in "$@"; do
  tools/wyslij-prompt.sh "$agent" "$id"
  stan=$(herdr agent get "$agent" | sed -n 's/.*"agent_status":"\([a-z]*\)".*/\1/p')
  herdr agent read "$agent" --source visible --format ansi > "zrzuty/kadr-$id.ansi"
  PYTHONUTF8=1 python tools/ansi_do_png.py "zrzuty/kadr-$id.ansi" "zrzuty/oryginaly/kadr-$id.png" || true
  if [ "$stan" != "done" ] && [ "$stan" != "idle" ]; then echo "STOP po $id: stan=$stan"; exit 1; fi
done
echo "KONIEC: $*"

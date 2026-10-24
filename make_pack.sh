#!/usr/bin/env bash
# Build the hand-over zip. Run from anywhere:  bash tools/make_pack.sh P3done
# Writes MANIFEST.sha256, zips the whole pack as Aria_Graveyard_Pack_v2_1_<label>.zip into /mnt/user-data/outputs and verifies it.
set -euo pipefail
LABEL="${1:?usage: bash tools/make_pack.sh <label>   e.g. P3done or P3WIP}"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
NAME="Aria_Graveyard_Pack_v2_1_${LABEL}"
TMP="$(mktemp -d)"
python3 "$ROOT/tools/make_paste.py" >/dev/null
cp -r "$ROOT" "$TMP/$NAME"
find "$TMP/$NAME" -name __pycache__ -prune -exec rm -rf {} + 2>/dev/null || true
( cd "$TMP/$NAME" && rm -f MANIFEST.sha256 && find . -type f ! -name MANIFEST.sha256 | sort | xargs sha256sum > MANIFEST.sha256 )
( cd "$TMP" && rm -f "$NAME.zip" && zip -qr "$NAME.zip" "$NAME" && unzip -tq "$NAME.zip" )
mkdir -p /mnt/user-data/outputs
cp "$TMP/$NAME.zip" /mnt/user-data/outputs/
echo "OK /mnt/user-data/outputs/$NAME.zip  $(stat -c %s "/mnt/user-data/outputs/$NAME.zip") bytes  sha $(sha256sum "/mnt/user-data/outputs/$NAME.zip" | cut -c1-8)"
echo "files in zip: $(unzip -Z1 "/mnt/user-data/outputs/$NAME.zip" | grep -vc '/$')"

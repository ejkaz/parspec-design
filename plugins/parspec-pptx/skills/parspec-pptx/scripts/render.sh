#!/usr/bin/env bash
# parspec-pptx render — convert a .pptx to per-slide PNGs via PowerPoint.
#
# Usage:
#   render.sh <input.pptx> [out_dir] [dpi]
#   PPTX_DIRECT=1 render.sh <input.pptx> [out_dir] [dpi]    # skip daemon
#
# Defaults: out_dir = /tmp/parspec-pptx-out,  dpi = 110
#
# Two modes:
#   1. Default: use the keep-alive daemon (3s per render once warm).
#      Daemon needs Automation permission for PowerPoint — System Settings
#      → Privacy → Automation → grant python3 access to PowerPoint.
#   2. PPTX_DIRECT=1: foreground 3-call AppleScript pattern (~8s per render,
#      no daemon needed, works without Automation grant). Use this when the
#      daemon hangs (macOS sandbox prompt waiting on hidden dialog).
#
# Writes <out_dir>/<stem>.pdf and <out_dir>/<stem>-N.png per slide.
# Exit codes: 0 ok, 1 bad args, 2 render failure, 3 daemon start failure

set -euo pipefail

PPTX="${1:?usage: render.sh <input.pptx> [out_dir] [dpi]}"
OUT_DIR="${2:-/tmp/parspec-pptx-out}"
DPI="${3:-110}"
DIRECT="${PPTX_DIRECT:-0}"

if [[ ! -f "$PPTX" ]]; then
    echo "render.sh: file not found: $PPTX" >&2
    exit 1
fi
if ! command -v pdftoppm >/dev/null; then
    echo "render.sh: pdftoppm not installed (try: brew install poppler)" >&2
    exit 1
fi

mkdir -p "$OUT_DIR"
PPTX_ABS="$(cd "$(dirname "$PPTX")" && pwd)/$(basename "$PPTX")"
STEM="$(basename "$PPTX" .pptx)"
PDF="$OUT_DIR/$STEM.pdf"

# ── direct mode: foreground osascript ─────────────────────────────────
if [[ "$DIRECT" == "1" ]]; then
    echo "render.sh: direct mode (no daemon)"
    PDF_ABS="$(cd "$(dirname "$PDF")" && pwd)/$(basename "$PDF")"
    # Quit any existing PowerPoint first to start clean
    osascript -e 'tell application "Microsoft PowerPoint" to quit saving no' \
        >/dev/null 2>&1 || true
    sleep 2
    osascript -e 'tell application "Microsoft PowerPoint" to activate' \
        >/dev/null 2>&1
    sleep 5
    osascript <<APP 2>&1 || { echo "render.sh: open failed" >&2; exit 2; }
tell application "Microsoft PowerPoint"
    open POSIX file "$PPTX_ABS"
end tell
APP
    sleep 3
    osascript <<APP 2>&1 || { echo "render.sh: save-as-PDF failed" >&2; exit 2; }
tell application "Microsoft PowerPoint"
    save active presentation in POSIX file "$PDF_ABS" as save as PDF
end tell
APP
    sleep 2
    osascript -e 'tell application "Microsoft PowerPoint" to close active presentation saving no' \
        >/dev/null 2>&1 || true
    if [[ ! -f "$PDF" ]]; then
        echo "render.sh: PDF not written after save" >&2
        exit 2
    fi
else
    # ── daemon mode ───────────────────────────────────────────────────
    REQ_DIR="/tmp/parspec-pptx-render"
    mkdir -p "$REQ_DIR"
    DAEMON_SCRIPT="$(cd "$(dirname "$0")/.." && pwd)/daemon/ppt_render_daemon.py"
    PID_FILE="$REQ_DIR/daemon.pid"

    daemon_alive() {
        [[ -f "$PID_FILE" ]] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null
    }

    if ! daemon_alive; then
        echo "render.sh: starting daemon..."
        nohup python3 "$DAEMON_SCRIPT" >/dev/null 2>&1 &
        for _ in $(seq 1 20); do
            sleep 0.25
            daemon_alive && break
        done
        if ! daemon_alive; then
            echo "render.sh: daemon failed to start (see $REQ_DIR/daemon.log)" >&2
            exit 3
        fi
    fi

    REQ_ID="$(uuidgen 2>/dev/null || date +%s%N)"
    REQ="$REQ_DIR/$REQ_ID.req"
    printf '%s\n%s\n' "$PPTX_ABS" "$PDF" > "$REQ"

    DONE="${REQ%.req}.done"
    ERR="${REQ%.req}.err"
    # First render: Office cold-start (≤ 20s) + open (~3s) + save (~5s)
    DEADLINE=$(( $(date +%s) + 180 ))

    while [[ ! -f "$DONE" && ! -f "$ERR" ]]; do
        if (( $(date +%s) >= DEADLINE )); then
            echo "render.sh: timeout waiting for daemon (180s) — try PPTX_DIRECT=1" >&2
            rm -f "$REQ"
            exit 2
        fi
        sleep 0.2
    done

    if [[ -f "$ERR" ]]; then
        echo "render.sh: daemon reported error:" >&2
        cat "$ERR" >&2
        echo "Hint: try PPTX_DIRECT=1 $0 ... for foreground fallback" >&2
        rm -f "$ERR"
        exit 2
    fi
    rm -f "$DONE"
fi

# ── rasterize to per-slide PNGs ───────────────────────────────────────
rm -f "$OUT_DIR/$STEM"-*.png
pdftoppm -png -r "$DPI" "$PDF" "$OUT_DIR/$STEM"

echo "render.sh: pdf  → $PDF"
echo "render.sh: pngs → $OUT_DIR/$STEM-*.png"
ls "$OUT_DIR/$STEM"-*.png

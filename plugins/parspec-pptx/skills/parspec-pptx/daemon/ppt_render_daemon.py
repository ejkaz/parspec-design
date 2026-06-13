#!/usr/bin/env python3
"""
PowerPoint render daemon — keeps PowerPoint open and ready to convert
.pptx → .pdf without the 6-second cold-start cycle.

Architecture: file-watcher loop. Polls a request directory for *.req files.
Each .req file is plain text: one .pptx path per line. The daemon opens it
in PowerPoint, saves as PDF to a paired path, then writes a *.done marker
the client can wait on. The .req is deleted on completion.

Why polling vs. FIFO: macOS launchd doesn't play well with named pipes,
and we want this restart-clean.

Usage:
    # start in background
    python3 ppt_render_daemon.py &

    # from any process — render a .pptx
    REQ="/tmp/parspec-pptx-render/$(uuidgen).req"
    echo "/path/to/deck.pptx" > "$REQ"
    echo "/path/to/out.pdf"   >> "$REQ"
    while [ ! -f "${REQ%.req}.done" ]; do sleep 0.2; done
    rm "${REQ%.req}.done"

The companion shell wrapper at scripts/render.sh handles all of that.
"""

from __future__ import annotations

import os
import signal
import subprocess
import sys
import time
from pathlib import Path

REQ_DIR = Path("/tmp/parspec-pptx-render")
POLL_INTERVAL = 0.25  # seconds
IDLE_TIMEOUT = 30 * 60  # quit PPT after 30min idle
PID_FILE = REQ_DIR / "daemon.pid"
LOG_FILE = REQ_DIR / "daemon.log"


def log(msg: str) -> None:
    """Append timestamped line to the daemon log."""
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}\n"
    LOG_FILE.write_text(LOG_FILE.read_text() + line if LOG_FILE.exists() else line)
    sys.stdout.write(line)
    sys.stdout.flush()


def osascript(script: str, timeout: int = 120) -> tuple[int, str]:
    """Run AppleScript, return (returncode, combined output)."""
    r = subprocess.run(
        ["osascript", "-e", script],
        capture_output=True, text=True, timeout=timeout,
    )
    return r.returncode, (r.stdout + r.stderr).strip()


def is_ppt_running() -> bool:
    rc, out = osascript(
        'tell application "System Events" to '
        '(name of processes) contains "Microsoft PowerPoint"',
        timeout=10,
    )
    return rc == 0 and "true" in out.lower()


def ensure_ppt_running() -> bool:
    """Launch PowerPoint if not running and wait until it's responsive."""
    if is_ppt_running():
        return True
    rc, msg = osascript(
        'tell application "Microsoft PowerPoint" to activate', timeout=30
    )
    if rc != 0:
        log(f"Failed to activate PowerPoint: {msg}")
        return False
    # Wait for cold start to complete — PowerPoint can take 5–10s
    for i in range(40):
        time.sleep(0.5)
        if is_ppt_running():
            # Extra cushion for the Office welcome dialog to finish initialising
            time.sleep(2.0)
            return True
    log("PowerPoint failed to start within 20s")
    return False


def close_all_presentations() -> None:
    """Close any open presentations without saving."""
    osascript('''
        tell application "Microsoft PowerPoint"
            set ps to every presentation
            repeat with p in ps
                try
                    close p saving no
                end try
            end repeat
        end tell
    ''')


def render_one(src_pptx: Path, dst_pdf: Path) -> tuple[bool, str]:
    """Open .pptx, save as PDF, close. Returns (ok, message).

    Splits into three osascript calls — empirically this avoids the
    -9074 race that hits when activate / open / save run in one tell block.
    """
    src_pptx = src_pptx.resolve()
    dst_pdf = dst_pdf.resolve()

    if not src_pptx.exists():
        return False, f"source not found: {src_pptx}"

    # 0. Make sure PowerPoint is up and responsive
    if not ensure_ppt_running():
        return False, "PowerPoint failed to start"

    # 1. Try open up to 3 times; on -9074 / -609 (broken connection) hard-
    #    restart PowerPoint and retry from cold start
    for attempt in (1, 2, 3):
        # Clear stale docs before each attempt
        close_all_presentations()
        time.sleep(0.5)
        osascript(
            'tell application "Microsoft PowerPoint" to activate', timeout=10
        )
        time.sleep(1.0)

        rc, out = osascript(f'''
            tell application "Microsoft PowerPoint"
                open POSIX file "{src_pptx}"
            end tell
        ''', timeout=60)

        if rc == 0:
            break

        if ("9074" in out or "609" in out) and attempt < 3:
            log(f"open hit Office-busy error on attempt {attempt}; "
                "hard-restarting PowerPoint")
            osascript(
                'tell application "Microsoft PowerPoint" to quit saving no',
                timeout=10,
            )
            time.sleep(3.0)
            ensure_ppt_running()
            continue

        return False, f"open failed (rc={rc}, attempt {attempt}): {out}"

    # 2a. Verify the file actually opened — poll until a presentation appears
    for _ in range(20):  # up to 10s
        time.sleep(0.5)
        rc, out = osascript(
            'tell application "Microsoft PowerPoint" to count of presentations',
            timeout=10,
        )
        if rc == 0 and out.strip().isdigit() and int(out.strip()) >= 1:
            break
    else:
        return False, "PowerPoint did not load the file (count stayed 0)"

    # 3. Save as PDF — ensure output dir exists
    dst_pdf.parent.mkdir(parents=True, exist_ok=True)
    rc, out = osascript(f'''
        tell application "Microsoft PowerPoint"
            save active presentation in POSIX file "{dst_pdf}" as save as PDF
        end tell
    ''', timeout=90)
    if rc != 0:
        return False, f"save-as-PDF failed (rc={rc}): {out}"

    # 4. Wait for the PDF to actually land on disk — Office's "save as PDF"
    #    can return before the file is flushed
    for _ in range(40):  # up to 10s
        if dst_pdf.exists() and dst_pdf.stat().st_size > 0:
            break
        time.sleep(0.25)

    # 5. Close (no-save) — non-critical
    osascript('''
        tell application "Microsoft PowerPoint"
            try
                close active presentation saving no
            end try
        end tell
    ''', timeout=15)

    if not dst_pdf.exists():
        return False, f"PDF not written within 10s of save call"
    return True, f"rendered → {dst_pdf}"


def write_pid() -> None:
    PID_FILE.write_text(str(os.getpid()))


def cleanup_pid(*_) -> None:
    if PID_FILE.exists():
        PID_FILE.unlink()
    log("Daemon stopped.")
    sys.exit(0)


def main() -> None:
    REQ_DIR.mkdir(parents=True, exist_ok=True)

    # Honor only one daemon at a time
    if PID_FILE.exists():
        existing = PID_FILE.read_text().strip()
        try:
            os.kill(int(existing), 0)
            log(f"Daemon already running at pid {existing}; exiting.")
            sys.exit(1)
        except (ValueError, OSError):
            PID_FILE.unlink()  # stale pid file

    write_pid()
    signal.signal(signal.SIGTERM, cleanup_pid)
    signal.signal(signal.SIGINT, cleanup_pid)

    log(f"Daemon starting, pid={os.getpid()}, watching {REQ_DIR}")
    ensure_ppt_running()

    last_work = time.time()

    while True:
        reqs = sorted(REQ_DIR.glob("*.req"))
        for req in reqs:
            try:
                lines = req.read_text().strip().splitlines()
                if len(lines) < 2:
                    log(f"Malformed request {req}: needs src + dst lines")
                    req.with_suffix(".err").write_text("malformed request")
                    req.unlink()
                    continue

                src, dst = Path(lines[0]), Path(lines[1])
                t0 = time.time()
                ok, msg = render_one(src, dst)
                elapsed = time.time() - t0

                if ok:
                    log(f"{req.name}: OK ({elapsed:.1f}s) {msg}")
                    req.with_suffix(".done").write_text(str(dst))
                else:
                    log(f"{req.name}: FAIL ({elapsed:.1f}s) {msg}")
                    req.with_suffix(".err").write_text(msg)

                req.unlink()
                last_work = time.time()
            except Exception as e:
                log(f"Exception handling {req}: {e}")
                req.with_suffix(".err").write_text(str(e))
                req.unlink(missing_ok=True)

        # Idle-timeout: quit PowerPoint after a long idle to free memory
        if time.time() - last_work > IDLE_TIMEOUT:
            log("Idle timeout — closing all presentations to free memory.")
            close_all_presentations()
            last_work = time.time()

        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    main()

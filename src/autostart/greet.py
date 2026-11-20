"""Ultra-fast (<300ms) standalone greeting engine for Jellyfish World.

Performance constraints:
- Uses ONLY Python standard library (no torch, transformers, httpx, or heavy imports).
- Starts execution in < 50ms.
- Maximum duration: 2.5 - 3.0 seconds.
- Instantly skippable upon any keypress (via msvcrt.kbhit on Windows, select on Unix).
- Cleanly returns control to the shell prompt.
"""
from __future__ import annotations

import os
import select
import sys
import time

from src.autostart.guards import (
    is_quiet_mode,
    mark_seen,
    should_suppress_greeting,
)

# Standard ANSI colors (only applied if NO_COLOR is not set)
CYAN = "\033[96m"
ELECTRIC_CYAN = "\033[38;5;123m"
PINK = "\033[95m"
GOLD = "\033[93m"
DIM = "\033[2m"
RESET = "\033[0m"
BOLD = "\033[1m"


def is_no_color() -> bool:
    val = os.environ.get("NO_COLOR", "").strip()
    return bool(val and val.lower() not in ("0", "false", "no"))


def is_reduced_motion() -> bool:
    val = os.environ.get("REDUCED_MOTION", "").strip().lower()
    return val in ("1", "true", "yes", "on")


def check_keypress() -> bool:
    """Check if the user pressed any key on Windows or Unix."""
    if sys.platform == "win32":
        try:
            import msvcrt
            if msvcrt.kbhit():
                # Consume key so it does not spill into the next shell prompt
                msvcrt.getch()
                return True
        except Exception:
            pass
    else:
        # Unix: use select to check if stdin has data ready
        try:
            if select.select([sys.stdin], [], [], 0)[0]:
                # Consume the input
                sys.stdin.read(1)
                return True
        except Exception:
            pass
    return False


# 4 lightweight frames (6 lines each)
FRAMES: list[list[str]] = [
    [
        "     .-~~~-.     ",
        "    /  o o  \\    ",
        "   (   ‿‿    )   ",
        "    '-.___.-'    ",
        "     ) | | (     ",
        "     ( | | )     ",
    ],
    [
        "   .---~~~---.   ",
        "  /   o   o   \\  ",
        " (     ‿‿      ) ",
        "  '--._____.-'   ",
        "    (  | |  )    ",
        "     ) | | (     ",
    ],
    [
        "  .----~~~----.  ",
        " /    o   o    \\ ",
        "(      ‿‿      ) ",
        " '---._____.-'   ",
        "     | | | |     ",
        "    (  | |  )    ",
    ],
    [
        "   .---~~~---.   ",
        "  /   o   o   \\  ",
        " (     ‿‿      ) ",
        "  '--._____.-'   ",
        "    )  | |  (    ",
        "   (   | |   )   ",
    ],
]


def render_greet_frame(frame: list[str], no_color: bool) -> str:
    """Style and format a single frame string."""
    out = []
    for line in frame:
        if no_color:
            out.append(f"  {line}")
        else:
            colored_line = (
                line.replace("‿‿", f"{PINK}‿‿{ELECTRIC_CYAN}")
                    .replace("o o", f"{BOLD}o o{RESET}{ELECTRIC_CYAN}")
                    .replace("o   o", f"{BOLD}o   o{RESET}{ELECTRIC_CYAN}")
            )
            out.append(f"  {ELECTRIC_CYAN}{colored_line}{RESET}")
    return "\n".join(out)


def play_greeting(
    max_seconds: float = 2.5,
    frame_interval: float = 0.22,
    force: bool = False,
    is_autostart: bool = False,
) -> bool:
    """Execute the greeting animation.

    Args:
        max_seconds: Maximum run duration before returning to prompt.
        frame_interval: Delay between animation frames.
        force: Bypass all guards (for testing or explicit manual call).
        is_autostart: Whether invoked automatically on terminal startup.

    Returns True if played, False if skipped/suppressed.
    """
    if is_quiet_mode() and not force:
        return False

    if is_autostart and not force:
        suppress, reason = should_suppress_greeting()
        if suppress:
            return False

    # Mark seen so subshells don't re-trigger
    mark_seen()

    no_color = is_no_color()
    reduced_motion = is_reduced_motion()

    # Greeting message
    if no_color:
        header = "\n  ~ A calm jellyfish drifts past... (press any key to skip) ~\n"
        footer = "  jellyfish <message> | jelly --help\n"
    else:
        header = f"\n  {CYAN}~ A calm jellyfish drifts past...{DIM} (press any key to skip){RESET} ~\n"
        footer = f"  {DIM}jellyfish <message> | jelly --help{RESET}\n"

    sys.stdout.write(header)
    sys.stdout.flush()

    if reduced_motion:
        # Show one static frame for a brief moment
        static_str = render_greet_frame(FRAMES[0], no_color)
        sys.stdout.write(static_str + "\n")
        sys.stdout.write(footer + "\n")
        sys.stdout.flush()
        t0 = time.time()
        while time.time() - t0 < 0.8:
            if check_keypress():
                break
            time.sleep(0.05)
        return True

    # Animated loop
    start_time = time.time()
    frame_idx = 0
    total_frames = len(FRAMES)
    first_render = True

    try:
        while time.time() - start_time < max_seconds:
            if check_keypress():
                break

            rendered = render_greet_frame(FRAMES[frame_idx % total_frames], no_color)

            if not first_render:
                # Move cursor up 6 lines to overwrite previous frame
                sys.stdout.write("\033[6A\r")

            sys.stdout.write(rendered + "\n")
            sys.stdout.flush()
            first_render = False

            frame_idx += 1
            time.sleep(frame_interval)
    finally:
        sys.stdout.write(footer + "\n")
        sys.stdout.flush()

    return True


if __name__ == "__main__":
    force_run = "--force" in sys.argv or "-f" in sys.argv
    autostart_run = "--autostart" in sys.argv

    t0 = time.perf_counter()
    played = play_greeting(force=force_run, is_autostart=autostart_run)
    elapsed_ms = (time.perf_counter() - t0) * 1000

    if os.environ.get("JELLY_BENCHMARK"):
        sys.stderr.write(f"Startup & run: {elapsed_ms:.2f} ms (played={played})\n")

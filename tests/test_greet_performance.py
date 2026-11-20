"""Performance and responsiveness tests for `jelly greet`."""
import os
import subprocess
import sys
import time
from pathlib import Path


def test_greet_import_and_execution_under_50ms():
    """Verify that importing and running greet in-process is lightning fast (< 50ms) with zero heavy libraries."""
    # Ensure heavy libraries are not imported BY THE GREET MODULE
    # (They may be in sys.modules from other tests, but greet should not import them)
    heavy_libs = {"torch", "transformers", "httpx"}
    before_import = set(sys.modules.keys()) & heavy_libs

    t0 = time.perf_counter()
    from src.autostart.greet import play_greeting
    play_greeting(max_seconds=0.01, is_autostart=True)
    elapsed_ms = (time.perf_counter() - t0) * 1000

    # In-process startup must be well under 50 ms
    assert elapsed_ms < 50, f"In-process greet initialization too slow: {elapsed_ms:.2f} ms"

    # Confirm heavy libraries were NOT loaded by greet module import
    after_import = set(sys.modules.keys()) & heavy_libs
    newly_imported = after_import - before_import
    assert not newly_imported, f"Greet module imported heavy libraries: {newly_imported}"


def test_greet_subprocess_cold_start():
    """Verify that launching `jelly greet` as a child process executes cleanly and rapidly."""
    repo_root = Path(__file__).resolve().parent.parent
    cli_path = repo_root / "src" / "cli" / "jelly.py"

    env = os.environ.copy()
    env["JELLY_QUIET"] = "1"
    env["PYTHONPATH"] = str(repo_root)

    t0 = time.perf_counter()
    res = subprocess.run(
        [sys.executable, str(cli_path), "greet", "--autostart"],
        capture_output=True,
        text=True,
        env=env,
    )
    elapsed_ms = (time.perf_counter() - t0) * 1000

    assert res.returncode == 0
    # Process startup on Windows can take a few seconds under concurrent test load
    assert elapsed_ms < 5000, f"Subprocess start too slow: {elapsed_ms:.1f} ms"

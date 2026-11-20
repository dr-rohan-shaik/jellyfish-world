#!/usr/bin/env bash
set -e

echo "==================================================="
echo "       Jellyfish World — Quick Setup (Unix/Termux)"
echo "==================================================="

# 1. Check Python
PYTHON_BIN=$(command -v python3 || command -v python)
if [ -z "$PYTHON_BIN" ]; then
    echo "[ERROR] Python 3.11+ is required but not found."
    exit 1
fi
echo "[1/4] Found Python: $($PYTHON_BIN --version)"

# 2. Virtual environment
if [ ! -d "venv" ]; then
    echo "[2/4] Creating venv..."
    $PYTHON_BIN -m venv venv
else
    echo "[2/4] Virtual environment exists."
fi

# 3. Install dependencies
echo "[3/4] Installing dependencies..."
./venv/bin/python -m pip install --quiet --upgrade pip
./venv/bin/python -m pip install --quiet -r requirements.txt

# 4. Verify
echo "[4/4] Running tests..."
export PYTHONPATH=.
./venv/bin/python -m pytest tests --quiet

echo ""
echo "==================================================="
echo "      [SUCCESS] Jellyfish World is ready!"
echo "==================================================="
echo "To start: ./venv/bin/python src/companion/session.py"

#!/data/data/com.termux/files/usr/bin/bash
# ==============================================================================
# Daily Intelligence - Automated Termux Setup for Infinix (Android 14)
# ==============================================================================

set -e

echo "=== [1/6] Updating Termux Repositories & Base Packages ==="
pkg update -y && pkg upgrade -y

echo "=== [2/6] Installing Python, Git, and Core Tools ==="
pkg install -y python git sqlite build-essential libffi openssl

echo "=== [3/6] Setting Up Python Virtual Environment ==="
VENV_DIR="$HOME/.envs/daily-intel"
if [ ! -d "$VENV_DIR" ]; then
    python -m venv "$VENV_DIR"
    echo "Virtual environment created at: $VENV_DIR"
fi

source "$VENV_DIR/bin/activate"

echo "=== [4/6] Upgrading pip and Installing Dependencies ==="
pip install --upgrade pip
pip install -r requirements.txt

echo "=== [5/6] Initializing Database & Running Alembic Migrations ==="
mkdir -p data logs
alembic upgrade head

echo "=== [6/6] Verifying Installation with Test Suite ==="
pytest -v

echo ""
echo "=================================================================="
echo " Daily Intelligence installed successfully on Android!"
echo " Start the server using: ./scripts/start_termux.sh"
echo " Access locally in your phone browser at: http://127.0.0.1:8000"
echo "=================================================================="

#!/data/data/com.termux/files/usr/bin/bash
# ==============================================================================
# Daily Intelligence - Production Launcher for Termux (Android 14)
# ==============================================================================

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_DIR="$HOME/.envs/daily-intel"

cd "$PROJECT_DIR"

# Acquire Termux Wake Lock to ensure morning/evening briefing scheduler runs smoothly
if command -v termux-wake-lock &> /dev/null; then
    termux-wake-lock
    echo "[INFO] Termux WakeLock acquired. Background scheduler will persist."
fi

# Activate Python Virtual Environment
if [ -d "$VENV_DIR" ]; then
    source "$VENV_DIR/bin/activate"
elif [ -d "venv" ]; then
    source "venv/bin/activate"
else
    echo "[WARNING] No virtual environment found. Using system python."
fi

# Export Environment
export HOST="127.0.0.1"
export PORT="8000"
export TIMEZONE="Asia/Kolkata"

echo "=============================================================="
echo "  DAILY INTELLIGENCE (ದೈನಂದಿನ ಇಂಟೆಲಿಜೆನ್ಸ್)"
echo "  Starting local intelligence engine on Android..."
echo "  URL: http://127.0.0.1:8000"
echo "  Scheduled Briefings: 06:00 AM & 06:00 PM IST"
echo "=============================================================="

# Launch Uvicorn
exec uvicorn app.main:app --host 127.0.0.1 --port 8000 --log-level info

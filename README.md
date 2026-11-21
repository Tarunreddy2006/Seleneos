# Daily Intelligence (ದೈನಂದಿನ ಇಂಟೆಲಿಜೆನ್ಸ್)

A private, self-hosted personal news and knowledge intelligence platform engineered for Python 3.13+, designed to run on Windows during development and Android 14 via Termux for personal daily production.

---

## 1. System Architecture

```
Daily Intelligence Pipeline:
COLLECTION ──► NORMALIZATION ──► DEDUPLICATION ──► CLASSIFICATION ──► SUMMARIZATION ──► TRANSLATION ──► STORAGE ──► PRESENTATION
 (RSS/Web)       (URL/HTML)         (Hash/Title)      (Heuristics/ML)     (AI / Rule Fallback) (EN & Kannada)  (SQLite WAL)   (Editorial UI)
```

- **Backend Framework:** FastAPI with Uvicorn.
- **Database:** SQLite with WAL mode (`PRAGMA journal_mode=WAL`), foreign keys enabled, and Alembic versioned migrations.
- **Core Categories:**
  1. Global Business (ಜಾಗತಿಕ ವ್ಯಾಪಾರ)
  2. Global Politics (ಜಾಗತಿಕ ರಾಜಕೀಯ)
  3. Indian Politics (ಭಾರತೀಯ ರಾಜಕೀಯ)
  4. Indian Economy (ಭಾರತೀಯ ಆರ್ಥಿಕತೆ)
  5. Karnataka Politics (ಕರ್ನಾಟಕ ರಾಜಕೀಯ)
  6. Technology & Science (ತಂತ್ರಜ್ಞಾನ ಮತ್ತು ವಿಜ್ಞಾನ)
  7. Education (ಶಿಕ್ಷಣ)
- **Frontend:** Vanilla HTML, CSS, JavaScript (zero heavy JS build steps, optimized for mobile battery and Termux).
- **Dual Language:** Full English and Kannada support with instant client-side toggling and robust fallback.
- **Automation:** 12-hour automated briefing schedule (6:00 AM IST and 6:00 PM IST) with missed-job recovery.

---

## 2. Quick Start (Windows Development)

### Prerequisites
- Python 3.13.6
- Virtual environment at `.\venv`

### Installation & Execution
```powershell
# 1. Activate virtual environment
.\venv\Scripts\Activate.ps1

# 2. Install dependencies
pip install -r requirements.txt

# 3. Apply database migrations
alembic upgrade head

# 4. Start local development server
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000) in your browser.
API Health endpoint: [http://127.0.0.1:8000/api/health](http://127.0.0.1:8000/api/health)

---

## 3. Running Automated Tests

```powershell
.\venv\Scripts\python.exe -m pytest -v
```

---

## 4. Android (Termux) Deployment Target

The codebase avoids platform-specific binary dependencies and relies on pure-Python / standard libraries wherever possible (`html.parser`, SQLite stdlib, standard HTTPX/feedparser) to guarantee seamless deployment on Android 14 without compilation bottlenecks.

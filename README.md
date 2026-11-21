# Seleneos (ಸೆಲೆನಿಯೋಸ್)

> Seleneos is a private knowledge intelligence platform that transforms an Android phone into a personal knowledge hub. It autonomously collects local, national, and global developments across 7 key spheres and synthesizes them in **Kannada** and **English** with 100% on-device local storage privacy — your data never leaves your device.

---

## 📱 Standalone Android 14 APK (Zero Dependencies)

Seleneos runs **100% autonomously on Android 14** without requiring Termux, without a PC connection, and without external servers:

- **Download APK:** [`Seleneos.apk`](./Seleneos.apk) *(0.28 MB, signed with Android 14 API 34 compatibility)*
- **Privacy Guaranteed:** Ingestion, categorization, deduplication, summarization, and translation run directly on-device.
- **Offline Capable:** Stored articles, briefings, and quizzes persist in on-device storage across phone restarts.

---

## 🏛️ System Architecture

```
COLLECTION ──► NORMALIZATION ──► DEDUPLICATION ──► CLASSIFICATION ──► SUMMARIZATION ──► TRANSLATION ──► ON-DEVICE STORAGE ──► EDITORIAL UI
 (RSS Feeds)     (URL/HTML Clean)   (Hash/Jaccard)     (7-Taxonomy)       (Why It Matters)  (English & Kannada)  (IndexedDB / SQLite)   (Editorial Shell)
```

### 1. The 7 Core Intelligence Spheres
1. **Global Business (ಜಾಗತಿಕ ವ್ಯಾಪಾರ)** — Global markets, trade, central banks, enterprise acquisitions.
2. **Global Politics (ಜಾಗತಿಕ ರಾಜಕೀಯ)** — International relations, treaties, multilateral bodies, conflicts.
3. **Indian Politics (ಭಾರತೀಯ ರಾಜಕೀಯ)** — Union Parliament, national policies, constitutional developments.
4. **Indian Economy (ಭಾರತೀಯ ಆರ್ಥಿಕತೆ)** — RBI announcements, repo rates, inflation, fiscal deficit, budget.
5. **Karnataka Politics (ಕರ್ನಾಟಕ ರಾಜಕೀಯ)** — State policies, Vidhana Soudha, regional governance, Bengaluru infrastructure.
6. **Technology & Science (ತಂತ್ರಜ್ಞಾನ ಮತ್ತು ವಿಜ್ಞಾನ)** — AI & LLMs, ISRO space missions, semiconductors, energy.
7. **Education (ಶಿಕ್ಷಣ)** — National education policies, competitive exams, universities, scholarships.

### 2. Dual Deployment Topologies
- **Android Standalone Mode (Production):** Native Android WebView with Java `AndroidBridge` executing CORS-free HTTP calls, bundled with `engine.js` on-device intelligence pipeline and IndexedDB.
- **Windows Desktop Mode (Development):** Python 3.13 + FastAPI + SQLite (WAL mode) + SQLAlchemy 2.0 + APScheduler.

---

## 🚀 Windows Development Quickstart

### Prerequisites
- Python 3.13+
- Windows PowerShell

### Setup & Run
```powershell
# 1. Activate virtual environment
.\venv\Scripts\Activate.ps1

# 2. Install dependencies
pip install -r requirements.txt

# 3. Apply database migrations
alembic upgrade head

# 4. Start development server
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Access the editorial dashboard at: `http://127.0.0.1:8000`

---

## 🧪 Testing & Verification

The test suite covers database models, ingestion, normalizer, Jaccard deduplication, weighted categorization, fallback heuristic summarizer, Kannada glossary translation, and scheduler execution:

```powershell
pytest -v
```
*(All 20 unit and integration tests passing).*

---

## 📦 Building the Android APK

To rebuild the signed standalone APK from source using the raw Android SDK tools (no Android Studio required):

```powershell
python scripts/build_apk.py
```
Outputs: `Seleneos.apk`

---

## 🔒 Confidentiality & Security

- **Zero Telemetry / Zero Tracking:** No third-party analytics, user tracking, or advertising SDKs.
- **Safe Secrets:** Database files (`*.db`), logs (`*.log`), and environment secrets (`.env`) are strictly excluded from source control via `.gitignore`.
- **Public Domain News:** Collects only permitted public RSS metadata and excerpts, synthesizing independent original summaries.

---

## 📄 License
Personal & Private Edition. All rights reserved.

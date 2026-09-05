# opsPilot

**opsPilot** is a lightweight, intelligent IT operations monitoring platform built from scratch in Python. It continuously watches a machine's CPU, memory, and disk health, automatically detects and tracks incidents, alerts a human by email the moment something goes wrong, and uses an LLM to suggest a likely root cause and fix — all visible on a live, auto-updating dashboard.

It was built as a hands-on learning project to go deep on Python, systems monitoring, databases, REST/WebSocket APIs, and practical LLM integration — not by following a single tutorial, but by designing and debugging each layer end-to-end.

---

## What it actually does

- **Monitors** CPU, memory, and disk usage every 10 seconds using `psutil`.
- **Persists** every reading to a local SQLite database for historical review.
- **Detects incidents** — when a metric crosses a severity threshold, it opens a structured incident record (type, severity, value, timestamps), and automatically resolves it once the metric recovers. Duplicate incidents are prevented (idempotent detection), so a metric flapping above threshold doesn't spam ten "new" incidents.
- **Sends email alerts** via SMTP the moment a new incident is created, with basic rate-limiting so a noisy metric can't flood an inbox.
- **Analyzes incidents with AI** — each new incident is sent to Google's Gemini API with structured context (type, severity, server, value), which returns a plausible root cause and a suggested fix. The AI only *suggests* — nothing is auto-applied. A human always reviews before acting.
- **Serves everything over an API** — a FastAPI backend exposes REST endpoints for current status, historical readings, and incidents, plus a WebSocket endpoint for live metric pushes.
- **Displays a live dashboard** — a single static HTML page connects to the WebSocket for real-time CPU/RAM/Disk cards and polls the incidents endpoint for a continuously refreshing incident table — no manual reload required.

---

## Architecture

```
┌─────────────┐       writes every 10s        ┌──────────────────────┐
│ moniter.py  │ ─────────────────────────────▶ │  SQLite database      │
│ (collector) │                                │  (health_metrics,     │
└─────────────┘                                │   incidents)          │
      │                                        └──────────────────────┘
      │ on new incident                                   ▲
      ▼                                                    │ reads
┌─────────────┐        ┌─────────────┐                     │
│ incidents/  │──────▶ │ notifications│ (SMTP email alert)  │
│ detector.py │        └─────────────┘                     │
│             │                                             │
│             │──────▶ ┌─────────────┐                     │
│             │        │ ai/analyzer  │ (Gemini root cause) │
└─────────────┘        └─────────────┘                     │
                                                             │
                                                     ┌───────┴────────┐
                                                     │    api.py       │
                                                     │  (FastAPI +     │
                                                     │   uvicorn)      │
                                                     └───────┬────────┘
                                                   REST + WebSocket
                                                             │
                                                   ┌─────────▼──────────┐
                                                   │ dashboard/index.html│
                                                   │ (live in browser)  │
                                                   └────────────────────┘
```

`moniter.py` and `api.py` run as two independent processes. They never call each other directly — they communicate purely through the shared SQLite database, which acts as the single source of truth. The dashboard is the only piece that talks to `api.py` over an actual network connection (WebSocket + HTTP).

---

## Tech stack

| Layer | Technology |
|---|---|
| Monitoring | Python, `psutil` |
| Persistence | SQLite |
| Backend API | FastAPI, Uvicorn |
| Real-time updates | WebSockets |
| Alerting | SMTP (`smtplib`) |
| AI root-cause analysis | Google Gemini API (`google-genai`) |
| Frontend | Static HTML, CSS, vanilla JavaScript |
| Config/secrets | `python-dotenv` (`.env`) |

No frontend framework, no ORM, no heavy dependencies — deliberately built close to the metal to actually understand each layer.

---

## Project structure

```
opsPilot/
├── moniter.py              # main monitoring loop — the entry point you run
├── database.py             # SQLite schema + read/write functions
├── api.py                  # FastAPI app — REST + WebSocket endpoints
├── incidents/
│   ├── detector.py         # incident create/resolve logic, idempotency
│   └── severity.py         # maps a usage % to a severity level
├── notifications/
│   ├── config.py           # loads SMTP credentials from .env
│   └── notifier.py         # sends email alerts, with rate-limiting
├── ai/
│   └── analyzer.py         # calls Gemini for root cause + suggested fix
├── dashboard/
│   └── index.html          # live dashboard (WebSocket + REST)
├── .env                    # secrets — never committed (see below)
├── .gitignore
└── requirements.txt
```

---

## Getting started

### 1. Clone and enter the project
```bash
git clone https://github.com/Muhammad1Mujahid/Operations_Pilot.git
cd Operations_Pilot
```

### 2. Create and activate a virtual environment
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root:

```env
# SMTP (email alerts)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_16_char_app_password
ALERT_TO=your_email@gmail.com

# Gemini (AI root cause analysis)
GEMINI_API_KEY=your_gemini_api_key
```

> Gmail requires an **App Password**, not your regular password (Google Account → Security → 2-Step Verification → App Passwords). Get a Gemini key from [Google AI Studio](https://aistudio.google.com/).

### 5. Run the monitor (Terminal 1)
```bash
python3 moniter.py
```

### 6. Run the API server (Terminal 2)
```bash
source venv/bin/activate
uvicorn api:app --reload
```

### 7. Open the dashboard
```
http://127.0.0.1:8000/dashboard/
```

---

## API reference

| Endpoint | Method | Description |
|---|---|---|
| `/system-status` | GET | Latest single health reading |
| `/history?limit=20` | GET | Recent health readings (default 20) |
| `/incidents` | GET | All incidents, newest first, including AI suggestions |
| `/ws/live-status` | WebSocket | Pushes the latest health reading whenever a new one is saved |

Interactive docs (auto-generated by FastAPI) are available at:
```
http://127.0.0.1:8000/docs
```

---

## How incident detection works

Each metric (CPU, Disk Space, Memory) is checked independently every loop pass:

1. If the value crosses a severity threshold (LOW/MEDIUM/HIGH) **and** no incident of that type is currently open → a new incident is created, an email alert fires, and Gemini is asked for a likely cause and fix.
2. If a value crosses a threshold **and** an incident of that type is already open → nothing happens (idempotency — no duplicate spam).
3. If a value returns to healthy **and** an incident of that type is open → the incident is automatically marked `RESOLVED`.

This means a metric that stays critical for ten minutes creates exactly **one** incident, not sixty.

---

## What I learned building this

This project was built iteratively, in phases, with a lot of real debugging along the way — filename typos silently creating phantom SQLite databases, a misindented loop causing triplicate database rows, mismatched severity thresholds across two files causing "silent" failures with no errors, and migrating off a deprecated Gemini SDK mid-project. Working through these was as valuable as the initial build — the codebase reflects a system that's actually been broken and fixed, not just written once.

Concepts practiced: structured data modeling, stateful vs. stateless logic, idempotency, REST vs. WebSocket communication, environment-based secrets management, prompt engineering for structured output, and human-in-the-loop AI design (the model suggests, it never auto-applies fixes).

---

## Roadmap / possible next steps

- [ ] Dockerize `moniter.py` and `api.py` as separate services
- [ ] Add automated tests (`pytest`) for severity logic and incident idempotency
- [ ] CI pipeline via GitHub Actions
- [ ] Deploy to a cloud VM with a live demo link
- [ ] Support monitoring multiple servers, not just localhost

---

## Author

**Muhammad Mujahid** — Computer Science student focused on DevOps, Cloud Engineering, and AI.
GitHub: [@Muhammad1Mujahid](https://github.com/Muhammad1Mujahid)

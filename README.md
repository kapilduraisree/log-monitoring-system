# Log Security Monitoring System v2.0

A full-stack real-time security log monitoring platform with **10 new features** added on top of the original system.

---

## 🆕 10 New Features

| # | Feature | Description |
|---|---------|-------------|
| 1 | **Email Alert Notifications** | SMTP email sent automatically when CRITICAL/HIGH alerts fire |
| 2 | **IP Geolocation** | Country, city, lat/lon shown for every attacker IP (ip-api.com) |
| 3 | **Alert Acknowledgement** | Mark alerts as resolved with reviewer notes; filter by ack status |
| 4 | **User Activity Audit Log** | Every login, delete, upload, and ack action is recorded (admin view) |
| 5 | **Scheduled Reports** | Auto-generate and email daily/weekly/monthly PDF reports via cron |
| 6 | **Dark / Light Theme Toggle** | One-click theme switch with localStorage persistence |
| 7 | **Alert Suppression Rules** | Whitelist IPs or regex patterns to suppress false positives |
| 8 | **Multi-file / Directory Monitoring** | Watch unlimited paths simultaneously; add/remove targets live |
| 9 | **Threat Timeline** | Visual per-IP chronological attack timeline with severity dots |
| 10 | **Two-Factor Authentication (TOTP)** | TOTP 2FA setup via QR code; required at login when enabled |

---

## Tech Stack

| Layer      | Technology |
|------------|-----------|
| Frontend   | React 18, Vite 5, Tailwind CSS 3, Recharts, Axios |
| Backend    | Python 3.11+, FastAPI, SQLAlchemy, SQLite |
| Auth       | JWT (python-jose), bcrypt, TOTP (pyotp) |
| Realtime   | WebSockets (FastAPI native) |
| Monitoring | Watchdog (multi-path) |
| Geo        | ip-api.com (free, no key) |
| Reports    | ReportLab (PDF), csv, json |
| Email      | smtplib (SMTP/TLS) |

---

## Project Structure

```
.
├── app/                        # FastAPI backend
│   ├── api/                    # Route handlers
│   │   ├── auth.py             # Register, login, TOTP (F10)
│   │   ├── logs.py             # Logs CRUD + timeline (F9)
│   │   ├── alerts.py           # Alerts + acknowledge (F3)
│   │   ├── reports.py          # PDF/CSV/JSON + email (F1,F5)
│   │   ├── monitoring.py       # Multi-target monitor (F8)
│   │   ├── suppression.py      # Suppression rules (F7)
│   │   ├── audit.py            # Audit log (F4)
│   │   └── deps.py             # Auth dependencies
│   ├── models/                 # SQLAlchemy ORM models
│   ├── schemas/                # Pydantic schemas
│   ├── database/               # Engine, session, init_db
│   ├── services/               # Business logic
│   ├── detector/               # Engine, rules, log_parser
│   ├── utils/                  # config, logger, helpers, email, geo
│   └── main.py                 # FastAPI app entry point
├── src/                        # React frontend
│   ├── charts/                 # SeverityPie, HourlyEvents, TopIPs, AttackCategories
│   ├── components/             # Layout, Sidebar, Topbar, StatCard, etc.
│   ├── context/                # AuthContext, ThemeContext (F6)
│   ├── hooks/                  # useDashboard, useLogs, useAlerts, useWebSocket, useMonitor
│   ├── pages/                  # Dashboard, Logs, Alerts, Reports, Settings,
│   │                           #   Timeline (F9), Suppression (F7), AuditLog (F4)
│   ├── services/               # api.js + all service modules
│   ├── App.jsx                 # Router
│   ├── main.jsx                # React entry
│   └── index.css               # Tailwind + light/dark theme (F6)
├── uploads/                    # Uploaded log files
├── run.py                      # Uvicorn launcher
├── requirements.txt
├── package.json
├── vite.config.js
├── tailwind.config.js
└── .env
```

---

## Quick Start

### 1 — Backend

```bash
# Create and activate virtual environment
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Configure environment
copy .env.example .env          # Windows
# cp .env.example .env          # macOS/Linux
# Edit .env with your settings

# Start the server
python run.py
# API: http://localhost:8000
# Docs: http://localhost:8000/docs
```

### 2 — Frontend

```bash
npm install
npm run dev
# Open http://localhost:5173
```

### Default Admin Credentials

| Field    | Value         |
|----------|---------------|
| Username | `admin`       |
| Password | `Admin@12345` |

---

## Environment Variables

```env
# Database
DATABASE_URL=sqlite:///./logs_security.db

# Auth
SECRET_KEY=change-me-to-32-chars
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Admin seed
ADMIN_USERNAME=admin
ADMIN_PASSWORD=Admin@12345

# CORS
FRONTEND_URL=http://localhost:5173

# Detection
ALERT_THRESHOLD=5
BRUTE_FORCE_WINDOW=300
MAX_UPLOAD_SIZE_MB=50

# Feature 1: Email alerts
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USER=your@gmail.com
EMAIL_PASSWORD=app-password
EMAIL_FROM=your@gmail.com
EMAIL_TO=admin@company.com
EMAIL_USE_TLS=true

# Feature 5: Scheduled reports
REPORT_SCHEDULE_ENABLED=false
REPORT_SCHEDULE_HOUR=7
REPORT_EMAIL_TO=
```

---

## API Endpoints

```
POST   /api/v1/auth/register
POST   /api/v1/auth/login           (supports totp_code field)
GET    /api/v1/auth/me
POST   /api/v1/auth/logout
POST   /api/v1/auth/totp/setup      # F10
POST   /api/v1/auth/totp/verify     # F10
POST   /api/v1/auth/totp/disable    # F10

GET    /api/v1/logs                 ?page, page_size, severity, event_type, search, sort_desc
GET    /api/v1/logs/stats
GET    /api/v1/logs/hourly
GET    /api/v1/logs/top-ips
GET    /api/v1/logs/attack-categories
GET    /api/v1/logs/timeline        ?ip  (F9)
GET    /api/v1/logs/{id}
DELETE /api/v1/logs/{id}            (admin)

GET    /api/v1/alerts               ?acknowledged filter (F3)
GET    /api/v1/alerts/summary
GET    /api/v1/alerts/critical
POST   /api/v1/alerts/{id}/acknowledge    (F3)
POST   /api/v1/alerts/{id}/unacknowledge  (F3)

GET    /api/v1/report               ?period=daily|weekly|monthly
GET    /api/v1/export/csv
GET    /api/v1/export/json
GET    /api/v1/export/pdf
POST   /api/v1/report/send-email    (F5)

POST   /api/v1/monitor/start
POST   /api/v1/monitor/stop
GET    /api/v1/monitor/status
GET    /api/v1/monitor/targets      (F8)
POST   /api/v1/monitor/targets      (F8)
DELETE /api/v1/monitor/targets/{id} (F8)
POST   /api/v1/upload-log

GET    /api/v1/suppression          (F7)
POST   /api/v1/suppression          (F7)
PATCH  /api/v1/suppression/{id}/toggle (F7)
DELETE /api/v1/suppression/{id}     (F7)

GET    /api/v1/audit                (F4 — admin)

WS     /ws                          real-time alert push
GET    /health
```

---

## Detection Rules

| Rule                 | Severity | Example Pattern |
|----------------------|----------|----------------|
| SQL Injection        | CRITICAL | `UNION SELECT`, `OR 1=1` |
| Brute Force          | CRITICAL | `brute force`, `account locked` |
| Malware              | CRITICAL | `ransomware`, `mimikatz` |
| SSH Auth Failure     | HIGH     | `sshd.*failed` |
| XSS                  | HIGH     | `<script>`, `onerror=` |
| Suspicious IP        | HIGH     | `blacklisted ip` |
| Unauthorized Access  | HIGH     | `access denied`, `sudo.*FAILED` |
| Port Scan            | MEDIUM   | `nmap`, `masscan` |
| Failed Login         | MEDIUM   | `failed login`, `invalid user` |

---

## Production Checklist

- [ ] Change `SECRET_KEY` to a random 32+ char string
- [ ] Change `ADMIN_PASSWORD`
- [ ] Switch `DATABASE_URL` to PostgreSQL
- [ ] Set `FRONTEND_URL` to your domain
- [ ] Configure SMTP for email alerts (Feature 1)
- [ ] Enable `REPORT_SCHEDULE_ENABLED=true` (Feature 5)
- [ ] Serve frontend via `npm run build` + nginx/CDN
- [ ] Run behind HTTPS (TLS at reverse proxy)

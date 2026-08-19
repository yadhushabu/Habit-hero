# Habit Hero

A full-stack habit tracker to build better routines and stay consistent — create habits, check in daily/weekly, track streaks and success rate, earn XP and badges, and export progress as a PDF report.

**Live app:** https://habit-hero-murex.vercel.app
**Backend API:** https://habit-hero-production-5cd7.up.railway.app/api/

---

## Features

### Core
- Create habits with name, frequency (daily/weekly), category (health, work, learning, fitness, mental health, productivity), and start date
- Check in on a habit for a given date, with an optional note
- Delete habits
- Dashboard view of all habits as cards

### Analytics
- **Current streak** — consecutive days/weeks checked in, up to today
- **Best streak** — longest streak ever achieved
- **Success rate** — % of eligible days/weeks checked in since the habit's start date
- **Best days** — which weekday(s) a habit is most often completed on

### Gamification
- **XP system** — 10 XP per check-in, plus bonus XP at streak milestones (7, 14, 30, 60, 100 days)
- **Levels** — XP-based leveling with a simple progress bar to the next level
- **Badges** — unlockable achievements (First Step, Week Warrior, Consistency King, Century Club, High Achiever) based on streak/check-in milestones

### Reporting
- **Export as PDF** — one-click download of a progress report summarizing all habits (streaks, success rate, XP) as a formatted PDF table

---

## Tech Stack

| Layer      | Technology                                      |
|------------|--------------------------------------------------|
| Frontend   | React (Vite), plain CSS                          |
| Backend    | Django + Django REST Framework                   |
| Database   | PostgreSQL (production) / SQLite (local dev)     |
| PDF export | ReportLab                                         |
| Hosting    | Vercel (frontend) + Railway (backend + Postgres) |

---

## Project Structure

```
habit-hero/
├── backend/
│   ├── config/          # Django project settings, URLs, WSGI
│   ├── habits/           # Main app: models, views, serializers, gamification, PDF report
│   ├── manage.py
│   ├── requirements.txt
│   └── Procfile
└── frontend/
    ├── src/
    │   ├── api/           # API client (habits.js)
    │   ├── components/    # HabitCard, HabitForm, GamificationSummary
    │   ├── App.jsx
    │   └── App.css
    └── package.json
```

---

## Local Setup

### Prerequisites
- Python 3.11+
- Node.js 18+
- pip and npm

### Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

pip install -r requirements.txt

python manage.py migrate
python manage.py runserver
```

The API will be running at `http://127.0.0.1:8000/api/`.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

The app will be running at `http://localhost:5173`.

By default, the frontend points at `http://127.0.0.1:8000/api` for local development. To point it at a different backend, set an environment variable:

```
VITE_API_URL=http://127.0.0.1:8000/api
```

---

## API Endpoints

| Method | Endpoint                          | Description                          |
|--------|-------------------------------------|---------------------------------------|
| GET    | `/api/habits/`                     | List all habits (with analytics)      |
| POST   | `/api/habits/`                     | Create a new habit                    |
| GET    | `/api/habits/<id>/`                | Retrieve a single habit               |
| DELETE | `/api/habits/<id>/`                | Delete a habit                        |
| POST   | `/api/habits/<id>/check_in/`       | Check in on a habit                   |
| GET    | `/api/checkins/`                   | List all check-ins                    |
| GET    | `/api/gamification/summary/`       | Get total XP, level, and unlocked badges |
| GET    | `/api/habits/report/pdf/`          | Download a PDF progress report        |

---

## Deployment

- **Backend** is deployed on Railway with a managed PostgreSQL database, served via Gunicorn, static files handled by WhiteNoise.
- **Frontend** is deployed on Vercel as a static Vite build.
- CORS is restricted to the live Vercel origin; `ALLOWED_HOSTS` restricted to the live Railway domain.

---

## Possible Next Steps

- Persist XP on a `Profile` model instead of computing it live, once habit/check-in volume grows
- Calendar view for check-in history
- AI-suggested habits based on existing ones
- Google Calendar sync

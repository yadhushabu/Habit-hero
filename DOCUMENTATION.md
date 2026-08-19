# Habit Hero — Project Documentation

This document covers the architecture, data model, and key design decisions behind Habit Hero. For setup instructions and a feature list, see `README.md`.

---

## 1. Architecture Overview

Habit Hero is a two-tier application: a React single-page frontend and a Django REST API backend, communicating over HTTPS as separate deployments.

```
┌─────────────────┐         HTTPS/JSON          ┌──────────────────────┐
│  React (Vite)    │ ───────────────────────────▶│  Django + DRF         │
│  Vercel           │◀─────────────────────────── │  Railway               │
└─────────────────┘                              │  ┌─────────────────┐  │
                                                    │  │  PostgreSQL      │  │
                                                    │  └─────────────────┘  │
                                                    └──────────────────────┘
```

- The frontend never touches the database directly — all reads/writes go through the DRF API.
- The backend is stateless per request; all persistent state lives in Postgres.
- CORS is used (not a proxy or same-origin setup) since frontend and backend are on different domains (Vercel vs Railway).

---

## 2. Data Model

### `Habit`
| Field         | Type      | Notes                                      |
|---------------|-----------|---------------------------------------------|
| `name`        | CharField | |
| `frequency`   | CharField | `daily` or `weekly`, choice-constrained     |
| `category`    | CharField | health/work/learning/fitness/mental_health/productivity |
| `start_date`  | DateField | Used as the baseline for success-rate calculations |
| `created_at`  | DateTimeField (auto) | |

### `CheckIn`
| Field       | Type       | Notes                                    |
|-------------|------------|--------------------------------------------|
| `habit`     | ForeignKey → Habit, `related_name="checkins"` | |
| `date`      | DateField  | |
| `note`      | TextField (optional) | |
| `created_at`| DateTimeField (auto) | |

`unique_together = ("habit", "date")` — a habit can only be checked in once per calendar date. This is what makes the `check_in` endpoint idempotent (see below).

There is intentionally **no separate model for XP or badges** — see §4.

---

## 3. Analytics Logic (`Habit` model properties)

All analytics are computed **on read**, not stored, via Python `@property` methods on the `Habit` model:

- **`current_streak`** — walks backward day-by-day (or week-by-week for weekly habits) from today, counting consecutive check-ins until a gap is found.
- **`best_streak`** — sorts all check-in dates and finds the longest run of consecutive days (or consecutive week-starts for weekly habits).
- **`success_rate`** — `(check-ins / days-or-weeks-elapsed-since-start) × 100`, capped at 100%.
- **`best_days`** — tallies weekday frequency across all check-ins with `collections.Counter`, returns whichever weekday(s) have the highest count (ties included).

**Why computed properties instead of stored/cached fields:** at the scale of a personal habit tracker (dozens to low hundreds of check-ins per habit), recomputing on every read is cheap and guarantees the numbers are never stale — there's no risk of a cached streak drifting out of sync after a check-in or deletion. The tradeoff is documented in the README's "Next Steps" — this would need to change (cache + update-on-write) if the app scaled to many users or years of daily data.

Weekly-frequency habits use `date.isocalendar()[:2]` (ISO year + week number) to group check-ins into weeks, rather than raw day differences, so streaks correctly span week boundaries regardless of which day of the week a check-in lands on.

---

## 4. Gamification Design

Kept deliberately **stateless and derived**, same philosophy as the analytics above:

- **XP** (`Habit.xp` property) = `check-ins × 10` + streak-milestone bonuses (7/14/30/60/100-day thresholds). Computed live, not stored.
- **Badges** (`Habit.badges` property) — a list of badge definitions in `gamification.py`, each with a `condition` lambda evaluated against the habit's own computed properties (`best_streak`, `checkins.count()`, `success_rate`). A badge "unlocks" simply by its condition evaluating true at read time — there's no `UserBadge` table tracking *when* it was earned.
- **Level** (`gamification.level_for_xp()`) — a simple triangular curve where level *N* requires cumulative `N × 100` XP. Pure function, no model dependency, easy to unit test in isolation.
- **App-wide summary** (`/api/gamification/summary/`) — sums XP and de-duplicates badges across *all* habits, since the product intent is one XP bar/badge shelf per user, not per habit.

**Why this design:** badge definitions can be tuned (thresholds, new badges added) by editing one list in `gamification.py`, with zero migrations and zero risk of stale/inconsistent badge records in the database. The explicit tradeoff — no historical "earned on X date" record — is acceptable for v1 and flagged as a possible next step (a `Profile` model with persisted XP would be needed once check-in volume makes live computation expensive, or if "date earned" becomes a product requirement).

---

## 5. PDF Report Generation

Uses **ReportLab** rather than an HTML-to-PDF renderer (e.g. WeasyPrint):

- Builds the PDF as a sequence of "flowable" elements (`Paragraph`, `Table`, `Spacer`) fed into a `SimpleDocTemplate`, which reportlab lays out and paginates.
- The report is generated **in memory** (`io.BytesIO()`) and streamed back as a `FileResponse` — nothing is written to disk on the server, which matters on Railway/most PaaS hosts where the filesystem is ephemeral between deploys.
- Data source is the same `Habit` queryset and computed properties used everywhere else — the report can never show numbers inconsistent with the live dashboard, since there's only one source of truth for the analytics.

---

## 6. Frontend Structure

- **`api/habits.js`** — single module wrapping all backend calls. A shared `request()` helper handles JSON requests/errors; the PDF download uses a separate function since it needs `.blob()` instead of `.json()`.
- **`App.jsx`** — owns all top-level state (habit list, loading, error) and passes data + callbacks down. No global state library — the app is small enough that prop drilling one level deep is simpler to reason about and explain than introducing Redux/Context for its own sake.
- **`GamificationSummary.jsx`** — fetches its own data independently on mount. Kept deliberately decoupled from the habit list rather than folded into `App.jsx`'s state, so it can be dropped into any page without wiring. It's refreshed after check-ins/deletes via a `key` prop bump on the parent (forces a remount → refetch) rather than a shared state store — a minimal pattern that avoids extra state management for a single dependent component.
- **Environment-based API URL** — `import.meta.env.VITE_API_URL` with a localhost fallback, so the same build can point at different backends (local dev vs. Railway) purely via environment configuration, no code change.

---

## 7. Deployment Notes

- **Backend (Railway)**: Gunicorn as the WSGI server (Django's built-in dev server isn't production-safe — single-threaded, no process management), WhiteNoise for static file serving (avoids needing a separate static file host/CDN for a project this size), `dj-database-url` to parse Railway's injected `DATABASE_URL` into Django's `DATABASES` config.
- **Frontend (Vercel)**: static Vite build; environment variable `VITE_API_URL` is baked in **at build time** (a Vite constraint — changing it requires a rebuild, not just a redeploy, which is a common gotcha).
- **CORS**: `CORS_ALLOWED_ORIGINS` restricted to the live Vercel domain in production, rather than left wide open — the two localhost origins remain as defaults for local dev only.
- **Case sensitivity**: Windows/local dev is case-insensitive for file paths, but Vercel's Linux build environment is not — a component filename/import casing mismatch (`HabitForm` vs `Habitform`) that worked locally broke the production build, which is documented here since it's a common cross-platform gotcha worth knowing for the interview.

---

## 8. Known Limitations / Future Work

- Analytics and gamification are recomputed on every request rather than cached — fine at current scale, would need revisiting under heavier load or larger datasets.
- No authentication/multi-user support — all habits are global to the single deployed instance.
- No historical record of *when* a badge was earned or *when* a level was reached — only current state is derivable.
- PDF report covers all habits in one document; no per-habit or date-range filtering yet.

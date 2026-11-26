# Weaver Workout — Ron & Cindy

Static, offline-capable PWA for the 8-week programs Arnold wrote for **Ron** (calf tear + right THA)
and **Cindy** (left plantar fasciitis, left TKA, right knee OA). No build step, no external dependencies.

Live: https://rweaver3318.github.io/workout-tracker/

## Run locally

```bash
python3 -m http.server 8765   # then open http://127.0.0.1:8765/
```

## Program data (regenerate after Arnold edits a plan)

| File | Source | Builder |
|------|--------|---------|
| `program-ron-2027.json` | `/workspace/arnold/pickleball-2027/plan.md` (Ron's Pickleball & Golf Year 2026-27, **current**) | `build_program_ron_2027.py` (+ `ron2027_*.py`) |
| `program-ron.json` | `/workspace/arnold/program.md` (Ron's old 8-week plan, archived, no longer loaded) | `build_program.py` |
| `program-cindy.json` | `/workspace/arnold/cindy/program.md` | `build_program_cindy.py` |

```bash
python3 build_program_ron_2027.py  # Ron's current plan (also rewrites plan.md)
python3 build_program.py         # rebuilds BOTH old 8-week files
python3 build_program_cindy.py   # Cindy only
```

The builders are structured Python mirrors of the markdown plans (edit the lists, re-run).
The shared JSON schema is documented at the top of `program_common.py`: level system (Ron calf 0–7,
Cindy PF 0–5), week/knee-band blocks, static lists, per-session-type templates, dated schedule, pain fields.
**Keep exercise ids stable**: they key the logged data.

## Ron's plan is a sequence, not a schedule

`program-ron-2027.json` has `"kind": "sequence"`: 117 numbered workouts (39 weeks x Legs / Sport / Upper) with
phase and week context, an exercise `library` (how-to, demo link, easier option, swap) and `phases` / `weeks`.
The home screen shows the first unfinished workout. Dates are only *projected*: unfinished workouts are laid onto
the training days in Settings (default Sun, Tue, Fri), one per day from today (tomorrow if one was finished today),
never before the plan start date; finished ones sit on the day they were done. No reminders or notifications.
Logs are keyed by workout id (`w001`...), with `completedOn` and per-exercise `pain`.

## Data

- localStorage: Ron's current plan `workout:v3:ron:pg2026-27`; Cindy `workout:v2:cindy`; last person `workout:v2:activePerson`.
- Ron's old 8-week plan log stays untouched in `workout:v2:ron` (archive; exportable from Settings and included in JSON exports).
- v1 data (`ron-workout-v1`) is copied into the `workout:v2:ron` archive on first load, and the old key is kept as a backup.
- Settings → Backup: export JSON/CSV for the selected person or both. Import accepts either kind, plus v1 Ron backups.

## Release checklist

Bump `CACHE` in `sw.js` and `APP_BUILD` in `app.js` so installed phones pick up the new version.

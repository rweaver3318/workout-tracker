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
| `program-ron.json` | `/workspace/arnold/program.md` (+ Sep 24 hip update / priorities) | `build_program.py` |
| `program-cindy.json` | `/workspace/arnold/cindy/program.md` | `build_program_cindy.py` |

```bash
python3 build_program.py         # rebuilds BOTH
python3 build_program_cindy.py   # Cindy only
```

The builders are structured Python mirrors of the markdown plans (edit the lists, re-run).
The shared JSON schema is documented at the top of `program_common.py`: level system (Ron calf 0–7,
Cindy PF 0–5), week/knee-band blocks, static lists, per-session-type templates, dated schedule, pain fields.
**Keep exercise ids stable**: they key the logged data.

## Data

- localStorage, one key per person: `workout:v2:ron`, `workout:v2:cindy`; last person: `workout:v2:activePerson`.
- v1 data (`ron-workout-v1`) is copied into Ron's namespace on first load, and the old key is kept as a backup.
- Settings → Backup: export JSON/CSV for the selected person or both. Import accepts either kind, plus v1 Ron backups.

## Release checklist

Bump `CACHE` in `sw.js` and `APP_BUILD` in `app.js` so installed phones pick up the new version.

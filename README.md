# Ron Workout — phone-friendly tracker

Static PWA for Ron Weaver’s 8-week calf rehab + strength plan (Arnold).

## Run locally

```bash
cd /workspace/workout-app
python3 -m http.server 8765
# open http://127.0.0.1:8765/
```

No build step. Offline after first load (service worker).

## Regenerate program.json

Edit `build_program.py` (structured mirror of `/workspace/arnold/program.md`), then:

```bash
python3 build_program.py
```

Do **not** edit Arnold’s files from this app.

## Data

Logs live in `localStorage` key `ron-workout-v1`. Use Settings → Export JSON/CSV or Import JSON.

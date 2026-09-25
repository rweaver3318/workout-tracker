#!/usr/bin/env python3
"""
Build program-cindy.json from Arnold's plan for Cindy Weaver.

Source: /workspace/arnold/cindy/program.md (+ sessions/2026-09-27.md).
Run standalone (`python3 build_program_cindy.py`) or via build_program.py (builds both).
Schema: see program_common.py. Keep exercise ids stable (they key logged data).

Mapping:
  heel levels 0–5          → levelSystem.levels (set manually in Settings)
  Daily DiGiovanni etc.  → lists.daily (shown at the top of every session)
  Knee bands A–D         → blocks.knee (keyed by schedule row kneeBand); ◆ = diamond
  Shoulders / hips wks   → blocks.shoulders / blocks.hips (keyed by weekBand)
  Sun H / Tue S / Fri M  → sessionTemplates (S = knee ◆ only + full shoulders;
                           M = full knee + first 2 hip + first 2 shoulder)
  † answer-dependent     → exercise.flag = "†" + flagNote; table in answerDependent
"""
from __future__ import annotations

from program_common import ex, week_band, write

T = "†"

PROGRAM = {
    "person": "cindy",
    "displayName": "Cindy",
    "athlete": "Cindy Weaver",
    "timezone": "America/New_York",
    "conditions": "LEFT plantar fasciitis (first-step heel pain 5/10 baseline) · LEFT TKA ~2.5 yrs ago (no surgeon limits) · RIGHT knee OA (1/10 typical, 2/10 after pickleball)",
    "programWindow": "Sun Sep 27 – Fri Nov 20, 2026 · Sun/Tue/Fri · 24 sessions",
    "startDate": "2026-09-27",
    "endDate": "2026-11-20",
    "disclaimer": (
        "Educational training plan, not a medical diagnosis or prescription. "
        "Stop and see a doctor for any red-flag symptoms."
    ),
    "banner": "Heel & knee pain ≤2–3/10, settled within 24 h, first-step heel pain no worse than baseline (5/10). Knee over 2nd toe, slow. Stop for locking, giving way, hot swollen knee, numbness, calf swelling.",
    "painRules": {
        "ceiling": 3,
        "pass": "Pain ≤2–3/10 during AND settles within 24 h AND first-step heel pain no worse than baseline (5/10 or current usual if lower)",
        "hold": "Pain >3 during, OR not settled in 24 h, OR first-step worse, OR knee more swollen → HOLD heel level / reduce knee load; DROP a heel level after 2 fails",
        "advance": "2–3 consecutive PASS sessions to advance a heel level",
        "kneeBand": "Knee band moves up every 2 weeks only if most sessions in the band were PASS; otherwise repeat the band",
        "pickleball": "Pickleball = heel load. If first-step pain ≥7/10 (2+ above baseline) for 2 days, HOLD heel level and trim court time first",
        "quality": "GLA:D quality: knee over 2nd toe, pelvis level, slow control. If form breaks, reduce load/range before adding weight",
    },
    "redFlags": [
        "Heel pain worse at rest/night or not matching the usual first-step pattern",
        "Numbness, tingling, or burning in the foot/heel",
        "Calf swelling, warmth, redness, or new deep calf pain (possible clot)",
        "Knee locking, giving way, or a hot, swollen knee",
        "Pain or instability in the replaced (left) knee",
        "Sudden pop in heel/arch with sharp pain or bruising",
        "Fever, feeling unwell, chest pain, or shortness of breath",
    ],
    "sessionTypes": {
        "H": "Heel level + Knee band + Hips/Glutes",
        "S": "Heel level + Knee band (◆ only) + Shoulders",
        "M": "Heel level + Knee band + Mixed (2 hip + 2 shoulder)",
        "R": "Week 8 reassessment (light heel work + tests)",
    },
    "optionalTypes": [],
    "notes": [
        "Heel levels (left foot) = symptom-based levels 0–5. Start Level 0; stay double-leg through Level 3; don't skip levels.",
        "Knee bands A–D move every 2 weeks if sessions PASS. No high-impact, no deep kneeling, no deep loaded knee flexion early.",
        "Keep her playing: gym sessions on lighter/no-pickleball days or AFTER play – never heavy heel/knee work right before play.",
        "Pickleball = heel load: log first-step heel pain the morning after play. ≥7/10 two days running → hold the heel level, trim court time first.",
        "DiGiovanni stretch daily (incl. rest days), first set before first steps. Supportive shoes; no barefoot on hard floors.",
        "Week 8 success marker: first-step heel pain ≤3/10 (baseline 5/10).",
        "† = answer-dependent: progress only per the note on that exercise.",
    ],
    "pain": {
        "title": "Heel/foot + knee pain trend",
        "ceiling": 3,
        "fields": [
            {"key": "heelDuring", "label": "Heel/foot pain during session", "short": "Heel (during)", "when": "during", "color": "#7b3f8c"},
            {"key": "kneeDuring", "label": "Knee pain during session", "short": "Knee (during)", "when": "during", "color": "#1d6fa5"},
            {"key": "firstStep", "label": "First-step heel pain next morning", "short": "First-step heel (AM)", "when": "morning", "color": "#c45c26", "baseline": 5, "goal": 3},
            {"key": "kneeMorning", "label": "Knee pain next morning", "short": "Knee (next AM)", "when": "morning", "color": "#6b7280"},
        ],
    },
}

# ---------------- heel levels ----------------
PF_LEVELS = [
    {"level": 0, "name": "Gentle activation", "estimate": "Weeks 1–2",
     "entry": "Heel pain present; no red flags.",
     "exit": "Pain ≤2–3/10; first-step pain not worse; exercises feel easy. Advance after 2–3 PASS.",
     "exercises": [
         ex("pf0-seated-raise", "Seated heel raises (both feet)", "2", reps="15", load="Bodyweight · 2 seconds up, hold 1 second, 2 seconds down", notes="Knees bent ~90°."),
         ex("pf0-short-foot", "Short foot (arch doming), seated", "5", hold="5 s", load="Gentle", notes="Shorten the foot without curling the toes."),
         ex("pf0-toe-yoga", "Toe yoga", "2", reps="10", load="Slow", notes="Big toe up / others down, then switch. Seated."),
         ex("pf0-towel", "Towel curls, seated", "2", hold="30–45 s", load="Easy", notes="Scrunch a towel toward the heel."),
         ex("pf0-calf-stretch", "Gentle wall calf stretch (straight + bent knee)", "2", hold="30 s each", load="Comfortable", notes="No bouncing."),
     ]},
    {"level": 1, "name": "Loaded seated + supported standing", "estimate": "Weeks 2–3",
     "entry": "Level 0 exit met.",
     "exit": "2–3 PASS; 3×15 seated raises at 20 lb and 2×10 standing raises comfortable.",
     "exercises": [
         ex("pf1-seated-calf", "Seated calf raise (soleus)", "3", reps="12–15", load="10–20 lb dumbbell on knees · 2 seconds up, hold 1 second, 2 seconds down", notes="Both feet."),
         ex("pf1-standing-dl", "Standing double-leg heel raise, flat floor", "2", reps="10", load="Bodyweight · 2 seconds up, hold 1 second, 2 seconds down", notes="Hands on counter/rack."),
         ex("pf1-short-foot", "Short foot, standing", "5", hold="5 s", load="Gentle", notes="Both feet."),
         ex("pf1-towel-yoga", "Towel curls or toe yoga", "2", reps="10 / 30 s", load="—", notes="Pick one."),
     ]},
    {"level": 2, "name": "Standing double-leg strength", "estimate": "Weeks 3–4",
     "entry": "Level 1 exit met.",
     "exit": "2–3 PASS; 3×15 standing double-leg raises through full range with control.",
     "exercises": [
         ex("pf2-dl-straight", "Standing double-leg heel raise (straight knee)", "3", reps="12–15", load="Bodyweight · 3 seconds up, no pause, 3 seconds down", notes="Light hand support."),
         ex("pf2-dl-bent", "Standing double-leg heel raise (bent knee ~20–30°)", "3", reps="10–12", load="Bodyweight · 3 seconds up, no pause, 3 seconds down", notes="Soleus bias; knees over toes."),
         ex("pf2-seated-calf", "Seated calf raise", "3", reps="12", load="20–30 lb · 2 seconds up, hold 1 second, 2 seconds down", notes=""),
         ex("pf2-short-foot", "Short foot, standing (hold during raise set-up)", "5", hold="5 s", load="—", notes=""),
     ]},
    {"level": 3, "name": "Double-leg Rathleff-style raise (towel under toes)", "estimate": "Weeks 4–5",
     "entry": "Level 2 exit met.",
     "exit": "2–3 PASS; 3×12 towel raises with some load; first-step pain stable or improving.",
     "exercises": [
         ex("pf3-rathleff-dl", "double-leg heel raise on step edge, rolled towel under toes", "3", reps="12",
            load="Bodyweight → light backpack", notes="3 s up, 2 s hold, 3 s down. Heels drop only to comfortable depth.",
            cues="3 seconds up, hold 2 seconds, 3 seconds down tempo."),
         ex("pf3-bent-knee", "Bent-knee double-leg heel raise", "3", reps="12", load="Hold 10–15 lb dumbbell · 3 seconds up, no pause, 3 seconds down", notes=""),
         ex("pf3-seated-calf", "Seated calf raise", "3", reps="12", load="30 lb · 2 seconds up, hold 1 second, 2 seconds down", notes=""),
     ]},
    {"level": 4, "name": "Single-leg transition (assisted)", "estimate": "Weeks 5–6",
     "entry": "Level 3 exit met.",
     "exit": "2–3 PASS; 3×12 unassisted single-leg towel raises on the left, pain ≤2–3/10.",
     "exercises": [
         ex("pf4-rathleff-sl-l", "Rathleff heel raise (LEFT), assisted", "3", reps="12-repetition maximum", load="Bodyweight · 3 seconds up, hold 2 seconds, 3 seconds down",
            notes="Towel under toes, step edge; right foot helps lightly. Wean off assist over sessions.",
            flag=T, flag_note="Heel irritability and balance – stays double-leg if first-step pain is high."),
         ex("pf4-sl-r", "Right side for balance", "3", reps="12", load="3 seconds up, hold 2 seconds, 3 seconds down", notes="Match both sides."),
         ex("pf4-bent-knee", "Bent-knee heel raise (double-leg)", "3", reps="12", load="15–20 lb · 3 seconds up, no pause, 3 seconds down", notes=""),
     ]},
    {"level": 5, "name": "Full Rathleff high-load protocol", "estimate": "Weeks 6–8+",
     "entry": "Level 4 exit met.",
     "exit": "Maintain 2–3×/week; first-step pain ≤3/10 (success marker); pickleball weeks tolerated without flare.",
     "exercises": [
         ex("pf5-rathleff", "Rathleff single-leg heel raise (towel, step edge)", "3 / 4 / 5", reps="12-repetition maximum / 10-repetition maximum / 8-repetition maximum",
            load="Backpack or dumbbell in same-side hand",
            notes="Stage 5a 3×12-repetition maximum → 5b 4×10-repetition maximum → 5c 5×8-repetition maximum. 3 s up / 2 s hold / 3 s down. Move stages only after 2–3 PASS at each. Log your stage in the note.",
            flag=T, flag_note="Heel irritability and balance – stays double-leg if first-step pain is high."),
         ex("pf5-soleus", "Bent-knee soleus raise", "3", reps="12", load="Moderate", notes="Keep one bent-knee soleus exercise."),
     ]},
]

# ---------------- Static lists ----------------
DAILY = [
    ex("cd-digiovanni", "DiGiovanni plantar fascia stretch (left)", "10", hold="10 s",
       load="Up to 3×/day", notes="Seated, left ankle over right knee, pull toes back until the arch tightens. First set BEFORE first steps in the morning; also at cool-down.",
       cues="Daily, including rest days."),
]
WARMUP = [
    ex("cw-bike", "Warm-up: upright bike or brisk walk", "1", hold="5 min", load="Easy",
       notes="Bike at Fayetteville; otherwise easy walk in supportive shoes."),
]
BASELINE = [
    ex("cb-chair-stand", "Baseline: 30-s chair stand (standard chair, arms crossed)", "1", reps="max in 30 s", load="bodyweight", notes="Record reps."),
    ex("cb-dl-raise", "Baseline: double-leg heel raises (3 seconds up, no pause, 3 seconds down) to fatigue", "1", reps="max", load="bodyweight", notes="Record reps."),
    ex("cb-sl-stand", "Baseline: single-leg stand L / R", "1", hold="max 30 s each", load="Near support", notes="Record L and R seconds in the note."),
    ex("cb-first-step", "Baseline: first-step heel pain this morning", "1", reps="0–10", load="—", notes="Intake baseline 5/10; goal by Week 8 ≤3/10."),
]
REASSESSMENT = [
    ex("cr-heel", "Heel pain: avg first-step pain, last 7 days", "1", reps="0–10", load="—", notes="Success marker ≤3/10 (baseline 5/10)."),
    ex("cr-heel-raise", "Heel raise test: max double-leg (3 seconds up, no pause, 3 seconds down) and max single-leg each side", "1", reps="max", load="bodyweight", notes=""),
    ex("cr-chair-stand", "30-s chair stand", "1", reps="max in 30 s", load="bodyweight", notes="Standard chair, arms crossed."),
    ex("cr-walk", "40-m fast-paced walk (10 m × 4)", "1", reps="time", load="—", notes="Record seconds."),
    ex("cr-stepup", "Step-up: highest step 8×/side, good alignment", "1", reps="8/side", load="bodyweight", notes=""),
    ex("cr-sl-stand", "Single-leg stand each side", "1", hold="max 30 s", load="—", notes=""),
    ex("cr-shoulders", "Shoulders: band external rotation 15/side; arm raise at an angle (thumbs up) 10 at current load", "1", reps="as listed", load="Band / dumbbell", notes="Pain-free."),
    ex("cr-knee", "Knee check: pain/swelling after + next morning", "1", reps="—", load="—", notes="Note any change in the replaced knee."),
    ex("cr-sport", "Sport tolerance + confidence 0–10", "1", reps="—", load="—", notes="Pickleball 5×/wk and golf 2–3×/wk over the last 2 weeks."),
]

# ---------------- Knee bands (Sun/Fri full; ◆ = Tue list) ----------------
STEP_NOTE = "Stairs mildly bother the right OA knee – progress height only if next-day knee pain ≤2/10."
SQUAT_NOTE = "No TKA limits; depth set by right-knee OA tolerance (next-day response)."
KNEE = {
    "A": [
        ex("ka-sts-high", "Sit-to-stand, HIGH seat (chair + cushion)", "3", reps="8", load="3 s down / 1 s up · bodyweight",
           notes="Knees over 2nd toe; hands free if possible.", diamond=True),
        ex("ka-knee-ext", "Seated knee extension, band", "2", reps="10/side", load="2 seconds up, hold 1 second, 3 seconds down · light band",
           notes="Band anchored to chair leg.", diamond=True),
        ex("ka-ham-curl", "Standing hamstring curl, band", "2", reps="10/side", load="2 seconds up, hold 1 second, 2 seconds down · light band", notes="Hold counter."),
        ex("ka-wall-sit", "Wall sit, shallow (~30–45°)", "3", hold="20 s", load="Isometric", notes="Pain ≤2–3/10."),
    ],
    "B": [
        ex("kb-sts", "Sit-to-stand, standard chair", "3", reps="10", load="3 seconds down, no pause, 1 second up · bodyweight → 10 lb goblet", notes="", diamond=True),
        ex("kb-stepup-low", "Step-up, low step (~4–6\")", "2", reps="8/side", load="Controlled", notes="Rail/wall support; knee over foot."),
        ex("kb-knee-ext", "Seated knee extension, band", "3", reps="12/side", load="2 seconds up, hold 1 second, 3 seconds down · medium band", notes="", diamond=True),
        ex("kb-ham-curl", "Hamstring curl, band (standing or seated)", "3", reps="10/side", load="2 seconds up, hold 1 second, 2 seconds down", notes=""),
        ex("kb-wall-sit", "Wall sit or Spanish squat (~45°)", "3", hold="30 s", load="Isometric", notes="Spanish squat: band around rack post (Fayetteville)."),
    ],
    "C": [
        ex("kc-box-squat", "Box squat to bench", "3", reps="8", load="3 seconds down, hold 1 second, 1 second up · 10–15 lb goblet",
           notes="Touch bench lightly, don't collapse.", diamond=True, flag=T, flag_note=SQUAT_NOTE),
        ex("kc-stepup", "Step-up, low to higher step (~6–8\")", "3", reps="8/side", load="bodyweight → 10 lb dumbbells",
           notes="Controlled.", flag=T, flag_note=STEP_NOTE),
        ex("kc-knee-ext", "Seated knee extension, band or dumbbell between feet", "3", reps="12", load="2 seconds up, hold 1 second, 3 seconds down · heavier band", notes="", diamond=True),
        ex("kc-ham-curl", "Hamstring curl, band", "3", reps="12/side", load="2 seconds up, hold 1 second, 2 seconds down", notes=""),
        ex("kc-spanish", "Spanish squat / wall sit", "4", hold="30–45 s", load="Isometric", notes=""),
    ],
    "D": [
        ex("kd-goblet", "Goblet squat to comfortable depth (≈ bench height)", "3", reps="8", load="3 seconds down, hold 1 second, 1 second up · 15–20 lb",
           notes="Knees over toes; stop before pain. Not deep.", diamond=True, flag=T, flag_note=SQUAT_NOTE),
        ex("kd-stepup", "Step-up, 8\"", "3", reps="8/side", load="10–15 lb dumbbells", notes="", flag=T, flag_note=STEP_NOTE),
        ex("kd-stepdown", "Forward step-down, low step", "2", reps="6/side", load="Slow 3 s lower",
           notes="Knee-over-foot control.", flag=T, flag_note=STEP_NOTE),
        ex("kd-knee-ext", "Knee extension (band/dumbbell)", "3", reps="12", load="2 seconds up, hold 1 second, 3 seconds down", notes="", diamond=True),
        ex("kd-ham-curl", "Hamstring curl, band", "3", reps="12", load="2 seconds up, hold 1 second, 2 seconds down", notes=""),
        ex("kd-bike-int", "Bike intervals (finisher)", "6", hold="30 s moderate / 60 s easy", load="Upright bike", notes="", optional=True),
    ],
}

# ---------------- Shoulders (Tue full; Fri first 2) ----------------
SHOULDERS = {
    "1-2": [
        ex("cs12-er", "Band external rotation (elbow at side, towel roll)", "2", reps="12/side", load="Lightest band", notes=""),
        ex("cs12-ir", "Band internal rotation", "2", reps="12/side", load="Lightest band", notes=""),
        ex("cs12-row", "Seated band row", "2", reps="12", load="Light band", notes="Squeeze shoulder blades."),
        ex("cs12-wallslide", "Wall slides", "2", reps="8", load="—", notes="Forearms on wall."),
        ex("cs12-scaption", "Arm raise at an angle (thumbs up) to shoulder height (slight V)", "2", reps="10", load="None / water bottles", notes=""),
    ],
    "3-4": [
        ex("cs34-erir", "Band external rotation / internal rotation", "3", reps="12/side", load="Light–medium band", notes=""),
        ex("cs34-facepull", "Band face pull", "3", reps="12", load="Light band", notes="Anchor at face height."),
        ex("cs34-pullapart", "Band pull-apart", "2", reps="12", load="Light band", notes=""),
        ex("cs34-scaption", "Arm raise at an angle (thumbs up)", "3", reps="10", load="Water bottles or half-gallon jug", notes=""),
        ex("cs34-wallpush", "Wall push-up", "2", reps="8–10", load="Bodyweight", notes=""),
    ],
    "5-6": [
        ex("cs56-erir", "Band external rotation / internal rotation", "3", reps="12–15/side", load="Medium band", notes=""),
        ex("cs56-dbrow", "One-arm dumbbell row (hand on bench)", "3", reps="10/side", load="10–15 lb", notes=""),
        ex("cs56-facepull", "Face pull", "3", reps="12", load="Medium band", notes=""),
        ex("cs56-scaption", "Arm raise at an angle (thumbs up)", "3", reps="10", load="10 lb dumbbells or gallon jugs", notes="Stop at shoulder height."),
        ex("cs56-incline-push", "Incline push-up (bench or rack bar)", "3", reps="8", load="Bodyweight", notes=""),
    ],
    "7-8": [
        ex("cs78-er45", "Band external rotation at 45° abduction", "3", reps="12/side", load="Medium band", notes="Pain-free."),
        ex("cs78-dbrow", "dumbbell row", "3", reps="10/side", load="15–20 lb", notes=""),
        ex("cs78-ohp", "Seated dumbbell overhead press (light)", "2", reps="8", load="10 lb", notes="Pain-free range only."),
        ex("cs78-superset", "Face pull + wall slide superset", "3", reps="12 / 8", load="Medium band", notes=""),
        ex("cs78-chop", "Standing band chop (golf rotation prep)", "2", reps="10/side", load="Light band",
           notes="Pivot on feet, soft knees.", flag=T,
           flag_note="Standing as written. Any half-kneel version depends on kneeling tolerance on the replaced knee – pad required."),
    ],
}

# ---------------- Hips (Sun full; Fri first 2) ----------------
HIPS = {
    "1-2": [
        ex("ch12-bridge", "Glute bridge", "2", reps="10", load="Bodyweight", notes="2 s squeeze at top."),
        ex("ch12-abd", "Side-lying hip abduction", "2", reps="10/side", load="Bodyweight", notes="Toes forward, slow lower."),
        ex("ch12-hinge", "Hip hinge with dowel/broomstick", "2", reps="8", load="Dowel on back", notes="Head, upper back, tailbone contact. Learn the pattern."),
        ex("ch12-band-abd", "Standing band hip abduction", "2", reps="10/side", load="Light band", notes="Hold support."),
    ],
    "3-4": [
        ex("ch34-bridge", "Glute bridge", "3", reps="12", load="bodyweight → band above knees", notes=""),
        ex("ch34-abd", "Side-lying abduction", "3", reps="12/side", load="Bodyweight", notes=""),
        ex("ch34-latwalk", "Lateral band walk (band above knees)", "3", reps="8 steps each way", load="Light band", notes="Knees over toes."),
        ex("ch34-rdl", "Hip hinge to dumbbell Romanian deadlift", "3", reps="8", load="Dowel → 10 lb dumbbells", notes="Soft knees, flat back."),
    ],
    "5-6": [
        ex("ch56-rdl", "dumbbell Romanian deadlift", "3", reps="8–10", load="15–20 lb dumbbells", notes=""),
        ex("ch56-slbridge", "Single-leg bridge (or staggered-stance)", "3", reps="8/side", load="Bodyweight", notes=""),
        ex("ch56-latwalk", "Lateral band walk", "3", reps="10 steps each way", load="Medium band", notes=""),
        ex("ch56-abd", "Side-lying abduction", "3", reps="15/side", load="Light ankle band optional", notes=""),
    ],
    "7-8": [
        ex("ch78-rdl", "dumbbell Romanian deadlift", "3", reps="8", load="20–30 lb dumbbells", notes="Or light barbell if form is excellent."),
        ex("ch78-thrust", "Hip thrust (upper back on bench)", "3", reps="10", load="bodyweight → 20 lb dumbbell on hips", notes="Pad under dumbbell."),
        ex("ch78-bandwalk", "Band walks (forward + lateral)", "3", reps="10 steps", load="Medium band", notes=""),
        ex("ch78-sl-stand", "Single-leg stand (balance)", "3", hold="20–30 s/side", load="Near support", notes="Golf/pickleball balance."),
    ],
}

SCHEDULE_ROWS = [
    ("2026-09-27", "Sun", 1, "A", "H", "H — Session 1 (Heel Level 0 start; record baseline)"),
    ("2026-09-29", "Tue", 1, "A", "S", "S"),
    ("2026-10-02", "Fri", 1, "A", "M", "M"),
    ("2026-10-04", "Sun", 2, "A", "H", "H"),
    ("2026-10-06", "Tue", 2, "A", "S", "S"),
    ("2026-10-09", "Fri", 2, "A", "M", "M"),
    ("2026-10-11", "Sun", 3, "B", "H", "H"),
    ("2026-10-13", "Tue", 3, "B", "S", "S"),
    ("2026-10-16", "Fri", 3, "B", "M", "M"),
    ("2026-10-18", "Sun", 4, "B", "H", "H"),
    ("2026-10-20", "Tue", 4, "B", "S", "S"),
    ("2026-10-23", "Fri", 4, "B", "M", "M"),
    ("2026-10-25", "Sun", 5, "C", "H", "H"),
    ("2026-10-27", "Tue", 5, "C", "S", "S"),
    ("2026-10-30", "Fri", 5, "C", "M", "M"),
    ("2026-11-01", "Sun", 6, "C", "H", "H"),
    ("2026-11-03", "Tue", 6, "C", "S", "S"),
    ("2026-11-06", "Fri", 6, "C", "M", "M"),
    ("2026-11-08", "Sun", 7, "D", "H", "H"),
    ("2026-11-10", "Tue", 7, "D", "S", "S"),
    ("2026-11-13", "Fri", 7, "D", "M", "M"),
    ("2026-11-15", "Sun", 8, "D", "H", "H"),
    ("2026-11-17", "Tue", 8, "D", "S", "S"),
    ("2026-11-20", "Fri", 8, "D", "R", "R — Week 8 reassessment (Session 24; light heel work + tests)"),
]

ANSWER_DEPENDENT = [
    {"exercise": "Goblet squat / box squat depth", "why": "No surgeon limits on the TKA. Depth is set by right-knee OA tolerance (next-day response)"},
    {"exercise": "Step-ups 8\" and step-downs", "why": "Stairs are mildly bothersome for the right OA knee. Progress height only if next-day pain ≤2/10"},
    {"exercise": "Any half-kneel (e.g., band chops)", "why": "Kneeling tolerance on the replaced knee; pad required"},
    {"exercise": "Rathleff single-leg heel raise (Level 4–5)", "why": "Heel irritability and balance; stays double-leg if first-step pain is high"},
    {"exercise": "Treadmill incline / walking volume", "why": "Current walking tolerance and first-step pain"},
    {"exercise": "Pickleball volume/intensity", "why": "Already playing 5×/week with no TKA limits. Adjust by the next-morning first-step heel pain rule"},
]


def build() -> dict:
    data = dict(PROGRAM)
    data["levelSystem"] = {
        "key": "pf",
        "label": "Heel level",
        "short": "Heel L",
        "advanceRule": "Advance after 2–3 consecutive PASS sessions (pain ≤2–3/10, settled in 24 h, first-step heel pain not worse). Stay double-leg through Level 3.",
        "levels": PF_LEVELS,
    }
    data["blocks"] = {
        "knee": {"label": "Knees", "keyField": "kneeBand", "bands": KNEE},
        "hips": {"label": "Hips / Glutes", "keyField": "weekBand", "bands": HIPS},
        "shoulders": {"label": "Shoulders", "keyField": "weekBand", "bands": SHOULDERS},
    }
    data["lists"] = {
        "daily": {"title": "Daily foot care", "exercises": DAILY},
        "warmup": {"title": "Warm-up (5 min)", "exercises": WARMUP},
        "baseline": {"title": "Baseline tests (end of session)", "exercises": BASELINE},
        "reassessment": {"title": "Week 8 Reassessment", "exercises": REASSESSMENT},
    }
    pf = {"title": "Foot — Heel Level {level}: {levelName}", "source": "level"}
    daily = {"title": "Daily foot care", "source": "list", "list": "daily"}
    warm = {"title": "Warm-up (5 min)", "source": "list", "list": "warmup"}
    data["sessionTemplates"] = {
        "H": [daily, warm, pf,
              {"title": "Knees — Band {kneeBand}", "source": "block", "block": "knee"},
              {"title": "Hips / Glutes (Weeks {weekBand})", "source": "block", "block": "hips"}],
        "S": [daily, warm, pf,
              {"title": "Knees — Band {kneeBand} (◆ items only)", "source": "block", "block": "knee", "filter": "diamond"},
              {"title": "Shoulders (Weeks {weekBand})", "source": "block", "block": "shoulders"}],
        "M": [daily, warm, pf,
              {"title": "Knees — Band {kneeBand}", "source": "block", "block": "knee"},
              {"title": "Mixed — Hips (first 2, Weeks {weekBand})", "source": "block", "block": "hips", "first": 2},
              {"title": "Mixed — Shoulders (first 2, Weeks {weekBand})", "source": "block", "block": "shoulders", "first": 2}],
        "R": [daily,
              {"title": "Light heel work — Level {level} (first 2)", "source": "level", "first": 2},
              {"title": "Week 8 Reassessment", "source": "list", "list": "reassessment"}],
    }
    data["answerDependent"] = ANSWER_DEPENDENT
    data["conditioningNotes"] = [
        "Upright bike: best low-impact option; 5-min warm-up each session, +10–15 min easy on non-training days if wanted.",
        "Walking: supportive shoes, flat routes, build ~5 min/week if first-step pain stays stable.",
        "Treadmill: walking only, no incline early; small incline after Heel Level 3 (†).",
        "Assault bike: optional from Week 5, short easy bouts.",
        "Pickleball is her main conditioning – no extra running/jumping this block.",
    ]
    data["schedule"] = []
    for d, day, week, band, typ, label in SCHEDULE_ROWS:
        row = {"date": d, "day": day, "week": week, "type": typ, "label": label,
               "weekBand": week_band(week), "kneeBand": band}
        if d == "2026-09-27":
            row["extras"] = ["baseline"]
        data["schedule"].append(row)
    data["source"] = {"programMd": "/workspace/arnold/cindy/program.md",
                      "sessionExample": "/workspace/arnold/cindy/sessions/2026-09-27.md"}
    return data


def main() -> None:
    write(build(), "program-cindy.json")


if __name__ == "__main__":
    main()

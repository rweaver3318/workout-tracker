#!/usr/bin/env python3
"""
Build program.json from Arnold's 8-week plan.

Source of truth for content: /workspace/arnold/program.md
(and Session 1 detail in /workspace/arnold/sessions/2026-09-25.md).

This script embeds a structured mirror of that content so regenerating
or editing is easy — re-run after Arnold adjusts the plan:

    python3 build_program.py

JSON schema (top-level):
  athlete, injury, programWindow, startDate, endDate
  painRules, redFlags
  calfLevels[]     — criteria-based levels 0–7 (exercises change by level)
  shouldersByWeek  — { "1-2": [...], "3-4": [...], ... }
  hipsByWeek       — same week-band keys
  conditioningNotes[]
  schedule[]       — dated sessions {date, day, week, type, label}
  sessionTypes     — H / S / C / R meanings

Exercise object:
  id, name, sets, reps | hold, load, notes, cues?, optional?, hipDependent?

Calf content for a session = calfLevels[currentLevel].exercises
Accessory content = shouldersByWeek[band] or hipsByWeek[band] by session type + week.
"""
from __future__ import annotations

import json
from pathlib import Path

OUT = Path(__file__).resolve().parent / "program.json"

# ---------------------------------------------------------------------------
# Structured mirror of program.md
# ---------------------------------------------------------------------------

PROGRAM = {
    "athlete": "Ron Weaver",
    "timezone": "America/New_York",
    "injury": "Likely grade 2 right gastrocnemius tear, Sat Sep 19, 2026",
    "also": "Right THA Mar 4, 2026 (anterior, no restrictions as of Sep 24). Pickleball + golf return.",
    "programWindow": "Fri Sep 25 – Fri Nov 20, 2026",
    "startDate": "2026-09-25",
    "endDate": "2026-11-20",
    "disclaimer": (
        "Educational training plan, not a medical diagnosis or prescription. "
        "Seek medical care for diagnosis, imaging, and clearance before return to sport."
    ),
    "painRules": {
        "ceiling": 3,
        "pass": "Pain ≤3/10 during AND settles by next morning AND no new/increased swelling",
        "hold": "Pain >3 during, OR worse next morning, OR more swelling → HOLD level (DROP after 2 fails)",
        "advance": "2–3 consecutive PASS sessions to advance a calf level",
    },
    "redFlags": [
        "Calf swelling, warmth, redness, or new deep calf pain (possible DVT)",
        "Sudden pop, sharp pain increase, or clear loss of push-off",
        "New/escalating night or rest pain",
        "Unusual hip symptoms (giving way, sharp groin/lateral pain, instability)",
        "Shortness of breath, chest pain, or unexplained fever",
    ],
    "sessionTypes": {
        "H": "Calf (current level) + Hips/Glutes",
        "S": "Calf (current level) + Shoulders/Upper body",
        "C": "Optional calf isometrics/ROM or light conditioning + mobility",
        "R": "Week 8 reassessment",
    },
    "notes": [
        "Calf work is criteria-based LEVELS — start Level 0; do not skip.",
        "Shoulders and hips advance on a fixed weekly schedule independent of calf level.",
        "Both issues are RIGHT side — right-leg loading that stresses the calf must match current calf level.",
        "Air/goblet squats are in from Session 1 (flat-footed). Hold split squats/lunges until calf Level 2+ and a pain-free test.",
    ],
}


def ex(
    id: str,
    name: str,
    sets: str,
    *,
    reps: str | None = None,
    hold: str | None = None,
    load: str = "",
    notes: str = "",
    cues: str = "",
    optional: bool = False,
    hip_dependent: bool = False,
) -> dict:
    d: dict = {"id": id, "name": name, "sets": sets, "load": load, "notes": notes}
    if reps is not None:
        d["reps"] = reps
    if hold is not None:
        d["hold"] = hold
    if cues:
        d["cues"] = cues
    if optional:
        d["optional"] = True
    if hip_dependent:
        d["hipDependent"] = True
    return d


CALF_LEVELS = [
    {
        "level": 0,
        "name": "Protect + gentle activation",
        "estimate": "Days 5–10 post-injury (≈ program days 1–5)",
        "entry": "Acute/subacute calf tear with walking possible but irritable; no red flags.",
        "exit": "Pain ≤3 during/after; no morning increase; no swelling increase; walking indoor distances tolerable. Advance after 2–3 PASS.",
        "exercises": [
            ex(
                "c0-arom",
                "Seated AROM PF ↔ DF",
                "2",
                reps="15",
                load="Bodyweight",
                notes="Knee bent ~90°. Slow, pain-free. No forcing stretch.",
                cues="Gentle pump through comfortable range only.",
            ),
            ex(
                "c0-iso-bent",
                "Seated PF isometric (bent knee)",
                "5",
                hold="20–30 s",
                load="20–40% effort",
                notes="Ball of foot into floor or light band. Rest 30–45 s. Stop if pain >3/10.",
                cues="Gentle push — not a hard contraction.",
            ),
            ex(
                "c0-pumps",
                "Ankle pumps / circles",
                "2–3",
                reps="20",
                load="Bodyweight",
                notes="Pain-free range.",
                optional=True,
            ),
            ex(
                "c0-towel",
                "Towel-assisted gentle stretch",
                "1–2",
                hold="20–30 s",
                load="Comfort edge only",
                notes="Skip if any pull >2/10.",
                optional=True,
            ),
        ],
    },
    {
        "level": 1,
        "name": "Longer / slightly firmer isometrics",
        "estimate": "~Days 7–14",
        "entry": "Level 0 exit criteria met.",
        "exit": "2–3 PASS; can stand briefly on right with mild load; swelling stable.",
        "exercises": [
            ex(
                "c1-iso-bent",
                "Seated bent-knee PF isometric",
                "5",
                hold="30–45 s",
                load="~40–50% effort",
                notes="Rest between holds. Pain ≤3.",
            ),
            ex(
                "c1-iso-straight",
                "Seated straight-knee PF isometric (gastroc bias)",
                "4",
                hold="30 s",
                load="~30–40% effort",
                notes="Keep very gentle.",
                cues="Gastroc bias — soft effort only.",
            ),
            ex(
                "c1-weight-shift",
                "Standing weight-shift onto right foot",
                "3",
                hold="20 s",
                load="Bodyweight + support nearby",
                notes="Support nearby.",
            ),
            ex(
                "c1-arom",
                "Continue AROM",
                "2",
                reps="15",
                load="Bodyweight",
                notes="Pain-free range.",
            ),
        ],
    },
    {
        "level": 2,
        "name": "Seated isotonics (soleus bias)",
        "estimate": "~Weeks 2–3 of program",
        "entry": "Level 1 exit; pain-free or ≤2/10 walking most of day.",
        "exit": "2–3 PASS; 3×15 seated raises with ~20–30 lb comfortable.",
        "exercises": [
            ex(
                "c2-seated-raise",
                "Seated calf raise (DB on knees or band)",
                "3",
                reps="12–15",
                load="10–20 lb total to start",
                notes="Tempo 2-1-2.",
                cues="Slow: 2 up, 1 hold, 2 down.",
            ),
            ex(
                "c2-iso-finisher",
                "Seated isometric finisher",
                "3",
                hold="30 s",
                load="Moderate effort",
                notes="",
            ),
            ex(
                "c2-bike",
                "Easy bike (Fayetteville)",
                "1",
                hold="10–15 min",
                load="Low resistance",
                notes="No calf stretch at bottom of stroke.",
                optional=True,
            ),
        ],
    },
    {
        "level": 3,
        "name": "Double-leg standing calf raises",
        "estimate": "~Weeks 3–4",
        "entry": "Level 2 exit; single-leg balance 10 s ok with support nearby.",
        "exit": "2–3 PASS; 3×15 DL raises through near-full ROM, next-day ok.",
        "exercises": [
            ex(
                "c3-dl-raise",
                "DL standing calf raise (floor → step)",
                "3",
                reps="12–15",
                load="Bodyweight → light DB",
                notes="Tempo 2-1-2. Progress to step for more ROM when ready.",
            ),
            ex(
                "c3-seated",
                "Bent-knee seated raises",
                "3",
                reps="12",
                load="Moderate",
                notes="",
            ),
            ex(
                "c3-walk",
                "Easy walking",
                "1",
                hold="10–20 min",
                load="As tolerated",
                notes="Increase time before speed.",
                optional=True,
            ),
        ],
    },
    {
        "level": 4,
        "name": "Single-leg strength endurance",
        "estimate": "~Weeks 4–5",
        "entry": "Level 3 exit; DL raises easy.",
        "exit": "≥25 SL calf raises on right at ≥90% of left quality/count, pain ≤3, no next-morning flare.",
        "exercises": [
            ex(
                "c4-sl-raise",
                "SL calf raise (floor → step)",
                "3",
                reps="work toward 25+",
                load="Bodyweight; left assist at top if needed",
                notes="Tempo 2-1-2. Wean assist. Key RTS gate: ≥25 @ ≥90% left.",
                cues="Quality over rush — match left side.",
            ),
            ex(
                "c4-soleus",
                "Seated soleus raises",
                "3",
                reps="10–12",
                load="Moderate",
                notes="",
            ),
            ex(
                "c4-wall-hold",
                "Wall SL heel raise holds",
                "3",
                hold="20–30 s",
                load="Bodyweight",
                notes="",
                optional=True,
            ),
        ],
    },
    {
        "level": 5,
        "name": "Heavy slow resistance (HSR)",
        "estimate": "~Weeks 5–6",
        "entry": "Level 4 exit criteria.",
        "exit": "2–3 PASS at meaningful load; hopping readiness testing pain-free.",
        "exercises": [
            ex(
                "c5-standing-hsr",
                "Standing calf raise HSR (barbell/Smith/DB/backpack)",
                "3–4",
                reps="6–15",
                load="Progress as reps drop toward 6–8",
                notes="3 s up / 3 s down.",
                cues="Heavy and slow — full control.",
            ),
            ex(
                "c5-seated-hsr",
                "Seated soleus HSR",
                "3",
                reps="6–12",
                load="Progress load",
                notes="Same 3-3 tempo.",
            ),
            ex(
                "c5-step-rom",
                "Incline/decline step for ROM",
                "3",
                reps="8–12",
                load="As controlled",
                notes="Once control is solid.",
                optional=True,
            ),
        ],
    },
    {
        "level": 6,
        "name": "Low-level plyometrics",
        "estimate": "~Weeks 6–7",
        "entry": "Level 5 exit; SL raises ≥25 @ ≥90% contralateral; pain-free DL and SL hopping in place (start DL).",
        "exit": "2–3 PASS; SL hop in place 20+ contacts pain-free; confidence high.",
        "exercises": [
            ex(
                "c6-pogos",
                "Rope or in-place pogos DL",
                "3",
                reps="20–30 soft contacts",
                load="Bodyweight",
                notes="Soft contacts.",
            ),
            ex(
                "c6-line-hops",
                "DL line hops forward/back",
                "3",
                reps="8",
                load="Bodyweight",
                notes="",
            ),
            ex(
                "c6-sl-pogos",
                "SL pogos",
                "3",
                reps="15–20",
                load="Bodyweight",
                notes="Only when DL is easy and pain-free.",
                optional=True,
            ),
        ],
    },
    {
        "level": 7,
        "name": "Agility + return-to-sport prep",
        "estimate": "~Weeks 7–8",
        "entry": "Level 6 exit.",
        "exit": "See Return-to-Sport section and Week 8 reassessment.",
        "exercises": [
            ex(
                "c7-multi-hop",
                "Multidirectional hops / lateral shuffles / deceleration",
                "3",
                reps="6–10 each pattern",
                load="Bodyweight",
                notes="Gradual volume.",
            ),
            ex(
                "c7-pickleball",
                "Pickleball-specific: side shuffle → plant → recover",
                "3",
                hold="5–8 min total",
                load="No full games yet",
                notes="",
            ),
            ex(
                "c7-golf",
                "Golf: putt/chip → half-swing → progressive full swing",
                "1",
                hold="10–20 min",
                load="Soft footing",
                notes="Watch trail/lead calf push-off.",
            ),
            ex(
                "c7-hsr-maint",
                "HSR calf maintenance",
                "3",
                reps="6–10",
                load="Prior HSR loads",
                notes="Continue 2×/week.",
            ),
        ],
    },
]

SHOULDERS = {
    "1-2": [
        ex("s12-er", "Band external rotation (elbow at side)", "3", reps="15/side", load="Light band", notes=""),
        ex("s12-pullapart", "Band pull-apart", "3", reps="15", load="Light band", notes=""),
        ex("s12-row", "Scapular retraction (seated band row)", "3", reps="12", load="Band", notes="Upright torso.", cues="Squeeze shoulder blades."),
        ex("s12-pushup", "Wall or elevated push-up", "3", reps="8–12", load="Bodyweight", notes="Heels comfortable; avoid forced calf stretch."),
        ex("s12-scaption", "Light DB scaption to eye level", "2", reps="12", load="Light DB", notes="", optional=True),
    ],
    "3-4": [
        ex("s34-er90", "Band 90/90 ER", "3", reps="10–12", load="Light", notes="Only if comfortable."),
        ex("s34-dbrow", "DB row (bench supported)", "3", reps="10", load="DB", notes=""),
        ex("s34-pushup", "Push-up progression (elevated → floor)", "3", reps="8–12", load="Bodyweight", notes=""),
        ex("s34-facepull", "Face pull or band high row", "3", reps="12", load="Band", notes=""),
        ex("s34-farmer", "Farmer carry short walks", "3", hold="20–30 m", load="Moderate DBs", notes="Watch calf; keep easy until Level 3+."),
    ],
    "5-6": [
        ex("s56-cuff", "Cuff / scap work (ER + pull-apart)", "3", reps="12–15", load="Band", notes=""),
        ex("s56-ohp", "Overhead press light DB (seated ok)", "3", reps="8–10", load="Light DB", notes=""),
        ex("s56-pullup", "Pull-up / assisted / lat-pulldown alt", "3", reps="5–8", load="As able", notes="Fayetteville rack."),
        ex("s56-serratus", "Serratus wall slides", "3", reps="10", load="Bodyweight", notes=""),
    ],
    "7-8": [
        ex("s78-cuff", "Maintain cuff work", "3", reps="12–15", load="Band", notes="2–3×/week."),
        ex("s78-er-vel", "Slightly higher velocity band ER (controlled)", "3", reps="12", load="Band", notes="Still controlled."),
        ex("s78-chops", "Light med-ball or band chops", "2", reps="8/side", load="Light", notes="Sport-arm care.", optional=True),
    ],
}

# Hips reflect Sep 24 updates: * unlocked; air/goblet squat from Session 1;
# split squats / lunges deferred until calf Level 2+ (noted in cues).
HIPS = {
    "1-2": [
        ex(
            "h12-bridge",
            "Glute bridge (short / neutral ROM)",
            "3",
            reps="10",
            load="Bodyweight",
            notes="Feet flat. Squeeze gently. Avoid max extension + toes out.",
            hip_dependent=True,
        ),
        ex(
            "h12-abd-side",
            "Side-lying hip abduction",
            "3",
            reps="12/side",
            load="Bodyweight",
            notes="Legs stacked, slight hip flexion ok. Controlled.",
        ),
        ex(
            "h12-abd-stand",
            "Standing band hip abduction",
            "2–3",
            reps="12/side",
            load="Light band",
            notes="Soft knee. Hold support if needed.",
        ),
        ex(
            "h12-squat",
            "Air squat → goblet squat",
            "3",
            reps="8–10",
            load="BW → goblet 10–15 lb if easy",
            notes="Flat feet, weight through heels. Pain-free depth. Stop if calf >2/10.",
            cues="Heels down. Progress load weekly if form clean.",
            hip_dependent=True,
        ),
        ex(
            "h12-catcow",
            "Cat–cow",
            "2",
            reps="10",
            load="—",
            notes="Slow with breath.",
        ),
    ],
    "3-4": [
        ex(
            "h34-bridge",
            "Bridge with 2 s squeeze",
            "3",
            reps="12",
            load="Bodyweight",
            notes="Still avoid end-range extension + ER.",
            hip_dependent=True,
        ),
        ex(
            "h34-clam",
            "Side-lying clam (small range)",
            "3",
            reps="12",
            load="Bodyweight / light band",
            notes="Neutral pelvis. Keep knees from collapsing inward aggressively.",
            hip_dependent=True,
        ),
        ex(
            "h34-stepup",
            "Step-up low step",
            "3",
            reps="8/side",
            load="Bodyweight → light DB",
            notes="Limit trunk lean / deep hip fold. Heel load until calf Level 3+.",
            hip_dependent=True,
        ),
        ex(
            "h34-rdl",
            "Hip hinge / RDL pattern light DB",
            "3",
            reps="8",
            load="Light DB",
            notes="Soft knees; no aggressive end-range.",
            hip_dependent=True,
        ),
        ex(
            "h34-squat",
            "Goblet squat",
            "3",
            reps="8–10",
            load="10–30 lb DB",
            notes="Flat-footed. Progress from weeks 1–2.",
            hip_dependent=True,
        ),
    ],
    "5-6": [
        ex(
            "h56-sl-bridge",
            "Single-leg bridge (limited extension)",
            "3",
            reps="8/side",
            load="Bodyweight",
            notes="",
            hip_dependent=True,
        ),
        ex(
            "h56-latwalk",
            "Lateral band walk",
            "3",
            reps="8 steps each way",
            load="Band",
            notes="",
        ),
        ex(
            "h56-split",
            "Split squat shallow",
            "3",
            reps="6–8/side",
            load="BW → light DB",
            notes="Only after calf Level 2+ and a one-set pain-free test (≤2/10, no worse morning).",
            cues="Introduce carefully — not tested with calf yet.",
            hip_dependent=True,
        ),
        ex(
            "h56-bike",
            "Optional easy bike intervals (Fayetteville)",
            "1",
            hold="10–15 min",
            load="Easy",
            notes="",
            optional=True,
        ),
    ],
    "7-8": [
        ex(
            "h78-glute",
            "Glute med emphasis (abd / clam / band walk)",
            "3",
            reps="10–12",
            load="Band / BW",
            notes="Continue 2×/week.",
        ),
        ex(
            "h78-latlunge",
            "Controlled lateral lunges shallow",
            "3",
            reps="6/side",
            load="BW → light",
            notes="Only after calf Level 2+ pain-free test.",
            hip_dependent=True,
        ),
        ex(
            "h78-balance",
            "Single-leg stand",
            "3",
            hold="20–30 s",
            load="Near support",
            notes="",
        ),
    ],
}

OPTIONAL_C = [
    ex(
        "opt-iso",
        "Gentle calf isometrics / ROM (current level light version)",
        "3",
        hold="20–30 s",
        load="Very light",
        notes="Only if pain rules met. Soft day.",
    ),
    ex(
        "opt-walk",
        "Easy walk",
        "1",
        hold="10–20 min",
        load="As tolerated",
        notes="Soft surfaces first.",
    ),
    ex(
        "opt-mobility",
        "Mobility: cat–cow, gentle hip openers, shoulder circles",
        "2",
        reps="10 each",
        load="—",
        notes="",
    ),
]

REASSESSMENT = [
    ex("r-pain", "Pain / swelling check", "1", reps="—", load="—", notes="Resting pain, morning stiffness, calf girth if tape available."),
    ex("r-sl-raise", "SL calf raise max reps (R vs L)", "1", reps="max", load="BW, ~1s up/1s down", notes="Cadence controlled."),
    ex("r-hsr8", "HSR 8RM estimate — standing calf raise", "1", reps="~8", load="Find 8RM @ 3-1-3", notes=""),
    ex("r-hop", "Hop battery", "1", reps="DL 30s; SL 20/side; triple hop if pain-free", load="BW", notes=""),
    ex("r-balance", "Single-leg balance eyes open", "1", hold="30 s", load="—", notes=""),
    ex("r-hip", "Hip screen: STS 10; side-lying abd 15/side", "1", reps="as listed", load="BW", notes="Note any precaution limits."),
    ex("r-shoulder", "Shoulder screen: band ER 15/side; scaption 12/side", "1", reps="as listed", load="Band / light DB", notes="Pain-free."),
    ex("r-sport", "Sport readiness confidence 0–10 (pickleball & golf)", "1", reps="—", load="—", notes="Review log trends."),
]

SCHEDULE_ROWS = [
    ("2026-09-25", "Fri", 1, "H", "H — Session 1 (Calf Level 0 start)"),
    ("2026-09-26", "Sat", 1, "C", "C (optional)"),
    ("2026-09-28", "Mon", 1, "H", "H"),
    ("2026-09-30", "Wed", 1, "S", "S"),
    ("2026-10-02", "Fri", 2, "H", "H"),
    ("2026-10-03", "Sat", 2, "C", "C (optional)"),
    ("2026-10-05", "Mon", 2, "H", "H"),
    ("2026-10-07", "Wed", 2, "S", "S"),
    ("2026-10-09", "Fri", 3, "H", "H"),
    ("2026-10-10", "Sat", 3, "C", "C (optional)"),
    ("2026-10-12", "Mon", 3, "H", "H"),
    ("2026-10-14", "Wed", 3, "S", "S"),
    ("2026-10-16", "Fri", 4, "H", "H"),
    ("2026-10-17", "Sat", 4, "C", "C (optional)"),
    ("2026-10-19", "Mon", 4, "H", "H"),
    ("2026-10-21", "Wed", 4, "S", "S"),
    ("2026-10-23", "Fri", 5, "H", "H"),
    ("2026-10-24", "Sat", 5, "C", "C (optional)"),
    ("2026-10-26", "Mon", 5, "H", "H"),
    ("2026-10-28", "Wed", 5, "S", "S"),
    ("2026-10-30", "Fri", 6, "H", "H"),
    ("2026-10-31", "Sat", 6, "C", "C (optional)"),
    ("2026-11-02", "Mon", 6, "H", "H"),
    ("2026-11-04", "Wed", 6, "S", "S"),
    ("2026-11-06", "Fri", 7, "H", "H"),
    ("2026-11-07", "Sat", 7, "C", "C (optional)"),
    ("2026-11-09", "Mon", 7, "H", "H"),
    ("2026-11-11", "Wed", 7, "S", "S"),
    ("2026-11-13", "Fri", 8, "H", "H"),
    ("2026-11-14", "Sat", 8, "C", "C (optional)"),
    ("2026-11-16", "Mon", 8, "H", "H"),
    ("2026-11-18", "Wed", 8, "S", "S"),
    ("2026-11-20", "Fri", 8, "R", "R — Week 8 reassessment"),
]


def week_band(week: int) -> str:
    if week <= 2:
        return "1-2"
    if week <= 4:
        return "3-4"
    if week <= 6:
        return "5-6"
    return "7-8"


def build() -> dict:
    data = dict(PROGRAM)
    data["calfLevels"] = CALF_LEVELS
    data["shouldersByWeek"] = SHOULDERS
    data["hipsByWeek"] = HIPS
    data["optionalConditioning"] = OPTIONAL_C
    data["reassessment"] = REASSESSMENT
    data["conditioningNotes"] = [
        "Walking: daily as tolerated; increase time before speed. Soft surfaces first.",
        "Bike (Fayetteville): excellent early cardio — Level 0–2 era, 10–20 min easy.",
        "Assault bike: wait until Level 4+ and pain rules pass.",
        "Treadmill: prefer after Level 3; jog only after Level 6 entry.",
    ]
    data["schedule"] = [
        {
            "date": d,
            "day": day,
            "week": week,
            "type": typ,
            "label": label,
            "weekBand": week_band(week),
        }
        for d, day, week, typ, label in SCHEDULE_ROWS
    ]
    data["source"] = {
        "programMd": "/workspace/arnold/program.md",
        "sessionExample": "/workspace/arnold/sessions/2026-09-25.md",
        "builtBy": "build_program.py",
    }
    return data


def main() -> None:
    data = build()
    OUT.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {OUT} ({len(data['schedule'])} sessions, {len(data['calfLevels'])} calf levels)")


if __name__ == "__main__":
    main()

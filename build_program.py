#!/usr/bin/env python3
"""
Build program-ron.json (and program-cindy.json) for the workout tracker.

    python3 build_program.py          # rebuilds BOTH people
    python3 build_program_cindy.py    # rebuilds Cindy only

Ron's content mirrors /workspace/arnold/program.md (incl. the Sep 24 hip update
and "Ron's priorities") and sessions/2026-09-25.md. Cindy's lives in
build_program_cindy.py (mirrors /workspace/arnold/cindy/program.md).
JSON schema is documented in program_common.py. Keep exercise ids stable –
they key the logged data in localStorage.
"""
from __future__ import annotations

from program_common import ex, week_band, write

PROGRAM = {
    "person": "ron",
    "displayName": "Ron",
    "athlete": "Ron Weaver",
    "timezone": "America/New_York",
    "conditions": "Likely grade 2 RIGHT gastrocnemius tear (Sat Sep 19, 2026) · RIGHT THA Mar 4, 2026 – anterior approach, no surgeon restrictions (Sep 24 update)",
    "programWindow": "Fri Sep 25 – Fri Nov 20, 2026",
    "startDate": "2026-09-25",
    "endDate": "2026-11-20",
    "disclaimer": (
        "Educational training plan, not a medical diagnosis or prescription. "
        "Seek medical care for diagnosis, imaging, and clearance before return to sport."
    ),
    "banner": "Calf pain ceiling ≤3/10. Stop for red flags (calf swelling/warmth, pop, night pain, hip instability, SOB).",
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
        "C": "Optional calf isometrics or light conditioning + mobility",
        "R": "Week 8 reassessment",
    },
    "optionalTypes": ["C"],
    "notes": [
        "Calf is the MAIN focus: criteria-based levels, start Level 0, do not skip.",
        "Hip update (Sep 24): right anterior THA, no restrictions – hip-dependent (*) exercises unlocked on normal progression; build end-range extension + external rotation gradually.",
        "Both issues are RIGHT side: right-leg moves that load the calf (push-off, back-leg split squat, toe step-ups, lunges) must match the calf level. Flat foot / weight through heel until calf Level 3+.",
        "Air squat → goblet squat (10–30 lb dumbbell, flat-footed, heels down) from Session 1, progressing weekly.",
        "Split squats, sumo squats, lunges: HOLD until calf Level 2+ AND a one-set pain-free test (calf ≤2/10 during, no worse next morning).",
        "Keep hip and shoulder volume modest so calf work gets priority.",
    ],
    "pain": {
        "title": "Calf pain trend",
        "ceiling": 3,
        "fields": [
            {"key": "painDuring", "label": "Calf pain during session", "short": "Calf (during)", "when": "during", "color": "#0d6e4f"},
            {"key": "painMorning", "label": "Calf pain next morning", "short": "Calf (next AM)", "when": "morning", "color": "#c45c26"},
        ],
    },
}

SPLIT_GATE = "Hold until calf Level 2+ and a one-set pain-free test (calf ≤2/10 during, no worse next morning)."

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
                "Seated ankle point and flex (toes down, then toes up)",
                "2",
                reps="15",
                load="Bodyweight",
                notes="Knee bent ~90°. Slow, pain-free. No forcing stretch.",
                cues="Gentle pump through comfortable range only.",
            ),
            ex(
                "c0-iso-bent",
                "Seated calf hold (knee bent)",
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
                "Seated calf hold (knee bent)",
                "5",
                hold="30–45 s",
                load="~40–50% effort",
                notes="Rest between holds. Pain ≤3.",
            ),
            ex(
                "c1-iso-straight",
                "Seated calf hold (knee straight)",
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
                "Continue seated ankle point and flex",
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
                "Seated calf raise (dumbbell on knees or band)",
                "3",
                reps="12–15",
                load="10–20 lb total to start",
                notes="Tempo: 2 seconds up, hold 1, 2 seconds down.",
                cues="Slow: 2 seconds up, hold 1, 2 seconds down.",
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
        "exit": "2–3 PASS; 3×15 double-leg raises through near-full range of motion, next-day ok.",
        "exercises": [
            ex(
                "c3-dl-raise",
                "Double-leg standing calf raise (floor → step)",
                "3",
                reps="12–15",
                load="Bodyweight → light dumbbell",
                notes="Tempo: 2 seconds up, hold 1, 2 seconds down. Progress to step for more range of motion when ready.",
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
        "entry": "Level 3 exit; double-leg raises easy.",
        "exit": "≥25 single-leg calf raises on right at ≥90% of left quality/count, pain ≤3, no next-morning flare.",
        "exercises": [
            ex(
                "c4-sl-raise",
                "Single-leg calf raise (floor → step)",
                "3",
                reps="work toward 25+",
                load="Bodyweight; left assist at top if needed",
                notes="Tempo: 2 seconds up, hold 1, 2 seconds down. Wean assist. Key return-to-sport gate: ≥25 at ≥90% of left.",
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
                "Wall single-leg heel raise holds",
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
        "name": "Heavy slow resistance",
        "estimate": "~Weeks 5–6",
        "entry": "Level 4 exit criteria.",
        "exit": "2–3 PASS at meaningful load; hopping readiness testing pain-free.",
        "exercises": [
            ex(
                "c5-standing-hsr",
                "Standing calf raise with heavy slow resistance (barbell/Smith/dumbbell/backpack)",
                "3–4",
                reps="6–15",
                load="Progress as reps drop toward 6–8",
                notes="3 seconds up / 3 seconds down.",
                cues="Heavy and slow — full control.",
            ),
            ex(
                "c5-seated-hsr",
                "Seated soleus heavy slow resistance",
                "3",
                reps="6–12",
                load="Progress load",
                notes="Same 3 seconds up / 3 seconds down tempo.",
            ),
            ex(
                "c5-step-rom",
                "Incline/decline step for range of motion",
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
        "entry": "Level 5 exit; Single-leg raises ≥25 at ≥90% of the other side; pain-free double-leg and single-leg hopping in place (start double-leg).",
        "exit": "2–3 PASS; single-leg hop in place 20+ contacts pain-free; confidence high.",
        "exercises": [
            ex(
                "c6-pogos",
                "Rope or in-place double-leg pogos",
                "3",
                reps="20–30 soft contacts",
                load="Bodyweight",
                notes="Soft contacts.",
            ),
            ex(
                "c6-line-hops",
                "Double-leg line hops forward/back",
                "3",
                reps="8",
                load="Bodyweight",
                notes="",
            ),
            ex(
                "c6-sl-pogos",
                "Single-leg pogos",
                "3",
                reps="15–20",
                load="Bodyweight",
                notes="Only when double-leg is easy and pain-free.",
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
                "Heavy slow resistance calf maintenance",
                "3",
                reps="6–10",
                load="Prior heavy slow resistance loads",
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
        ex("s12-scaption", "Light dumbbell arm raise at an angle (thumbs up) to eye level", "2", reps="12", load="Light dumbbell", notes="", optional=True),
    ],
    "3-4": [
        ex("s34-er90", "Band 90/90 external rotation", "3", reps="10–12", load="Light", notes="Only if comfortable."),
        ex("s34-dbrow", "Dumbbell row (bench supported)", "3", reps="10", load="dumbbell", notes=""),
        ex("s34-pushup", "Push-up progression (elevated → floor)", "3", reps="8–12", load="Bodyweight", notes=""),
        ex("s34-facepull", "Face pull or band high row", "3", reps="12", load="Band", notes=""),
        ex("s34-farmer", "Farmer carry short walks", "3", hold="20–30 m", load="Moderate dumbbells", notes="Watch calf; keep easy until Level 3+."),
    ],
    "5-6": [
        ex("s56-cuff", "Rotator cuff / shoulder blade work (external rotation + pull-apart)", "3", reps="12–15", load="Band", notes=""),
        ex("s56-ohp", "Overhead press with light dumbbell (seated ok)", "3", reps="8–10", load="Light dumbbell", notes=""),
        ex("s56-pullup", "Pull-up / assisted / lat-pulldown alt", "3", reps="5–8", load="As able", notes="Fayetteville rack."),
        ex("s56-serratus", "Serratus wall slides", "3", reps="10", load="Bodyweight", notes=""),
    ],
    "7-8": [
        ex("s78-cuff", "Maintain cuff work", "3", reps="12–15", load="Band", notes="2–3×/week."),
        ex("s78-er-vel", "Slightly higher velocity band external rotation (controlled)", "3", reps="12", load="Band", notes="Still controlled."),
        ex("s78-chops", "Light med-ball or band chops", "2", reps="8/side", load="Light", notes="Sport-arm care.", optional=True),
    ],
}

# Hips reflect Sep 24 updates: * unlocked; air/goblet squat from Session 1;
# split squats / lunges deferred until calf Level 2+ (noted in cues).
# Hips reflect the Sep 24 hip update (right anterior THA, no restrictions → * unlocked)
# and Ron's priorities (air/goblet squat from Session 1; split squats / lunges /
# sumo squats gated on calf Level 2+ plus a pain-free test).
HIPS = {
    "1-2": [
        ex("h12-bridge", "Glute bridge", "3", reps="10", load="Bodyweight",
           notes="Feet flat, squeeze. Hip unlocked – build end-range extension gradually."),
        ex("h12-abd-side", "Side-lying hip abduction", "3", reps="12/side", load="Bodyweight",
           notes="Legs stacked, controlled."),
        ex("h12-abd-stand", "Standing band hip abduction", "2–3", reps="12/side", load="Light band",
           notes="Soft knee. Hold support if needed."),
        ex("h12-squat", "Air squat → goblet squat", "3", reps="8–10", load="bodyweight → goblet 10–15 lb",
           notes="Flat feet, heels down, weight through heels. Stop if calf >2/10.",
           cues="Heels down. Progress load weekly if form clean."),
        ex("h12-catcow", "Cat–cow", "2", reps="10", load="—", notes="Slow with breath."),
    ],
    "3-4": [
        ex("h34-bridge", "Bridge with 2-second squeeze", "3", reps="12", load="Bodyweight",
           notes="Build end-range extension + external rotation gradually."),
        ex("h34-clam", "Side-lying clam", "3", reps="12", load="Bodyweight / light band",
           notes="Neutral pelvis, controlled."),
        ex("h34-stepup", "Step-up low step", "3", reps="8/side", load="Bodyweight → light dumbbell",
           notes="Flat foot, drive through the heel – no toe push-off until calf Level 3+."),
        ex("h34-rdl", "Hip hinge / Romanian deadlift with light dumbbell", "3", reps="8", load="Light dumbbell",
           notes="Soft knees; normal progression (hip unlocked)."),
        ex("h34-squat", "Goblet squat", "3", reps="8–10", load="10–30 lb dumbbell",
           notes="Flat-footed, heels down. Progress weekly."),
    ],
    "5-6": [
        ex("h56-sl-bridge", "Single-leg bridge", "3", reps="8/side", load="Bodyweight",
           notes="Unlocked by hip update."),
        ex("h56-latwalk", "Lateral band walk", "3", reps="8 steps each way", load="Band", notes=""),
        ex("h56-squat", "Goblet squat", "3", reps="8–10", load="10–30 lb dumbbell",
           notes="Flat-footed, heels down. Keep progressing weekly."),
        ex("h56-split", "Split squat", "3", reps="6–8/side", load="bodyweight → light dumbbell",
           notes="Right leg back = calf push-off load; keep it matched to calf level.",
           min_level=2, gate_note=SPLIT_GATE),
        ex("h56-bike", "Easy bike intervals (Fayetteville)", "1", hold="10–15 min", load="Easy",
           notes="", optional=True),
    ],
    "7-8": [
        ex("h78-glute", "Glute med emphasis (abd / clam / band walk)", "3", reps="10–12",
           load="Band / bodyweight", notes="Continue 2×/week."),
        ex("h78-squat", "Goblet squat", "3", reps="8–10", load="up to 30 lb dumbbell",
           notes="Flat-footed until calf Level 3+."),
        ex("h78-latlunge", "Controlled lateral lunge", "3", reps="6/side", load="bodyweight → light",
           notes="", min_level=2, gate_note=SPLIT_GATE),
        ex("h78-balance", "Single-leg stand", "3", hold="20–30 s", load="Near support", notes=""),
    ],
}

OPTIONAL_C = [
    ex(
        "opt-iso",
        "Gentle calf isometrics (current level light version)",
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
    ex("r-sl-raise", "Single-leg calf raise maximum reps (right versus left)", "1", reps="max", load="bodyweight, about 1 second up/1 second down", notes="Cadence controlled."),
    ex("r-hsr8", "Heavy slow resistance 8-repetition maximum estimate — standing calf raise", "1", reps="~8", load="Find 8-repetition maximum at 3 seconds up, 1 second hold, 3 seconds down", notes=""),
    ex("r-hop", "Hop battery", "1", reps="double-leg 30 seconds; single-leg 20/side; triple hop if pain-free", load="bodyweight", notes=""),
    ex("r-balance", "Single-leg balance eyes open", "1", hold="30 s", load="—", notes=""),
    ex("r-hip", "Hip screen: sit-to-stand 10; side-lying abduction 15/side", "1", reps="as listed", load="bodyweight", notes="Note any precaution limits."),
    ex("r-shoulder", "Shoulder screen: band external rotation 15/side; arm raise at an angle (thumbs up) 12/side", "1", reps="as listed", load="Band / light dumbbell", notes="Pain-free."),
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



def build() -> dict:
    data = dict(PROGRAM)
    data["levelSystem"] = {
        "key": "calf",
        "label": "Calf level",
        "short": "Calf L",
        "advanceRule": "Advance only after 2–3 PASS sessions (pain ≤3, no worse next morning, no extra swelling).",
        "levels": CALF_LEVELS,
    }
    data["blocks"] = {
        "hips": {"label": "Hips / Glutes", "keyField": "weekBand", "bands": HIPS},
        "shoulders": {"label": "Shoulders / Upper", "keyField": "weekBand", "bands": SHOULDERS},
    }
    data["lists"] = {
        "optionalConditioning": {"title": "Optional: gentle calf work + conditioning/mobility", "exercises": OPTIONAL_C},
        "reassessment": {"title": "Week 8 Reassessment", "exercises": REASSESSMENT},
    }
    data["sessionTemplates"] = {
        "H": [
            {"title": "Calf — Level {level}: {levelName}", "source": "level"},
            {"title": "Hips / Glutes (Weeks {weekBand})", "source": "block", "block": "hips"},
        ],
        "S": [
            {"title": "Calf — Level {level}: {levelName}", "source": "level"},
            {"title": "Shoulders / Upper (Weeks {weekBand})", "source": "block", "block": "shoulders"},
        ],
        "C": [{"title": "Optional — light calf + conditioning/mobility", "source": "list", "list": "optionalConditioning"}],
        "R": [{"title": "Week 8 Reassessment", "source": "list", "list": "reassessment"}],
    }
    data["conditioningNotes"] = [
        "Walking: daily as tolerated; increase time before speed. Soft surfaces first.",
        "Bike (Fayetteville): excellent early cardio — Level 0–2 era, 10–20 min easy.",
        "Assault bike: wait until Level 4+ and pain rules pass.",
        "Treadmill: prefer after Level 3; jog only after Level 6 entry.",
    ]
    data["schedule"] = [
        {"date": d, "day": day, "week": week, "type": typ, "label": label, "weekBand": week_band(week)}
        for d, day, week, typ, label in SCHEDULE_ROWS
    ]
    data["source"] = {"programMd": "/workspace/arnold/program.md",
                      "sessionExample": "/workspace/arnold/sessions/2026-09-25.md"}
    return data


def main() -> None:
    write(build(), "program-ron.json")
    import build_program_cindy
    build_program_cindy.main()


if __name__ == "__main__":
    main()

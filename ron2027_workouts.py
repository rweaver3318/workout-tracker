"""The three workouts of each week (Legs, Sport, Upper) for every phase.
n = build-week number within the phase (1, 2, 3 ...), used to progress loads, reps and holds."""
from __future__ import annotations

from ron2027_phases import (EACH, RIGHT_ARM_EXTRA, RIGHT_EXTRA, RIGHT_ONLY, T_BAND, T_BRIDGE, T_CALF, T_ECC, T_FAST, T_HINGE,
                            T_PALLOF, T_ROW, T_SLOW, X, pick, rec, reliever, wu_legs, wu_sport, wu_upper)


def legs(ph, n, recovery):
    k = ph["key"]
    if k == "runin":
        S = [
            ("Warm-up", wu_legs()),
            ("Main", [
                X("bridge", 2, reps=pick([10, 10, 12], n), tempo=T_BRIDGE),
                X("box_squat", 2, reps=8, tempo="3 seconds down, light touch, 2 seconds up", load="no weight" if n == 1 else "10 lb dumbbell at your chest"),
                X("db_hinge", 2, reps=8, tempo=T_HINGE, load=pick(["15 lb each hand", "20 lb each hand", "20 lb each hand"], n)),
            ]),
            ("Tendon holds", [
                X("calf_hold", 2, hold="30 seconds, single leg", side=RIGHT_EXTRA, effort=pick(["about 5 out of 10 effort", "about 6 out of 10 effort", "about 6 out of 10 effort"], n),
                  notes="Two legs is fine for the first workout if single-leg feels like too much." if n == 1 else ""),
                X("split_hold", 2, hold="20 seconds", side=EACH, load="holding a counter", effort="comfortable, about 5 out of 10") if n < 3 else
                X("fwd_lunge", 2, reps=5, side=EACH, tempo="2 seconds down, 2 seconds back up", load="body weight, holding a counter, short step and shallow"),
            ]),
            ("Grip", [X("farmer_hold", 2, hold="30 seconds", load="20 lb each hand" if n == 1 else "30 lb each hand")]),
            ("Cool-down", [X("calf_stretch", 1, hold="30 seconds each position", side=EACH)]),
        ]
    elif k == "base":
        S = [
            ("Warm-up", wu_legs()),
            ("Main", [
                X("hip_thrust", 2, reps=pick([10, 12, 12, 10, 12, 12], n), tempo=T_BRIDGE, load=pick(["20 lb", "20 lb", "30 lb", "30 lb", "30 lb", "50 lb"], n)),
                X("box_squat", 2, reps=pick([8, 10, 10, 8, 10, 10], n), tempo="3 seconds down, light touch and pause 1, 2 seconds up",
                  load=pick(["15 lb", "15 lb", "20 lb", "20 lb", "30 lb", "30 lb"], n) + " dumbbell at your chest"),
                X("db_hinge", 2, reps=pick([10, 10, 12, 10, 10, 12], n), tempo=T_HINGE, load=pick(["20 lb", "30 lb", "30 lb", "30 lb", "30 lb", "30 lb"], n) + " each hand"),
            ]),
            ("Slow calf work and holds", [
                X("calf_slow", 2, reps=pick([8, 10, 12, 8, 10, 12], n), tempo=T_CALF, side=RIGHT_EXTRA,
                  load=pick(["body weight, flat floor", "body weight, flat floor", "body weight, step edge", "10 lb in hand, step edge", "15 lb in hand, step edge", "20 lb in hand, step edge"], n)),
                X("calf_bent", 2, reps=pick([12, 12, 15, 12, 12, 15], n), tempo=T_CALF, load=pick(["two 20 lb", "two 20 lb", "two 30 lb", "two 30 lb", "two 30 lb", "a 50 lb and a 30 lb"], n) + " dumbbells on your knees"),
                X("fwd_lunge", 2, reps=pick([6, 8, 8, 6, 8, 8], n), side=EACH, tempo="3 seconds down, 1 second back up",
                  load=pick(["body weight, hand on a counter", "body weight", "body weight", "10 lb in each hand", "10 lb in each hand", "15 lb in each hand"], n)),
            ]),
            ("Hips", [X("clamshell" if n % 2 else "side_leg_lift", 2, reps=12, side=EACH, tempo="2 seconds up, hold 1, 2 seconds down")]),
            ("Cool-down", [X("calf_stretch", 1, hold="30 seconds each position", side=EACH)]),
        ]
    elif k == "strength":
        S = [
            ("Warm-up", wu_legs()),
            ("Main", [
                X("bb_rdl", 3, reps=pick([8, 6, 6, 8, 6, 5], n), tempo=T_HINGE,
                  load=pick(["bar plus light plates (about 65 lb)", "about 75 lb", "about 85 lb", "about 85 lb", "about 95 lb", "about 105 lb"], n),
                  effort="Leave 2 reps in the tank; add weight only if the last set felt that way", rest=75),
                X("hip_thrust", 3, reps=pick([8, 8, 6, 8, 8, 6], n), tempo=T_BRIDGE, load=pick(["50 lb", "50 lb", "50 lb plus 10 lb", "50 lb plus 20 lb", "50 lb plus 20 lb", "50 lb plus 30 lb"], n),
                  notes="Stack a second dumbbell on the 50 if you need more, or switch to single-leg bridges holding the 30."),
            ]),
            ("Heavy slow calf work", [
                X("calf_slow", 2, reps=pick([8, 7, 6, 8, 7, 6], n), tempo=T_CALF, side=RIGHT_EXTRA,
                  load=pick(["20 lb", "30 lb", "30 lb", "30 lb", "30 lb plus a backpack", "50 lb"], n) + " in hand, step edge", rest=60),
                X("calf_bent", 2, reps=pick([10, 8, 8, 10, 8, 8], n), tempo=T_CALF, load="a 50 lb and a 30 lb dumbbell on your knees"),
            ]),
            ("Hips and grip", [
                X("fwd_lunge", 2, reps=pick([8, 8, 6, 8, 8, 6], n), side=EACH, tempo="3 seconds down, 1 second back up",
                  load=pick(["15 lb", "20 lb", "20 lb", "20 lb", "30 lb", "30 lb"], n) + " in each hand", effort="Leave 2 reps in the tank"),
                X("bb_top_hold", 2, hold=pick(["20 seconds", "25 seconds", "30 seconds", "25 seconds", "30 seconds", "30 seconds"], n), load="your Romanian deadlift weight",
                  notes="Skip in heavy pickleball-plus-golf weeks (elbow rule)."),
            ]),
            ("Cool-down", [X("calf_stretch", 1, hold="30 seconds each position", side=EACH), X("hip_front_stretch", 1, hold="30 seconds", side=EACH)]),
        ]
    elif k == "power":
        hop = "pogo" if n >= 2 else "quick_feet"
        S = [
            ("Warm-up", wu_legs()),
            ("Quick feet", [
                X(hop, 3, hold="10 seconds" if hop == "quick_feet" else None, reps=None if hop == "quick_feet" else pick([10, 10, 15, 15], n), rest=40,
                  notes="Only if you pass the hop checklist in the notes; otherwise 10 seconds of quick feet in place." if hop == "pogo" else "Light and quiet."),
            ]),
            ("Main", [
                X("bb_rdl", 3, reps=5, tempo=T_FAST, load="about 70 percent of your heaviest strength-phase weight",
                  effort="Every rep quick on the way up; end the set if it slows down", rest=75),
                X("hip_thrust", 2, reps=6, tempo="drive up fast, hold 1, 3 seconds down", load="your strength-phase weight minus about 20 lb"),
                X("fwd_lunge", 2, reps=6, side=EACH, tempo="2 seconds down, push back up quickly", load="15 lb in each hand" if n == 1 else "20 lb in each hand",
                  effort="Every push-back quick; leave 3 reps in the tank"),
            ]),
            ("Heavy calf", [
                X("calf_slow", 2, reps=6, tempo="rise quickly, hold 1, 3 seconds down", side=RIGHT_EXTRA, load="30 lb in hand, step edge"),
                X("calf_hold", 2, hold="30 seconds, single leg", side=RIGHT_EXTRA, load="30 lb in hand", effort="about 7 to 8 out of 10"),
            ]),
            ("Cool-down", [X("calf_stretch", 1, hold="30 seconds each position", side=EACH)]),
        ]
    else:  # peak
        S = [
            ("Warm-up", wu_legs()),
            ("Quick feet", [X("pogo", 2, reps=pick([15, 15, 20], n), rest=40,
                              notes="Only if you pass the hop checklist; otherwise 10 seconds of quick feet in place.")]),
            ("Main", [
                X("bb_rdl", 2, reps=5, tempo=T_FAST, load="your strength-phase working weight", effort="Leave 2 to 3 reps in the tank", rest=75),
                X("hip_thrust", 2, reps=8, tempo=T_BRIDGE, load="50 lb or more"),
            ]),
            ("Calf and hips", [
                X("calf_slow", 2, reps=6, tempo=T_CALF, side=RIGHT_EXTRA, load="30 lb in hand, step edge"),
                X("fwd_lunge", 2, reps=6, side=EACH, tempo="2 seconds down, push back up quickly", load="20 lb in each hand", effort="Leave 3 reps in the tank"),
                X("wall_press_hold", 2, hold="30 seconds", side=EACH),
            ]),
            ("Grip", [X("farmer_hold", 1, hold="40 seconds", load="50 lb each hand (or 30s)",
                        notes="Skip in heavy pickleball-plus-golf weeks (elbow rule).")]),
            ("Cool-down", [X("calf_stretch", 1, hold="30 seconds each position", side=EACH)]),
        ]
    if recovery:
        S = [(t, rec(items)) for t, items in S]
    return S


def retest_workout(k):
    return [
        ("Warm-up", wu_sport()),
        ("Shoulder Reliever", [reliever(k, 3)]),
        ("Retest (type your numbers in the Reps / hold box)", [
            X("test_calf", 1, side=EACH), X("test_chair", 1), X("test_balance", 1, side=EACH),
            X("test_side_plank", 1, side=EACH), X("test_grip", 1), X("test_hang", 1), X("test_elbow", 1),
        ]),
        ("Cool-down", [X("forearm_stretch", 1, hold="30 seconds", side=EACH)]),
    ]


def sport(ph, n, recovery, retest):
    k = ph["key"]
    if retest:
        return retest_workout(k)
    if k == "runin":
        S = [
            ("Warm-up", wu_sport()),
            ("Shoulder Reliever", [reliever(k, n)]),
            ("Balance and core", [
                X("pallof_hold", 2, hold="20 seconds", side=EACH, effort="moderate band tension"),
                X("sl_balance", 2, hold="20 seconds", side=EACH, notes="Eyes open." if n < 3 else "Eyes open, slow head turns."),
                X("side_lunge", 2, hold="15 seconds in a shallow side lunge", side=EACH, load="hand on a counter") if n == 1 else
                X("side_lunge", 2, reps=5, side=EACH, tempo="2 seconds down, 2 seconds back", load="body weight, hand on a counter, small step"),
            ]),
            ("Calf and elbow", [
                X("calf_slow", 2, reps=10, tempo=T_CALF, load="two legs, flat floor", notes="Add 1 single-leg set of 6 on the right if it feels easy." if n > 1 else ""),
                X("pronation_hold", 2, hold="30 seconds", side=RIGHT_ARM_EXTRA, load="10 lb dumbbell held by one end", effort="about 5 out of 10"),
            ]),
        ]
    elif k == "base":
        S = [
            ("Warm-up", wu_sport()),
            ("Shoulder Reliever", [reliever(k, n)]),
            ("Rotation and core", [
                X("pallof_press", 2, reps=pick([8, 10, 10, 8, 10, 10], n), side=EACH, tempo=T_PALLOF,
                  notes="In a short split stance from week 10." if n >= 4 else ""),
                X("band_chop" if n % 2 else "band_lift", 2, reps=10, side=EACH, tempo="2 seconds across, 2 seconds back"),
            ]),
            ("Balance and legs", [
                X("side_lunge", 2, reps=pick([6, 8, 8, 6, 8, 8], n), side=EACH, tempo="3 seconds down, 1 second back",
                  load=pick(["body weight, hand on a counter", "body weight", "body weight", "10 lb dumbbell at your chest", "10 lb dumbbell at your chest", "15 lb dumbbell at your chest"], n)),
                X("sl_balance", 2, hold="30 seconds", side=EACH, notes=pick(["Slow head turns.", "Slow head turns.", "Toss a ball hand to hand.", "Toss a ball hand to hand.", "Eyes closed for 10 seconds, counter right there.", "Eyes closed for 10 to 15 seconds."], n)),
            ]),
            ("Tendon holds", [
                X("calf_hold", 2, hold=pick(["30 seconds", "40 seconds", "45 seconds", "40 seconds", "45 seconds", "45 seconds"], n) + ", single leg",
                  side=RIGHT_EXTRA, load="body weight" if n < 4 else "10 to 15 lb in hand", effort="about 6 to 7 out of 10"),
                X("pronation_hold", 2, hold="30 seconds", side=RIGHT_ARM_EXTRA, load="10 lb held by one end" if n < 4 else "15 lb held by one end"),
            ]),
            ("Shoulder", [X("face_pull", 1, reps=15, tempo=T_BAND)]),
        ]
    elif k == "strength":
        S = [
            ("Warm-up", wu_sport()),
            ("Shoulder Reliever", [reliever(k, n)]),
            ("Single-leg strength and braking", [
                X("sl_rdl", 2, reps=8, side=EACH, tempo=T_HINGE, load=pick(["no weight", "10 lb", "15 lb", "15 lb", "20 lb", "20 lb"], n) + " in the opposite hand"),
                X("step_down", 2, reps=pick([6, 8, 8, 6, 8, 8], n), side=EACH, tempo="3 seconds down, light tap, 1 second up"),
                X("side_lunge", 2, reps=pick([8, 8, 6, 8, 8, 6], n), side=EACH, tempo="3 seconds down, 1 second back",
                  load=pick(["15 lb", "20 lb", "20 lb", "20 lb", "30 lb", "30 lb"], n) + " dumbbell at your chest", effort="Leave 2 reps in the tank"),
            ]),
            ("Rotation", [
                X("band_lift" if n % 2 else "band_chop", 2, reps=8, side=EACH, tempo="2 seconds across, 3 seconds back", load="medium to heavy band"),
                X("pallof_press", 2, reps=8, side=EACH, tempo=T_PALLOF, notes="Press out, raise your arms overhead and back down, then bring the band in."),
            ]),
            ("Tendon holds", [
                X("calf_hold", 2, hold="30 seconds, single leg", side=RIGHT_EXTRA, load=pick(["20 lb", "20 lb", "30 lb", "30 lb", "30 lb", "50 lb"], n) + " in hand", effort="about 7 to 8 out of 10"),
                X("adductor_side_plank" if n > 2 else "adductor_squeeze", 2, hold="20 seconds" if n > 2 else "30 seconds", side=EACH if n > 2 else ""),
            ]),
        ]
    elif k == "power":
        S = [
            ("Warm-up", wu_sport()),
            ("Shoulder Reliever", [reliever(k, n)]),
            ("Footwork and braking", [
                X("split_step", 3, reps=6, notes="Alternate left and right."),
                X("shuffle_stop", 2, reps=4, side=EACH),
                X("reaction_lunge", 2, reps=pick([6, 8, 8, 8], n), notes="Mix front-left, front-right, left and right. Body weight."),
            ]),
            ("Rotation speed", [
                X("fast_chop", 3, reps=6, side=EACH, tempo="fast across, 3 seconds back", notes="Alternate chop and lift each set."),
                X("golf_turn", 1, reps="6 slow turns, then 5 practice swings pausing 2 seconds at the top"),
            ]),
            ("Tendon holds", [
                X("pronation_hold", 2, hold="30 seconds", side=RIGHT_ARM_EXTRA, load="15 lb held by one end"),
                X("sl_balance", 1, hold="30 seconds", side=EACH, notes="Eyes closed or ball toss."),
            ]),
            ("Optional", [X("bike_intervals", 1, reps="4 rounds of 20 seconds hard, 40 seconds easy", minutes=4, notes="Only if you have time and energy.")]),
        ]
    else:  # peak
        S = [
            ("Warm-up", wu_sport()),
            ("Shoulder Reliever", [reliever(k, n)]),
            ("Footwork and braking", [
                X("reaction_lunge", 2, reps=8, notes="Start each rep with a small split step if you pass the hop checklist. Mix the directions."),
                X("side_lunge", 1, reps=6, side=EACH, tempo="2 seconds down, push back quickly", load="15 lb dumbbell at your chest"),
                X("line_hops", 2, hold="10 seconds", rest=40, notes="Only if you pass the hop checklist; otherwise quick side-steps over the line."),
            ]),
            ("Rotation and core", [
                X("fast_chop", 2, reps=6, side=EACH, tempo="fast across, 3 seconds back"),
                X("side_plank", 2, hold="30 seconds", side=EACH),
            ]),
            ("Tendon holds", [
                X("calf_hold", 2, hold="45 seconds, single leg", side=RIGHT_EXTRA, load="20 to 30 lb in hand", effort="about 7 out of 10"),
                X("pronation_hold", 2, hold="30 seconds", side=RIGHT_ARM_EXTRA, load="15 lb held by one end"),
            ]),
        ]
    if recovery:
        S = [(t, rec(items)) for t, items in S if t != "Optional"]
    return S


def bar_item(k, n):
    if k == "runin":
        return X("dead_hang", 2, hold="15 to 20 seconds", notes="Feet on the floor taking some weight.")
    if k == "base":
        if n % 2:
            return X("scap_hang", 3, reps="5 pulls, holding 3 seconds each")
        return X("top_hold", 3, hold=pick(["5 seconds", "5 seconds", "8 seconds", "8 seconds", "10 seconds", "10 seconds"], n))
    if k == "strength":
        return X("slow_lower", 3, reps=pick([2, 3, 3, 3, 3, 4], n), tempo="4 to 5 seconds down", rest=75)
    if k == "power":
        return X("slow_lower", 2, reps=3, tempo="5 seconds down", notes="Try 1 strict pull-up at the start of the first set if you feel fresh.")
    return X("top_hold", 2, hold="10 to 15 seconds", notes="Then 1 or 2 slow lowerings if you feel good.")


def upper(ph, n, recovery):
    k = ph["key"]
    bar = ("Optional bar (Fayetteville; swap listed)", [bar_item(k, n)])
    if k == "runin":
        S = [
            ("Warm-up", wu_upper()),
            ("Shoulder Reliever", [reliever(k, n)]),
            ("Main", [
                X("incline_pushup", 2, reps=pick([8, 8, 10], n), tempo=T_SLOW, load="hands on the counter" if n == 1 else "hands on the bench"),
                X("db_row", 2, reps=8, side=EACH, tempo=T_ROW, load="20 lb"),
            ]),
            ("Elbow and shoulder holds", [
                X("wrist_flex_hold", 2, hold="30 seconds", side=RIGHT_ARM_EXTRA, load="10 lb", effort="about 5 to 6 out of 10"),
                X("er_hold", 2, hold="30 seconds", side=EACH, effort="about 5 out of 10"),
            ]),
            bar,
            ("Core and cool-down", [X("dead_bug", 2, reps=5, side=EACH, tempo="3 seconds reach, 2 seconds back"),
                                    X("forearm_stretch", 1, hold="30 seconds", side=EACH)]),
        ]
    elif k == "base":
        S = [
            ("Warm-up", wu_upper()),
            ("Shoulder Reliever", [reliever(k, n)]),
            ("Main", [
                X("incline_press", 3, reps=pick([10, 10, 10, 12, 10, 10], n), tempo=T_SLOW, load=pick(["15 lb", "15 lb", "20 lb", "20 lb", "20 lb", "20 lb"], n) + " each hand")
                if n > 2 else X("pushup_plus", 3, reps=10, tempo=T_SLOW, load="hands on the bench"),
                X("db_row", 2, reps=pick([10, 12, 12, 10, 10, 12], n), side=EACH, tempo=T_ROW, load=pick(["20 lb", "30 lb", "30 lb", "30 lb", "30 lb", "30 lb"], n)),
            ]),
            ("Elbow", [
                X("wrist_flex_hold", 2, hold=pick(["30 seconds", "40 seconds", "45 seconds", "40 seconds", "45 seconds", "45 seconds"], n), side=RIGHT_ARM_EXTRA,
                  load="10 lb" if n < 4 else "15 lb", effort="about 6 out of 10"),
                X("wrist_flex_lower", 2, reps=15, side=RIGHT_ONLY, tempo=T_ECC, load="10 lb",
                  notes="Mild discomfort up to 3 out of 10 is OK if it settles by the next morning."),
            ]),
            ("Shoulder", [
                X("er_goalpost" if n % 2 else "er_side", 2, reps=12, side=EACH, tempo=T_BAND, load="light band") if n % 2 or n == 2 else
                X("y_raise", 2, reps=10, tempo="2 seconds up, hold 2, 3 seconds down", load="no weight" if n < 5 else "10 lb if easy"),
            ]),
            bar,
            ("Core", [X("side_plank", 2, hold=pick(["20 seconds", "25 seconds", "30 seconds", "25 seconds", "30 seconds", "35 seconds"], n), side=EACH, notes="Knees bent.")]),
        ]
    elif k == "strength":
        S = [
            ("Warm-up", wu_upper()),
            ("Shoulder Reliever", [reliever(k, n)]),
            ("Main", [
                X("incline_press", 3, reps=pick([8, 8, 6, 8, 8, 6], n), tempo=T_SLOW, load=pick(["20 lb", "30 lb", "30 lb", "30 lb", "30 lb", "30 lb"], n) + " each hand", rest=75),
                X("db_row", 2, reps=pick([8, 8, 6, 8, 8, 6], n), side=EACH, tempo=T_ROW, load=pick(["30 lb", "30 lb", "50 lb", "50 lb", "50 lb", "50 lb"], n)),
                X("overhead_hold", 2, hold="20 seconds", side=EACH, load=pick(["15 lb", "15 lb", "20 lb", "20 lb", "20 lb", "20 lb"], n)) if n % 2 else
                X("db_press", 2, reps=8, side=EACH, tempo="2 seconds up, 3 seconds down", load=pick(["15 lb", "15 lb", "20 lb", "20 lb", "20 lb", "20 lb"], n)),
            ]),
            bar,
            ("Elbow and shoulder", [
                X("wrist_flex_lower", 2, reps=15, side=RIGHT_ONLY, tempo=T_ECC, load="15 lb" if n < 4 else "15 to 20 lb"),
                X("pronation_lower", 2, reps=12, side=RIGHT_ONLY, tempo="3 to 4 seconds of lowering", load="10 to 15 lb held by one end") if n % 2 else
                X("er_goalpost", 2, reps=10, side=EACH, tempo=T_BAND, load="medium band"),
            ]),
            ("Core", [X("suitcase_hold", 2, hold="30 seconds", side=EACH, load="30 lb" if n < 4 else "50 lb")]),
        ]
    elif k == "power":
        S = [
            ("Warm-up", wu_upper()),
            ("Shoulder Reliever", [reliever(k, n)]),
            ("Main", [
                X("incline_press", 3, reps=6, tempo="press up fast, 3 seconds down", load="20 lb each hand"),
                X("db_row", 3, reps=6, side=EACH, tempo="pull fast, hold 1, 3 seconds down", load="30 lb"),
            ]),
            bar,
            ("Elbow and shoulder", [
                X("wrist_flex_lower", 2, reps=15, side=RIGHT_ONLY, tempo=T_ECC, load="15 to 20 lb"),
                X("er_goalpost", 2, reps=12, side=EACH, tempo="quick up, 3 seconds down", load="light to medium band"),
                X("wall_slide", 1, reps=10),
            ]),
            ("Core", [X("side_plank", 2, hold="30 to 40 seconds", side=EACH, notes="Legs straight if you're ready.")]),
        ]
    else:  # peak
        S = [
            ("Warm-up", wu_upper()),
            ("Shoulder Reliever", [reliever(k, n)]),
            ("Main", [
                X("incline_press", 2, reps=6, tempo=T_SLOW, load="30 lb each hand"),
                X("db_row", 2, reps=8, side=EACH, tempo=T_ROW, load="50 lb"),
            ]),
            bar,
            ("Elbow and shoulder", [
                X("wrist_flex_hold", 2, hold="45 seconds", side=RIGHT_ARM_EXTRA, load="15 lb", notes="In heavy-play weeks, these holds are the only elbow work."),
                X("wrist_flex_lower", 2, reps=15, side=RIGHT_ONLY, tempo=T_ECC, load="15 to 20 lb", notes="Skip in heavy pickleball-plus-golf weeks."),
                X("er_goalpost", 2, reps=12, side=EACH, tempo=T_BAND),
            ]),
            ("Cool-down", [X("doorway_stretch", 1, hold="30 seconds", side=EACH)]),
        ]
    if recovery:
        S = [(t, rec(items)) for t, items in S]
    return S

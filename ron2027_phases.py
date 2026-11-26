"""Macrocycle, prescription helpers and the three weekly workouts for each phase."""
from __future__ import annotations

PHASES = [
    dict(key="runin", name="Run-in", weeks=(1, 4), minutes="15 to 20 minutes",
         ball="Ball 1 (lightest), waist to chest height, 20 circles each way building to 30",
         goal="Learn the movements, wake up the tendons with gentle holds, and find comfortable weights. Low volume, nothing hard. Week 4 is Christmas week: lighter, plus a short retest so we have starting numbers.",
         effort="Easy: leave 4 or more reps in the tank. Holds at about 5 to 6 out of 10 effort."),
    dict(key="base", name="Base: tendon and muscle building", weeks=(5, 13), minutes="20 to 30 minutes",
         ball="Ball 2, then Ball 3 once Ball 2 is easy at shoulder height (usually around week 10)",
         goal="Build tendon and muscle capacity (the general preparation phase): lots of isometric holds, slow 3-second lowering, moderate weights for 8 to 15 reps. Week 5 is New Year week and stays light. Week 9 is a recovery week, and week 13 is a recovery week that ends with a retest.",
         effort="Leave 3 reps in the tank. Holds at about 6 to 7 out of 10 effort."),
    dict(key="strength", name="Strength", weeks=(14, 21), minutes="25 to 30 minutes",
         ball="Ball 3, then Ball 4 when Ball 3 is easy at shoulder height",
         goal="Heavier, still slow and controlled: 5 to 8 reps, heavy slow calf raises, barbell Romanian deadlifts, slow pull-up lowering. Holds get heavier rather than longer. Week 17 is a recovery week, and week 21 is a recovery week with a retest.",
         effort="Leave 2 reps in the tank. Holds at about 7 to 8 out of 10 effort."),
    dict(key="power", name="Power and sport-specific", weeks=(22, 27), minutes="25 to 30 minutes",
         ball="Ball 4 (or stay on Ball 3 if 4 isn't easy yet)",
         goal="Turn strength into quickness for pickleball and golf: lift fast and lower slowly with moderate weights, fast band rotations, footwork and braking, and small ankle hops only if you pass the hop checklist. Week 25 is a recovery week, and week 27 is a lighter week with a retest heading into summer.",
         effort="Fast but crisp: end each set while every rep is still quick. Leave 3 reps in the tank on lifts."),
    dict(key="peak", name="Peak and maintain (summer)", weeks=(28, 39), minutes="20 to 25 minutes",
         ball="Ball 4, or Ball 3 in heavy-play weeks",
         goal="Hold your strength and quickness while you play a lot of pickleball: fewer sets, the same weights, short sport drills, and plenty of elbow and calf care. Weeks 31 and 35 are recovery weeks. Week 39 (the end of August) is the final retest, and then the next year's cycle starts over.",
         effort="Leave 2 to 3 reps in the tank. Short and sharp, never exhausting."),
]

RECOVERY = {4, 5, 9, 13, 17, 21, 25, 27, 31, 35, 39}
RETEST = {4, 13, 21, 27, 39}
HOLIDAY = {4: "Christmas week (Dec 21 to 27): lighter on purpose.", 5: "New Year week (Dec 28 to Jan 3): lighter on purpose."}

LIB = None  # set by the builder


def phase_of(week):
    for p in PHASES:
        if p["weeks"][0] <= week <= p["weeks"][1]:
            return p
    raise ValueError(week)


def pick(lst, n):
    return lst[min(max(n, 1), len(lst)) - 1]


def X(id, sets, reps=None, hold=None, tempo="", load="", effort="", side="", notes="", minutes=None, rest=None):
    assert id in LIB, id
    d = {"id": id, "sets": sets}
    if reps is not None:
        d["reps"] = str(reps)
    if hold is not None:
        d["hold"] = hold
    for k, v in (("tempo", tempo), ("load", load), ("effort", effort), ("side", side), ("notes", notes)):
        if v:
            d[k] = v
    if minutes is not None:
        d["minutes"] = minutes
    if rest is not None:
        d["rest"] = rest
    return d


RIGHT_EXTRA = "each leg, right first; right gets 1 extra set"
RIGHT_ARM_EXTRA = "each arm, right first; right gets 1 extra set"
EACH = "each side"
RIGHT_ONLY = "right arm only (left arm optional)"

T_SLOW = "3 seconds down, 1 second up"
T_HINGE = "3 seconds down, 2 seconds up"
T_ROW = "2 seconds up, hold 1, 3 seconds down"
T_BRIDGE = "2 seconds up, hold 2, 3 seconds down"
T_CALF = "3 seconds up, hold 1 at the top, 3 seconds down"
T_BAND = "2 seconds out, hold 1, 2 seconds back"
T_FAST = "lift fast, then 3 seconds down"
T_PALLOF = "2 seconds out, hold 3, 2 seconds back"
T_ECC = "help it up with the other hand, then 4 seconds down"


def rec(items):
    """Recovery-week version: about 40 percent fewer sets, nothing new."""
    out = []
    for it in items:
        it = dict(it)
        if isinstance(it["sets"], int) and it["sets"] > 1 and not it.get("minutes"):
            it["sets"] = max(1, round(it["sets"] * 0.6))
        out.append(it)
    return out


def wu_legs():
    return [X("warm_cardio", 1, minutes=3),
            X("ankle_prep", 1, reps="10 circles each way, then 15 raises"),
            X("leg_swings", 1, reps="10 each direction", side=EACH)]


def wu_sport():
    return [X("warm_cardio", 1, minutes=2),
            X("open_book", 1, reps=6, side=EACH, tempo="2 seconds open while breathing out, 2 seconds back")]


def wu_upper():
    # The Shoulder Reliever that follows doubles as the shoulder warm-up.
    return [X("pullapart", 1, reps=15, tempo="2 seconds apart, 2 seconds back"),
            X("open_book", 1, reps=5, side=EACH, tempo="2 seconds open while breathing out, 2 seconds back")]


def reliever(phase_key, n):
    circles = pick(["20", "25", "30"], n) if phase_key == "runin" else "30"
    ball = {"runin": "Ball 1", "base": "Ball 2 (Ball 3 from about week 10 if Ball 2 is easy)", "strength": "Ball 3 (Ball 4 when ready)",
            "power": "Ball 4 (or 3)", "peak": "Ball 4 (Ball 3 in heavy-play weeks)"}[phase_key]
    return X("shoulder_reliever", 1, reps=f"{circles} circles each way in each of the 4 positions, each arm",
             load=ball, minutes=4 if circles == "20" else 5,
             notes="Once a day at most: if you've already done it today, skip it here.")

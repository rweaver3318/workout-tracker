#!/usr/bin/env python3
"""
Ron's "Pickleball & Golf Year 2026-27" plan (Arnold).

    python3 build_program_ron_2027.py

Writes:
  program-ron-2027.json                          (loaded by the app for Ron)
  /workspace/arnold/pickleball-2027/plan.md      (readable copy of the same plan)

How it's organized (edit the data below, then re-run):
  LIB      - exercise library: name, how-to, demo link, easier option, swap
  PHASES   - the macrocycle (weeks, goals, Shoulder Reliever ball, time target)
  RECOVERY / RETEST - which of the 39 weeks are lighter / end with a retest
  legs() / sport() / upper()  - the three workouts of each week, per phase
The app shows workouts as a numbered sequence (1..117) with no fixed dates.
Exercise ids key the logged data - keep them stable when editing.
"""
from __future__ import annotations

import json
import re
from datetime import date, timedelta
from pathlib import Path
from urllib.parse import quote_plus

HERE = Path(__file__).resolve().parent
PLAN_MD = Path("/workspace/arnold/pickleball-2027/plan.md")
START = date(2026, 11, 30)  # Monday, week 1
PROGRAM_ID = "ron-pickleball-golf-2026-27"


def yt(q: str) -> str:
    return "https://www.youtube.com/results?search_query=" + quote_plus(q)


LIB: dict[str, dict] = {}


def L(id, name, area, how, demo, easier="", swap="", optional=False, where=""):
    LIB[id] = {k: v for k, v in dict(id=id, name=name, area=area, how=how, demo=demo, easier=easier,
                                     swap=swap, optional=optional, where=where).items() if v not in ("", False)}


from ron2027_library import define_library  # noqa: E402

define_library(L, yt)

import ron2027_phases as PH  # noqa: E402

PH.LIB = LIB
from ron2027_phases import HOLIDAY, PHASES, RECOVERY, RETEST, phase_of  # noqa: E402
from ron2027_workouts import legs, sport, upper  # noqa: E402

DAY_TYPES = {
    "legs": {"name": "Legs, hips and calves", "short": "Legs",
             "why": "The hardest leg day. Best on a day that isn't the day before pickleball (for example Tuesday)."},
    "sport": {"name": "Golf and pickleball: rotation, balance and footwork", "short": "Sport",
              "why": "Moderate. Fine on Friday morning before golf, or on Saturday."},
    "upper": {"name": "Shoulders, back, arms and elbow", "short": "Upper",
              "why": "Easy on the legs, so it's fine the day before pickleball (for example Sunday)."},
}
ORDER = ["legs", "sport", "upper"]  # Sun/Tue/Fri with Monday-to-Sunday weeks: Tue legs, Fri sport, Sun upper


def secs(text):
    m = re.search(r"(\d+)", str(text or ""))
    return int(m.group(1)) if m else 0


def est_minutes(items):
    """Rough time estimate for the 'about N minutes' label."""
    total = 0
    for it in items:
        if it.get("minutes"):
            total += it["minutes"] * 60
            continue
        area = LIB[it["id"]]["area"]
        sides = 2 if it.get("side") else 1
        extra = 1 if "extra set" in it.get("side", "") else 0
        if it.get("hold"):
            work = secs(it["hold"]) or 30
        else:
            r = secs(it.get("reps")) or 10
            per = sum(int(x) for x in re.findall(r"(\d+) second", it.get("tempo", ""))) or 3
            work = r * min(per, 6)
        if area == "Retest":
            work, sides = 60, 1
        rest = it.get("rest", 30 if sides == 1 else 10)  # sided work: the other side rests while one works
        if area in ("Warm-up", "Cool-down"):
            rest = 0
        sets = it["sets"]
        total += (sets * sides + extra) * work + max(sets - 1, 0) * rest + 15
    return int(round(total / 60))


def build():
    workouts, weeks = [], []
    builds = {p["key"]: 0 for p in PHASES}
    for w in range(1, 40):
        ph = phase_of(w)
        recovery, retest = w in RECOVERY, w in RETEST
        if not recovery:
            builds[ph["key"]] += 1
        n = max(builds[ph["key"]], 1)
        ws = START + timedelta(weeks=w - 1)
        weeks.append({"week": w, "phase": ph["key"], "weekInPhase": w - ph["weeks"][0] + 1,
                      "phaseWeeks": ph["weeks"][1] - ph["weeks"][0] + 1, "recovery": recovery, "retest": retest,
                      "start": ws.isoformat(), "end": (ws + timedelta(days=6)).isoformat(), "note": HOLIDAY.get(w, "")})
        for slot, kind in enumerate(ORDER):
            S = legs(ph, n, recovery) if kind == "legs" else sport(ph, n, recovery, retest) if kind == "sport" else upper(ph, n, recovery)
            num = len(workouts) + 1
            sections = [{"title": t, "items": items} for t, items in S if items]
            ids = [it["id"] for s in sections for it in s["items"]]
            assert len(ids) == len(set(ids)), (num, ids)
            is_retest = retest and kind == "sport"
            workouts.append({
                "id": f"w{num:03d}", "num": num, "week": w, "slot": slot + 1, "type": kind, "phase": ph["key"],
                "weekInPhase": w - ph["weeks"][0] + 1, "recovery": recovery, "retest": is_retest,
                "title": DAY_TYPES[kind]["name"],
                "tag": "Retest" if is_retest else ("Recovery week" if recovery else "Build week"),
                "minutes": est_minutes([it for s in sections for it in s["items"]]), "sections": sections,
            })
    phases = []
    for p in PHASES:
        a, b = p["weeks"]
        nums = [x["num"] for x in workouts if x["phase"] == p["key"]]
        phases.append(dict(p, start=(START + timedelta(weeks=a - 1)).isoformat(), end=(START + timedelta(weeks=b, days=-1)).isoformat(),
                           recoveryWeeks=[w for w in range(a, b + 1) if w in RECOVERY], retestWeeks=[w for w in range(a, b + 1) if w in RETEST],
                           workouts=[min(nums), max(nums)]))
    return workouts, weeks, phases


NOTES = [
    "Workouts are a numbered list, not dates. Do the next one whenever you can; aim for about 3 a week (for example Sunday, Tuesday, and Friday or Saturday). Days off don't matter.",
    "Each week runs Legs, then Sport, then Upper. On a Sunday-Tuesday-Friday rhythm that puts the hard leg day on Tuesday (two days before Thursday pickleball), the sport day on Friday or Saturday, and the easy-on-the-legs upper day on Sunday, the day before Monday pickleball.",
    "If the next workout is a Legs day and you play pickleball tomorrow, it's fine to do the following workout first. The app keeps the skipped one as your next workout until you do it.",
    "Pain rule: joint or tendon pain up to 3 out of 10 during exercise is OK if it settles by the next morning. If it goes above 3, or you're worse the next morning, drop back a step: use the previous week's weight or hold, or the easier option.",
    "Going up: when every set feels easy (3 or more reps left in the tank, or holds feel like 5 out of 10 or less) for 2 workouts in a row and pain stays at 0 to 2, move up one dumbbell (10, 15, 20, 30, 50 lb), add 5 to 10 lb on the barbell, or add 5 to 10 seconds to a hold. The weights listed are a guide; your log wins.",
    "Big jumps between dumbbells (30 to 50 lb): bridge the gap with slower lowering, an extra rep or two, or a backpack with books.",
    "Missed time: after 7 to 14 days off, repeat the last workout you did before moving on (open it and mark it done again, or just redo it). After 3 or more weeks off, go back about 3 workouts.",
    "Recovery weeks are lighter on purpose (about 40 percent fewer sets). Do them even if you feel great; that's when the tendons catch up.",
    "Retests come at the end of each phase in the Sport workout: calf raise count each leg, 30-second sit-to-stand, single-leg balance, side plank, farmer hold time, hang or pulldown hold, and an elbow and shoulder check.",
    "Elbow rule for heavy weeks: in any week with 3 or more pickleball days plus golf, back-to-back days of both, or inner-elbow pain above 3 out of 10 (or still there the next morning), skip the slow wrist lowering, the farmer hold, the barbell top hold and the bar hangs, and keep only the gentle palm-up wrist holds (they tend to calm tendon pain). Go back to normal the next week if the elbow is at 0 to 2. Also check your paddle and club grip size, and don't strangle the grip.",
    "Hop checklist (before any ankle hops, line hops or a split-step bounce off the ground): 25 or more single-leg calf raises on the right, within about 90 percent of the left; no calf pain during or the next morning for 2 weeks; hips quiet (no groin pain or painful clicking). If anything is missing, use the no-hop option listed.",
    "Hips: no deep loaded squats or lunges, no barbell squats, no hard jumping, no heavy loaded twisting at the hip. Rotation exercises turn the upper body with the hips and back foot pivoting together. Every lower-body exercise lists an easier option.",
    "Shoulder Reliever: it's in the Sport and Upper workouts (about twice a week). The maker says no more than once a day. Stay on each ball at least 10 days and until all 4 positions at shoulder height feel easy, then start the next ball back at waist height. Not with you? Each workout lists a band swap.",
    "Optional items: the pull-up bar and bike work are Fayetteville only; each lists a swap for The Villages. Everything else uses dumbbells, bands, the barbell, the bench, the step and the curl bar, which you have at both houses.",
    "Effort in plain English: 'leave 3 reps in the tank' means stop when you could still do about 3 more good reps. Hold effort is out of 10, where 10 is the hardest you could push.",
]
RED_FLAGS = [
    "Calf swelling, warmth or redness, or new deep calf pain (can be a blood clot: get checked the same day)",
    "A pop or sudden sharp pain in the calf, elbow or shoulder",
    "Pain at night or at rest that is new or getting worse",
    "Hip groin pain, clicking with pain, a feeling of the hip giving way, or a sudden change in how the hip moves",
    "Numbness or tingling down the arm, or the elbow or shoulder getting weaker",
    "Chest pain, unusual shortness of breath, dizziness or fainting",
]
SOURCES = [
    ("The Movement System (the YouTube post you shared): traditional periodization, where volume goes down and intensity goes up toward the peak", "https://youtube.com/post/UgkxPEczcoGmprLw6nS8DorAVd-cpIZJ0YwC"),
    ("Haff GG, Triplett NT (eds). Essentials of Strength Training and Conditioning, 4th ed. NSCA / Human Kinetics, 2016 (periodization chapter)", "https://www.nsca.com/education/books/"),
    ("Fragala MS, et al. Resistance training for older adults: position statement from the NSCA. J Strength Cond Res. 2019;33(8):2019-2052", "https://pubmed.ncbi.nlm.nih.gov/31343601/"),
    ("Rio E, et al. Isometric exercise induces analgesia and reduces inhibition in patellar tendinopathy. Br J Sports Med. 2015;49(19):1277-1283 (later studies are mixed on the pain relief; holds are used here mainly because they're joint-friendly and build tendon capacity)", "https://pubmed.ncbi.nlm.nih.gov/25979840/"),
    ("Beyer R, et al. Heavy slow resistance versus eccentric training as treatment for Achilles tendinopathy: a randomized controlled trial. Am J Sports Med. 2015;43(7):1704-1711", "https://pubmed.ncbi.nlm.nih.gov/26018970/"),
    ("Alfredson H, et al. Heavy-load eccentric calf muscle training for the treatment of chronic Achilles tendinosis. Am J Sports Med. 1998;26(3):360-366", "https://pubmed.ncbi.nlm.nih.gov/9617396/"),
    ("Malliaras P, et al. Achilles and patellar tendinopathy loading programmes: a systematic review. Sports Med. 2013;43(4):267-286", "https://pubmed.ncbi.nlm.nih.gov/23494258/"),
    ("Tyler TF, et al. Clinical outcomes of the addition of eccentrics for rehabilitation of previously failed treatments of golfer's elbow. Int J Sports Phys Ther. 2014;9(3):365-370", "https://pubmed.ncbi.nlm.nih.gov/24944855/"),
    ("Andersson SH, et al. Preventing overuse shoulder injuries among throwing athletes: a cluster-randomised controlled trial in 660 elite handball players. Br J Sports Med. 2017;51(14):1073-1080 (outward rotation, shoulder blade and push-up plus work about 3 times a week)", "https://pubmed.ncbi.nlm.nih.gov/27313171/"),
    ("Kolasinski SL, et al. 2019 American College of Rheumatology/Arthritis Foundation guideline for the management of osteoarthritis of the hand, hip, and knee. Arthritis Care Res. 2020;72(2):149-162 (exercise strongly recommended for hip arthritis)", "https://pubmed.ncbi.nlm.nih.gov/31908149/"),
    ("Meira EP, Zeni J Jr. Sports participation following total hip arthroplasty. Int J Sports Phys Ther. 2014;9(6):839-850", "https://pubmed.ncbi.nlm.nih.gov/25383251/"),
    ("CDC STEADI: 30-Second Chair Stand test", "https://www.cdc.gov/steadi/media/pdfs/STEADI-Assessment-30Sec-508.pdf"),
    ("Shoulder Reliever (Dr. Michael Carroll): instructional video and how-to", "https://shoulderreliever.com/pages/instructional-video"),
]


def nice(iso):
    return date.fromisoformat(iso).strftime("%a %b %-d, %Y")


def amount(it):
    s = it["sets"]
    if it.get("minutes") and not it.get("reps"):
        return f"about {it['minutes']} minutes"
    if it.get("reps"):
        return f"{s} sets of {it['reps']}" if s != 1 else (f"{it['reps']} reps" if str(it["reps"]).isdigit() else str(it["reps"]))
    if it.get("hold"):
        return f"{s} hold{'s' if s != 1 else ''} of {it['hold']}"
    return f"{s} round"


def item_line(it):
    e = LIB[it["id"]]
    bits = [amount(it)] + [it[k] for k in ("side", "tempo", "load", "effort", "notes") if it.get(k)]
    opt = " (optional)" if e.get("optional") else ""
    return f"- [{e['name']}]({e['demo']}){opt}: " + "; ".join(bits)


def workout_md(w):
    out = [f"#### Workout {w['num']}: {w['title']}", "",
           f"Week {w['week']}, {w['tag'].lower()}, about {w['minutes']} minutes.", ""]
    for s in w["sections"]:
        out.append(f"*{s['title']}*")
        out.append("")
        out.extend(item_line(it) for it in s["items"])
        out.append("")
    return "\n".join(out)


def write_md(data):
    W = data["workouts"]
    md = [f"# {data['title']}: Ron's plan", "",
          f"Starts Mon Nov 30, 2026. Peak and maintain through the end of August 2027, then start over. 39 weeks, 3 workouts a week, {len(W)} workouts in all, 15 to 30 minutes each.",
          "", "Live in the app: https://rweaver3318.github.io/workout-tracker/ (choose Ron). Generated by build_program_ron_2027.py in the app repo.", "",
          data["disclaimer"], "", "## Who it's for", "", data["conditions"], "", "## How it works", ""]
    md += [f"- {n}" for n in data["notes"]]
    md += ["", "## Phases", "", "| Phase | Weeks | Planned dates | Workouts | Session length | Goal |", "|---|---|---|---|---|---|"]
    for p in data["phases"]:
        md.append(f"| {p['name']} | {p['weeks'][0]} to {p['weeks'][1]} | {nice(p['start'])} to {nice(p['end'])} | {p['workouts'][0]} to {p['workouts'][1]} | {p['minutes']} | {p['goal']} |")
    md += ["", "Recovery weeks: " + ", ".join(str(w) for w in sorted(RECOVERY)) + ". Retests at the end of weeks " + ", ".join(str(w) for w in sorted(RETEST)) + ".",
           "", "Holiday stretch: week 4 (Christmas, Dec 21 to 27) and week 5 (New Year, Dec 28 to Jan 3) are both light on purpose.",
           "", "Planned dates assume about 3 workouts a week from Nov 30. The app re-projects the dates from wherever you actually are.", "",
           "Effort and Shoulder Reliever ball by phase:", ""]
    md += [f"- **{p['name']}**: {p['effort']} Shoulder Reliever: {p['ball']}." for p in data["phases"]]
    md += ["", "## The three workouts each week", ""] + [f"- **{v['name']}** ({v['short']}): {v['why']}" for v in data["dayTypes"].values()]
    md += ["", "## Red flags: stop and see your doctor or PT", ""] + [f"- {r}" for r in data["redFlags"]]
    md += ["", "## A sample build week from each phase", ""]
    for p in data["phases"]:
        wk = next(w["week"] for w in W if w["phase"] == p["key"] and not w["recovery"])
        md += [f"### {p['name']} (week {wk})", ""] + [workout_md(w) for w in W if w["week"] == wk]
    md += ["## Exercise library", ""]
    by_area: dict[str, list] = {}
    for e in LIB.values():
        by_area.setdefault(e["area"], []).append(e)
    for area, exs in by_area.items():
        md += [f"### {area}", ""]
        for e in exs:
            tag = f" (optional, {e['where']} only)" if e.get("where") else (" (optional)" if e.get("optional") else "")
            md.append(f"**[{e['name']}]({e['demo']})**{tag}: {e['how']}")
            md.append("")
            if e.get("easier"):
                md += [f"- Easier: {e['easier']}"]
            if e.get("swap"):
                md += [f"- Swap: {e['swap']}"]
            if e.get("easier") or e.get("swap"):
                md.append("")
    md += ["## Sources", ""] + [f"- [{s['text']}]({s['url']})" for s in data["sources"]]
    md += ["", "## Every workout", "", "The app has the same list with how-to text, easier options and swaps on every exercise.", ""]
    cur = None
    for w in W:
        if w["phase"] != cur:
            cur = w["phase"]
            md += [f"### {phase_of(w['week'])['name']}", ""]
        md.append(workout_md(w))
    PLAN_MD.parent.mkdir(parents=True, exist_ok=True)
    PLAN_MD.write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"Wrote {PLAN_MD} ({len(md)} lines)")


def main():
    workouts, weeks, phases = build()
    used = {it["id"] for w in workouts for s in w["sections"] for it in s["items"]}
    unused = sorted(set(LIB) - used)
    if unused:
        print("Library entries not used by any workout:", unused)
    data = {
        "person": "ron", "displayName": "Ron", "athlete": "Ron Weaver", "kind": "sequence",
        "programId": PROGRAM_ID, "storageKey": "workout:v3:ron:pg2026-27",
        "title": "Pickleball & Golf Year 2026-27",
        "programWindow": "Pickleball & Golf Year 2026-27",
        "conditions": "Age 55. Right hip replacement (anterior approach, Mar 4, 2026), pain-free; mild arthritis in the left hip. Right calf tear (Sep 19, 2026), now pain-free, right calf still a bit weaker than the left. Right inner elbow (golfer's elbow pattern) flares with lots of pickleball plus golf. No shoulder pain; the shoulder work is for prevention.",
        "startDate": START.isoformat(), "endDate": (START + timedelta(weeks=39, days=-1)).isoformat(),
        "defaultTrainingDays": [0, 2, 5],
        "disclaimer": "Arnold is a coach, not a doctor. This is a training plan, not medical advice. If something feels wrong, stop and check with your doctor or physical therapist.",
        "banner": "Pain up to 3 out of 10 that settles by the next morning is OK. Higher, or worse the next morning: drop back a step. Calf swelling or warmth, a pop, night pain, or hip groin pain: stop and see your doctor or PT.",
        "dayTypes": DAY_TYPES, "phases": phases, "weeks": weeks, "workouts": workouts, "library": LIB,
        "notes": NOTES, "redFlags": RED_FLAGS, "sources": [{"text": t, "url": u} for t, u in SOURCES],
        "pain": {"title": "Pain trend", "ceiling": 3, "fields": [
            {"key": "calfPain", "label": "Right calf pain during", "short": "Calf", "when": "during", "color": "#0d6e4f"},
            {"key": "hipPain", "label": "Hip pain during (either side)", "short": "Hip", "when": "during", "color": "#7c3aed"},
            {"key": "elbowPain", "label": "Right inner elbow pain during", "short": "Elbow", "when": "during", "color": "#c45c26"},
            {"key": "shoulderPain", "label": "Shoulder pain during", "short": "Shoulder", "when": "during", "color": "#2563eb"},
            {"key": "morningPain", "label": "Worst pain the next morning (any of these)", "short": "Next morning", "when": "morning", "color": "#b91c1c"},
        ]},
    }
    out = HERE / "program-ron-2027.json"
    out.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
    print(f"Wrote {out.name}: {len(workouts)} workouts, {len(LIB)} exercises, {out.stat().st_size // 1024} KB")
    for p in phases:
        mins = [w["minutes"] for w in workouts if w["phase"] == p["key"]]
        print(f"  {p['name']:<36} wk {p['weeks']} {p['start']}..{p['end']} #{p['workouts']} min {min(mins)}-{max(mins)}")
    write_md(data)


if __name__ == "__main__":
    main()

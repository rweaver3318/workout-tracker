"""Shared helpers for the program builders (build_program.py, build_program_cindy.py).

Per-person program JSON schema (program-<person>.json)
------------------------------------------------------
person, displayName, athlete, conditions, programWindow, startDate, endDate, disclaimer
banner                 – short safety line shown on every session
notes[]                – key coaching notes (shown in Settings > About)
redFlags[]
painRules              – {ceiling, pass, hold, advance, ...}
levelSystem            – {key, label, short, advanceRule, levels:[{level, name, estimate, entry, exit, exercises[]}]}
blocks                 – {<name>: {label, keyField: "weekBand"|"kneeBand", bands: {<key>: exercises[]}}}
lists                  – {<name>: {title, exercises[]}}   static lists (warm-up, reassessment, baseline ...)
sessionTypes           – {code: description}
optionalTypes[]        – session codes that don't break the streak if skipped
sessionTemplates       – {code: [section, ...]}; section =
                           {title, source:"level"}                       current level's exercises
                           {title, source:"block", block:"hips"}         band chosen by schedule row keyField
                           {title, source:"list",  list:"reassessment"}
                         optional section filters: "filter":"diamond" (◆ items only), "first": N
                         title placeholders: {level} {levelName} {weekBand} {kneeBand} {week}
schedule[]             – {date, day, week, type, label, weekBand, kneeBand?, extras?: [listName]}
pain                   – {ceiling, fields:[{key, label, short, when:"during"|"morning", color, baseline?, goal?}]}
answerDependent[]      – Cindy's † table {exercise, why}

Exercise object: id, name, sets, reps|hold, load, notes, cues?, optional?,
                 diamond? (◆), flag? ("†") + flagNote?, minLevel? + gateNote?
Exercise ids are the keys for logged data – keep them stable when editing.
"""
from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def ex(id, name, sets, *, reps=None, hold=None, load="", notes="", cues="",
       optional=False, diamond=False, flag=None, flag_note="", min_level=None, gate_note=""):
    d = {"id": id, "name": name, "sets": sets, "load": load, "notes": notes}
    if reps is not None:
        d["reps"] = reps
    if hold is not None:
        d["hold"] = hold
    if cues:
        d["cues"] = cues
    if optional:
        d["optional"] = True
    if diamond:
        d["diamond"] = True
    if flag:
        d["flag"] = flag
        if flag_note:
            d["flagNote"] = flag_note
    if min_level is not None:
        d["minLevel"] = min_level
        if gate_note:
            d["gateNote"] = gate_note
    return d


def week_band(week: int) -> str:
    return "1-2" if week <= 2 else "3-4" if week <= 4 else "5-6" if week <= 6 else "7-8"


def check_ids(data: dict) -> None:
    """Fail loudly on duplicate exercise ids (they key the logs)."""
    seen = {}
    def walk(exs, where):
        for e in exs:
            if e["id"] in seen and seen[e["id"]] != e["name"]:
                raise SystemExit(f"Duplicate id {e['id']} ({where})")
            seen[e["id"]] = e["name"]
    for lvl in data["levelSystem"]["levels"]:
        walk(lvl["exercises"], f"level {lvl['level']}")
    for bname, b in data["blocks"].items():
        for k, exs in b["bands"].items():
            walk(exs, f"{bname} {k}")
    for lname, l in data["lists"].items():
        walk(l["exercises"], lname)


def write(data: dict, filename: str) -> Path:
    check_ids(data)
    out = HERE / filename
    out.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {out.name}: {len(data['schedule'])} sessions, "
          f"{len(data['levelSystem']['levels'])} {data['levelSystem']['label']}s")
    return out

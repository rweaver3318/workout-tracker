/* Weaver Workout Tracker — Ron + Cindy (Arnold programs) */
(function () {
  "use strict";

  const APP_BUILD = "2026.09.24-two-person";
  const PEOPLE = [
    { id: "ron", label: "Ron", file: "program-ron.json" },
    { id: "cindy", label: "Cindy", file: "program-cindy.json" },
  ];
  const LS_ACTIVE = "workout:v2:activePerson";
  const lsKey = (id) => `workout:v2:${id}`;
  const LEGACY_KEY = "ron-workout-v1"; // v1 (Ron-only) storage — migrated, never deleted
  const BACKUP_APP = "weaver-workout-tracker";
  const VIEWS = ["today", "pick", "progress", "settings"];

  const programs = {}; // id -> program json
  const stores = {}; // id -> {version, settings:{startDate, level}, sessions}
  let person = "ron";
  let viewDate = todayISO();
  let currentView = "today";

  // ---------- helpers ----------
  function isoOf(d) {
    return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
  }
  function todayISO() { return isoOf(new Date()); }
  function parseISO(s) { const [y, m, d] = s.split("-").map(Number); return new Date(y, m - 1, d); }
  function shiftDate(iso, days) { const d = parseISO(iso); d.setDate(d.getDate() + days); return isoOf(d); }
  function daysBetween(a, b) { return Math.round((parseISO(b) - parseISO(a)) / 86400000); }
  function formatNice(iso) {
    return parseISO(iso).toLocaleDateString("en-US", { weekday: "short", month: "short", day: "numeric", year: "numeric" });
  }
  function dayName(iso) { return parseISO(iso).toLocaleDateString("en-US", { weekday: "short" }); }
  const $ = (sel, root) => (root || document).querySelector(sel);
  const $all = (sel, root) => Array.from((root || document).querySelectorAll(sel));
  function escapeHtml(s) {
    return String(s ?? "").replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
  }
  const escapeAttr = (s) => escapeHtml(s).replace(/'/g, "&#39;");
  function toast(msg) {
    const el = $("#toast");
    el.textContent = msg;
    el.classList.add("show");
    clearTimeout(toast._t);
    toast._t = setTimeout(() => el.classList.remove("show"), 2200);
  }
  const P = () => programs[person];
  const S = () => stores[person];
  const personLabel = (id) => (PEOPLE.find((p) => p.id === id) || {}).label || id;

  // ---------- storage ----------
  function defaultStore(id) {
    const prog = programs[id];
    return { version: 2, person: id, settings: { startDate: prog.startDate, level: 0 }, sessions: {} };
  }
  function normalizeStore(id, raw) {
    const s = raw && typeof raw === "object" ? raw : {};
    const d = defaultStore(id);
    s.version = 2;
    s.person = id;
    const rawSettings = Object.assign({}, s.settings || {});
    if (rawSettings.level == null && rawSettings.calfLevel != null) rawSettings.level = Number(rawSettings.calfLevel) || 0; // v1 → v2
    delete rawSettings.calfLevel;
    s.settings = Object.assign({}, d.settings, rawSettings);
    s.settings.level = Number(s.settings.level) || 0;
    if (!s.sessions || typeof s.sessions !== "object") s.sessions = {};
    return s;
  }
  function loadStore(id) {
    try {
      const raw = localStorage.getItem(lsKey(id));
      if (raw) return normalizeStore(id, JSON.parse(raw));
    } catch (e) {
      console.warn("Bad stored data for " + id, e);
    }
    return defaultStore(id);
  }
  function saveStore(id) {
    localStorage.setItem(lsKey(id || person), JSON.stringify(stores[id || person]));
  }
  /** Copy v1 Ron data (key ron-workout-v1) into Ron's v2 namespace. Legacy key is left in place as a backup. */
  function migrateLegacy() {
    try {
      const legacy = localStorage.getItem(LEGACY_KEY);
      if (!legacy || localStorage.getItem(lsKey("ron"))) return false;
      const old = JSON.parse(legacy);
      const s = normalizeStore("ron", {
        settings: old.settings || {},
        sessions: old.sessions || {},
      });
      s.migratedFrom = LEGACY_KEY;
      s.migratedAt = new Date().toISOString();
      localStorage.setItem(lsKey("ron"), JSON.stringify(s));
      return true;
    } catch (e) {
      console.warn("Legacy migration failed; legacy data left untouched", e);
      return false;
    }
  }

  // ---------- program resolution ----------
  function offsetDays() {
    return daysBetween(P().startDate, S().settings.startDate || P().startDate);
  }
  function schedule() {
    const off = offsetDays();
    return P().schedule.map((r) => {
      if (!off) return r;
      const date = shiftDate(r.date, off);
      return Object.assign({}, r, { date, day: dayName(date) });
    });
  }
  function scheduleFor(date) { return schedule().find((s) => s.date === date) || null; }
  function currentLevel() {
    const ls = P().levelSystem;
    return ls.levels.find((l) => l.level === S().settings.level) || ls.levels[0];
  }
  function fill(title, ctx) {
    return title.replace(/\{(\w+)\}/g, (_, k) => (ctx[k] != null ? ctx[k] : ""));
  }
  function buildWorkout(date) {
    const prog = P();
    const sched = scheduleFor(date);
    const lvl = currentLevel();
    if (!sched) return { date, scheduled: false, sections: [] };
    const ctx = { level: lvl.level, levelName: lvl.name, weekBand: sched.weekBand, kneeBand: sched.kneeBand, week: sched.week };
    const sections = [];
    const tmpl = (prog.sessionTemplates[sched.type] || []).slice();
    for (const extra of sched.extras || []) tmpl.push({ title: prog.lists[extra]?.title || extra, source: "list", list: extra });
    for (const t of tmpl) {
      let exs = [];
      if (t.source === "level") exs = lvl.exercises;
      else if (t.source === "list") exs = (prog.lists[t.list] || {}).exercises || [];
      else if (t.source === "block") {
        const b = prog.blocks[t.block];
        exs = (b && b.bands[sched[b.keyField]]) || [];
      }
      if (t.filter === "diamond") exs = exs.filter((e) => e.diamond);
      if (t.first) exs = exs.slice(0, t.first);
      if (exs.length) sections.push({ title: fill(t.title, ctx), exercises: exs });
    }
    return {
      date, scheduled: true, week: sched.week, type: sched.type, label: sched.label,
      kneeBand: sched.kneeBand, sections, typeName: prog.sessionTypes[sched.type] || sched.type,
    };
  }
  const flatExercises = (w) => w.sections.flatMap((s) => s.exercises);
  function allProgramExercises(prog) {
    const out = {};
    prog.levelSystem.levels.forEach((l) => l.exercises.forEach((e) => (out[e.id] = e)));
    Object.values(prog.blocks).forEach((b) => Object.values(b.bands).forEach((exs) => exs.forEach((e) => (out[e.id] = e))));
    Object.values(prog.lists).forEach((l) => l.exercises.forEach((e) => (out[e.id] = e)));
    return out;
  }

  // ---------- session logs ----------
  function emptyLog(date) {
    const pain = {};
    P().pain.fields.forEach((f) => (pain[f.key] = null));
    return Object.assign({ date, completed: false, rpe: null, sessionNote: "", exercises: [] }, pain);
  }
  /** Returns the stored log or an unsaved draft (days are only stored once touched). */
  function getLog(date) { return S().sessions[date] || emptyLog(date); }
  function mutateLog(date, fn) {
    const st = S();
    if (!st.sessions[date]) st.sessions[date] = emptyLog(date);
    fn(st.sessions[date]);
    saveStore();
  }
  function exRow(log, id) { return (log.exercises || []).find((x) => x.id === id); }
  function ensureExRow(log, id) {
    let r = exRow(log, id);
    if (!r) { r = { id, done: false, weight: "", repsOrHold: "", note: "" }; log.exercises.push(r); }
    return r;
  }
  function isTouched(s) {
    if (!s) return false;
    if (s.completed || s.sessionNote) return true;
    if ((s.exercises || []).some((e) => e.done || e.weight || e.repsOrHold || e.note)) return true;
    // legacy v1 logs defaulted painDuring=0 / rpe=5 on view; only count morning ratings as real signal
    return P().pain.fields.some((f) => f.when === "morning" && s[f.key] != null);
  }

  // ---------- header / person ----------
  function renderSwitcher() {
    $all("[data-person]").forEach((b) => {
      const on = b.getAttribute("data-person") === person;
      b.classList.toggle("on", on);
      b.setAttribute("aria-pressed", on ? "true" : "false");
    });
    document.body.setAttribute("data-active-person", person);
    $("#header-sub").textContent = `${P().athlete} · ${P().programWindow}`;
  }
  function setPerson(id, opts) {
    if (!programs[id]) return;
    person = id;
    localStorage.setItem(LS_ACTIVE, id);
    viewDate = defaultViewDate();
    renderSwitcher();
    if (!opts || !opts.silent) toast(`Switched to ${personLabel(id)}`);
    showView(currentView);
  }
  function defaultViewDate() {
    const t = todayISO();
    const sch = schedule();
    const first = sch[0].date, last = sch[sch.length - 1].date;
    return t >= first && t <= last ? t : t < first ? first : last;
  }

  // ---------- views ----------
  function showView(name) {
    if (!VIEWS.includes(name)) name = "today";
    currentView = name;
    $all(".view").forEach((v) => v.classList.add("hidden"));
    $(`#view-${name}`).classList.remove("hidden");
    $all(".nav button").forEach((b) => b.classList.toggle("active", b.dataset.view === name));
    if (location.hash.replace(/^#/, "") !== name) history.replaceState(null, "", "#" + name);
    ({ today: renderToday, pick: renderPicker, progress: renderProgress, settings: renderSettings })[name]();
    window.scrollTo(0, 0);
  }

  function exerciseHtml(e, le) {
    const lvlNum = S().settings.level;
    const ls = P().levelSystem;
    const locked = e.minLevel != null && lvlNum < e.minLevel;
    const meta = [e.sets ? `${e.sets} sets` : null, e.reps ? `× ${e.reps}` : null, e.hold ? `hold ${e.hold}` : null, e.load || null]
      .filter(Boolean).join(" · ");
    const chips = [
      e.optional ? '<span class="chip">optional</span>' : "",
      e.diamond ? '<span class="chip">◆</span>' : "",
      e.flag ? `<span class="chip warn">${escapeHtml(e.flag)} depends</span>` : "",
      e.minLevel != null ? (locked
        ? `<span class="chip danger">HOLD · needs ${escapeHtml(ls.short)}${e.minLevel}+</span>`
        : `<span class="chip warn">test set first</span>`) : "",
    ].join(" ");
    const extra = [
      e.flagNote ? `<p class="ex-flag">${escapeHtml(e.flag || "†")} ${escapeHtml(e.flagNote)}</p>` : "",
      e.gateNote ? `<p class="ex-flag">${escapeHtml(e.gateNote)}</p>` : "",
    ].join("");
    return `<div class="exercise ${le.done ? "done" : ""} ${locked ? "locked" : ""}" data-ex="${escapeAttr(e.id)}">
      <button type="button" class="check ${le.done ? "on" : ""}" data-toggle="${escapeAttr(e.id)}" aria-label="Mark ${escapeAttr(e.name)} complete">${le.done ? "✓" : ""}</button>
      <div>
        <p class="ex-name">${escapeHtml(e.name)} ${chips}</p>
        <p class="ex-meta">${escapeHtml(meta)}${e.notes ? " — " + escapeHtml(e.notes) : ""}${e.cues ? " · Cue: " + escapeHtml(e.cues) : ""}</p>
        ${extra}
        <div class="ex-fields">
          <div><label class="field">Weight / load</label>
            <input type="text" inputmode="decimal" data-field="weight" data-id="${escapeAttr(e.id)}" value="${escapeAttr(le.weight)}" placeholder="e.g. 15 lb"></div>
          <div><label class="field">Reps / hold</label>
            <input type="text" data-field="repsOrHold" data-id="${escapeAttr(e.id)}" value="${escapeAttr(le.repsOrHold)}" placeholder="${e.hold ? "sec" : "reps"}"></div>
          <div class="full"><label class="field">Note</label>
            <input type="text" data-field="note" data-id="${escapeAttr(e.id)}" value="${escapeAttr(le.note)}" placeholder="optional"></div>
        </div>
      </div>
    </div>`;
  }

  function sliderHtml(key, label, value, min, max, hint) {
    const set = value != null;
    return `<div class="pain-field" data-slider="${key}">
      <label class="field">${escapeHtml(label)}${hint ? ` <span class="muted">(${escapeHtml(hint)})</span>` : ""}</label>
      <div class="slider-row">
        <input type="range" min="${min}" max="${max}" step="1" data-range="${key}" value="${set ? value : min}" aria-label="${escapeAttr(label)}">
        <span class="slider-val" data-val="${key}">${set ? value : "—"}</span>
        <button type="button" class="btn small" data-clear="${key}" ${set ? "" : "disabled"}>Clear</button>
      </div>
    </div>`;
  }

  function renderToday() {
    const root = $("#view-today");
    const prog = P();
    const w = buildWorkout(viewDate);
    const log = getLog(viewDate);
    const isToday = viewDate === todayISO();
    const ls = prog.levelSystem;
    let html = `<div class="card">
      <div class="row" style="margin-bottom:8px">
        <button class="btn" type="button" id="prev-day" aria-label="Previous day">‹</button>
        <div style="text-align:center;flex:2">
          <div style="font-weight:800;font-size:1.1rem">${formatNice(viewDate)}</div>
          <div class="muted">${isToday ? "Today" : escapeHtml(personLabel(person))} · ${w.scheduled ? "Week " + w.week : "rest day"}</div>
        </div>
        <button class="btn" type="button" id="next-day" aria-label="Next day">›</button>
      </div>
      <div class="session-meta">${w.scheduled
        ? `<span class="chip accent">Week ${w.week}</span><span class="chip">${escapeHtml(w.type)}</span>${w.kneeBand ? `<span class="chip">Knee band ${escapeHtml(w.kneeBand)}</span>` : ""}<span class="chip">${escapeHtml(ls.short)}${S().settings.level}</span>`
        : `<span class="chip">Rest day</span>`}</div>
      <p class="muted" style="margin:0">${w.scheduled ? escapeHtml(w.label.length > 3 ? w.label : w.typeName) + (w.label.length > 3 ? "" : "") : "No scheduled session."}</p>
      ${w.scheduled && w.label.length > 3 ? `<p class="muted" style="margin:4px 0 0">${escapeHtml(w.typeName)}</p>` : ""}
    </div>
    <div class="banner-warn">${escapeHtml(prog.banner)}</div>`;

    if (!w.scheduled) {
      const note = person === "cindy" ? "Pickleball/golf, rest, or easy bike. Do the daily DiGiovanni stretch." : "Rest or easy walking/ROM only.";
      html += `<div class="card rest-day"><div class="big">😌</div><h2>Rest / recovery</h2>
        <p class="muted">${escapeHtml(note)}</p>
        <button class="btn primary block" type="button" data-goto="pick">Pick a training day</button></div>`;
      root.innerHTML = html;
      bindTodayNav();
      return;
    }

    for (const sec of w.sections) {
      html += `<div class="card"><h3>${escapeHtml(sec.title)}</h3>`;
      for (const e of sec.exercises) html += exerciseHtml(e, exRow(log, e.id) || { done: false, weight: "", repsOrHold: "", note: "" });
      html += `</div>`;
    }

    html += `<div class="card"><h2>Session check-in</h2>
      <p class="muted" style="margin-top:0">Pain 0–10 (ceiling ${prog.pain.ceiling}). Morning ratings: fill in tomorrow.</p>`;
    for (const f of prog.pain.fields) {
      const hint = f.baseline != null ? `baseline ${f.baseline}, goal ≤${f.goal}` : f.when === "morning" ? "tomorrow" : "";
      html += sliderHtml(f.key, f.label, log[f.key], 0, 10, hint);
    }
    html += sliderHtml("rpe", "Session RPE (1–10)", log.rpe, 1, 10, "");
    html += `<label class="field">Session note</label>
      <textarea id="session-note" placeholder="${person === "cindy" ? "Pickleball/golf today? Swelling? How did it feel?" : "How did it feel? Swelling?"}">${escapeHtml(log.sessionNote || "")}</textarea>
      <div style="height:10px"></div>
      <button class="btn primary block" type="button" id="mark-complete">${log.completed ? "✓ Session completed — tap to undo" : "Mark session complete"}</button>
      <p class="muted" style="text-align:center;margin-bottom:0">Entries save automatically on this device.</p>
    </div>`;
    root.innerHTML = html;
    bindTodayNav();
    bindSession(viewDate);
  }

  function bindTodayNav() {
    $("#prev-day").onclick = () => { viewDate = shiftDate(viewDate, -1); renderToday(); };
    $("#next-day").onclick = () => { viewDate = shiftDate(viewDate, 1); renderToday(); };
    const g = $("[data-goto=pick]");
    if (g) g.onclick = () => showView("pick");
  }

  function bindSession(date) {
    $all("[data-toggle]").forEach((btn) => {
      btn.onclick = () => {
        const id = btn.getAttribute("data-toggle");
        mutateLog(date, (log) => { const r = ensureExRow(log, id); r.done = !r.done; });
        const done = exRow(getLog(date), id).done;
        btn.classList.toggle("on", done);
        btn.textContent = done ? "✓" : "";
        btn.closest(".exercise").classList.toggle("done", done);
      };
    });
    $all("[data-field]").forEach((inp) => {
      inp.addEventListener("change", () => {
        const id = inp.getAttribute("data-id"), field = inp.getAttribute("data-field");
        mutateLog(date, (log) => { ensureExRow(log, id)[field] = inp.value; });
      });
    });
    $all("[data-range]").forEach((r) => {
      const key = r.getAttribute("data-range");
      r.addEventListener("input", () => {
        mutateLog(date, (log) => { log[key] = Number(r.value); });
        $(`[data-val="${key}"]`).textContent = r.value;
        $(`[data-clear="${key}"]`).disabled = false;
      });
    });
    $all("[data-clear]").forEach((b) => {
      const key = b.getAttribute("data-clear");
      b.onclick = () => {
        mutateLog(date, (log) => { log[key] = null; });
        $(`[data-val="${key}"]`).textContent = "—";
        b.disabled = true;
      };
    });
    const note = $("#session-note");
    note.addEventListener("change", () => mutateLog(date, (log) => { log.sessionNote = note.value; }));
    $("#mark-complete").onclick = () => {
      mutateLog(date, (log) => { log.sessionNote = note.value; log.completed = !log.completed; });
      toast(getLog(date).completed ? "Session marked complete" : "Marked incomplete");
      renderToday();
    };
  }

  // ---------- picker ----------
  function renderPicker() {
    const root = $("#view-pick");
    const byWeek = {};
    schedule().forEach((s) => (byWeek[s.week] = byWeek[s.week] || []).push(s));
    let html = `<div class="card"><h2>${escapeHtml(personLabel(person))} — week / day picker</h2>
      <p class="muted">${escapeHtml(P().programWindow)}. ${escapeHtml(P().levelSystem.label)} content uses the current level (Settings).</p></div>`;
    Object.keys(byWeek).sort((a, b) => a - b).forEach((wk) => {
      html += `<div class="card"><h3>Week ${wk}</h3><div class="week-list">`;
      for (const s of byWeek[wk]) {
        const done = S().sessions[s.date]?.completed;
        const lbl = s.label.length > 3 ? s.label.replace(/^\w\s—\s*/, "") : P().sessionTypes[s.type];
        html += `<button type="button" class="btn" data-jump="${s.date}">
          <span><strong>${s.day} ${s.date.slice(5)}</strong> · ${escapeHtml(s.type)}${s.kneeBand ? " · Band " + escapeHtml(s.kneeBand) : ""}<br><span class="muted">${escapeHtml(lbl)}</span></span>
          <span class="right">${done ? "✓" : ""}</span></button>`;
      }
      html += `</div></div>`;
    });
    root.innerHTML = html;
    $all("[data-jump]").forEach((b) => (b.onclick = () => { viewDate = b.getAttribute("data-jump"); showView("today"); }));
  }

  // ---------- progress ----------
  function renderProgress() {
    const root = $("#view-progress");
    const prog = P(), st = S();
    const completed = Object.keys(st.sessions).filter((d) => st.sessions[d].completed).sort();
    const perWeek = sessionsPerWeek();
    let html = `<div class="card"><h2>${escapeHtml(personLabel(person))} — progress</h2>
      <div class="stat-grid">
        <div class="stat"><div class="num">${calcStreak(completed)}</div><div class="lbl">Completion streak</div></div>
        <div class="stat"><div class="num">${completed.length}<span class="of">/${prog.schedule.length}</span></div><div class="lbl">Sessions done</div></div>
      </div></div>
      <div class="card"><h2>Sessions per week</h2><div class="chart-wrap">${svgBarChart(perWeek.labels, perWeek.values, perWeek.targets)}</div></div>`;

    const pain = painSeries();
    const baselineField = prog.pain.fields.find((f) => f.baseline != null);
    html += `<div class="card"><h2>${escapeHtml(prog.pain.title || "Pain trend")}</h2>
      <div class="legend">${prog.pain.fields.map((f) => `<span><i style="background:${f.color}"></i>${escapeHtml(f.short)}</span>`).join("")}
        <span><i class="dash" style="border-color:#b91c1c"></i>ceiling ${prog.pain.ceiling}</span>
        ${baselineField ? `<span><i class="dash" style="border-color:${baselineField.color}"></i>${escapeHtml(baselineField.short.split(" (")[0])} baseline ${baselineField.baseline}</span>` : ""}</div>
      <div class="chart-wrap">${svgMultiLine(pain.labels, prog.pain.fields.map((f) => ({ color: f.color, values: pain.series[f.key] })), prog.pain.ceiling, baselineField)}</div></div>`;

    const opts = loadOptions();
    const sel = opts[0] ? opts[0].id : "";
    html += `<div class="card"><h2>Load over time</h2>
      <label class="field">Exercise</label>
      <select id="load-ex">${opts.map((o) => `<option value="${escapeAttr(o.id)}">${escapeHtml(o.name)}${o.n ? ` (${o.n})` : ""}</option>`).join("")}</select>
      <div class="chart-wrap" id="load-chart"></div><p class="muted" id="load-hint"></p></div>`;

    const recent = Object.keys(st.sessions).filter((d) => isTouched(st.sessions[d])).sort().reverse().slice(0, 10);
    html += `<div class="card"><h2>Recent sessions</h2>${recent.length ? "" : '<p class="empty">No sessions logged yet.</p>'}`;
    const pf0 = prog.pain.fields[0];
    for (const d of recent) {
      const s = st.sessions[d];
      const n = (s.exercises || []).filter((e) => e.done).length;
      html += `<button type="button" class="btn block recent" data-jump="${d}"><span>${formatNice(d)}</span>
        <span class="right">${s.completed ? "✓ " : ""}${n} ex · ${escapeHtml(pf0.short.split(" ")[0])} ${s[pf0.key] ?? "—"} · RPE ${s.rpe ?? "—"}</span></button>`;
    }
    html += `</div>`;
    root.innerHTML = html;

    const drawLoad = (id) => {
      const s = loadSeries(id);
      $("#load-chart").innerHTML = svgLineChart(s.labels, s.values, getComputedStyle(document.body).getPropertyValue("--accent").trim() || "#0d6e4f");
      $("#load-hint").textContent = s.values.every((v) => v == null) ? "Log a weight on this exercise to see a trend." : "";
    };
    $("#load-ex").onchange = (e) => drawLoad(e.target.value);
    drawLoad(sel);
    $all("[data-jump]").forEach((b) => (b.onclick = () => { viewDate = b.getAttribute("data-jump"); showView("today"); }));
  }

  function calcStreak(completedAsc) {
    if (!completedAsc.length) return 0;
    const done = new Set(completedAsc);
    const optional = new Set(P().optionalTypes || []);
    const t = todayISO();
    let streak = 0;
    for (const s of schedule().filter((s) => s.date <= t || done.has(s.date)).reverse()) {
      if (done.has(s.date)) streak++;
      else if (optional.has(s.type) || s.date === t) continue; // optional days / today don't break it
      else break;
    }
    return streak;
  }
  function sessionsPerWeek() {
    const sch = schedule();
    const weeks = [...new Set(sch.map((s) => s.week))].sort((a, b) => a - b);
    const optional = new Set(P().optionalTypes || []);
    return {
      labels: weeks.map((w) => `W${w}`),
      values: weeks.map((w) => sch.filter((s) => s.week === w && S().sessions[s.date]?.completed).length),
      targets: weeks.map((w) => sch.filter((s) => s.week === w && !optional.has(s.type)).length),
    };
  }
  function painSeries() {
    const st = S();
    const dates = Object.keys(st.sessions).filter((d) => isTouched(st.sessions[d])).sort();
    const series = {};
    P().pain.fields.forEach((f) => (series[f.key] = dates.map((d) => st.sessions[d][f.key] ?? null)));
    return { labels: dates.map((d) => d.slice(5)), series };
  }
  const parseLoad = (s) => { const m = String(s ?? "").match(/(\d+(\.\d+)?)/); return m ? Number(m[1]) : null; };
  function loadOptions() {
    const all = allProgramExercises(P());
    const counts = {};
    Object.values(S().sessions).forEach((s) => (s.exercises || []).forEach((e) => {
      if (parseLoad(e.weight) != null) counts[e.id] = (counts[e.id] || 0) + 1;
      if (!all[e.id]) all[e.id] = { id: e.id, name: e.id };
    }));
    return Object.values(all).map((e) => ({ id: e.id, name: e.name, n: counts[e.id] || 0 }))
      .sort((a, b) => b.n - a.n || a.name.localeCompare(b.name));
  }
  function loadSeries(id) {
    const st = S();
    const dates = Object.keys(st.sessions).sort().filter((d) => parseLoad(exRow(st.sessions[d], id)?.weight) != null);
    return { labels: dates.map((d) => d.slice(5)), values: dates.map((d) => parseLoad(exRow(st.sessions[d], id).weight)) };
  }

  // ---------- SVG charts ----------
  const W = 320, H = 170, PAD = 28;
  const xAt = (i, n) => PAD + (i * (W - PAD * 2)) / Math.max(n - 1, 1);
  function xLabels(labels) {
    const step = labels.length > 8 ? Math.ceil(labels.length / 6) : 1;
    return labels.map((lb, i) => (i % step ? "" : `<text x="${xAt(i, labels.length)}" y="${H - 8}" text-anchor="middle" font-size="10" fill="#5c5c5c">${lb}</text>`)).join("");
  }
  const noData = (msg) => `<svg viewBox="0 0 ${W} ${H}"><text x="50%" y="50%" text-anchor="middle" fill="#5c5c5c" font-size="13">${msg}</text></svg>`;
  function svgBarChart(labels, values, targets) {
    const max = Math.max(3, ...values, ...targets);
    const bw = (W - PAD * 2) / labels.length;
    const color = getComputedStyle(document.body).getPropertyValue("--accent").trim() || "#0d6e4f";
    let out = "";
    values.forEach((v, i) => {
      const x = PAD + i * bw + 4, h0 = H - PAD * 2;
      const th = (h0 * targets[i]) / max, bh = (h0 * v) / max;
      out += `<rect x="${x}" y="${H - PAD - th}" width="${bw - 8}" height="${th}" rx="4" fill="#e8e2d6"/>`;
      out += `<rect x="${x}" y="${H - PAD - bh}" width="${bw - 8}" height="${bh}" rx="4" fill="${color}"/>`;
      out += `<text x="${x + (bw - 8) / 2}" y="${H - 8}" text-anchor="middle" font-size="11" fill="#5c5c5c">${labels[i]}</text>`;
      out += `<text x="${x + (bw - 8) / 2}" y="${H - PAD - th - 4}" text-anchor="middle" font-size="11" font-weight="700" fill="#1a1a1a">${v}/${targets[i]}</text>`;
    });
    return `<svg viewBox="0 0 ${W} ${H}" role="img" aria-label="Sessions per week">${out}</svg>`;
  }
  function svgLineChart(labels, values, color) {
    const nums = values.filter((v) => v != null);
    if (!nums.length) return noData("No data yet");
    const max = Math.max(...nums, 1) * 1.15;
    const pts = values.map((v, i) => (v == null ? null : { x: xAt(i, labels.length), y: H - PAD - (v / max) * (H - PAD * 2), v })).filter(Boolean);
    return `<svg viewBox="0 0 ${W} ${H}" role="img"><path d="${pts.map((p, i) => `${i ? "L" : "M"}${p.x},${p.y}`).join(" ")}" fill="none" stroke="${color}" stroke-width="2.5"/>
      ${pts.map((p) => `<circle cx="${p.x}" cy="${p.y}" r="4" fill="${color}"/><text x="${p.x}" y="${p.y - 8}" text-anchor="middle" font-size="10" fill="#1a1a1a">${p.v}</text>`).join("")}${xLabels(labels)}</svg>`;
  }
  function svgMultiLine(labels, series, ceiling, baselineField) {
    if (!labels.length || series.every((s) => s.values.every((v) => v == null))) return noData("No pain data yet");
    const yOf = (v) => H - PAD - (v / 10) * (H - PAD * 2);
    let parts = `<line x1="${PAD}" y1="${yOf(ceiling)}" x2="${W - PAD}" y2="${yOf(ceiling)}" stroke="#b91c1c" stroke-dasharray="4 4" stroke-width="1.5"/>`;
    if (baselineField) parts += `<line x1="${PAD}" y1="${yOf(baselineField.baseline)}" x2="${W - PAD}" y2="${yOf(baselineField.baseline)}" stroke="${baselineField.color}" stroke-dasharray="2 4" stroke-width="1.5"/>`;
    [0, 5, 10].forEach((v) => (parts += `<text x="${PAD - 6}" y="${yOf(v) + 3}" text-anchor="end" font-size="10" fill="#5c5c5c">${v}</text>`));
    for (const s of series) {
      const pts = s.values.map((v, i) => (v == null ? null : { x: xAt(i, labels.length), y: yOf(v) })).filter(Boolean);
      if (!pts.length) continue;
      parts += `<path d="${pts.map((p, i) => `${i ? "L" : "M"}${p.x},${p.y}`).join(" ")}" fill="none" stroke="${s.color}" stroke-width="2.5"/>`;
      parts += pts.map((p) => `<circle cx="${p.x}" cy="${p.y}" r="3.5" fill="${s.color}"/>`).join("");
    }
    return `<svg viewBox="0 0 ${W} ${H}" role="img" aria-label="Pain trend">${parts}${xLabels(labels)}</svg>`;
  }

  // ---------- settings / backup ----------
  function renderSettings() {
    const root = $("#view-settings");
    const prog = P(), st = S(), ls = prog.levelSystem;
    const name = personLabel(person);
    const lvl = currentLevel();
    const levels = ls.levels.map((l) => `<option value="${l.level}" ${st.settings.level === l.level ? "selected" : ""}>Level ${l.level} — ${escapeHtml(l.name)}</option>`).join("");
    const other = PEOPLE.filter((p) => p.id !== person).map((p) => p.label).join(", ");
    root.innerHTML = `
      <div class="card settings-block">
        <h2>${escapeHtml(name)}'s settings</h2>
        <label class="field">Program start date (default ${escapeHtml(prog.startDate)})</label>
        <input type="date" id="set-start" value="${escapeAttr(st.settings.startDate)}">
        <p class="muted">Changing it shifts the whole dated schedule.</p>
        <label class="field">Current ${escapeHtml(ls.label)}</label>
        <select id="set-level">${levels}</select>
        <p class="muted">${escapeHtml(ls.advanceRule)}</p>
        <div class="level-info"><strong>Level ${lvl.level} exit:</strong> ${escapeHtml(lvl.exit)}</div>
        <div style="height:10px"></div>
        <button class="btn primary block" type="button" id="save-settings">Save ${escapeHtml(name)}'s settings</button>
      </div>
      <div class="card settings-block">
        <h2>Backup &amp; restore</h2>
        <h3>${escapeHtml(name)} only</h3>
        <div class="row"><button class="btn" type="button" data-export="json:one">Export ${escapeHtml(name)} JSON</button>
          <button class="btn" type="button" data-export="csv:one">Export ${escapeHtml(name)} CSV</button></div>
        <h3>Both people (Ron + Cindy)</h3>
        <div class="row"><button class="btn" type="button" data-export="json:all">Export BOTH JSON</button>
          <button class="btn" type="button" data-export="csv:all">Export BOTH CSV</button></div>
        <h3>Import JSON restore</h3>
        <p class="muted">Restores whoever is in the file (one person or both). You'll confirm before anything is replaced. Old single-person backups from the first version restore into Ron.</p>
        <input type="file" id="import-json" accept="application/json,.json">
      </div>
      <div class="card">
        <h2>About ${escapeHtml(prog.athlete)}'s plan</h2>
        <p class="muted">${escapeHtml(prog.conditions)}</p>
        <ul class="notes">${prog.notes.map((n) => `<li>${escapeHtml(n)}</li>`).join("")}</ul>
        ${prog.answerDependent ? `<h3>† Answer-dependent exercises</h3><ul class="notes">${prog.answerDependent.map((a) => `<li><strong>${escapeHtml(a.exercise)}</strong> — ${escapeHtml(a.why)}</li>`).join("")}</ul>` : ""}
        <h3>Red flags — stop and see a doctor</h3>
        <ul class="notes">${prog.redFlags.map((n) => `<li>${escapeHtml(n)}</li>`).join("")}</ul>
        <p class="muted">${escapeHtml(prog.disclaimer)}</p>
        <p class="muted">Data stays on this device (localStorage, separate for each person). Build ${APP_BUILD}.</p>
      </div>
      <div class="card"><button class="btn danger block" type="button" id="reset-data">Clear ${escapeHtml(name)}'s logged data</button>
        <p class="muted" style="text-align:center;margin-bottom:0">${escapeHtml(other)}'s data is not affected.</p></div>`;

    $("#save-settings").onclick = () => {
      st.settings.startDate = $("#set-start").value || prog.startDate;
      st.settings.level = Number($("#set-level").value) || 0;
      saveStore();
      viewDate = defaultViewDate();
      toast(`${name}'s settings saved`);
      renderSettings();
    };
    $all("[data-export]").forEach((b) => {
      const [kind, scope] = b.getAttribute("data-export").split(":");
      const ids = scope === "all" ? PEOPLE.map((p) => p.id) : [person];
      b.onclick = () => (kind === "json" ? exportJSON(ids) : exportCSV(ids));
    });
    $("#import-json").onchange = importJSON;
    $("#reset-data").onclick = () => {
      if (confirm(`Clear all of ${name}'s workout logs on this device? Settings are kept. Export first if unsure.`)) {
        st.sessions = {};
        saveStore();
        toast(`${name}'s logs cleared`);
      }
    };
  }

  function fileTag(ids) { return ids.length > 1 ? "ron-cindy" : ids[0]; }
  function exportJSON(ids) {
    const people = {};
    ids.forEach((id) => (people[id] = stores[id]));
    const data = { app: BACKUP_APP, format: 2, build: APP_BUILD, exportedAt: new Date().toISOString(), people };
    downloadBlob(new Blob([JSON.stringify(data, null, 2)], { type: "application/json" }), `workout-${fileTag(ids)}-${todayISO()}.json`);
    toast(`JSON downloaded (${ids.map(personLabel).join(" + ")})`);
  }
  function exportCSV(ids) {
    const painKeys = [];
    ids.forEach((id) => programs[id].pain.fields.forEach((f) => painKeys.includes(f.key) || painKeys.push(f.key)));
    const rows = [["person", "date", "completed", ...painKeys, "rpe", "session_note", "exercise_id", "exercise_name", "exercise_done", "weight", "reps_or_hold", "note"]];
    for (const id of ids) {
      const names = allProgramExercises(programs[id]);
      const sess = stores[id].sessions;
      for (const d of Object.keys(sess).sort()) {
        const s = sess[d];
        const base = [id, d, !!s.completed, ...painKeys.map((k) => s[k] ?? ""), s.rpe ?? "", csvEscape(s.sessionNote)];
        const exs = s.exercises || [];
        if (!exs.length) rows.push([...base, "", "", "", "", "", ""]);
        exs.forEach((e) => rows.push([...base, e.id, csvEscape(names[e.id]?.name || ""), !!e.done, csvEscape(e.weight), csvEscape(e.repsOrHold), csvEscape(e.note)]));
      }
    }
    downloadBlob(new Blob([rows.map((r) => r.join(",")).join("\n")], { type: "text/csv" }), `workout-${fileTag(ids)}-${todayISO()}.csv`);
    toast(`CSV downloaded (${ids.map(personLabel).join(" + ")})`);
  }
  function csvEscape(v) { const s = String(v ?? ""); return /[",\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s; }
  function downloadBlob(blob, name) {
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = name;
    document.body.appendChild(a);
    a.click();
    a.remove();
    setTimeout(() => URL.revokeObjectURL(a.href), 1000);
  }
  /** Accepts: v2 backup {app, format:2, people:{ron?,cindy?}} or legacy v1 {version:1, settings, sessions} (Ron). */
  function parseBackup(data) {
    if (data && data.people && typeof data.people === "object") {
      const out = {};
      Object.keys(data.people).forEach((id) => { if (programs[id]) out[id] = data.people[id]; });
      if (!Object.keys(out).length) throw new Error("No Ron or Cindy data in this file");
      return out;
    }
    if (data && data.sessions && data.settings) return { ron: data }; // v1 single-person backup (Ron)
    throw new Error("Not a workout tracker backup");
  }
  function importJSON(ev) {
    const file = ev.target.files && ev.target.files[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = () => {
      try {
        const found = parseBackup(JSON.parse(String(reader.result)));
        const ids = Object.keys(found);
        const summary = ids.map((id) => `${personLabel(id)} (${Object.keys(found[id].sessions || {}).length} days)`).join(" + ");
        if (!confirm(`Restore ${summary}? This REPLACES the current data for ${ids.map(personLabel).join(" and ")} on this device.`)) return;
        ids.forEach((id) => { stores[id] = normalizeStore(id, found[id]); saveStore(id); });
        toast(`Imported ${ids.map(personLabel).join(" + ")}`);
        showView(currentView);
      } catch (e) {
        alert("Import failed: " + e.message);
      }
    };
    reader.readAsText(file);
    ev.target.value = "";
  }

  // ---------- boot ----------
  async function init() {
    const loaded = await Promise.all(PEOPLE.map((p) => fetch(p.file).then((r) => { if (!r.ok) throw new Error(`${p.file}: ${r.status}`); return r.json(); })));
    PEOPLE.forEach((p, i) => (programs[p.id] = loaded[i]));
    const migrated = migrateLegacy();
    PEOPLE.forEach((p) => { stores[p.id] = loadStore(p.id); saveStore(p.id); });

    const saved = localStorage.getItem(LS_ACTIVE);
    person = programs[saved] ? saved : "ron";
    viewDate = defaultViewDate();

    $all("[data-person]").forEach((b) => (b.onclick = () => setPerson(b.getAttribute("data-person"))));
    $all(".nav button").forEach((b) => (b.onclick = () => showView(b.dataset.view)));
    window.addEventListener("hashchange", () => {
      const h = location.hash.replace(/^#/, "");
      if (VIEWS.includes(h) && h !== currentView) showView(h);
    });
    renderSwitcher();
    const initial = location.hash.replace(/^#/, "");
    showView(VIEWS.includes(initial) ? initial : "today");
    if (migrated) toast("Ron's earlier data was carried over");

    if ("serviceWorker" in navigator) navigator.serviceWorker.register("./sw.js").catch(() => {});
  }

  window.__workoutApp = {
    build: APP_BUILD, getStore: (id) => stores[id || person], getProgram: (id) => programs[id || person],
    person: () => person, setPerson, showView, buildWorkout, setViewDate: (d) => { viewDate = d; showView("today"); },
  };

  init().catch((e) => {
    console.error(e);
    document.querySelector("main").innerHTML = `<div class="card"><h2>Failed to load</h2><p>${escapeHtml(e.message)}</p></div>`;
  });
})();

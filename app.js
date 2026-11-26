/* Weaver Workout Tracker — Ron + Cindy (Arnold programs) */
(function () {
  "use strict";

  const APP_BUILD = "2026.11.26-pickleball-golf-year";
  const PEOPLE = [
    { id: "ron", label: "Ron", file: "program-ron-2027.json" },
    { id: "cindy", label: "Cindy", file: "program-cindy.json" },
  ];
  const LS_ACTIVE = "workout:v2:activePerson";
  const lsKey = (id) => (programs[id] && programs[id].storageKey) || `workout:v2:${id}`;
  // Ron's earlier 8-week plan (Sep to Dec 2026) stays untouched under its old key as an archive.
  const RON_ARCHIVE_KEY = "workout:v2:ron";
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
    if (prog.kind === "sequence") {
      return { version: 3, person: id, programId: prog.programId,
        settings: { startDate: prog.startDate, trainingDays: (prog.defaultTrainingDays || [0, 2, 5]).slice() }, sessions: {} };
    }
    return { version: 2, person: id, settings: { startDate: prog.startDate, level: 0 }, sessions: {} };
  }
  function normalizeStore(id, raw) {
    if (programs[id].kind === "sequence") return normalizeSeqStore(id, raw);
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
      if (!legacy || localStorage.getItem(RON_ARCHIVE_KEY)) return false;
      const old = JSON.parse(legacy);
      const settings = Object.assign({}, old.settings || {});
      if (settings.level == null && settings.calfLevel != null) settings.level = Number(settings.calfLevel) || 0;
      const s = { version: 2, person: "ron", settings, sessions: old.sessions || {} };
      s.migratedFrom = LEGACY_KEY;
      s.migratedAt = new Date().toISOString();
      localStorage.setItem(RON_ARCHIVE_KEY, JSON.stringify(s));
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
    if (prog.kind === "sequence") return Object.assign(out, prog.library);
    prog.levelSystem.levels.forEach((l) => l.exercises.forEach((e) => (out[e.id] = e)));
    Object.values(prog.blocks).forEach((b) => Object.values(b.bands).forEach((exs) => exs.forEach((e) => (out[e.id] = e))));
    Object.values(prog.lists).forEach((l) => l.exercises.forEach((e) => (out[e.id] = e)));
    return out;
  }

  // ---------- session logs ----------
  function emptyLog(date) {
    if (isSeq()) return emptySeqLog(date);
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
    if (!r) { r = { id, done: false, weight: "", repsOrHold: "", pain: "", note: "" }; log.exercises.push(r); }
    return r;
  }
  function isTouched(s) {
    if (!s) return false;
    if (s.completed || s.sessionNote) return true;
    if ((s.exercises || []).some((e) => e.done || e.weight || e.repsOrHold || e.note || (e.pain !== "" && e.pain != null))) return true;
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
    const pickBtn = $('.nav button[data-view="pick"]');
    if (pickBtn) pickBtn.innerHTML = isSeq() ? '<span aria-hidden="true">▦</span>Plan' : '<span aria-hidden="true">☰</span>Days';
    const todayBtn = $('.nav button[data-view="today"]');
    if (todayBtn) todayBtn.innerHTML = isSeq() ? '<span aria-hidden="true">●</span>Next' : '<span aria-hidden="true">●</span>Today';
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
    if (isSeq()) return t;
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
    if (isSeq()) ({ today: renderSeqToday, pick: renderSeqPlan, progress: renderSeqProgress, settings: renderSeqSettings })[name]();
    else ({ today: renderToday, pick: renderPicker, progress: renderProgress, settings: renderSettings })[name]();
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
    if (isSeq()) { renderSeqToday(); return; }
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
      mutateLog(date, (log) => {
        log.sessionNote = note.value;
        log.completed = !log.completed;
        if (isSeq()) log.completedOn = log.completed ? todayISO() : null;
      });
      if (isSeq()) { afterSeqToggle(date); return; }
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
    const arch = ids.includes("ron") ? readRonArchive() : null;
    if (arch) data.archives = { ron_8week_2026: arch };
    downloadBlob(new Blob([JSON.stringify(data, null, 2)], { type: "application/json" }), `workout-${fileTag(ids)}-${todayISO()}.json`);
    toast(`JSON downloaded (${ids.map(personLabel).join(" + ")})`);
  }
  function exportCSV(ids) {
    const painKeys = [];
    ids.forEach((id) => programs[id].pain.fields.forEach((f) => painKeys.includes(f.key) || painKeys.push(f.key)));
    const rows = [["person", "session", "date", "completed", ...painKeys, "rpe", "session_note", "exercise_id", "exercise_name", "exercise_done", "weight", "reps_or_hold", "exercise_pain", "note"]];
    for (const id of ids) {
      const names = allProgramExercises(programs[id]);
      const sess = stores[id].sessions;
      const seq = programs[id].kind === "sequence";
      for (const d of Object.keys(sess).sort()) {
        const s = sess[d];
        const base = [id, d, seq ? (s.completedOn || "") : d, !!s.completed, ...painKeys.map((k) => s[k] ?? ""), s.rpe ?? "", csvEscape(s.sessionNote)];
        const exs = s.exercises || [];
        if (!exs.length) rows.push([...base, "", "", "", "", "", "", ""]);
        exs.forEach((e) => rows.push([...base, e.id, csvEscape(names[e.id]?.name || ""), !!e.done, csvEscape(e.weight), csvEscape(e.repsOrHold), e.pain ?? "", csvEscape(e.note)]));
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
        const parsed = JSON.parse(String(reader.result));
        const found = parseBackup(parsed);
        const parsedArchives = parsed && parsed.archives;
        const ids = Object.keys(found);
        const summary = ids.map((id) => `${personLabel(id)} (${Object.keys(found[id].sessions || {}).length} entries)`).join(" + ");
        if (!confirm(`Restore ${summary}? This REPLACES the current data for ${ids.map(personLabel).join(" and ")} on this device.`)) return;
        ids.forEach((id) => {
          const raw = found[id];
          if (programs[id].kind === "sequence" && raw && raw.programId !== programs[id].programId) {
            localStorage.setItem(RON_ARCHIVE_KEY, JSON.stringify(raw)); // old dated plan: keep as archive
            return;
          }
          stores[id] = normalizeStore(id, raw);
          saveStore(id);
        });
        if (parsedArchives && parsedArchives.ron_8week_2026 && !localStorage.getItem(RON_ARCHIVE_KEY)) {
          localStorage.setItem(RON_ARCHIVE_KEY, JSON.stringify(parsedArchives.ron_8week_2026));
        }
        toast(`Imported ${ids.map(personLabel).join(" + ")}`);
        showView(currentView);
      } catch (e) {
        alert("Import failed: " + e.message);
      }
    };
    reader.readAsText(file);
    ev.target.value = "";
  }

  // ======================================================================
  // Sequence programs (Ron's Pickleball & Golf Year): numbered workouts,
  // not tied to dates. Dates are projected from the next unfinished workout.
  // ======================================================================
  const DOW = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
  const TYPE_COLORS = { legs: "#0d6e4f", sport: "#c45c26", upper: "#2563eb" };
  let seqView = null;          // workout id being viewed; null = the next unfinished one
  let planTab = "upcoming";    // upcoming | month | quarter | phases
  let planMonth = null;        // "YYYY-MM-01" shown in the month views

  function isSeq(id) { const p = programs[id || person]; return !!(p && p.kind === "sequence"); }
  function normalizeSeqStore(id, raw) {
    const prog = programs[id];
    const s = raw && typeof raw === "object" ? raw : {};
    const d = defaultStore(id);
    s.version = 3;
    s.person = id;
    s.programId = prog.programId;
    s.settings = Object.assign({}, d.settings, s.settings || {});
    let days = Array.isArray(s.settings.trainingDays) ? s.settings.trainingDays.map(Number).filter((n) => n >= 0 && n <= 6) : [];
    if (!days.length) days = d.settings.trainingDays.slice();
    s.settings.trainingDays = [...new Set(days)].sort((a, b) => a - b);
    if (!/^\d{4}-\d{2}-\d{2}$/.test(String(s.settings.startDate || ""))) s.settings.startDate = prog.startDate;
    if (!s.sessions || typeof s.sessions !== "object") s.sessions = {};
    return s;
  }
  function emptySeqLog(wid) {
    const pain = {};
    P().pain.fields.forEach((f) => (pain[f.key] = null));
    return Object.assign({ workout: wid, completed: false, completedOn: null, rpe: null, sessionNote: "", exercises: [] }, pain);
  }
  function readRonArchive() {
    try { const raw = localStorage.getItem(RON_ARCHIVE_KEY); return raw ? JSON.parse(raw) : null; } catch (e) { return null; }
  }
  const seqWorkouts = () => P().workouts;
  const workoutById = (wid) => P().workouts.find((w) => w.id === wid) || null;
  const isDone = (wid) => !!(S().sessions[wid] && S().sessions[wid].completed);
  const phaseByKey = (k) => P().phases.find((p) => p.key === k);
  const weekInfo = (n) => P().weeks[n - 1];
  function nextWorkout() { return seqWorkouts().find((w) => !isDone(w.id)) || null; }
  function trainingDays() { return (S().settings.trainingDays && S().settings.trainingDays.length) ? S().settings.trainingDays : [0, 2, 5]; }
  function daysLabel(days) { return days.map((d) => DOW[d]).join(", "); }

  /** wid -> {date, projected}. Finished workouts sit on the day they were done; unfinished ones are
   *  laid onto the next training days (Settings), one per day, starting today (tomorrow if one was
   *  already finished today) and never before the plan start date. */
  function seqProjection() {
    const st = S(), out = {};
    const t = todayISO();
    let doneToday = false;
    for (const w of seqWorkouts()) {
      const s = st.sessions[w.id];
      if (s && s.completed) {
        out[w.id] = { date: s.completedOn || t, projected: false };
        if ((s.completedOn || t) === t) doneToday = true;
      }
    }
    const days = new Set(trainingDays());
    let cur = t < st.settings.startDate ? st.settings.startDate : (doneToday ? shiftDate(t, 1) : t);
    let guard = 0;
    for (const w of seqWorkouts()) {
      if (out[w.id]) continue;
      while (!days.has(parseISO(cur).getDay()) && guard++ < 4000) cur = shiftDate(cur, 1);
      out[w.id] = { date: cur, projected: true };
      cur = shiftDate(cur, 1);
    }
    return out;
  }
  function byDate(proj) {
    const m = {};
    for (const w of seqWorkouts()) { const p = proj[w.id]; (m[p.date] = m[p.date] || []).push(w); }
    return m;
  }
  function shortNice(iso) { return parseISO(iso).toLocaleDateString("en-US", { weekday: "short", month: "short", day: "numeric" }); }
  function weekContext(w) {
    const ph = phaseByKey(w.phase), wk = weekInfo(w.week);
    return { ph, wk, text: `${ph.name} · week ${wk.weekInPhase} of ${wk.phaseWeeks}` };
  }
  function prescription(it) {
    const s = it.sets;
    let amt;
    if (it.reps) amt = s > 1 ? `${s} sets of ${it.reps}` : (/^\d+$/.test(it.reps) ? `${it.reps} reps` : `${it.reps}`);
    else if (it.hold) amt = s > 1 ? `${s} holds of ${it.hold}` : `1 hold of ${it.hold}`;
    else if (it.minutes) amt = `about ${it.minutes} minutes`;
    else amt = `${s} round${s > 1 ? "s" : ""}`;
    return [amt, it.side, it.tempo, it.load].filter(Boolean).join(" · ");
  }
  function painSelect(id, val) {
    const opts = ['<option value="">—</option>'].concat(Array.from({ length: 11 }, (_, i) => `<option value="${i}" ${String(val) === String(i) ? "selected" : ""}>${i}</option>`));
    return `<select data-field="pain" data-id="${escapeAttr(id)}" aria-label="Pain 0 to 10">${opts.join("")}</select>`;
  }
  function seqExerciseHtml(it, le) {
    const e = P().library[it.id] || { name: it.id, how: "" };
    const chips = [
      e.optional ? `<span class="chip">optional${e.where ? " · " + escapeHtml(e.where) : ""}</span>` : "",
      e.area === "Retest" ? '<span class="chip warn">retest</span>' : "",
    ].join(" ");
    const extra = [it.effort ? `Effort: ${it.effort}.` : "", it.notes || ""].filter(Boolean).join(" ");
    return `<div class="exercise ${le.done ? "done" : ""}" data-ex="${escapeAttr(it.id)}">
      <button type="button" class="check ${le.done ? "on" : ""}" data-toggle="${escapeAttr(it.id)}" aria-label="Mark ${escapeAttr(e.name)} done">${le.done ? "✓" : ""}</button>
      <div>
        <p class="ex-name">${escapeHtml(e.name)} ${chips}</p>
        <p class="ex-rx">${escapeHtml(prescription(it))}</p>
        ${extra ? `<p class="ex-meta">${escapeHtml(extra)}</p>` : ""}
        <div class="ex-links">${e.demo ? `<a class="demo" href="${escapeAttr(e.demo)}" target="_blank" rel="noopener">▶ Demo video</a>` : ""}</div>
        <details class="howto"><summary>How to do it${e.easier ? ", easier option" : ""}${e.swap ? ", swap" : ""}</summary>
          <p>${escapeHtml(e.how)}</p>
          ${e.easier ? `<p><strong>Easier:</strong> ${escapeHtml(e.easier)}</p>` : ""}
          ${e.swap ? `<p><strong>Swap:</strong> ${escapeHtml(e.swap)}</p>` : ""}
        </details>
        ${["Warm-up", "Cool-down"].includes(e.area) ? "" : `<div class="ex-fields three">
          <div><label class="field">Weight / load</label>
            <input type="text" data-field="weight" data-id="${escapeAttr(it.id)}" value="${escapeAttr(le.weight)}" placeholder="e.g. 20"></div>
          <div><label class="field">Reps / hold</label>
            <input type="text" data-field="repsOrHold" data-id="${escapeAttr(it.id)}" value="${escapeAttr(le.repsOrHold)}" placeholder="${it.hold ? "sec" : "reps"}"></div>
          <div><label class="field">Pain 0–10</label>${painSelect(it.id, le.pain)}</div>
          <div class="full"><label class="field">Note</label>
            <input type="text" data-field="note" data-id="${escapeAttr(it.id)}" value="${escapeAttr(le.note)}" placeholder="optional"></div>
        </div>`}
      </div>
    </div>`;
  }

  // ---------- sequence: next workout ----------
  function renderSeqToday() {
    const root = $("#view-today");
    const prog = P(), all = seqWorkouts();
    const next = nextWorkout();
    if (seqView && !workoutById(seqView)) seqView = null;
    const w = seqView ? workoutById(seqView) : next;
    if (!w) {
      root.innerHTML = `<div class="card rest-day"><div class="big">🏆</div><h2>All ${all.length} workouts done</h2>
        <p class="muted">That's the full Pickleball & Golf Year. Time to retest and start the next cycle. Ask Arnold for next year's plan.</p>
        <button class="btn primary block" type="button" data-goto="pick">See the plan</button></div>`;
      $("[data-goto=pick]").onclick = () => showView("pick");
      return;
    }
    const proj = seqProjection();
    const log = getLog(w.id);
    const ctx = weekContext(w);
    const isNext = next && w.id === next.id;
    const when = proj[w.id];
    const whenText = !when ? "" : when.projected
      ? (when.date === todayISO() ? "Projected for today" : `Projected for ${shortNice(when.date)}`)
      : `Done ${formatNice(when.date)}`;
    const dt = prog.dayTypes[w.type];
    let html = `<div class="card">
      <div class="row" style="margin-bottom:8px">
        <button class="btn" type="button" id="prev-day" aria-label="Previous workout" ${w.num === 1 ? "disabled" : ""}>‹</button>
        <div style="text-align:center;flex:2">
          <div class="muted" style="font-weight:700">${isNext ? "Your next workout" : isDone(w.id) ? "Finished workout" : "Looking ahead"}</div>
          <div style="font-weight:800;font-size:1.15rem">Workout ${w.num} <span class="muted">of ${all.length}</span></div>
        </div>
        <button class="btn" type="button" id="next-day" aria-label="Next workout" ${w.num === all.length ? "disabled" : ""}>›</button>
      </div>
      <h2 style="margin:4px 0 6px">${escapeHtml(w.title)}</h2>
      <div class="session-meta">
        <span class="chip accent">${escapeHtml(ctx.ph.name)}</span>
        <span class="chip">Week ${ctx.wk.weekInPhase} of ${ctx.wk.phaseWeeks}</span>
        <span class="chip ${w.retest ? "warn" : w.recovery ? "rec" : ""}">${escapeHtml(w.tag)}</span>
        <span class="chip">about ${w.minutes} min</span>
      </div>
      <p class="muted" style="margin:6px 0 0">${escapeHtml(whenText)}${when && when.projected ? " · dates move with you" : ""}</p>
      ${ctx.wk.note ? `<p class="muted" style="margin:4px 0 0">🎄 ${escapeHtml(ctx.wk.note)}</p>` : ""}
      <p class="muted" style="margin:4px 0 0">${escapeHtml(dt.why)}</p>
      ${!isNext && next ? `<button class="btn small block" type="button" id="go-next" style="margin-top:8px">Back to my next workout (#${next.num})</button>` : ""}
    </div>`;
    const tmr = parseISO(shiftDate(todayISO(), 1)).getDay();
    if (isNext && w.type === "legs" && (tmr === 1 || tmr === 4) && all[w.num]) {
      html += `<div class="banner-tip">Pickleball tomorrow? You can do workout ${w.num + 1} (${escapeHtml(prog.dayTypes[all[w.num].type].short)}) today instead; this one stays next until you do it.
        <button class="btn small" type="button" id="swap-next">Open workout ${w.num + 1}</button></div>`;
    }
    html += `<div class="banner-warn">${escapeHtml(prog.banner)}</div>`;
    for (const sec of w.sections) {
      html += `<div class="card"><h3>${escapeHtml(sec.title)}</h3>`;
      for (const it of sec.items) html += seqExerciseHtml(it, exRow(log, it.id) || { done: false, weight: "", repsOrHold: "", pain: "", note: "" });
      html += `</div>`;
    }
    html += `<div class="card"><h2>How did it go?</h2>
      <p class="muted" style="margin-top:0">Pain 0 to 10. Up to ${prog.pain.ceiling} that settles by the next morning is OK. Fill in the next-morning number tomorrow.</p>`;
    for (const f of prog.pain.fields) html += sliderHtml(f.key, f.label, log[f.key], 0, 10, f.when === "morning" ? "tomorrow" : "");
    html += sliderHtml("rpe", "How hard was the whole workout? (1 very easy, 10 all-out)", log.rpe, 1, 10, "");
    html += `<label class="field">Notes</label>
      <textarea id="session-note" placeholder="Where did you train? Pickleball or golf this week? Anything feel off?">${escapeHtml(log.sessionNote || "")}</textarea>
      <div style="height:10px"></div>
      <button class="btn primary block" type="button" id="mark-complete">${log.completed ? "✓ Workout done — tap to undo" : "Mark workout done"}</button>
      <p class="muted" style="text-align:center;margin-bottom:0">Entries save automatically on this phone. No reminders, ever: the next workout simply waits here.</p>
    </div>`;
    root.innerHTML = html;
    $("#prev-day").onclick = () => { seqView = all[w.num - 2].id; renderSeqToday(); window.scrollTo(0, 0); };
    $("#next-day").onclick = () => { seqView = all[w.num].id; renderSeqToday(); window.scrollTo(0, 0); };
    const gn = $("#go-next"); if (gn) gn.onclick = () => { seqView = null; renderSeqToday(); window.scrollTo(0, 0); };
    const sw = $("#swap-next"); if (sw) sw.onclick = () => { seqView = all[w.num].id; renderSeqToday(); window.scrollTo(0, 0); };
    bindSession(w.id);
  }
  function afterSeqToggle(wid) {
    const w = workoutById(wid);
    if (getLog(wid).completed) {
      const nx = nextWorkout();
      seqView = null;
      toast(nx ? `Workout ${w.num} done. Workout ${nx.num} is ready.` : "Every workout done!");
    } else {
      toast(`Workout ${w.num} marked not done`);
    }
    renderSeqToday();
    window.scrollTo(0, 0);
  }
  function openWorkout(wid) { seqView = (nextWorkout() && nextWorkout().id === wid) ? null : wid; showView("today"); }

  // ---------- sequence: plan views ----------
  function monthStart(iso) { return iso.slice(0, 8) + "01"; }
  function addMonths(first, n) { const d = parseISO(first); d.setMonth(d.getMonth() + n); return isoOf(d); }
  function monthGrid(first, bd, compact) {
    const d0 = parseISO(first);
    const label = d0.toLocaleDateString("en-US", { month: "long", year: "numeric" });
    const lead = d0.getDay();
    const dim = new Date(d0.getFullYear(), d0.getMonth() + 1, 0).getDate();
    const t = todayISO();
    let cells = DOW.map((d) => `<div class="cal-dow">${d.slice(0, compact ? 1 : 3)}</div>`).join("");
    for (let i = 0; i < lead; i++) cells += `<div class="cal-cell empty"></div>`;
    for (let day = 1; day <= dim; day++) {
      const iso = `${first.slice(0, 8)}${String(day).padStart(2, "0")}`;
      const ws = bd[iso] || [];
      const inner = ws.map((w) => {
        const done = isDone(w.id);
        const lbl = compact ? `${w.num}` : `#${w.num} ${P().dayTypes[w.type].short}`;
        return `<button type="button" class="cal-w ${done ? "done" : "proj"} ${w.recovery ? "rec" : ""}" style="--c:${TYPE_COLORS[w.type]}" data-open="${w.id}" title="Workout ${w.num}: ${escapeAttr(w.title)}">${done ? "✓" : ""}${lbl}</button>`;
      }).join("");
      cells += `<div class="cal-cell ${iso === t ? "today" : ""}"><span class="cal-day">${day}</span>${inner}</div>`;
    }
    return `<div class="cal ${compact ? "compact" : ""}"><div class="cal-title">${escapeHtml(label)}</div><div class="cal-grid">${cells}</div></div>`;
  }
  function legendHtml() {
    return `<div class="legend">${Object.entries(P().dayTypes).map(([k, v]) => `<span><i style="background:${TYPE_COLORS[k]}"></i>${escapeHtml(v.short)}</span>`).join("")}
      <span><i class="dash" style="border-color:#5c5c5c"></i>projected</span><span>✓ done</span><span><i style="background:#e8e2d6"></i>recovery week = lighter</span></div>`;
  }
  function renderSeqPlan() {
    const root = $("#view-pick");
    const prog = P(), st = S();
    const proj = seqProjection(), bd = byDate(proj);
    const next = nextWorkout();
    if (!planMonth) planMonth = monthStart(next ? proj[next.id].date : todayISO());
    const tabs = [["upcoming", "Upcoming"], ["month", "Month"], ["quarter", "3 months"], ["phases", "Phases"]];
    let html = `<div class="card"><h2>${escapeHtml(prog.title)}</h2>
      <p class="muted" style="margin:0 0 8px">${seqWorkouts().filter((w) => isDone(w.id)).length} of ${seqWorkouts().length} workouts done. Dates are <strong>projected</strong> at ${trainingDays().length} a week on ${escapeHtml(daysLabel(trainingDays()))} (change in Settings) and move automatically whenever you finish one early or late.</p>
      <div class="tabs" role="tablist">${tabs.map(([k, l]) => `<button type="button" role="tab" class="tab ${planTab === k ? "on" : ""}" data-tab="${k}" aria-selected="${planTab === k}">${l}</button>`).join("")}</div></div>`;
    if (planTab === "upcoming") {
      const up = seqWorkouts().filter((w) => !isDone(w.id)).slice(0, 24);
      html += `<div class="card"><h3>Coming up, by day</h3>`;
      if (!up.length) html += `<p class="empty">Nothing left. Every workout is done.</p>`;
      let lastPhase = null;
      for (const w of up) {
        const p = proj[w.id], ctx = weekContext(w);
        if (w.phase !== lastPhase) { html += `<div class="phase-divider">${escapeHtml(ctx.ph.name)}</div>`; lastPhase = w.phase; }
        html += `<button type="button" class="btn block up-row" data-open="${w.id}" style="--c:${TYPE_COLORS[w.type]}">
          <span class="up-date"><strong>${escapeHtml(shortNice(p.date))}</strong><br><span class="muted">projected</span></span>
          <span class="up-main"><strong>#${w.num} ${escapeHtml(prog.dayTypes[w.type].short)}</strong>${next && w.id === next.id ? ' <span class="chip accent">next</span>' : ""}<br>
          <span class="muted">Week ${ctx.wk.weekInPhase} of ${ctx.wk.phaseWeeks} · ${escapeHtml(w.tag)} · about ${w.minutes} min</span></span></button>`;
      }
      const recent = seqWorkouts().filter((w) => isDone(w.id)).sort((a, b) => (proj[b.id].date + b.num).localeCompare(proj[a.id].date + a.num)).slice(0, 5);
      if (recent.length) {
        html += `<h3>Recently done</h3>`;
        for (const w of recent) html += `<button type="button" class="btn block up-row done" data-open="${w.id}" style="--c:${TYPE_COLORS[w.type]}">
          <span class="up-date"><strong>${escapeHtml(shortNice(proj[w.id].date))}</strong></span><span class="up-main">✓ #${w.num} ${escapeHtml(prog.dayTypes[w.type].short)}</span></button>`;
      }
      html += `</div>`;
    } else if (planTab === "month" || planTab === "quarter") {
      const n = planTab === "month" ? 1 : 3;
      html += `<div class="card"><div class="row" style="margin-bottom:6px">
          <button class="btn small" type="button" id="cal-prev" aria-label="Earlier">‹ Earlier</button>
          <button class="btn small" type="button" id="cal-now">This month</button>
          <button class="btn small" type="button" id="cal-next" aria-label="Later">Later ›</button></div>
          ${legendHtml()}`;
      for (let i = 0; i < n; i++) {
        const m = addMonths(planMonth, i);
        html += monthGrid(m, bd, n > 1);
        const inMonth = seqWorkouts().filter((w) => proj[w.id].date.slice(0, 7) === m.slice(0, 7));
        const phs = [...new Set(inMonth.map((w) => phaseByKey(w.phase).name))];
        if (phs.length) html += `<p class="muted cal-note">${inMonth.length} workouts · ${escapeHtml(phs.join(" → "))}</p>`;
      }
      html += `<p class="muted">Tap a workout to open it.</p></div>`;
    } else {
      const totalWeeks = prog.weeks.length;
      const cur = next ? next.phase : null;
      html += `<div class="card"><h3>The whole year</h3><div class="timeline">${prog.phases.map((p) => {
        const wks = p.weeks[1] - p.weeks[0] + 1;
        return `<div class="tl-seg ${p.key === cur ? "on" : ""}" style="flex:${wks}" title="${escapeAttr(p.name)}">${escapeHtml(p.name.split(/[:(]/)[0].trim())}</div>`;
      }).join("")}</div><p class="muted" style="margin:6px 0 0">${totalWeeks} weeks · planned Mon Nov 30, 2026 to Sun Aug 29, 2027, then start over.</p></div>`;
      for (const p of prog.phases) {
        const ws = seqWorkouts().filter((w) => w.phase === p.key);
        const done = ws.filter((w) => isDone(w.id)).length;
        const a = proj[ws[0].id].date, b = proj[ws[ws.length - 1].id].date;
        const pct = Math.round((100 * done) / ws.length);
        html += `<div class="card phase-card ${p.key === cur ? "current" : ""}">
          <h2>${escapeHtml(p.name)} ${p.key === cur ? '<span class="chip accent">you are here</span>' : ""}</h2>
          <p class="muted" style="margin:0">Weeks ${p.weeks[0]} to ${p.weeks[1]} · workouts ${p.workouts[0]} to ${p.workouts[1]} · ${escapeHtml(p.minutes)}</p>
          <p style="margin:6px 0"><strong>Planned:</strong> ${escapeHtml(shortNice(p.start))} to ${escapeHtml(shortNice(p.end))}<br>
            <strong>At your pace:</strong> ${escapeHtml(shortNice(a))} to ${escapeHtml(shortNice(b))}</p>
          <div class="bar"><i style="width:${pct}%"></i></div><p class="muted" style="margin:2px 0 8px">${done} of ${ws.length} done</p>
          <p style="margin:0 0 6px">${escapeHtml(p.goal)}</p>
          <p class="muted" style="margin:0 0 4px"><strong>Effort:</strong> ${escapeHtml(p.effort)}</p>
          <p class="muted" style="margin:0 0 4px"><strong>Shoulder Reliever:</strong> ${escapeHtml(p.ball)}</p>
          <p class="muted" style="margin:0">Recovery weeks: ${p.recoveryWeeks.join(", ") || "none"}${p.retestWeeks.length ? ` · retest in week ${p.retestWeeks.join(", ")}` : ""}</p>
          <button class="btn small" type="button" data-open="${ws.find((w) => !isDone(w.id))?.id || ws[0].id}" style="margin-top:8px">Open ${done < ws.length ? "next" : "first"} workout in this phase</button>
        </div>`;
      }
    }
    root.innerHTML = html;
    $all("[data-tab]").forEach((b) => (b.onclick = () => { planTab = b.getAttribute("data-tab"); renderSeqPlan(); }));
    $all("[data-open]").forEach((b) => (b.onclick = () => openWorkout(b.getAttribute("data-open"))));
    const step = planTab === "quarter" ? 3 : 1;
    const cp = $("#cal-prev"); if (cp) cp.onclick = () => { planMonth = addMonths(planMonth, -step); renderSeqPlan(); };
    const cn = $("#cal-next"); if (cn) cn.onclick = () => { planMonth = addMonths(planMonth, step); renderSeqPlan(); };
    const cw = $("#cal-now"); if (cw) cw.onclick = () => { planMonth = monthStart(todayISO()); renderSeqPlan(); };
  }

  // ---------- sequence: progress ----------
  function renderSeqProgress() {
    const root = $("#view-progress");
    const prog = P(), st = S();
    const proj = seqProjection();
    const doneW = seqWorkouts().filter((w) => isDone(w.id)).sort((a, b) => (proj[a.id].date + String(a.num).padStart(3, "0")).localeCompare(proj[b.id].date + String(b.num).padStart(3, "0")));
    const t = todayISO();
    const mon = shiftDate(t, -((parseISO(t).getDay() + 6) % 7));
    const thisWeek = doneW.filter((w) => proj[w.id].date >= mon).length;
    const next = nextWorkout();
    let html = `<div class="card"><h2>Ron — progress</h2><div class="stat-grid">
        <div class="stat"><div class="num">${doneW.length}<span class="of">/${seqWorkouts().length}</span></div><div class="lbl">Workouts done</div></div>
        <div class="stat"><div class="num">${thisWeek}<span class="of">/3</span></div><div class="lbl">This week (Mon–Sun)</div></div>
      </div><p class="muted" style="margin:8px 0 0">${next ? `Next: workout ${next.num}, ${escapeHtml(phaseByKey(next.phase).name)}.` : "All done."}</p></div>
      <div class="card"><h2>By phase</h2>${prog.phases.map((p) => {
        const ws = seqWorkouts().filter((w) => w.phase === p.key), d = ws.filter((w) => isDone(w.id)).length;
        return `<p style="margin:6px 0 2px"><strong>${escapeHtml(p.name)}</strong> <span class="muted">${d}/${ws.length}</span></p><div class="bar"><i style="width:${Math.round((100 * d) / ws.length)}%"></i></div>`;
      }).join("")}</div>`;
    const logged = seqWorkouts().filter((w) => isTouched(st.sessions[w.id]));
    const labels = logged.map((w) => `#${w.num}`);
    html += `<div class="card"><h2>Pain trend</h2><div class="legend">${prog.pain.fields.map((f) => `<span><i style="background:${f.color}"></i>${escapeHtml(f.short)}</span>`).join("")}
        <span><i class="dash" style="border-color:#b91c1c"></i>OK up to ${prog.pain.ceiling}</span></div>
      <div class="chart-wrap">${svgMultiLine(labels, prog.pain.fields.map((f) => ({ color: f.color, values: logged.map((w) => st.sessions[w.id][f.key] ?? null) })), prog.pain.ceiling, null)}</div></div>`;
    const counts = {};
    Object.values(st.sessions).forEach((s) => (s.exercises || []).forEach((e) => { if (parseLoad(e.weight) != null) counts[e.id] = (counts[e.id] || 0) + 1; }));
    const opts = Object.values(prog.library).filter((e) => e.area !== "Retest").map((e) => ({ id: e.id, name: e.name, n: counts[e.id] || 0 }))
      .sort((a, b) => b.n - a.n || a.name.localeCompare(b.name));
    html += `<div class="card"><h2>Weight over time</h2><label class="field">Exercise</label>
      <select id="load-ex">${opts.map((o) => `<option value="${escapeAttr(o.id)}">${escapeHtml(o.name)}${o.n ? ` (${o.n})` : ""}</option>`).join("")}</select>
      <div class="chart-wrap" id="load-chart"></div><p class="muted" id="load-hint"></p></div>`;
    const tests = seqWorkouts().filter((w) => w.retest);
    html += `<div class="card"><h2>Retests</h2>${tests.map((w) => {
      const s = st.sessions[w.id];
      const vals = (s && s.exercises || []).filter((e) => e.repsOrHold || e.weight || e.note).map((e) => `${escapeHtml(prog.library[e.id]?.name.replace(/^Test: /, "") || e.id)}: ${escapeHtml([e.repsOrHold, e.weight, e.note].filter(Boolean).join(", "))}`);
      return `<button type="button" class="btn block recent" data-open="${w.id}"><span>#${w.num} · ${escapeHtml(phaseByKey(w.phase).name)}</span><span class="right">${isDone(w.id) ? "✓" : "—"}</span></button>${vals.length ? `<ul class="notes">${vals.map((v) => `<li>${v}</li>`).join("")}</ul>` : ""}`;
    }).join("")}</div>`;
    root.innerHTML = html;
    const drawLoad = (id) => {
      const pts = doneW.concat(seqWorkouts().filter((w) => !isDone(w.id))).filter((w) => parseLoad(exRow(st.sessions[w.id] || { exercises: [] }, id)?.weight) != null);
      $("#load-chart").innerHTML = svgLineChart(pts.map((w) => `#${w.num}`), pts.map((w) => parseLoad(exRow(st.sessions[w.id], id).weight)), getComputedStyle(document.body).getPropertyValue("--accent").trim() || "#0d6e4f");
      $("#load-hint").textContent = pts.length ? "" : "Log a weight on this exercise to see a trend.";
    };
    $("#load-ex").onchange = (e) => drawLoad(e.target.value);
    if (opts[0]) drawLoad(opts[0].id);
    $all("[data-open]").forEach((b) => (b.onclick = () => openWorkout(b.getAttribute("data-open"))));
  }

  // ---------- sequence: settings ----------
  function renderSeqSettings() {
    const root = $("#view-settings");
    const prog = P(), st = S();
    const name = personLabel(person);
    const other = PEOPLE.filter((p) => p.id !== person).map((p) => p.label).join(", ");
    const days = new Set(trainingDays());
    const arch = readRonArchive();
    const archCount = arch && arch.sessions ? Object.keys(arch.sessions).length : 0;
    root.innerHTML = `
      <div class="card settings-block">
        <h2>${escapeHtml(name)}'s settings</h2>
        <label class="field">Training days used to project dates (aim for 3)</label>
        <div class="dow-pick">${DOW.map((d, i) => `<label class="dow"><input type="checkbox" value="${i}" ${days.has(i) ? "checked" : ""}> ${d}</label>`).join("")}</div>
        <p class="muted">Only for the calendar and upcoming list. Workouts never lock to a day: whatever day you train, the next one is ready.</p>
        <label class="field">Plan start date</label>
        <input type="date" id="set-start" value="${escapeAttr(st.settings.startDate)}">
        <p class="muted">Projected dates never fall before this day. Default ${escapeHtml(shortNice(prog.startDate))}.</p>
        <button class="btn primary block" type="button" id="save-settings">Save settings</button>
        <p class="muted" style="margin-bottom:0">No reminders or notifications: this app never sends any.</p>
      </div>
      <div class="card settings-block">
        <h2>Backup</h2>
        <p class="muted">Logs live only on this phone. Export now and then, or to share with Arnold.</p>
        <div class="row"><button class="btn" type="button" data-export="json:one">Export ${escapeHtml(name)} JSON</button>
          <button class="btn" type="button" data-export="csv:one">Export ${escapeHtml(name)} CSV</button></div>
        <h3>Both people (Ron + Cindy)</h3>
        <div class="row"><button class="btn" type="button" data-export="json:all">Export BOTH JSON</button>
          <button class="btn" type="button" data-export="csv:all">Export BOTH CSV</button></div>
        <h3>Import JSON restore</h3>
        <p class="muted">Restores whoever is in the file. You'll confirm before anything is replaced. A backup of the old 8-week plan goes back into the archive below, not into this plan.</p>
        <input type="file" id="import-json" accept="application/json,.json">
      </div>
      <div class="card settings-block">
        <h2>Earlier 8-week plan (Sep to Dec 2026)</h2>
        <p class="muted">${archCount ? `${archCount} logged day${archCount === 1 ? "" : "s"} kept safely on this phone (separate from the new plan). It's included in the JSON export.` : "Nothing logged on this phone from the earlier plan."}</p>
        ${archCount ? `<button class="btn block" type="button" id="export-archive">Download the earlier plan's log (JSON)</button>` : ""}
      </div>
      <div class="card">
        <h2>About this plan</h2>
        <p class="muted">${escapeHtml(prog.conditions)}</p>
        <h3>How it works</h3>
        <ul class="notes">${prog.notes.map((n) => `<li>${escapeHtml(n)}</li>`).join("")}</ul>
        <h3>Red flags: stop and see your doctor or PT</h3>
        <ul class="notes">${prog.redFlags.map((n) => `<li>${escapeHtml(n)}</li>`).join("")}</ul>
        <h3>Sources</h3>
        <ul class="notes">${prog.sources.map((s) => `<li><a href="${escapeAttr(s.url)}" target="_blank" rel="noopener">${escapeHtml(s.text)}</a></li>`).join("")}</ul>
        <p class="muted">${escapeHtml(prog.disclaimer)}</p>
        <p class="muted">Data stays on this phone (separate for each person). Build ${APP_BUILD}.</p>
      </div>
      <div class="card"><button class="btn danger block" type="button" id="reset-data">Clear ${escapeHtml(name)}'s logs for this plan</button>
        <p class="muted" style="text-align:center;margin-bottom:0">${escapeHtml(other)}'s data and the earlier plan's archive are not affected.</p></div>`;

    $("#save-settings").onclick = () => {
      const picked = $all(".dow input").filter((c) => c.checked).map((c) => Number(c.value));
      if (!picked.length) { alert("Pick at least one training day."); return; }
      st.settings.trainingDays = picked;
      st.settings.startDate = $("#set-start").value || prog.startDate;
      saveStore();
      toast(`Saved. Dates projected on ${daysLabel(picked)}.`);
      renderSeqSettings();
    };
    $all("[data-export]").forEach((b) => {
      const [kind, scope] = b.getAttribute("data-export").split(":");
      const ids = scope === "all" ? PEOPLE.map((p) => p.id) : [person];
      b.onclick = () => (kind === "json" ? exportJSON(ids) : exportCSV(ids));
    });
    $("#import-json").onchange = importJSON;
    const ea = $("#export-archive");
    if (ea) ea.onclick = () => downloadBlob(new Blob([JSON.stringify({ app: BACKUP_APP, format: 2, build: APP_BUILD, exportedAt: new Date().toISOString(), people: { ron: arch } }, null, 2)], { type: "application/json" }), `workout-ron-8week-plan-${todayISO()}.json`);
    $("#reset-data").onclick = () => {
      if (confirm(`Clear all of ${name}'s logs for the ${prog.title} plan on this phone? Settings are kept. Export first if unsure.`)) {
        st.sessions = {};
        saveStore();
        seqView = null;
        toast(`${name}'s logs cleared`);
      }
    };
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
    build: APP_BUILD, getStore: (id) => stores[id || person], getProgram: (id) => programs[id || person], projection: () => seqProjection(),
    person: () => person, setPerson, showView, buildWorkout, setViewDate: (d) => { viewDate = d; showView("today"); },
  };

  init().catch((e) => {
    console.error(e);
    document.querySelector("main").innerHTML = `<div class="card"><h2>Failed to load</h2><p>${escapeHtml(e.message)}</p></div>`;
  });
})();

/* Ron Weaver — Workout Tracker (Arnold program) */
(function () {
  "use strict";

  const STORAGE_KEY = "ron-workout-v1";
  const DEFAULT_START = "2026-09-25";

  /** @type {any} */
  let PROGRAM = null;
  /** @type {ReturnType<typeof loadState>} */
  let state = null;
  let viewDate = todayISO();
  let currentView = "today";

  // ---------- helpers ----------
  function todayISO() {
    const d = new Date();
    const y = d.getFullYear();
    const m = String(d.getMonth() + 1).padStart(2, "0");
    const day = String(d.getDate()).padStart(2, "0");
    return `${y}-${m}-${day}`;
  }

  function parseISO(s) {
    const [y, m, d] = s.split("-").map(Number);
    return new Date(y, m - 1, d);
  }

  function formatNice(iso) {
    const d = parseISO(iso);
    return d.toLocaleDateString("en-US", {
      weekday: "short",
      month: "short",
      day: "numeric",
      year: "numeric",
    });
  }

  function weekBand(week) {
    if (week <= 2) return "1-2";
    if (week <= 4) return "3-4";
    if (week <= 6) return "5-6";
    return "7-8";
  }

  function $(sel, root) {
    return (root || document).querySelector(sel);
  }
  function $all(sel, root) {
    return Array.from((root || document).querySelectorAll(sel));
  }

  function toast(msg) {
    const el = $("#toast");
    el.textContent = msg;
    el.classList.add("show");
    clearTimeout(toast._t);
    toast._t = setTimeout(() => el.classList.remove("show"), 2200);
  }

  // ---------- state ----------
  function defaultState() {
    return {
      version: 1,
      settings: {
        startDate: DEFAULT_START,
        calfLevel: 0,
      },
      sessions: {}, // date -> session log
    };
  }

  function loadState() {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (!raw) return defaultState();
      const parsed = JSON.parse(raw);
      if (!parsed.settings) parsed.settings = defaultState().settings;
      if (!parsed.sessions) parsed.sessions = {};
      if (parsed.settings.calfLevel == null) parsed.settings.calfLevel = 0;
      if (!parsed.settings.startDate) parsed.settings.startDate = DEFAULT_START;
      return parsed;
    } catch (e) {
      console.warn("Bad localStorage, resetting", e);
      return defaultState();
    }
  }

  function saveState() {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
  }

  function emptySessionLog(date, exercises) {
    return {
      date,
      completed: false,
      painDuring: 0,
      painMorning: null,
      rpe: 5,
      sessionNote: "",
      exercises: exercises.map((e) => ({
        id: e.id,
        done: false,
        weight: "",
        repsOrHold: "",
        note: "",
      })),
    };
  }

  function getOrCreateSession(date, exercises) {
    if (!state.sessions[date]) {
      state.sessions[date] = emptySessionLog(date, exercises);
      saveState();
    } else {
      // merge any new exercise ids
      const log = state.sessions[date];
      const byId = Object.fromEntries((log.exercises || []).map((x) => [x.id, x]));
      log.exercises = exercises.map((e) => {
        if (byId[e.id]) return byId[e.id];
        return { id: e.id, done: false, weight: "", repsOrHold: "", note: "" };
      });
    }
    return state.sessions[date];
  }

  // ---------- program resolution ----------
  function scheduleFor(date) {
    return (PROGRAM.schedule || []).find((s) => s.date === date) || null;
  }

  function programWeekForDate(date) {
    const start = state.settings.startDate || PROGRAM.startDate || DEFAULT_START;
    const diff = Math.floor((parseISO(date) - parseISO(start)) / 86400000);
    if (diff < 0) return null;
    return Math.min(8, Math.floor(diff / 7) + 1);
  }

  function buildWorkout(date) {
    const sched = scheduleFor(date);
    const calfLevel = Number(state.settings.calfLevel) || 0;
    const calf = PROGRAM.calfLevels.find((l) => l.level === calfLevel) || PROGRAM.calfLevels[0];

    if (!sched) {
      const week = programWeekForDate(date);
      return {
        date,
        scheduled: false,
        week,
        type: "REST",
        label: "Rest / easy walking",
        sections: [],
        calf,
      };
    }

    const band = sched.weekBand || weekBand(sched.week);
    /** @type {{title:string, kind:string, exercises:any[]}[]} */
    const sections = [];

    if (sched.type === "R") {
      sections.push({
        title: "Week 8 Reassessment",
        kind: "reassessment",
        exercises: PROGRAM.reassessment,
      });
    } else if (sched.type === "C") {
      sections.push({
        title: `Optional / light — Calf Level ${calf.level}`,
        kind: "calf",
        exercises: calf.exercises.filter((e) => e.optional || e.id.includes("iso") || e.id.includes("arom") || e.id.includes("pump")).length
          ? calf.exercises.filter((e) => e.optional || /iso|arom|pump|walk/i.test(e.id + e.name))
          : PROGRAM.optionalConditioning,
      });
      sections.push({
        title: "Conditioning & mobility",
        kind: "conditioning",
        exercises: PROGRAM.optionalConditioning,
      });
    } else {
      sections.push({
        title: `Calf — Level ${calf.level}: ${calf.name}`,
        kind: "calf",
        exercises: calf.exercises,
      });
      if (sched.type === "H") {
        sections.push({
          title: `Hips / Glutes (Weeks ${band})`,
          kind: "hips",
          exercises: PROGRAM.hipsByWeek[band] || [],
        });
      } else if (sched.type === "S") {
        sections.push({
          title: `Shoulders / Upper (Weeks ${band})`,
          kind: "shoulders",
          exercises: PROGRAM.shouldersByWeek[band] || [],
        });
      }
    }

    return {
      date,
      scheduled: true,
      week: sched.week,
      type: sched.type,
      label: sched.label,
      day: sched.day,
      weekBand: band,
      sections,
      calf,
      typeName: PROGRAM.sessionTypes[sched.type] || sched.type,
    };
  }

  function flatExercises(workout) {
    const list = [];
    for (const s of workout.sections) {
      for (const e of s.exercises) list.push(e);
    }
    return list;
  }

  // ---------- rendering ----------
  function showView(name) {
    currentView = name;
    $all(".view").forEach((v) => v.classList.add("hidden"));
    $(`#view-${name}`).classList.remove("hidden");
    $all(".nav button").forEach((b) => {
      b.classList.toggle("active", b.dataset.view === name);
    });
    if (location.hash.replace(/^#/, "") !== name) {
      history.replaceState(null, "", "#" + name);
    }
    if (name === "today") renderToday();
    if (name === "progress") renderProgress();
    if (name === "settings") renderSettings();
    if (name === "pick") renderPicker();
  }

  function renderToday() {
    const root = $("#view-today");
    const workout = buildWorkout(viewDate);
    const exercises = flatExercises(workout);
    const log = exercises.length ? getOrCreateSession(viewDate, exercises) : null;
    const logById = log
      ? Object.fromEntries(log.exercises.map((x) => [x.id, x]))
      : {};

    const isToday = viewDate === todayISO();
    let html = "";

    html += `<div class="card">
      <div class="row" style="margin-bottom:8px">
        <button class="btn" type="button" id="prev-day" aria-label="Previous day">‹</button>
        <div style="text-align:center;flex:2">
          <div style="font-weight:800;font-size:1.1rem">${formatNice(viewDate)}</div>
          <div class="muted">${isToday ? "Today" : "Browsing"} · Start ${state.settings.startDate}</div>
        </div>
        <button class="btn" type="button" id="next-day" aria-label="Next day">›</button>
      </div>
      <div class="session-meta">
        ${
          workout.scheduled
            ? `<span class="chip accent">Week ${workout.week}</span>
               <span class="chip">${workout.type}</span>
               <span class="chip">Calf L${state.settings.calfLevel}</span>`
            : `<span class="chip">Rest day</span>`
        }
      </div>
      <p class="muted" style="margin:0">${
        workout.scheduled
          ? escapeHtml(workout.typeName || workout.label)
          : "No scheduled session. Easy walk / ROM is fine."
      }</p>
    </div>`;

    html += `<div class="banner-warn">
      Calf pain ceiling <strong>≤3/10</strong>. Stop for red flags (swelling/warmth, pop, night pain, hip instability, SOB).
    </div>`;

    if (!workout.scheduled || exercises.length === 0) {
      html += `<div class="card rest-day">
        <div class="big">😌</div>
        <h2>Rest / recovery</h2>
        <p class="muted">Skipped dates are rest or easy walking/ROM only.</p>
        <button class="btn primary block" type="button" data-goto="pick">Pick a training day</button>
      </div>`;
      root.innerHTML = html;
      bindTodayNav();
      return;
    }

    for (const section of workout.sections) {
      html += `<div class="card"><h3>${escapeHtml(section.title)}</h3>`;
      for (const e of section.exercises) {
        const le = logById[e.id] || { done: false, weight: "", repsOrHold: "", note: "" };
        const meta = [
          e.sets ? `${e.sets} sets` : null,
          e.reps ? `× ${e.reps}` : null,
          e.hold ? `hold ${e.hold}` : null,
          e.load ? e.load : null,
        ]
          .filter(Boolean)
          .join(" · ");
        html += `<div class="exercise ${le.done ? "done" : ""}" data-ex="${escapeAttr(e.id)}">
          <button type="button" class="check ${le.done ? "on" : ""}" data-toggle="${escapeAttr(e.id)}" aria-label="Mark complete">${le.done ? "✓" : ""}</button>
          <div>
            <p class="ex-name">${escapeHtml(e.name)}${e.optional ? ' <span class="chip">opt</span>' : ""}${e.hipDependent ? ' <span class="chip warn">hip*</span>' : ""}</p>
            <p class="ex-meta">${escapeHtml(meta)}${e.notes ? " — " + escapeHtml(e.notes) : ""}${e.cues ? " · Cue: " + escapeHtml(e.cues) : ""}</p>
            <div class="ex-fields">
              <div>
                <label class="field">Weight / load</label>
                <input type="text" inputmode="decimal" data-field="weight" data-id="${escapeAttr(e.id)}" value="${escapeAttr(le.weight)}" placeholder="e.g. 15 lb">
              </div>
              <div>
                <label class="field">Reps / hold</label>
                <input type="text" inputmode="text" data-field="repsOrHold" data-id="${escapeAttr(e.id)}" value="${escapeAttr(le.repsOrHold)}" placeholder="${e.hold ? "sec" : "reps"}">
              </div>
              <div class="full">
                <label class="field">Note</label>
                <input type="text" data-field="note" data-id="${escapeAttr(e.id)}" value="${escapeAttr(le.note)}" placeholder="optional">
              </div>
            </div>
          </div>
        </div>`;
      }
      html += `</div>`;
    }

    html += `<div class="card">
      <h2>Session check-in</h2>
      <label class="field">Calf pain during (0–10)</label>
      <div class="slider-row">
        <input type="range" min="0" max="10" step="1" id="pain-during" value="${log.painDuring ?? 0}">
        <span class="slider-val" id="pain-during-val">${log.painDuring ?? 0}</span>
      </div>
      <label class="field">Calf pain next morning (0–10) — fill tomorrow</label>
      <div class="slider-row">
        <input type="range" min="0" max="10" step="1" id="pain-morning" value="${log.painMorning ?? 0}">
        <span class="slider-val" id="pain-morning-val">${log.painMorning == null ? "—" : log.painMorning}</span>
      </div>
      <p class="muted" style="margin-top:0">Leave morning at 0 and unticked if not yet rated; use the toggle below.</p>
      <label class="row" style="margin:8px 0;gap:10px;align-items:center">
        <input type="checkbox" id="pain-morning-set" ${log.painMorning != null ? "checked" : ""} style="width:28px;height:28px">
        <span>I rated next-morning pain</span>
      </label>
      <label class="field">Session RPE (1–10)</label>
      <div class="slider-row">
        <input type="range" min="1" max="10" step="1" id="rpe" value="${log.rpe ?? 5}">
        <span class="slider-val" id="rpe-val">${log.rpe ?? 5}</span>
      </div>
      <label class="field">Session note</label>
      <textarea id="session-note" placeholder="How did it feel? Swelling?">${escapeHtml(log.sessionNote || "")}</textarea>
      <div style="height:10px"></div>
      <button class="btn primary block" type="button" id="save-session">Save session</button>
      <div style="height:8px"></div>
      <button class="btn block" type="button" id="mark-complete">${log.completed ? "✓ Session completed — tap to undo" : "Mark session complete"}</button>
    </div>`;

    root.innerHTML = html;
    bindTodayNav();
    bindSessionEditors(viewDate, exercises);
  }

  function bindTodayNav() {
    const prev = $("#prev-day");
    const next = $("#next-day");
    if (prev)
      prev.onclick = () => {
        viewDate = shiftDate(viewDate, -1);
        renderToday();
      };
    if (next)
      next.onclick = () => {
        viewDate = shiftDate(viewDate, 1);
        renderToday();
      };
    const goto = $("[data-goto=pick]");
    if (goto) goto.onclick = () => showView("pick");
  }

  function shiftDate(iso, days) {
    const d = parseISO(iso);
    d.setDate(d.getDate() + days);
    const y = d.getFullYear();
    const m = String(d.getMonth() + 1).padStart(2, "0");
    const day = String(d.getDate()).padStart(2, "0");
    return `${y}-${m}-${day}`;
  }

  function bindSessionEditors(date, exercises) {
    const log = getOrCreateSession(date, exercises);

    $all("[data-toggle]").forEach((btn) => {
      btn.onclick = () => {
        const id = btn.getAttribute("data-toggle");
        const row = log.exercises.find((x) => x.id === id);
        if (!row) return;
        row.done = !row.done;
        saveState();
        renderToday();
      };
    });

    $all("[data-field]").forEach((inp) => {
      inp.addEventListener("change", () => {
        const id = inp.getAttribute("data-id");
        const field = inp.getAttribute("data-field");
        const row = log.exercises.find((x) => x.id === id);
        if (!row) return;
        row[field] = inp.value;
        saveState();
      });
    });

    const pd = $("#pain-during");
    const pdv = $("#pain-during-val");
    const pm = $("#pain-morning");
    const pmv = $("#pain-morning-val");
    const pms = $("#pain-morning-set");
    const rpe = $("#rpe");
    const rpev = $("#rpe-val");

    if (pd) {
      pd.oninput = () => {
        pdv.textContent = pd.value;
        log.painDuring = Number(pd.value);
        saveState();
      };
    }
    function syncMorning() {
      if (pms && pms.checked) {
        log.painMorning = Number(pm.value);
        pmv.textContent = String(log.painMorning);
      } else {
        log.painMorning = null;
        pmv.textContent = "—";
      }
      saveState();
    }
    if (pm) pm.oninput = () => { if (pms) pms.checked = true; syncMorning(); };
    if (pms) pms.onchange = syncMorning;
    if (rpe) {
      rpe.oninput = () => {
        rpev.textContent = rpe.value;
        log.rpe = Number(rpe.value);
        saveState();
      };
    }
    const note = $("#session-note");
    if (note) {
      note.onchange = () => {
        log.sessionNote = note.value;
        saveState();
      };
    }
    const saveBtn = $("#save-session");
    if (saveBtn) {
      saveBtn.onclick = () => {
        log.sessionNote = ($("#session-note") || {}).value || log.sessionNote;
        saveState();
        toast("Session saved");
      };
    }
    const doneBtn = $("#mark-complete");
    if (doneBtn) {
      doneBtn.onclick = () => {
        log.completed = !log.completed;
        if (log.completed) {
          log.exercises.forEach((e) => {
            /* leave individual checks as user set them */
          });
        }
        saveState();
        toast(log.completed ? "Session marked complete" : "Marked incomplete");
        renderToday();
      };
    }
  }

  function escapeHtml(s) {
    return String(s ?? "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }
  function escapeAttr(s) {
    return escapeHtml(s).replace(/'/g, "&#39;");
  }

  // ---------- picker ----------
  function renderPicker() {
    const root = $("#view-pick");
    const byWeek = {};
    for (const s of PROGRAM.schedule) {
      (byWeek[s.week] || (byWeek[s.week] = [])).push(s);
    }
    let html = `<div class="card"><h2>Week / day picker</h2>
      <p class="muted">Jump to any scheduled session. Calf content uses your current level (Settings).</p></div>`;
    for (let w = 1; w <= 8; w++) {
      html += `<div class="card"><h3>Week ${w}</h3><div class="week-list">`;
      for (const s of byWeek[w] || []) {
        const done = state.sessions[s.date]?.completed;
        html += `<button type="button" class="btn" data-jump="${s.date}">
          <span>${s.day} ${s.date.slice(5)} · ${s.type} ${escapeHtml(s.label.replace(/^.—\s*/, "").slice(0, 28))}</span>
          <span class="right">${done ? "✓" : ""}</span>
        </button>`;
      }
      html += `</div></div>`;
    }
    root.innerHTML = html;
    $all("[data-jump]").forEach((b) => {
      b.onclick = () => {
        viewDate = b.getAttribute("data-jump");
        showView("today");
      };
    });
  }

  // ---------- progress ----------
  function renderProgress() {
    const root = $("#view-progress");
    const sessions = Object.values(state.sessions).filter((s) => s.completed || (s.exercises || []).some((e) => e.done));
    const completedDates = Object.keys(state.sessions)
      .filter((d) => state.sessions[d].completed)
      .sort();

    const streak = calcStreak(completedDates);
    const perWeek = sessionsPerProgramWeek();

    let html = `<div class="card">
      <h2>Progress</h2>
      <div class="stat-grid">
        <div class="stat"><div class="num">${streak}</div><div class="lbl">Completion streak</div></div>
        <div class="stat"><div class="num">${completedDates.length}</div><div class="lbl">Sessions done</div></div>
      </div>
    </div>`;

    html += `<div class="card"><h2>Sessions per week</h2>
      <div class="chart-wrap">${svgBarChart(perWeek.labels, perWeek.values, "#0d6e4f")}</div>
    </div>`;

    const pain = calfPainSeries();
    html += `<div class="card"><h2>Calf pain trend</h2>
      <p class="muted">During (green) vs next morning (orange). Ceiling 3.</p>
      <div class="chart-wrap">${svgMultiLine(pain.labels, [
        { name: "During", color: "#0d6e4f", values: pain.during },
        { name: "Morning", color: "#c45c26", values: pain.morning },
      ], 10)}</div>
    </div>`;

    const loadSeries = loadOverTime();
    html += `<div class="card"><h2>Load over time</h2>
      <label class="field">Exercise</label>
      <select id="load-ex">${loadSeries.options
        .map((o) => `<option value="${escapeAttr(o.id)}" ${o.id === loadSeries.selected ? "selected" : ""}>${escapeHtml(o.name)}</option>`)
        .join("")}</select>
      <div class="chart-wrap" id="load-chart">${svgLineChart(loadSeries.labels, loadSeries.values, "#0d6e4f")}</div>
      <p class="muted" id="load-hint">${loadSeries.values.every((v) => v == null) ? "Log weight on exercises to see a trend." : ""}</p>
    </div>`;

    html += `<div class="card"><h2>Recent sessions</h2>`;
    const recent = Object.keys(state.sessions).sort().reverse().slice(0, 10);
    if (!recent.length) html += `<p class="empty">No sessions logged yet.</p>`;
    for (const d of recent) {
      const s = state.sessions[d];
      const nDone = (s.exercises || []).filter((e) => e.done).length;
      html += `<button type="button" class="btn block" style="margin-bottom:6px;justify-content:space-between" data-jump="${d}">
        <span>${formatNice(d)}</span>
        <span class="right">${s.completed ? "✓" : ""} ${nDone} ex · pain ${s.painDuring ?? "—"} · RPE ${s.rpe ?? "—"}</span>
      </button>`;
    }
    html += `</div>`;

    root.innerHTML = html;

    const sel = $("#load-ex");
    if (sel) {
      sel.onchange = () => {
        const series = loadOverTime(sel.value);
        $("#load-chart").innerHTML = svgLineChart(series.labels, series.values, "#0d6e4f");
        $("#load-hint").textContent = series.values.every((v) => v == null)
          ? "Log weight on exercises to see a trend."
          : "";
      };
    }
    $all("[data-jump]").forEach((b) => {
      b.onclick = () => {
        viewDate = b.getAttribute("data-jump");
        showView("today");
      };
    });
  }

  function calcStreak(completedSortedAsc) {
    if (!completedSortedAsc.length) return 0;
    // streak of consecutive *scheduled* training days completed ending at most recent
    const scheduled = new Set(PROGRAM.schedule.map((s) => s.date));
    const done = new Set(completedSortedAsc);
    const dates = PROGRAM.schedule.map((s) => s.date).filter((d) => d <= todayISO()).reverse();
    let streak = 0;
    for (const d of dates) {
      if (!scheduled.has(d)) continue;
      // optional C days don't break streak if skipped
      const typ = scheduleFor(d)?.type;
      if (typ === "C" && !done.has(d)) continue;
      if (done.has(d)) streak++;
      else break;
    }
    return streak;
  }

  function sessionsPerProgramWeek() {
    const labels = [];
    const values = [];
    for (let w = 1; w <= 8; w++) {
      labels.push(`W${w}`);
      const dates = PROGRAM.schedule.filter((s) => s.week === w).map((s) => s.date);
      values.push(dates.filter((d) => state.sessions[d]?.completed).length);
    }
    return { labels, values };
  }

  function calfPainSeries() {
    const dates = Object.keys(state.sessions).sort();
    const labels = dates.map((d) => d.slice(5));
    const during = dates.map((d) => state.sessions[d].painDuring ?? null);
    const morning = dates.map((d) => state.sessions[d].painMorning ?? null);
    return { labels, during, morning };
  }

  function parseLoadNumber(s) {
    if (s == null || s === "") return null;
    const m = String(s).match(/(\d+(\.\d+)?)/);
    return m ? Number(m[1]) : null;
  }

  function loadOverTime(selectedId) {
    // collect exercise ids that have any weight logged
    const names = {};
    const counts = {};
    for (const s of Object.values(state.sessions)) {
      for (const e of s.exercises || []) {
        names[e.id] = names[e.id] || e.id;
        if (parseLoadNumber(e.weight) != null) counts[e.id] = (counts[e.id] || 0) + 1;
      }
    }
    // also include common names from program
    for (const lvl of PROGRAM.calfLevels) {
      for (const e of lvl.exercises) names[e.id] = e.name;
    }
    for (const band of Object.values(PROGRAM.hipsByWeek)) {
      for (const e of band) names[e.id] = e.name;
    }
    for (const band of Object.values(PROGRAM.shouldersByWeek)) {
      for (const e of band) names[e.id] = e.name;
    }

    let options = Object.keys(names).map((id) => ({ id, name: names[id], n: counts[id] || 0 }));
    options.sort((a, b) => b.n - a.n || a.name.localeCompare(b.name));
    if (!options.length) options = [{ id: "c0-iso-bent", name: "Seated PF isometric (bent knee)", n: 0 }];
    const selected = selectedId || options[0].id;

    const dates = Object.keys(state.sessions).sort();
    const labels = dates.map((d) => d.slice(5));
    const values = dates.map((d) => {
      const row = (state.sessions[d].exercises || []).find((e) => e.id === selected);
      return row ? parseLoadNumber(row.weight) : null;
    });
    return { options, selected, labels, values };
  }

  // ---------- SVG charts ----------
  function svgBarChart(labels, values, color) {
    const w = 320, h = 160, pad = 28;
    const max = Math.max(4, ...values, 1);
    const bw = (w - pad * 2) / labels.length;
    let bars = "";
    values.forEach((v, i) => {
      const bh = ((h - pad * 2) * v) / max;
      const x = pad + i * bw + 4;
      const y = h - pad - bh;
      bars += `<rect x="${x}" y="${y}" width="${bw - 8}" height="${Math.max(bh, 0)}" rx="4" fill="${color}"/>`;
      bars += `<text x="${x + (bw - 8) / 2}" y="${h - 8}" text-anchor="middle" font-size="11" fill="#5c5c5c">${labels[i]}</text>`;
      bars += `<text x="${x + (bw - 8) / 2}" y="${y - 4}" text-anchor="middle" font-size="11" font-weight="700" fill="#1a1a1a">${v}</text>`;
    });
    return `<svg viewBox="0 0 ${w} ${h}" role="img" aria-label="Sessions per week">${bars}</svg>`;
  }

  function svgLineChart(labels, values, color) {
    const w = 320, h = 160, pad = 28;
    const nums = values.filter((v) => v != null);
    if (!labels.length || !nums.length) {
      return `<svg viewBox="0 0 ${w} ${h}"><text x="50%" y="50%" text-anchor="middle" fill="#5c5c5c" font-size="13">No data yet</text></svg>`;
    }
    const max = Math.max(...nums, 1) * 1.15;
    const min = 0;
    const pts = values
      .map((v, i) => {
        if (v == null) return null;
        const x = pad + (i * (w - pad * 2)) / Math.max(labels.length - 1, 1);
        const y = h - pad - ((v - min) / (max - min)) * (h - pad * 2);
        return { x, y, v, i };
      })
      .filter(Boolean);
    let path = pts.map((p, i) => `${i ? "L" : "M"}${p.x},${p.y}`).join(" ");
    let dots = pts.map((p) => `<circle cx="${p.x}" cy="${p.y}" r="4" fill="${color}"/>`).join("");
    let xlabels = labels
      .map((lb, i) => {
        if (labels.length > 8 && i % Math.ceil(labels.length / 6) !== 0) return "";
        const x = pad + (i * (w - pad * 2)) / Math.max(labels.length - 1, 1);
        return `<text x="${x}" y="${h - 8}" text-anchor="middle" font-size="10" fill="#5c5c5c">${lb}</text>`;
      })
      .join("");
    return `<svg viewBox="0 0 ${w} ${h}" role="img"><path d="${path}" fill="none" stroke="${color}" stroke-width="2.5"/>${dots}${xlabels}</svg>`;
  }

  function svgMultiLine(labels, series, yMax) {
    const w = 320, h = 160, pad = 28;
    if (!labels.length || series.every((s) => s.values.every((v) => v == null))) {
      return `<svg viewBox="0 0 ${w} ${h}"><text x="50%" y="50%" text-anchor="middle" fill="#5c5c5c" font-size="13">No pain data yet</text></svg>`;
    }
    const max = yMax || 10;
    // ceiling line at 3
    const y3 = h - pad - (3 / max) * (h - pad * 2);
    let parts = `<line x1="${pad}" y1="${y3}" x2="${w - pad}" y2="${y3}" stroke="#b91c1c" stroke-dasharray="4 4" stroke-width="1.5"/>`;
    parts += `<text x="${w - pad}" y="${y3 - 4}" text-anchor="end" font-size="10" fill="#b91c1c">≤3</text>`;
    for (const s of series) {
      const pts = s.values
        .map((v, i) => {
          if (v == null) return null;
          const x = pad + (i * (w - pad * 2)) / Math.max(labels.length - 1, 1);
          const y = h - pad - (v / max) * (h - pad * 2);
          return { x, y };
        })
        .filter(Boolean);
      if (!pts.length) continue;
      const path = pts.map((p, i) => `${i ? "L" : "M"}${p.x},${p.y}`).join(" ");
      parts += `<path d="${path}" fill="none" stroke="${s.color}" stroke-width="2.5"/>`;
      parts += pts.map((p) => `<circle cx="${p.x}" cy="${p.y}" r="3.5" fill="${s.color}"/>`).join("");
    }
    let xlabels = labels
      .map((lb, i) => {
        if (labels.length > 8 && i % Math.ceil(labels.length / 6) !== 0) return "";
        const x = pad + (i * (w - pad * 2)) / Math.max(labels.length - 1, 1);
        return `<text x="${x}" y="${h - 8}" text-anchor="middle" font-size="10" fill="#5c5c5c">${lb}</text>`;
      })
      .join("");
    return `<svg viewBox="0 0 ${w} ${h}" role="img">${parts}${xlabels}</svg>`;
  }

  // ---------- settings / export ----------
  function renderSettings() {
    const root = $("#view-settings");
    const levels = PROGRAM.calfLevels
      .map(
        (l) =>
          `<option value="${l.level}" ${Number(state.settings.calfLevel) === l.level ? "selected" : ""}>Level ${l.level} — ${escapeHtml(l.name)}</option>`
      )
      .join("");
    root.innerHTML = `
      <div class="card settings-block">
        <h2>Settings</h2>
        <label class="field">Program start date</label>
        <input type="date" id="set-start" value="${escapeAttr(state.settings.startDate || DEFAULT_START)}">
        <div style="height:10px"></div>
        <label class="field">Current calf level</label>
        <select id="set-calf">${levels}</select>
        <p class="muted">Advance only after 2–3 PASS sessions (pain ≤3, no worse morning, no extra swelling).</p>
        <button class="btn primary block" type="button" id="save-settings">Save settings</button>
      </div>
      <div class="card settings-block">
        <h2>Backup</h2>
        <button class="btn block" type="button" id="export-json">Export JSON</button>
        <div style="height:8px"></div>
        <button class="btn block" type="button" id="export-csv">Export CSV</button>
        <div style="height:8px"></div>
        <label class="field">Import JSON restore</label>
        <input type="file" id="import-json" accept="application/json,.json">
      </div>
      <div class="card">
        <h2>About</h2>
        <p class="muted">${escapeHtml(PROGRAM.athlete)} · ${escapeHtml(PROGRAM.programWindow)}</p>
        <p class="muted">${escapeHtml(PROGRAM.disclaimer)}</p>
        <p class="muted">Data stays on this device (localStorage). Install to home screen for offline use.</p>
      </div>
      <div class="card">
        <button class="btn danger block" type="button" id="reset-data">Clear all logged data</button>
      </div>`;

    $("#save-settings").onclick = () => {
      state.settings.startDate = $("#set-start").value || DEFAULT_START;
      state.settings.calfLevel = Number($("#set-calf").value) || 0;
      saveState();
      toast("Settings saved");
    };
    $("#export-json").onclick = exportJSON;
    $("#export-csv").onclick = exportCSV;
    $("#import-json").onchange = importJSON;
    $("#reset-data").onclick = () => {
      if (confirm("Clear all workout logs on this device? Settings kept.")) {
        state.sessions = {};
        saveState();
        toast("Logs cleared");
      }
    };
  }

  function exportJSON() {
    const blob = new Blob([JSON.stringify(state, null, 2)], { type: "application/json" });
    downloadBlob(blob, `ron-workout-${todayISO()}.json`);
    toast("JSON downloaded");
  }

  function exportCSV() {
    const rows = [
      [
        "date",
        "completed",
        "pain_during",
        "pain_morning",
        "rpe",
        "session_note",
        "exercise_id",
        "exercise_done",
        "weight",
        "reps_or_hold",
        "note",
      ],
    ];
    for (const d of Object.keys(state.sessions).sort()) {
      const s = state.sessions[d];
      const exs = s.exercises || [];
      if (!exs.length) {
        rows.push([d, s.completed, s.painDuring, s.painMorning, s.rpe, csvEscape(s.sessionNote), "", "", "", "", ""]);
      }
      for (const e of exs) {
        rows.push([
          d,
          s.completed,
          s.painDuring,
          s.painMorning ?? "",
          s.rpe,
          csvEscape(s.sessionNote),
          e.id,
          e.done,
          csvEscape(e.weight),
          csvEscape(e.repsOrHold),
          csvEscape(e.note),
        ]);
      }
    }
    const csv = rows.map((r) => r.join(",")).join("\n");
    downloadBlob(new Blob([csv], { type: "text/csv" }), `ron-workout-${todayISO()}.csv`);
    toast("CSV downloaded");
  }

  function csvEscape(v) {
    const s = String(v ?? "");
    if (/[",\n]/.test(s)) return `"${s.replace(/"/g, '""')}"`;
    return s;
  }

  function downloadBlob(blob, name) {
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = name;
    a.click();
    setTimeout(() => URL.revokeObjectURL(a.href), 1000);
  }

  function importJSON(ev) {
    const file = ev.target.files && ev.target.files[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = () => {
      try {
        const data = JSON.parse(String(reader.result));
        if (!data || typeof data !== "object" || !data.sessions) {
          throw new Error("Not a valid workout backup");
        }
        state = {
          version: data.version || 1,
          settings: Object.assign(defaultState().settings, data.settings || {}),
          sessions: data.sessions || {},
        };
        saveState();
        toast("Import complete");
        showView("today");
      } catch (e) {
        alert("Import failed: " + e.message);
      }
    };
    reader.readAsText(file);
    ev.target.value = "";
  }

  // ---------- boot ----------
  async function init() {
    state = loadState();
    const res = await fetch("program.json");
    PROGRAM = await res.json();
    if (!state.settings.startDate) state.settings.startDate = PROGRAM.startDate || DEFAULT_START;
    saveState();

    // Default view date: today if in/near program, else start date
    const t = todayISO();
    if (scheduleFor(t) || (t >= PROGRAM.startDate && t <= PROGRAM.endDate)) {
      viewDate = t;
    } else {
      viewDate = PROGRAM.startDate;
    }

    $all(".nav button").forEach((b) => {
      b.onclick = () => showView(b.dataset.view);
    });
    window.addEventListener("hashchange", () => {
      const h = location.hash.replace(/^#/, "");
      if (["today","pick","progress","settings"].includes(h) && h !== currentView) showView(h);
    });

    const initial = location.hash.replace(/^#/, "");
    showView(["today","pick","progress","settings"].includes(initial) ? initial : "today");

    if ("serviceWorker" in navigator) {
      navigator.serviceWorker.register("./sw.js").catch(() => {});
    }
  }

  // expose for headless checks
  window.__workoutApp = {
    getState: () => state,
    getProgram: () => PROGRAM,
    showView,
    buildWorkout,
  };

  init().catch((e) => {
    console.error(e);
    document.body.innerHTML = `<main class="card"><h2>Failed to load</h2><p>${escapeHtml(e.message)}</p></main>`;
  });
})();

/*
 * app.js — Kingdom Hearts Final Mix 100% tracker UI.
 * Renders the linear route from data/route.json, talks to state only via Store.
 * Sibling of zelda-oot-100-tracker's app.js, adapted for KH's Journal categories.
 */
(function () {
  "use strict";

  const $ = (sel, el) => (el || document).querySelector(sel);
  const elApp = $("#app");
  let DATA = null;
  let collapsed = new Set();
  let initedCollapse = false;
  let countdownTimer = null;
  let syncStatus = "";       // short status string shown next to the Sync button
  let syncInited = false;

  // ---------- cross-device sync (Cloudflare KV via /api/state) ----------
  const Sync = {
    pushTimer: null,
    on() { return ((Store.getPref("syncCode") || "").trim().length >= 4); },
    setStatus(s) {
      syncStatus = s;
      const el = $("#sync-status");
      if (el) el.textContent = s;
      const btn = $("#btn-sync");
      if (btn) btn.textContent = Sync.on() ? "☁ Synced" : "☁ Sync";
    },
    url() { return "/api/state?code=" + encodeURIComponent((Store.getPref("syncCode") || "").trim()); },

    async pull() {
      if (!Sync.on()) return;
      Sync.setStatus("syncing…");
      try {
        const r = await fetch(Sync.url(), { cache: "no-store" });
        if (!r.ok) { Sync.setStatus("sync error"); return; }
        const data = await r.json();
        const remoteMod = Number(data.lastModified) || 0;
        const localMod = Store.getLastModified();
        if (data.state && remoteMod > localMod) {
          Store.applySnapshot(data.state);
          initedCollapse = false; collapsed = new Set();
          render();
          Sync.setStatus("synced ↓ " + Sync.clock());
        } else if (remoteMod < localMod || !data.state) {
          await Sync.push();                 // remote is empty/older — upload local
        } else {
          Sync.setStatus("synced " + Sync.clock());
        }
      } catch (e) { Sync.setStatus("offline (saved locally)"); }
    },

    schedulePush() {
      if (!Sync.on()) return;
      clearTimeout(Sync.pushTimer);
      Sync.pushTimer = setTimeout(() => Sync.push(), 1000);
    },

    async push() {
      if (!Sync.on()) return;
      const snap = Store.snapshot();
      Sync.setStatus("saving…");
      try {
        const r = await fetch(Sync.url(), {
          method: "PUT",
          headers: { "content-type": "application/json" },
          body: JSON.stringify({ state: snap, lastModified: snap.lastModified })
        });
        if (r.status === 409) {
          const data = await r.json();        // someone saved newer — adopt it
          if (data.newer && data.newer.state) {
            Store.applySnapshot(data.newer.state);
            initedCollapse = false; collapsed = new Set();
            render();
            Sync.setStatus("synced ↓ " + Sync.clock());
          }
        } else if (r.ok) {
          Sync.setStatus("synced ↑ " + Sync.clock());
        } else {
          Sync.setStatus("sync error");
        }
      } catch (e) { Sync.setStatus("offline (saved locally)"); }
    },

    clock() {
      const d = new Date();
      return d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
    },

    setCode() {
      const cur = (Store.getPref("syncCode") || "").trim();
      const input = window.prompt(
        "Cross-device sync\n\nEnter a secret code and use the SAME code on every device to share your progress. Minimum 4 characters. Anyone who knows the code can see/edit this save, so make it non-obvious.\n\nLeave blank to turn sync OFF (stay local-only).",
        cur);
      if (input === null) return;             // cancelled
      const c = input.trim();
      if (c && c.length < 4) { flash("Code must be at least 4 characters"); return; }
      Store.setPref("syncCode", c);
      if (c) { flash("Sync on — pulling latest"); Sync.pull(); }
      else { flash("Sync off (local only)"); Sync.setStatus(""); }
      const btn = $("#btn-sync"); if (btn) btn.textContent = Sync.on() ? "☁ Synced" : "☁ Sync";
    }
  };

  // headline meters get big bars; everything else is a minigrid chip
  const HEADLINE = ["puppy", "trinity", "report"];
  const MINI_ORDER = ["postcard", "summon", "keyblade", "ability", "cup", "pooh",
                      "mushroom", "clock", "gummi", "synth", "boss", "optional", "treasure", "story"];
  // Dalmatians are stored as 33 triad checkboxes but shown as /99 (×3)
  const PUP_MULT = 3;

  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"]/g, (c) =>
      ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
  }
  function flash(msg) {
    let f = $(".flash");
    if (!f) { f = document.createElement("div"); f.className = "flash"; document.body.appendChild(f); }
    f.textContent = msg;
    f.classList.add("show");
    clearTimeout(f._t);
    f._t = setTimeout(() => f.classList.remove("show"), 1400);
  }

  function itemDone(it) {
    if (it.type === "tally") return Store.getTally(it.id) >= it.count;
    return Store.isChecked(it.id);
  }
  function stepItems(step) {
    if (step.items && step.items.length) return step.items;
    return [{ id: step.id + ":done", cat: "misc", label: "Mark this step done" }];
  }
  function stepDone(step) { return stepItems(step).every(itemDone); }
  function phaseDone(phase) { return phase.steps.every(stepDone); }

  // ---------- progress math ----------
  function tallyProgress() {
    const cats = {};
    let v = 0, max = 0;
    for (const ph of DATA.phases) {
      for (const st of ph.steps) {
        for (const it of (st.items || [])) {
          if (it.cat === "misc") continue;
          const c = cats[it.cat] || (cats[it.cat] = { v: 0, max: 0 });
          if (it.type === "tally") {
            c.max += it.count; max += it.count;
            const got = Math.min(Store.getTally(it.id), it.count);
            c.v += got; v += got;
          } else {
            c.max += 1; max += 1;
            if (Store.isChecked(it.id)) { c.v += 1; v += 1; }
          }
        }
      }
    }
    return { cats, overall: { v, max } };
  }
  // a category's display values (Dalmatians multiplied to /99)
  function catDisplay(cats, key) {
    const c = cats[key] || { v: 0, max: 0 };
    if (key === "puppy") return { v: c.v * PUP_MULT, max: c.max * PUP_MULT };
    return { v: c.v, max: c.max };
  }

  // ---------- countdown ----------
  function fmtCountdown(ms) {
    if (ms <= 0) return "IT'S TIME — GO!";
    const s = Math.floor(ms / 1000);
    const d = Math.floor(s / 86400);
    const h = Math.floor((s % 86400) / 3600);
    const m = Math.floor((s % 3600) / 60);
    const ss = s % 60;
    if (d > 0) return `${d}d ${h}h ${m}m`;
    return `${h}h ${m}m ${ss}s`;
  }
  function renderCountdown() {
    const wrap = $("#countdown");
    if (!wrap) return;
    const iso = Store.getPref("launchISO");
    const big = $("#cd-big", wrap);
    if (!iso) { big.textContent = "—"; wrap.classList.remove("live"); return; }
    const target = new Date(iso).getTime();
    if (isNaN(target)) { big.textContent = "—"; return; }
    big.textContent = fmtCountdown(target - Date.now());
    wrap.classList.toggle("live", target - Date.now() > 0);
  }

  // ---------- rendering ----------
  function meterBlock(label, v, max, blue, cls) {
    const pct = max ? Math.round((v / max) * 100) : 0;
    return `<div class="progress-block ${cls || ""}">
      <div class="progress-row"><span class="progress-label">${esc(label)}</span>
      <span class="progress-num">${v} / ${max}${cls === "overall" ? ` · ${pct}%` : ""}</span></div>
      <div class="progress ${blue ? "blue" : ""}"><div class="bar" style="width:${pct}%"></div></div>
    </div>`;
  }

  function renderHeader() {
    const p = tallyProgress();
    const cd = (k) => catDisplay(p.cats, k);
    const defs = DATA.categories;

    const stats = MINI_ORDER.filter((k) => p.cats[k]).map((k) => {
      const c = cd(k), full = c.max && c.v >= c.max;
      return `<div class="stat ${full ? "full" : ""}"><span>${defs[k].icon} ${esc(defs[k].label)}</span><span class="v">${c.v}/${c.max}</span></div>`;
    }).join("");

    const iso = Store.getPref("launchISO") || "";
    const pup = cd("puppy"), tri = cd("trinity"), rep = cd("report");
    return `
    <header class="app-header">
      <div class="title-row">
        <h1>Kingdom Hearts Final Mix — 100%</h1>
        <span class="subtitle">First run · Proud · one route</span>
      </div>
      <div class="scope">${esc(DATA.meta.scope)}</div>
      <div class="note"><b>Secret ending:</b> ${esc(DATA.meta.secretEnding)}</div>
    </header>

    <div class="countdown ${iso ? "live" : ""}" id="countdown">
      <span>⏱ Start countdown:</span>
      <span class="big" id="cd-big">—</span>
      <input type="datetime-local" id="launch-input" value="${esc(iso)}" />
      <span class="muted small">set your October start</span>
    </div>

    <div class="meters">
      ${meterBlock("Overall completion", p.overall.v, p.overall.max, false, "overall")}
      ${meterBlock("🐕 Dalmatians", pup.v, pup.max, false)}
      ${meterBlock("🔱 Trinities", tri.v, tri.max, true)}
      ${meterBlock("📕 Ansem's Reports", rep.v, rep.max, true)}
    </div>
    <div class="minigrid">${stats}</div>

    <div class="controls">
      <label class="toggle"><input type="checkbox" id="t-hide" ${Store.getPref("hideCompleted") ? "checked" : ""}/> Hide completed steps</label>
      <label class="toggle"><input type="checkbox" id="t-miss" ${Store.getPref("onlyMissable") ? "checked" : ""}/> Only missable steps</label>
      <div class="controls-right">
        <input class="search" id="search" type="search" placeholder="Search items / locations…" value="${esc(Store.getPref("search") || "")}" />
        <button class="btn" id="btn-sync" title="Sync progress across your devices with a shared code">${Sync.on() ? "☁ Synced" : "☁ Sync"}</button>
        <button class="btn" id="btn-export">Export</button>
        <button class="btn" id="btn-import">Import</button>
        <button class="btn danger" id="btn-reset">Reset</button>
      </div>
    </div>
    <div class="sync-row"><span class="sync-status" id="sync-status">${esc(syncStatus)}</span></div>`;
  }

  function renderFocus() {
    for (const ph of DATA.phases) {
      for (const st of ph.steps) {
        if (!stepDone(st)) {
          return `<div class="focus">
            <div class="lbl">▶ Up next</div>
            <div class="ttl">${esc(st.title)}</div>
            <div class="where">${esc(st.loc || "")}${st.do ? " — " + esc(st.do) : ""}</div>
            <div class="small" style="margin-top:6px"><a id="jump-focus" data-ph="${esc(ph.id)}" data-st="${esc(st.id)}">Jump to it ↓</a></div>
          </div>`;
        }
      }
    }
    return `<div class="focus" style="border-color:var(--done)">
      <div class="lbl" style="color:var(--done)">✔ Done</div>
      <div class="ttl">Jiminy's Journal at 100% — every collectible, trinity, report and superboss accounted for. 🗝️</div>
    </div>`;
  }

  function itemRow(it) {
    const done = itemDone(it);
    const pill = `<span class="cat-pill">${esc((DATA.categories[it.cat] || {}).label || it.cat)}</span>`;
    const verify = it.conf === "verify" ? `<span class="verify" title="Confirm in-game">verify</span>` : "";
    return `<li class="item ${done ? "checked" : ""}" data-search="${esc((it.label + " " + it.id).toLowerCase())}">
      <label><input type="checkbox" data-id="${esc(it.id)}" ${done ? "checked" : ""}/>
      <span class="txt">${esc(it.label)} ${verify}</span></label>${pill}
    </li>`;
  }

  function stepBlock(step) {
    const done = stepDone(step);
    const items = stepItems(step).map(itemRow).join("");
    const missFlag = step.missable ? `<span class="missable-flag">missable</span>` : "";
    const missNote = step.missableNote ? `<div class="missable-note">⚠ ${esc(step.missableNote)}</div>` : "";
    const tip = step.tip ? `<div class="tip"><span class="tip-lbl">💡 Strategy</span> ${esc(step.tip)}</div>` : "";
    return `<div class="step ${done ? "done" : ""} ${step.missable ? "missable" : ""}" id="step-${esc(step.id)}">
      <div class="step-head"><span class="stitle">${esc(step.title)}</span> ${missFlag} <span class="step-loc">${esc(step.loc || "")}</span></div>
      ${step.do ? `<div class="step-do">${esc(step.do)}</div>` : ""}
      ${missNote}
      ${tip}
      <ul class="items">${items}</ul>
    </div>`;
  }

  // map an era label to a CSS tier class
  function eraClass(era) {
    const e = (era || "").toLowerCase();
    if (e.includes("endgame")) return "endgame";
    if (e.includes("mastery")) return "mastery";
    if (e.includes("checklist")) return "check";
    if (e.includes("finale")) return "finale";
    return "";
  }
  function phaseTier(era) {
    const c = eraClass(era);
    if (c === "endgame") return "tier-endgame";
    if (c === "check") return "tier-check";
    return "";
  }

  function phaseBlock(phase) {
    const total = phase.steps.length;
    const doneN = phase.steps.filter(stepDone).length;
    const complete = doneN === total;
    const isCollapsed = collapsed.has(phase.id);
    const steps = phase.steps.map(stepBlock).join("");
    return `<section class="phase ${complete ? "complete" : ""} ${phaseTier(phase.era)} ${isCollapsed ? "collapsed" : ""}" id="phase-${esc(phase.id)}">
      <div class="phase-head" data-ph="${esc(phase.id)}">
        <span class="caret">▾</span>
        <h2>${esc(phase.title)}</h2>
        <span class="era ${eraClass(phase.era)}">${esc(phase.era)}</span>
        <span class="phase-count">${doneN}/${total}${complete ? " ✓" : ""}</span>
      </div>
      <div class="phase-blurb">${esc(phase.blurb || "")}</div>
      <div class="phase-body">${steps}</div>
    </section>`;
  }

  function render() {
    if (!initedCollapse) {
      for (const ph of DATA.phases) if (phaseDone(ph)) collapsed.add(ph.id);
      initedCollapse = true;
    }
    const phases = DATA.phases.map(phaseBlock).join("");
    elApp.innerHTML = `
      ${renderHeader()}
      ${renderFocus()}
      ${phases}
      <footer>
        ${esc(DATA.meta.confidencePolicy)}<br/>
        ${esc(DATA.meta.remakeNote)}<br/>
        Progress saved locally on this device. Export to back it up.
      </footer>`;
    applyFilters();
    wire();
    renderCountdown();
  }

  // ---------- filters ----------
  function applyFilters() {
    const hide = Store.getPref("hideCompleted");
    const onlyMiss = Store.getPref("onlyMissable");
    const q = (Store.getPref("search") || "").trim().toLowerCase();

    DATA.phases.forEach((ph) => {
      let anyVisible = false;
      ph.steps.forEach((st) => {
        const node = document.getElementById("step-" + st.id);
        if (!node) return;
        let show = true;
        if (hide && stepDone(st)) show = false;
        if (onlyMiss && !st.missable) show = false;
        if (q) {
          const hay = (st.title + " " + (st.loc || "") + " " + (st.do || "") + " " + (st.tip || "") + " " +
            stepItems(st).map((i) => i.label).join(" ")).toLowerCase();
          if (!hay.includes(q)) show = false;
        }
        node.style.display = show ? "" : "none";
        if (show) anyVisible = true;
      });
      const pnode = document.getElementById("phase-" + ph.id);
      if (pnode) pnode.style.display = anyVisible ? "" : "none";
    });
  }

  // ---------- events ----------
  function wire() {
    const li = $("#launch-input");
    if (li) li.addEventListener("change", (e) => { Store.setPref("launchISO", e.target.value); renderCountdown(); Sync.schedulePush(); });

    $("#t-hide").addEventListener("change", (e) => { Store.setPref("hideCompleted", e.target.checked); applyFilters(); Sync.schedulePush(); });
    $("#t-miss").addEventListener("change", (e) => { Store.setPref("onlyMissable", e.target.checked); applyFilters(); Sync.schedulePush(); });
    $("#search").addEventListener("input", (e) => { Store.setPref("search", e.target.value); applyFilters(); });

    $("#btn-sync").addEventListener("click", () => Sync.setCode());
    $("#btn-export").addEventListener("click", doExport);
    $("#btn-import").addEventListener("click", doImport);
    $("#btn-reset").addEventListener("click", () => {
      if (confirm("Reset ALL progress? (Your start date + settings are kept.)")) {
        Store.resetProgress(); initedCollapse = false; collapsed = new Set(); render(); Sync.schedulePush();
      }
    });

    elApp.querySelectorAll(".phase-head").forEach((h) => {
      h.addEventListener("click", () => {
        const id = h.getAttribute("data-ph");
        if (collapsed.has(id)) collapsed.delete(id); else collapsed.add(id);
        document.getElementById("phase-" + id).classList.toggle("collapsed");
      });
    });

    elApp.querySelectorAll('.item input[type=checkbox]').forEach((cb) => {
      cb.addEventListener("change", () => {
        Store.setChecked(cb.getAttribute("data-id"), cb.checked);
        softRefresh();
        Sync.schedulePush();
      });
    });

    const jf = $("#jump-focus");
    if (jf) jf.addEventListener("click", () => {
      const ph = jf.getAttribute("data-ph"), st = jf.getAttribute("data-st");
      collapsed.delete(ph);
      const pn = document.getElementById("phase-" + ph);
      if (pn) pn.classList.remove("collapsed");
      const sn = document.getElementById("step-" + st);
      if (sn) sn.scrollIntoView({ behavior: "smooth", block: "center" });
    });
  }

  let refreshPending = false;
  function softRefresh() {
    if (refreshPending) return;
    refreshPending = true;
    const y = window.scrollY;
    requestAnimationFrame(() => {
      refreshPending = false;
      render();
      window.scrollTo({ top: y });
    });
  }

  // ---------- import / export ----------
  function doExport() {
    const blob = new Blob([JSON.stringify(Store.exportState(), null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url; a.download = "kh1-100-progress.json"; a.click();
    URL.revokeObjectURL(url);
    flash("Progress exported");
  }
  function doImport() {
    const inp = document.createElement("input");
    inp.type = "file"; inp.accept = "application/json";
    inp.onchange = () => {
      const f = inp.files[0]; if (!f) return;
      const r = new FileReader();
      r.onload = () => {
        try {
          const ok = Store.importState(JSON.parse(r.result));
          if (ok) { initedCollapse = false; collapsed = new Set(); render(); flash("Progress imported"); Sync.schedulePush(); }
          else flash("Invalid file");
        } catch (e) { flash("Couldn't read that file"); }
      };
      r.readAsText(f);
    };
    inp.click();
  }

  // ---------- boot ----------
  fetch("data/route.json")
    .then((r) => { if (!r.ok) throw new Error("HTTP " + r.status); return r.json(); })
    .then((data) => {
      DATA = data;
      render();
      countdownTimer = setInterval(renderCountdown, 1000);
      if (!syncInited) {
        syncInited = true;
        if (Sync.on()) Sync.pull();
        // re-pull when returning to this tab/device so you pick up edits made elsewhere
        document.addEventListener("visibilitychange", () => {
          if (document.visibilityState === "visible" && Sync.on()) Sync.pull();
        });
      }
    })
    .catch((e) => {
      elApp.innerHTML = `<div class="error">Couldn't load <code>data/route.json</code>.<br/>${esc(e.message)}</div>`;
    });
})();

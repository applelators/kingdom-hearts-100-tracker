/*
 * store.js — persistence layer for the KH1 Final Mix 100% tracker.
 *
 * localStorage is the always-on local cache (works offline). app.js layers an
 * optional Cloudflare-KV sync on top via snapshot()/applySnapshot() + a
 * `lastModified` stamp; all state still flows through this object only.
 */
(function () {
  "use strict";

  const KEYS = {
    checked: "kh1fm:checked",     // array of checkbox item ids
    checkedAt: "kh1fm:checkedAt", // id -> epoch ms when checked
    tally: "kh1fm:tally",         // id -> integer (unused for KH1, kept for parity)
    done: "kh1fm:done",           // array of phase ids the player has collapsed/finished
    prefs: "kh1fm:prefs",         // ui preferences object (incl. launch date, syncCode)
    lastmod: "kh1fm:lastmod"      // epoch ms of last data change (for sync conflict resolution)
  };

  const DEFAULT_PREFS = {
    hideCompleted: false,
    onlyMissable: false,
    collapseDone: true,
    launchISO: "",
    search: "",
    syncCode: ""             // cross-device passphrase (NOT synced; local only)
  };
  // prefs that, when changed, should bump lastModified + trigger a remote push
  const SYNCED_PREF = (k) => k !== "syncCode" && k !== "search";

  function read(key, fallback) {
    try {
      const raw = localStorage.getItem(key);
      return raw == null ? fallback : JSON.parse(raw);
    } catch (e) { return fallback; }
  }
  function write(key, value) {
    try { localStorage.setItem(key, JSON.stringify(value)); } catch (e) { /* full/disabled */ }
  }

  let checked = new Set(read(KEYS.checked, []));
  let checkedAt = read(KEYS.checkedAt, {}) || {};
  let tally = read(KEYS.tally, {}) || {};
  let done = new Set(read(KEYS.done, []));
  let prefs = Object.assign({}, DEFAULT_PREFS, read(KEYS.prefs, {}));
  let lastModified = Number(read(KEYS.lastmod, 0)) || 0;

  function touch() {
    lastModified = Date.now();
    write(KEYS.lastmod, lastModified);
  }

  const Store = {
    // ---- single checkbox items ----
    isChecked: (id) => checked.has(id),
    setChecked(id, on) {
      if (on) { checked.add(id); checkedAt[id] = Date.now(); }
      else { checked.delete(id); delete checkedAt[id]; }
      write(KEYS.checked, [...checked]);
      write(KEYS.checkedAt, checkedAt);
      touch();
    },
    toggleChecked(id) { const on = !checked.has(id); this.setChecked(id, on); return on; },
    checkedAtOf: (id) => checkedAt[id] || null,

    // ---- tally items ----
    getTally: (id) => tally[id] || 0,
    setTally(id, value) {
      const v = Math.max(0, Math.floor(value || 0));
      if (v === 0) delete tally[id]; else tally[id] = v;
      write(KEYS.tally, tally);
      touch();
    },
    bumpTally(id, delta, max) {
      let v = (tally[id] || 0) + delta;
      if (typeof max === "number") v = Math.min(max, v);
      this.setTally(id, v);
      return tally[id] || 0;
    },

    // ---- finished phases (manual collapse) ----
    isDone: (id) => done.has(id),
    setDone(id, on) {
      if (on) done.add(id); else done.delete(id);
      write(KEYS.done, [...done]);
    },

    // ---- preferences ----
    getPref: (k) => prefs[k],
    setPref(k, v) {
      prefs[k] = v;
      write(KEYS.prefs, prefs);
      if (SYNCED_PREF(k)) touch();
    },

    // ---- sync support ----
    getLastModified: () => lastModified,
    // full state blob for cross-device sync (syncCode intentionally excluded)
    snapshot() {
      const p = Object.assign({}, prefs); delete p.syncCode;
      return { v: 1, checked: [...checked], checkedAt, tally, done: [...done], prefs: p, lastModified };
    },
    // adopt a remote blob (does NOT bump lastModified — we keep the remote stamp)
    applySnapshot(snap) {
      if (!snap || typeof snap !== "object") return false;
      const keepCode = prefs.syncCode || "";
      checked = new Set(Array.isArray(snap.checked) ? snap.checked : []);
      checkedAt = (snap.checkedAt && typeof snap.checkedAt === "object") ? snap.checkedAt : {};
      tally = (snap.tally && typeof snap.tally === "object") ? snap.tally : {};
      done = new Set(Array.isArray(snap.done) ? snap.done : []);
      prefs = Object.assign({}, DEFAULT_PREFS, snap.prefs || {}, { syncCode: keepCode });
      lastModified = Number(snap.lastModified) || Date.now();
      write(KEYS.checked, [...checked]);
      write(KEYS.checkedAt, checkedAt);
      write(KEYS.tally, tally);
      write(KEYS.done, [...done]);
      write(KEYS.prefs, prefs);
      write(KEYS.lastmod, lastModified);
      return true;
    },

    // ---- backup / restore (file) ----
    exportState() {
      return {
        app: "kh1fm", checked: [...checked], checkedAt, tally, done: [...done], prefs,
        lastModified, exportedAt: new Date().toISOString()
      };
    },
    importState(obj) {
      if (!obj || typeof obj !== "object") return false;
      const keepCode = prefs.syncCode || "";
      checked = new Set(Array.isArray(obj.checked) ? obj.checked : []);
      checkedAt = (obj.checkedAt && typeof obj.checkedAt === "object") ? obj.checkedAt : {};
      tally = (obj.tally && typeof obj.tally === "object") ? obj.tally : {};
      done = new Set(Array.isArray(obj.done) ? obj.done : []);
      prefs = Object.assign({}, DEFAULT_PREFS, obj.prefs || {}, { syncCode: keepCode });
      write(KEYS.checked, [...checked]);
      write(KEYS.checkedAt, checkedAt);
      write(KEYS.tally, tally);
      write(KEYS.done, [...done]);
      write(KEYS.prefs, prefs);
      touch();
      return true;
    },
    resetProgress() {
      const keepPrefs = Object.assign({}, prefs); // keep launch date, sync code + UI prefs
      checked = new Set(); checkedAt = {}; tally = {}; done = new Set();
      write(KEYS.checked, []); write(KEYS.checkedAt, {});
      write(KEYS.tally, {}); write(KEYS.done, []);
      prefs = keepPrefs; write(KEYS.prefs, prefs);
      touch();
    }
  };

  window.Store = Store;
})();

/* Rosebery direct-booking site — no framework, no tracking, no payment. */
(() => {
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => [...r.querySelectorAll(s)];
  const store = "rb_lang_v1";

  const COPY = window.__COPY__;      // {zh:{...}, en:{...}}
  const CFG = window.__CONFIG__;

  function applyLang(lang) {
    document.documentElement.lang = lang === "zh" ? "zh-Hans" : "en";
    document.documentElement.dataset.lang = lang;
    const t = COPY[lang];
    $$("[data-i18n]").forEach((el) => {
      const key = el.dataset.i18n;
      const val = key.split(".").reduce((o, k) => (o ? o[k] : null), t);
      if (val != null) el.innerHTML = val;
    });
    $$("[data-i18n-attr]").forEach((el) => {
      const [attr, key] = el.dataset.i18nAttr.split("|");
      const val = key.split(".").reduce((o, k) => (o ? o[k] : null), t);
      if (val != null) el.setAttribute(attr, val);
    });
    $$(".lang button").forEach((b) => b.setAttribute("aria-pressed", String(b.dataset.lang === lang)));
    try { localStorage.setItem(store, lang); } catch (e) {}
  }

  $$(".lang button").forEach((b) => b.addEventListener("click", () => applyLang(b.dataset.lang)));

  // ---------- availability from an iCal file (read-only) ----------
  async function loadCalendar() {
    const grid = $("#cal");
    if (!grid) return;
    try {
      let ics = (document.getElementById("ics") || {}).textContent || "";
      if (!ics.trim()) {
        const res = await fetch(CFG.calendarUrl, { cache: "no-store" });
        if (!res.ok) throw new Error(res.status);
        ics = await res.text();
      }
      const busy = new Set();
      const events = ics.split("BEGIN:VEVENT").slice(1);
      for (const ev of events) {
        const dt = (ev.match(/DTSTART;?[^:]*:(\d{8})/) || [])[1];
        const end = (ev.match(/DTEND;?[^:]*:(\d{8})/) || [])[1];
        if (!dt) continue;
        const start = new Date(dt.slice(0, 4), +dt.slice(4, 6) - 1, +dt.slice(6, 8));
        const fin = end ? new Date(end.slice(0, 4), +end.slice(4, 6) - 1, +end.slice(6, 8)) : new Date(start.getTime() + 864e5);
        for (let d = new Date(start); d < fin; d.setDate(d.getDate() + 1)) {
          busy.add(d.toISOString().slice(0, 10));
        }
      }
      renderCalendar(busy, events.length > 0);
    } catch (e) {
      grid.innerHTML = `<p class="small">${COPY[document.documentElement.dataset.lang || "en"].cal.offline}</p>`;
    }
  }

  function renderCalendar(busy, connected) {
    const grid = $("#cal");
    const t = COPY[document.documentElement.dataset.lang || "zh"];
    const now = new Date();
    const y = now.getFullYear(), m = now.getMonth();
    const first = new Date(y, m, 1);
    const days = new Date(y, m + 1, 0).getDate();
    const pad = (first.getDay() + 6) % 7;
    const heads = t.cal.week.map((d) => `<div class="h">${d}</div>`).join("");
    let cells = "";
    for (let i = 0; i < pad; i++) cells += `<div></div>`;
    for (let d = 1; d <= days; d++) {
      const iso = `${y}-${String(m + 1).padStart(2, "0")}-${String(d).padStart(2, "0")}`;
      const cls = busy.has(iso) ? "d busy" : "d free";
      cells += `<div class="${cls}" title="${iso}">${d}</div>`;
    }
    grid.innerHTML = heads + cells +
      `<p class="small" style="grid-column:1/-1;margin-top:8px">${connected ? t.cal.connected : t.cal.empty}</p>`;
  }

  // ---------- booking request ----------
  const form = $("#bookform");
  if (form) {
    form.addEventListener("submit", async (ev) => {
      ev.preventDefault();
      const lang = document.documentElement.dataset.lang || "zh";
      const t = COPY[lang];
      const data = Object.fromEntries(new FormData(form).entries());
      const errs = [];
      if (!data.name || data.name.trim().length < 2) errs.push(t.form.errName);
      if (!data.email || !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(data.email)) errs.push(t.form.errEmail);
      if (!data.checkin || !data.checkout || data.checkout <= data.checkin) errs.push(t.form.errDates);
      if (!(+data.guests >= 1 && +data.guests <= 2)) errs.push(t.form.errGuests);
      const box = $("#formstatus");
      if (errs.length) {
        box.className = "status err";
        box.textContent = errs.join(" · ");
        return;
      }
      const payload = { ...data, lang, sent_at: new Date().toISOString(), source: "direct-site" };
      try {
        if (CFG.formEndpoint) {
          const res = await fetch(CFG.formEndpoint, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
          });
          if (!res.ok) throw new Error(res.status);
        } else {
          const body = encodeURIComponent(Object.entries(payload).map(([k, v]) => `${k}: ${v}`).join("\n"));
          window.location.href = `mailto:${CFG.hostEmail}?subject=${encodeURIComponent("Booking request")}&body=${body}`;
        }
        box.className = "status ok";
        box.textContent = t.form.ok;
        form.reset();
      } catch (e) {
        box.className = "status err";
        box.textContent = t.form.errSend;
      }
    });
  }

  const saved = (() => { try { return localStorage.getItem(store); } catch (e) { return null; } })();
  const initial = saved || (navigator.language || "en").toLowerCase().startsWith("zh") ? "zh" : "en";
  applyLang(saved || ((navigator.language || "en").toLowerCase().startsWith("zh") ? "zh" : "en"));
  loadCalendar();
})();

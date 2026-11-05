/*
  Website Monitor web UI.

  Every check runs as its own POST /monitor/single request, a few at a time,
  so results arrive as each check finishes, a single check can be retried,
  and a scan can be cancelled. All text that comes from the API or from the
  scanned site goes into the page through textContent, never innerHTML.

  A check's verdict is the emoji it starts with, as the checks return it:
  green passed, yellow or orange warning, red failed, white no verdict
  (error, timeout or not applicable). Nothing else is guessed.

  Every string of the interface comes from docs/assets/locales/<lang>.json
  through t(). English is the fallback for a key a language lacks;
  tests/test_ui_locales.py keeps the files in step.
*/
(function () {
  'use strict';

  /* ---------- Catalog ---------- */

  // Names and descriptions live in the locale files: category.<id>,
  // check.<id>.name and check.<id>.hint.
  const CATEGORIES = [
    { id: 'security', icon: 'shield' },
    { id: 'performance', icon: 'gauge' },
    { id: 'seo', icon: 'search' },
    { id: 'domain', icon: 'server' },
    { id: 'privacy', icon: 'eye-off' },
    { id: 'accessibility', icon: 'accessibility' },
    { id: 'technical', icon: 'cpu' },
  ];
  const CATEGORY = Object.fromEntries(CATEGORIES.map(c => [c.id, c]));

  const CHECKS = [
    ['ssl_cert', 'security'],
    ['ssl_cipher_strength', 'security'],
    ['security_headers', 'security'],
    ['hsts', 'security'],
    ['xss_protection', 'security'],
    ['cors_headers', 'security'],
    ['mixed_content', 'security'],
    ['subresource_integrity', 'security'],
    ['rate_limiting', 'security'],
    ['data_leakage', 'security'],

    ['pagespeed_performances', 'performance'],
    ['website_load_time', 'performance'],
    ['server_response_time', 'performance'],
    ['brotli_compression', 'performance'],
    ['asset_minification', 'performance'],
    ['cdn', 'performance'],
    ['redirect_chains', 'performance'],
    ['redirects', 'performance'],

    ['sitemap', 'seo'],
    ['robot_txt', 'seo'],
    ['open_graph_protocol', 'seo'],
    ['alt_tags', 'seo'],
    ['semantic_markup', 'seo'],
    ['url_canonicalization', 'seo'],
    ['favicon', 'seo'],
    ['broken_links', 'seo'],
    ['external_links', 'seo'],

    ['domain_expiration', 'domain'],
    ['dnssec', 'domain'],
    ['dns_blacklist', 'domain'],
    ['domain_breach', 'domain'],
    ['domainsblacklists_blacklist', 'domain'],
    ['subdomain_enumeration', 'domain'],
    ['email_domain', 'domain'],

    ['cookie_policy', 'privacy'],
    ['cookie_flags', 'privacy'],
    ['cookie_duration', 'privacy'],
    ['cookie_samesite_attribute', 'privacy'],
    ['ad_and_tracking', 'privacy'],
    ['floc', 'privacy'],
    ['privacy_exposure', 'privacy'],
    ['privacy_protected_whois', 'privacy'],
    ['third_party_requests', 'privacy'],
    ['third_party_resources', 'privacy'],

    ['accessibility', 'accessibility'],
    ['mobile_friendly', 'accessibility'],
    ['amp_compatibility', 'accessibility'],
    ['internationalization', 'accessibility'],
    ['browser_compatibility', 'accessibility'],

    ['content_type_headers', 'technical'],
    ['cms_used', 'technical'],
    ['clientside_rendering', 'technical'],
    ['deprecated_libraries', 'technical'],
  ].map(([id, cat], order) => ({ id, cat, order }));
  const CHECK = Object.fromEntries(CHECKS.map(c => [c.id, c]));

  const STATUS = {
    fail: { badge: 'badge-danger', dot: 'dot-danger', rank: 0 },
    warn: { badge: 'badge-warning', dot: 'dot-warning', rank: 1 },
    unknown: { badge: 'badge-neutral', dot: 'dot-unknown', rank: 2 },
    pass: { badge: 'badge-success', dot: 'dot-success', rank: 3 },
    running: { badge: 'badge-accent', rank: 4 },
    queued: { badge: 'badge-neutral', rank: 5 },
    cancelled: { badge: 'badge-neutral', rank: 6 },
  };
  const VERDICT_EMOJI = [['🟢', 'pass'], ['🟡', 'warn'], ['🟠', 'warn'], ['🔴', 'fail'], ['⚪', 'unknown']];
  const DONE = new Set(['pass', 'warn', 'fail', 'unknown']);
  const HISTORY_CAP = 20;

  /* ---------- i18n ---------- */

  const LANGS = ['en', 'it'];
  // Bump with every change to app.js, app.css or a locale file, together with
  // the ?v= in index.html: browsers keep the previous files under the same URL.
  const ASSET_VERSION = '3';
  const i18n = { lang: 'en', dict: {}, fallback: {}, plural: new Intl.PluralRules('en') };

  function readLangPref() {
    try {
      const v = localStorage.getItem('wm.lang');
      return v === 'en' || v === 'it' ? v : 'auto';
    } catch (e) { return 'auto'; }
  }
  function resolveLang(pref) {
    if (LANGS.includes(pref)) return pref;
    const wanted = navigator.languages && navigator.languages.length ? navigator.languages : [navigator.language || 'en'];
    for (const tag of wanted) {
      const base = String(tag).toLowerCase().split('-')[0];
      if (LANGS.includes(base)) return base;
    }
    return 'en';
  }
  async function fetchLocale(lang) {
    const res = await fetch(`assets/locales/${lang}.json?v=${ASSET_VERSION}`);
    if (!res.ok) throw new Error(`${lang}.json: HTTP ${res.status}`);
    return res.json();
  }
  async function loadLanguage(lang) {
    if (!Object.keys(i18n.fallback).length) {
      try { i18n.fallback = await fetchLocale('en'); } catch (e) { console.error('Website Monitor: no English strings', e); }
    }
    let dict = i18n.fallback;
    if (lang !== 'en') {
      try { dict = await fetchLocale(lang); } catch (e) { console.error(`Website Monitor: no ${lang} strings, using English`, e); lang = 'en'; }
    }
    i18n.lang = lang;
    i18n.dict = dict;
    i18n.plural = new Intl.PluralRules(lang);
    setNumberFormats(lang);
    document.documentElement.lang = lang;
  }

  // t('count.check', { n: 3 }) -> "3 checks". A placeholder without a value
  // stays as written, so literal text like GET /check/{id} survives.
  function t(key, params) {
    let value = key in i18n.dict ? i18n.dict[key] : i18n.fallback[key];
    if (value === undefined) return key;
    if (value && typeof value === 'object') {
      const n = params && typeof params.n === 'number' ? params.n : 0;
      value = value[i18n.plural.select(n)] || value.other;
    }
    return String(value).replace(/\{(\w+)\}/g, (match, name) => {
      if (!params || !(name in params) || params[name] instanceof Node) return match;
      const v = params[name];
      return typeof v === 'number' ? nf.format(v) : String(v);
    });
  }
  // Like t(), but placeholders may be DOM nodes (a link, a <code>): returns
  // the pieces for h() to append, so no translated text goes through innerHTML.
  function tx(key, params) {
    const text = t(key, params);
    const parts = [];
    let last = 0;
    text.replace(/\{(\w+)\}/g, (match, name, offset) => {
      if (params && params[name] instanceof Node) {
        parts.push(text.slice(last, offset), params[name]);
        last = offset + match.length;
      }
      return match;
    });
    parts.push(text.slice(last));
    return parts;
  }
  const checkName = id => (CHECK[id] ? t(`check.${id}.name`) : id);
  const checkHint = id => (CHECK[id] ? t(`check.${id}.hint`) : '');
  const categoryLabel = id => (CATEGORY[id] ? t(`category.${id}`) : id);
  const statusLabel = s => t(`status.${STATUS[s] ? s : 'unknown'}`);
  const countChecks = n => t('count.check', { n });

  function applyStaticText() {
    document.querySelectorAll('[data-i18n]').forEach(el => { el.textContent = t(el.dataset.i18n); });
    document.querySelectorAll('[data-i18n-attr]').forEach(el => {
      for (const pair of el.dataset.i18nAttr.split(';')) {
        const [attr, key] = pair.split(':');
        el.setAttribute(attr.trim(), t(key.trim()));
      }
    });
  }

  /* ---------- Icons (Lucide, ISC) ---------- */

  const ICONS = {
    x: ['M18 6 6 18', 'm6 6 12 12'],
    menu: ['M4 12h16', 'M4 6h16', 'M4 18h16'],
    search: ['c:11,11,8', 'm21 21-4.3-4.3'],
    play: ['M6 3l14 9-14 9z'],
    gauge: ['m12 14 4-4', 'M3.34 19a10 10 0 1 1 17.32 0'],
    history: ['M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8', 'M3 3v5h5', 'M12 7v5l4 2'],
    'list-checks': ['m3 17 2 2 4-4', 'm3 7 2 2 4-4', 'M13 6h8', 'M13 12h8', 'M13 18h8'],
    book: ['M12 7v14', 'M3 18a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1h5a4 4 0 0 1 4 4 4 4 0 0 1 4-4h5a1 1 0 0 1 1 1v13a1 1 0 0 1-1 1h-6a3 3 0 0 0-3 3 3 3 0 0 0-3-3z'],
    settings: ['M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z', 'c:12,12,3'],
    'panel-left': ['r:3,3,18,18,2', 'M9 3v18', 'm16 15-3-3 3-3'],
    external: ['M15 3h6v6', 'M10 14 21 3', 'M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6'],
    globe: ['c:12,12,10', 'M12 2a14.5 14.5 0 0 0 0 20 14.5 14.5 0 0 0 0-20', 'M2 12h20'],
    shield: ['M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z', 'm9 12 2 2 4-4'],
    server: ['r:2,2,20,8,2', 'r:2,14,20,8,2', 'M6 6h.01', 'M6 18h.01'],
    'eye-off': ['M10.733 5.076a10.744 10.744 0 0 1 11.205 6.575 1 1 0 0 1 0 .696 10.747 10.747 0 0 1-1.444 2.49', 'M14.084 14.158a3 3 0 0 1-4.242-4.242', 'M17.479 17.499a10.75 10.75 0 0 1-15.417-5.151 1 1 0 0 1 0-.696 10.75 10.75 0 0 1 4.446-5.143', 'm2 2 20 20'],
    accessibility: ['c:16,4,1', 'm18 19 1-7-6 1', 'm5 8 3-3 5.5 3-2.36 3.5', 'M4.24 14.5a5 5 0 0 0 6.88 6', 'M13.76 17.5a5 5 0 0 0-6.88-6'],
    cpu: ['r:4,4,16,16,2', 'r:9,9,6,6,1', 'M15 2v2', 'M15 20v2', 'M2 15h2', 'M2 9h2', 'M20 15h2', 'M20 9h2', 'M9 2v2', 'M9 20v2'],
    retry: ['M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8', 'M3 3v5h5'],
    copy: ['r:8,8,14,14,2', 'M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2'],
    download: ['M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4', 'm7 10 5 5 5-5', 'M12 15V3'],
    trash: ['M3 6h18', 'M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6', 'M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2'],
    check: ['M20 6 9 17l-5-5'],
    alert: ['m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3', 'M12 9v4', 'M12 17h.01'],
    info: ['c:12,12,10', 'M12 16v-4', 'M12 8h.01'],
    loader: ['M21 12a9 9 0 1 1-6.219-8.56'],
    stop: ['r:6,6,12,12,1'],
    printer: ['M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2', 'M6 9V3a1 1 0 0 1 1-1h10a1 1 0 0 1 1 1v6', 'r:6,14,12,8,1'],
    github: ['M15 22v-4a4.8 4.8 0 0 0-1-3.5c3 0 6-2 6-5.5.08-1.25-.27-2.48-1-3.5.28-1.15.28-2.35 0-3.5 0 0-1 0-3 1.5-2.64-.5-5.36-.5-8 0C6 2 5 2 5 2c-.3 1.15-.3 2.35 0 3.5A5.403 5.403 0 0 0 4 9c0 3.5 3 5.5 6 5.5-.39.49-.68 1.05-.85 1.65-.17.6-.22 1.23-.15 1.85v4', 'M9 18c-4.51 2-5-2-7-2'],
    box: ['M21 8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16Z', 'm3.3 7 8.7 5 8.7-5', 'M12 22V12'],
  };

  const SVG_NS = 'http://www.w3.org/2000/svg';
  function icon(name, size, extraClass) {
    const svg = document.createElementNS(SVG_NS, 'svg');
    svg.setAttribute('viewBox', '0 0 24 24');
    svg.setAttribute('fill', 'none');
    svg.setAttribute('stroke', 'currentColor');
    svg.setAttribute('stroke-width', '1.75');
    svg.setAttribute('stroke-linecap', 'round');
    svg.setAttribute('stroke-linejoin', 'round');
    svg.setAttribute('aria-hidden', 'true');
    svg.setAttribute('class', `icon-${size || 18}${extraClass ? ' ' + extraClass : ''}`);
    for (const d of ICONS[name] || []) {
      let el;
      if (d.startsWith('c:')) {
        const [cx, cy, r] = d.slice(2).split(',');
        el = document.createElementNS(SVG_NS, 'circle');
        el.setAttribute('cx', cx); el.setAttribute('cy', cy); el.setAttribute('r', r);
      } else if (d.startsWith('r:')) {
        const [x, y, w, hgt, rx] = d.slice(2).split(',');
        el = document.createElementNS(SVG_NS, 'rect');
        el.setAttribute('x', x); el.setAttribute('y', y);
        el.setAttribute('width', w); el.setAttribute('height', hgt); el.setAttribute('rx', rx);
      } else {
        el = document.createElementNS(SVG_NS, 'path');
        el.setAttribute('d', d);
      }
      svg.appendChild(el);
    }
    return svg;
  }

  /* ---------- DOM ---------- */

  function h(tag, attrs, ...children) {
    const el = document.createElement(tag);
    if (attrs) {
      for (const [k, v] of Object.entries(attrs)) {
        if (v === null || v === undefined || v === false) continue;
        if (k === 'class') el.className = v;
        else if (k === 'text') el.textContent = v;
        else if (k.startsWith('on')) el.addEventListener(k.slice(2), v);
        else if (k === 'dataset') Object.assign(el.dataset, v);
        else if (v === true) el.setAttribute(k, '');
        else el.setAttribute(k, String(v));
      }
    }
    append(el, children);
    return el;
  }
  function append(el, children) {
    for (const c of children.flat(Infinity)) {
      if (c === null || c === undefined || c === false) continue;
      el.appendChild(c instanceof Node ? c : document.createTextNode(String(c)));
    }
    return el;
  }
  function clear(el) { while (el.firstChild) el.removeChild(el.firstChild); return el; }
  const $ = sel => document.querySelector(sel);

  /* ---------- Storage (every access can throw: private mode, blocked site data) ---------- */

  function load(key, fallback) {
    try {
      const raw = localStorage.getItem(key);
      return raw === null ? fallback : JSON.parse(raw);
    } catch (e) { return fallback; }
  }
  function save(key, value) {
    try { localStorage.setItem(key, JSON.stringify(value)); return true; } catch (e) { return false; }
  }

  /* ---------- State ---------- */

  const DEFAULT_SETTINGS = { apiBase: '', timeout: 30, concurrency: 4 };
  const state = {
    settings: Object.assign({}, DEFAULT_SETTINGS, load('wm.settings', {})),
    pagespeedKey: '',
    selection: new Set((load('wm.selection', null) || CHECKS.map(c => c.id)).filter(id => CHECK[id])),
    history: (load('wm.history', []) || []).filter(e => e && e.id && Array.isArray(e.rows)),
    api: { status: 'unknown', version: null, total: null, descriptions: {}, error: null },
    scan: null,
    route: { name: 'scan', param: null, query: new URLSearchParams() },
    query: '',
    filter: { status: 'all', category: 'all' },
    lastTarget: '',
  };

  function saveHistory() {
    state.history = state.history.slice(0, HISTORY_CAP);
    save('wm.history', state.history);
    renderNavCounts();
  }
  function upsertHistory(entry) {
    const i = state.history.findIndex(e => e.id === entry.id);
    const stored = snapshot(entry);
    if (i >= 0) state.history[i] = stored; else state.history.unshift(stored);
    saveHistory();
  }
  function snapshot(entry) {
    return {
      id: entry.id, target: entry.target, startedAt: entry.startedAt, finishedAt: entry.finishedAt,
      cancelled: !!entry.cancelled, timeout: entry.timeout, concurrency: entry.concurrency,
      rows: entry.rows.map(r => ({ id: r.id, status: r.status, text: r.text, error: r.error, ms: r.ms })),
    };
  }

  /* ---------- Formatting ---------- */

  let nf = new Intl.NumberFormat('en');
  let nf1 = new Intl.NumberFormat('en', { minimumFractionDigits: 1, maximumFractionDigits: 1 });
  function setNumberFormats(lang) {
    nf = new Intl.NumberFormat(lang);
    nf1 = new Intl.NumberFormat(lang, { minimumFractionDigits: 1, maximumFractionDigits: 1 });
  }
  function fmtDuration(ms) {
    if (ms === null || ms === undefined || !Number.isFinite(ms)) return '';
    if (ms < 1000) return `${nf.format(Math.round(ms))} ms`;
    const s = ms / 1000;
    if (s < 60) return `${s < 10 ? nf1.format(s) : nf.format(Math.round(s))} s`;
    const m = Math.floor(s / 60);
    return `${nf.format(m)} min ${nf.format(Math.round(s - m * 60))} s`;
  }
  // inline: inside a sentence ("started today 10:47"), not at its start.
  function fmtDateTime(ts, inline) {
    const d = new Date(ts);
    const time = d.toLocaleTimeString(i18n.lang, { hour: '2-digit', minute: '2-digit' });
    if (d.toDateString() === new Date().toDateString()) return t(inline ? 'time.todayInline' : 'time.today', { time });
    return `${d.toLocaleDateString(i18n.lang, { day: 'numeric', month: 'short', year: 'numeric' })} ${time}`;
  }

  /* ---------- Results ---------- */

  function parseResult(r) {
    const raw = r && r.result !== null && r.result !== undefined ? String(r.result).trim() : '';
    let status = 'unknown';
    let text = raw;
    let at = -1;
    for (const [emoji, verdict] of VERDICT_EMOJI) {
      const i = raw.indexOf(emoji);
      if (i >= 0 && (at < 0 || i < at)) { at = i; status = verdict; text = (raw.slice(0, i) + raw.slice(i + emoji.length)).trim(); }
    }
    if (/^\(.*\)$/.test(text)) text = text.slice(1, -1).trim();
    let error = r && r.error ? String(r.error) : '';
    if (r && r.status === 'error') { status = 'unknown'; if (!error) error = t('err.checkError'); }
    return { status, text, error };
  }

  function tally(rows) {
    const c = { pass: 0, warn: 0, fail: 0, unknown: 0, running: 0, queued: 0, cancelled: 0, total: rows.length };
    for (const r of rows) c[r.status] = (c[r.status] || 0) + 1;
    c.done = c.pass + c.warn + c.fail + c.unknown;
    c.verdicts = c.pass + c.warn + c.fail;
    c.passRate = c.verdicts ? Math.round((c.pass / c.verdicts) * 100) : null;
    return c;
  }
  function entryDuration(e) {
    return e.finishedAt ? e.finishedAt - e.startedAt : (isRunning(e) ? Date.now() - e.startedAt : null);
  }
  function isRunning(e) { return !!(state.scan && state.scan.id === e.id && state.scan.running); }
  const pct = n => `${nf.format(n)}%`;

  /* ---------- API ---------- */

  function apiBase() { return (state.settings.apiBase || '').trim().replace(/\/+$/, ''); }
  function apiUrl(path) { return apiBase() + path; }
  function apiDisplay() { return apiBase() || location.origin; }

  async function fetchJson(path, options, timeoutMs, outerSignal) {
    const controller = new AbortController();
    const onAbort = () => controller.abort();
    if (outerSignal) {
      if (outerSignal.aborted) controller.abort();
      else outerSignal.addEventListener('abort', onAbort, { once: true });
    }
    const timer = setTimeout(() => controller.abort(), timeoutMs);
    try {
      const res = await fetch(apiUrl(path), Object.assign({}, options, { signal: controller.signal }));
      let body = null;
      try { body = await res.json(); } catch (e) { /* not JSON */ }
      if (!res.ok) {
        const detail = body && (body.detail || body.error);
        throw new Error(`HTTP ${res.status}${detail ? `: ${typeof detail === 'string' ? detail : JSON.stringify(detail)}` : ''}`);
      }
      if (body === null) throw new Error(t('err.notJson'));
      return body;
    } catch (e) {
      if (outerSignal && outerSignal.aborted) throw new DOMException('Cancelled', 'AbortError');
      if (e.name === 'AbortError') throw new Error(t('err.timeout', { seconds: Math.round(timeoutMs / 1000) }));
      if (e instanceof TypeError) throw new Error(t('err.unreachable'));
      throw e;
    } finally {
      clearTimeout(timer);
      if (outerSignal) outerSignal.removeEventListener('abort', onAbort);
    }
  }

  let healthTimer = null;
  async function checkHealth() {
    clearTimeout(healthTimer);
    try {
      const body = await fetchJson('/health', { headers: { Accept: 'application/json' } }, 6000);
      if (body.status !== 'healthy') throw new Error(t('err.badStatus', { status: body.status }));
      const wasDown = state.api.status !== 'ok';
      state.api.status = 'ok';
      state.api.version = body.version || null;
      state.api.total = Number.isFinite(body.total_checks_available) ? body.total_checks_available : null;
      state.api.error = null;
      if (wasDown) loadDescriptions();
    } catch (e) {
      state.api.status = 'down';
      state.api.error = e.message;
    }
    renderHealth();
    if (state.route.name === 'scan' || state.route.name === 'settings') renderView();
    healthTimer = setTimeout(checkHealth, state.api.status === 'ok' ? 60000 : 15000);
  }

  async function loadDescriptions() {
    try {
      const body = await fetchJson('/checks', { headers: { Accept: 'application/json' } }, 10000);
      const map = {};
      for (const c of body.all_checks || []) {
        if (c && c.slug && CHECK[c.slug] && c.description) {
          map[c.slug] = String(c.description).split(/\n\s*\n/)[0].replace(/\s+/g, ' ').trim();
        }
      }
      state.api.descriptions = map;
      if (state.route.name === 'catalog') renderView();
    } catch (e) { /* descriptions are a nicety: the catalog falls back to the short hint */ }
  }

  function renderHealth() {
    const dot = $('#health-dot');
    const text = $('#health-text');
    const a = state.api;
    dot.className = 'dot ' + (a.status === 'ok' ? 'dot-success' : a.status === 'down' ? 'dot-danger' : 'dot-unknown');
    if (a.status === 'ok') {
      text.textContent = (a.version ? t('health.version', { version: a.version }) : t('health.online'))
        + (a.total ? ` · ${countChecks(a.total)}` : '');
    } else if (a.status === 'down') {
      text.textContent = t('health.down');
    } else {
      text.textContent = t('health.checking');
    }
    $('#health-row').title = a.status === 'down' ? `${apiDisplay()}: ${a.error}` : apiDisplay();
    $('#nav-api-docs').href = a.status === 'ok' ? apiUrl('/api/docs') : 'swagger.html';
    $('#sb-sub').textContent = apiBase() ? apiBase().replace(/^https?:\/\//, '') : t('app.tagline');
  }

  /* ---------- Scan engine ---------- */

  function newId() {
    return Date.now().toString(36) + Math.random().toString(36).slice(2, 7);
  }

  let ticker = null;
  function warnBeforeUnload(e) { e.preventDefault(); e.returnValue = ''; }

  function startScan(target, ids) {
    if (state.scan && state.scan.running) return;
    const order = CHECKS.filter(c => ids.includes(c.id)).map(c => c.id);
    const scan = {
      id: newId(), target, startedAt: Date.now(), finishedAt: null, cancelled: false,
      timeout: clampInt(state.settings.timeout, 5, 300, 30),
      concurrency: clampInt(state.settings.concurrency, 1, 8, 4),
      rows: order.map(id => ({ id, status: 'queued', text: '', error: '', ms: null })),
      running: true, controller: new AbortController(),
    };
    state.scan = scan;
    state.filter = { status: 'all', category: 'all' };
    setQuery('');
    upsertHistory(scan);
    navigate(`#/results/${scan.id}`);
    window.addEventListener('beforeunload', warnBeforeUnload);
    ticker = setInterval(() => { if (state.route.name === 'results') refreshResultsMeta(); }, 1000);

    const queue = scan.rows.slice();
    const worker = async () => {
      while (queue.length && !scan.controller.signal.aborted) {
        await runCheck(scan, queue.shift());
      }
    };
    Promise.all(Array.from({ length: Math.min(scan.concurrency, queue.length) }, worker)).then(() => {
      scan.running = false;
      scan.finishedAt = Date.now();
      for (const r of scan.rows) if (!DONE.has(r.status)) r.status = 'cancelled';
      upsertHistory(scan);
      clearInterval(ticker);
      window.removeEventListener('beforeunload', warnBeforeUnload);
      const c = tally(scan.rows);
      toast(scan.cancelled
        ? t('toast.scanCancelled', { checks: countChecks(c.done) })
        : t('toast.scanDone', { target: scan.target, pass: c.pass, warn: c.warn, fail: c.fail }), scan.cancelled ? 'info' : 'check');
      renderNavCounts();
      if (state.route.name === 'results') renderView();
    });
    renderNavCounts();
  }

  async function runCheck(entry, row) {
    row.status = 'running';
    row.text = ''; row.error = ''; row.ms = null;
    onRowChange(entry, row);
    const started = performance.now();
    const signal = entry.controller ? entry.controller.signal : undefined;
    try {
      const payload = { website: entry.target, checks: [row.id], timeout: entry.timeout };
      if (state.pagespeedKey && row.id === 'pagespeed_performances') payload.pagespeed_api_key = state.pagespeedKey;
      const body = await fetchJson('/monitor/single', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
        body: JSON.stringify(payload),
      }, (entry.timeout + 20) * 1000, signal);
      const results = Array.isArray(body.results) ? body.results : [];
      // Older APIs do not send check_id; they answer for this one check anyway.
      const r = results.find(x => x && x.check_id === row.id) || results[0];
      if (!r) throw new Error(t('err.noResult'));
      Object.assign(row, parseResult(r));
    } catch (e) {
      if (e.name === 'AbortError') { row.status = 'cancelled'; row.error = ''; }
      else { row.status = 'unknown'; row.text = ''; row.error = e.message; }
    }
    row.ms = performance.now() - started;
    onRowChange(entry, row);
  }

  function cancelScan() {
    const scan = state.scan;
    if (!scan || !scan.running) return;
    scan.cancelled = true;
    scan.controller.abort();
  }

  async function retryCheck(entry, id) {
    if (state.scan && state.scan.running) { toast(t('toast.waitScan'), 'info'); return; }
    if (!entry.rows.find(r => r.id === id)) return;
    const live = state.scan && state.scan.id === entry.id ? state.scan : entry;
    const liveRow = live.rows.find(r => r.id === id);
    live.timeout = live.timeout || clampInt(state.settings.timeout, 5, 300, 30);
    await runCheck(live, liveRow);
    upsertHistory(live);
    toast(t('toast.retried', { name: checkName(id), status: statusLabel(liveRow.status).toLocaleLowerCase(i18n.lang) }), 'retry');
  }

  let rafPending = false;
  function onRowChange(entry) {
    if (state.route.name !== 'results' || !currentResultsEntry() || currentResultsEntry().id !== entry.id) return;
    if (rafPending) return;
    rafPending = true;
    requestAnimationFrame(() => { rafPending = false; refreshResults(); });
  }

  /* ---------- Exports ---------- */

  function exportRows(entry) {
    return entry.rows.map(r => ({
      id: r.id, name: checkName(r.id), category: CHECK[r.id] ? CHECK[r.id].cat : 'other', status: r.status,
      result: r.text || '', error: r.error || '', duration_ms: r.ms === null ? null : Math.round(r.ms),
    }));
  }
  function fileStamp(ts) {
    const d = new Date(ts);
    const p = n => String(n).padStart(2, '0');
    return `${d.getFullYear()}${p(d.getMonth() + 1)}${p(d.getDate())}-${p(d.getHours())}${p(d.getMinutes())}`;
  }
  function download(name, type, text) {
    const url = URL.createObjectURL(new Blob([text], { type }));
    const a = h('a', { href: url, download: name });
    document.body.appendChild(a);
    a.click();
    a.remove();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  }
  function exportJson(entry) {
    const c = tally(entry.rows);
    const doc = {
      target: entry.target,
      started_at: new Date(entry.startedAt).toISOString(),
      finished_at: entry.finishedAt ? new Date(entry.finishedAt).toISOString() : null,
      duration_ms: entryDuration(entry),
      cancelled: !!entry.cancelled,
      api: apiDisplay(),
      timeout_s: entry.timeout,
      summary: { passed: c.pass, warnings: c.warn, failed: c.fail, no_verdict: c.unknown, pass_rate_percent: c.passRate },
      checks: exportRows(entry),
    };
    download(`website-monitor-${entry.target}-${fileStamp(entry.startedAt)}.json`, 'application/json', JSON.stringify(doc, null, 2) + '\n');
  }
  function csvCell(v) {
    let s = v === null || v === undefined ? '' : String(v);
    // A cell from the scanned site must not run as a formula in a spreadsheet.
    if (/^[=+\-@\t\r]/.test(s)) s = "'" + s;
    return /[",\n\r]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s;
  }
  function exportCsv(entry) {
    const rows = exportRows(entry);
    const cols = ['id', 'name', 'category', 'status', 'result', 'error', 'duration_ms'];
    const lines = [cols.join(',')].concat(rows.map(r => cols.map(c => csvCell(r[c])).join(',')));
    download(`website-monitor-${entry.target}-${fileStamp(entry.startedAt)}.csv`, 'text/csv', lines.join('\r\n') + '\r\n');
  }

  function curlFor(target, id) {
    const body = JSON.stringify({ website: target || 'example.com', checks: [id] });
    return `curl -s -X POST '${apiDisplay()}/monitor/single' -H 'Content-Type: application/json' -d '${body}'`;
  }
  async function copyCurl(text) {
    let ok = false;
    try {
      if (navigator.clipboard && window.isSecureContext) { await navigator.clipboard.writeText(text); ok = true; }
    } catch (e) { ok = false; }
    if (!ok) {
      // Plain HTTP on a LAN address is not a secure context: no Clipboard API there.
      const ta = h('textarea', { style: 'position:fixed;top:-1000px;opacity:0', readonly: true });
      ta.value = text;
      document.body.appendChild(ta);
      ta.select();
      try { ok = document.execCommand('copy'); } catch (e) { ok = false; }
      ta.remove();
    }
    toast(ok ? t('toast.curlCopied') : t('toast.curlNotCopied'), ok ? 'copy' : 'alert');
  }

  /* ---------- Toasts ---------- */

  function toast(message, iconName) {
    const el = h('div', { class: 'toast' }, iconName ? icon(iconName, 16) : null, h('span', { text: message }));
    $('#toast-box').appendChild(el);
    setTimeout(() => el.remove(), 4000);
  }

  /* ---------- Shared components ---------- */

  function pageHeader({ eyebrow, title, desc, actions }) {
    return h('header', { class: 'page-header' },
      h('div', { class: 'page-header-text' },
        eyebrow ? h('p', { class: 'eyebrow', text: eyebrow }) : null,
        h('h1', { class: 'page-title', text: title }),
        desc ? h('p', { class: 'page-desc' }, desc) : null),
      actions && actions.length ? h('div', { class: 'header-actions' }, actions) : null);
  }
  function panel({ title, desc, actions, toolbar, body, flush, id }) {
    return h('section', { class: 'panel', id, 'aria-label': title },
      title ? h('div', { class: 'panel-head' },
        h('div', { class: 'panel-head-text' },
          h('h2', { class: 'panel-title', text: title }),
          desc ? h('p', { class: 'panel-desc' }, desc) : null),
        actions ? h('div', { class: 'row' }, actions) : null) : null,
      toolbar ? h('div', { class: 'panel-toolbar' }, toolbar) : null,
      h('div', { class: `panel-body${flush ? ' flush' : ''}` }, body));
  }
  function button(label, { iconName, variant, size, onclick, title, disabled, type, ariaLabel } = {}) {
    const cls = ['btn', variant ? `btn-${variant}` : '', size ? `btn-${size}` : ''].filter(Boolean).join(' ');
    return h('button', { type: type || 'button', class: cls, onclick, title, disabled, 'aria-label': ariaLabel },
      iconName ? icon(iconName, 16) : null, label ? h('span', { text: label }) : null);
  }
  function iconButton(iconName, label, onclick, opts = {}) {
    return h('button', { type: 'button', class: 'btn btn-icon', 'aria-label': label, title: label, onclick, disabled: opts.disabled },
      icon(iconName, 16, opts.spin ? 'spin' : ''));
  }
  function statusBadge(status) {
    const s = STATUS[status] || STATUS.unknown;
    return h('span', { class: `badge ${s.badge}` },
      status === 'running' ? icon('loader', 14, 'spin') : s.dot ? h('span', { class: `dot ${s.dot}`, 'aria-hidden': 'true' }) : null,
      statusLabel(status));
  }
  function statCard(label, value, { tone, sub, missing } = {}) {
    return h('div', { class: 'stat-card' },
      h('p', { class: 'stat-label', text: label }),
      missing ? h('p', { class: 'stat-missing', text: missing })
        : h('p', { class: `stat-val${tone ? ' tone-' + tone : ''}`, text: value }),
      sub ? h('p', { class: 'stat-sub' }, sub) : null);
  }
  function emptyState(iconName, title, desc, action) {
    return h('div', { class: 'empty-state' },
      h('span', { class: 'empty-state-icon' }, icon(iconName, 22)),
      h('p', { class: 'empty-state-title', text: title }),
      desc ? h('p', { class: 'empty-state-desc' }, desc) : null,
      action || null);
  }
  function newScanLink() {
    return h('a', { class: 'btn btn-primary', href: '#/scan' }, icon('play', 16), h('span', { text: t('nav.newScan') }));
  }
  function segmented(label, options, value, onChange) {
    return h('div', { class: 'segmented', role: 'group', 'aria-label': label },
      options.map(o => h('button', {
        type: 'button', 'aria-pressed': String(o.value === value), dataset: { value: o.value },
        onclick: () => onChange(o.value),
      }, o.label, o.count !== undefined ? h('span', { class: 'seg-count', text: nf.format(o.count) }) : null)));
  }
  function categorySelect(onchange) {
    const select = h('select', { class: 'form-input filter-select', 'aria-label': t('filter.category'), onchange },
      h('option', { value: 'all', text: t('filter.allCategories') }),
      CATEGORIES.map(c => h('option', { value: c.id, text: categoryLabel(c.id) })));
    select.value = state.filter.category;
    return select;
  }
  function searchBox(placeholder) {
    const input = h('input', {
      class: 'form-input', type: 'search', placeholder, 'aria-label': placeholder, value: state.query, autocomplete: 'off',
      oninput: e => setQuery(e.target.value, e.target),
    });
    input.dataset.pageSearch = '1';
    return h('label', { class: 'input-icon sm grow' }, icon('search', 16), input);
  }
  function apiDownNotice() {
    if (state.api.status !== 'down') return null;
    const onPages = /github\.io$/.test(location.hostname) && !apiBase();
    const settingsLink = h('a', { href: '#/settings', text: t('nav.settings') });
    return h('div', { class: 'notice notice-warning', role: 'alert' },
      icon('alert', 18),
      h('div', null,
        h('p', { class: 'notice-title', text: onPages ? t('notice.pagesTitle') : t('notice.downTitle') }),
        h('p', null, onPages
          ? tx('notice.pagesBody', { command: h('code', { text: 'docker compose up -d website-monitor-api' }), settings: settingsLink })
          : tx('notice.downBody', { api: apiDisplay(), error: state.api.error || t('notice.noAnswer'), settings: settingsLink }))));
  }

  /* ---------- Search ---------- */

  function setQuery(value, source) {
    state.query = value;
    const global = $('#global-search');
    if (global !== source) global.value = value;
    document.querySelectorAll('[data-page-search]').forEach(el => { if (el !== source) el.value = value; });
    if (state.route.name === 'results') refreshResults();
    else if (state.route.name === 'catalog' || state.route.name === 'history') renderTableOnly();
  }
  function matches(q, ...fields) {
    if (!q) return true;
    const needle = q.toLocaleLowerCase(i18n.lang);
    return fields.some(f => f && String(f).toLocaleLowerCase(i18n.lang).includes(needle));
  }

  /* ---------- View: new scan ---------- */

  function normalizeTarget(input) {
    let s = (input || '').trim();
    if (!s) return { empty: true };
    if (!/^[a-z][a-z0-9+.-]*:\/\//i.test(s)) s = 'https://' + s;
    let u;
    try { u = new URL(s); } catch (e) { return { error: t('err.invalidUrl') }; }
    if (u.protocol !== 'http:' && u.protocol !== 'https:') return { error: t('err.scheme') };
    const host = u.hostname.toLowerCase().replace(/\.$/, '');
    if (!host || (!host.includes('.') && host !== 'localhost')) return { error: t('err.fullDomain') };
    const port = !!u.port;
    const path = (u.pathname && u.pathname !== '/') || !!u.search;
    const dropped = port && path ? 'scan.droppedBoth' : port ? 'scan.droppedPort' : path ? 'scan.droppedPath' : null;
    return { host, dropped };
  }

  function renderScanView(view) {
    const prefill = state.route.query.get('target') || state.lastTarget || '';
    const running = !!(state.scan && state.scan.running);
    const input = h('input', {
      id: 'target', class: 'form-input', type: 'text', inputmode: 'url', autocomplete: 'url', spellcheck: 'false',
      placeholder: t('scan.placeholder'), 'aria-describedby': 'target-help', value: prefill,
    });
    const help = h('p', { id: 'target-help', class: 'field-help', 'aria-live': 'polite' });
    const runBtn = button(t('scan.running'), { iconName: running ? 'loader' : 'play', variant: 'primary', type: 'submit', disabled: running });
    if (running) runBtn.querySelector('svg').classList.add('spin');

    const updateHelp = () => {
      const n = normalizeTarget(input.value);
      state.lastTarget = input.value;
      input.removeAttribute('aria-invalid');
      help.className = 'field-help';
      if (n.empty) help.textContent = t('scan.helpEmpty');
      else if (n.error) { help.textContent = n.error; help.className = 'field-help is-error'; }
      else help.textContent = n.dropped ? t('scan.helpHostDropped', { host: n.host, dropped: t(n.dropped) }) : t('scan.helpHost', { host: n.host });
    };
    const updateRunLabel = () => {
      const n = state.selection.size;
      runBtn.querySelector('span').textContent = running ? t('scan.running')
        : n === CHECKS.length ? t('scan.runAll', { n }) : t('scan.runSome', { checks: countChecks(n) });
      runBtn.disabled = running || n === 0;
    };
    input.addEventListener('input', updateHelp);

    const form = h('form', {
      class: 'stack', novalidate: true,
      onsubmit: e => {
        e.preventDefault();
        const n = normalizeTarget(input.value);
        if (n.empty || n.error) {
          input.setAttribute('aria-invalid', 'true');
          help.className = 'field-help is-error';
          help.textContent = n.error || t('err.enterDomain');
          input.focus();
          return;
        }
        if (!state.selection.size) { toast(t('toast.selectOne'), 'alert'); return; }
        startScan(n.host, Array.from(state.selection));
      },
    },
    h('div', { class: 'field' },
      h('label', { class: 'field-label', for: 'target', text: t('scan.field') }),
      h('div', { class: 'target-row' }, h('div', { class: 'input-icon' }, icon('globe', 16), input), runBtn),
      help),
    recentTargets(input, updateHelp),
    h('p', { class: 'text-muted' },
      t('scan.settingsLine', { timeout: state.settings.timeout, checks: countChecks(state.settings.concurrency) }), ' ',
      h('a', { href: '#/settings', text: t('scan.change') })));

    const selCount = h('span');
    const picker = h('div', { class: 'picker-grid' });
    const refreshPicker = () => {
      selCount.textContent = t('scan.selected', { n: state.selection.size, total: CHECKS.length });
      picker.querySelectorAll('[data-cat]').forEach(card => {
        const ids = CHECKS.filter(c => c.cat === card.dataset.cat).map(c => c.id);
        const on = ids.filter(id => state.selection.has(id)).length;
        const box = card.querySelector('.picker-cat-head input');
        box.checked = on === ids.length;
        box.indeterminate = on > 0 && on < ids.length;
        card.classList.toggle('is-off', on === 0);
        card.querySelector('.picker-cat-count').textContent = `${nf.format(on)}/${nf.format(ids.length)}`;
        card.querySelectorAll('.picker-item input').forEach(i => { i.checked = state.selection.has(i.value); });
      });
      save('wm.selection', Array.from(state.selection));
      updateRunLabel();
    };
    for (const cat of CATEGORIES) {
      const items = CHECKS.filter(c => c.cat === cat.id);
      const head = h('input', {
        type: 'checkbox', class: 'check', 'aria-label': t('scan.allInCategory', { category: categoryLabel(cat.id) }),
        onchange: e => { items.forEach(c => e.target.checked ? state.selection.add(c.id) : state.selection.delete(c.id)); refreshPicker(); },
      });
      picker.appendChild(h('div', { class: 'picker-cat', dataset: { cat: cat.id } },
        h('label', { class: 'picker-cat-head' },
          head,
          h('span', { class: 'picker-cat-icon' }, icon(cat.icon, 16)),
          h('span', { class: 'picker-cat-name', text: categoryLabel(cat.id) }),
          h('span', { class: 'picker-cat-count' })),
        h('ul', { class: 'picker-list' }, items.map(c => h('li', null,
          h('label', { class: 'picker-item' },
            h('input', {
              type: 'checkbox', class: 'check', value: c.id,
              onchange: e => { e.target.checked ? state.selection.add(c.id) : state.selection.delete(c.id); refreshPicker(); },
            }),
            h('span', { class: 'picker-item-text' },
              h('span', { class: 'picker-item-name', text: checkName(c.id) }),
              h('span', { class: 'picker-item-hint', text: checkHint(c.id) }))))))));
    }

    append(view, [
      pageHeader({ eyebrow: t('nav.analyze'), title: t('nav.newScan'), desc: t('scan.desc') }),
      apiDownNotice(),
      panel({ title: t('scan.panelTarget'), body: form }),
      panel({
        title: t('scan.checks'), desc: selCount,
        actions: [
          button(t('scan.selectAll'), { size: 'sm', onclick: () => { CHECKS.forEach(c => state.selection.add(c.id)); refreshPicker(); } }),
          button(t('scan.clear'), { size: 'sm', onclick: () => { state.selection.clear(); refreshPicker(); } }),
        ],
        body: picker,
      }),
    ]);
    updateHelp();
    refreshPicker();
    if (!running && !prefill) setTimeout(() => input.focus({ preventScroll: true }), 0);
  }

  function recentTargets(input, onPick) {
    const seen = [];
    for (const e of state.history) if (!seen.includes(e.target)) seen.push(e.target);
    if (!seen.length) return null;
    return h('div', { class: 'chip-row' },
      h('span', { class: 'text-muted', text: t('scan.recent') }),
      seen.slice(0, 6).map(target => h('button', {
        type: 'button', class: 'chip', text: target,
        onclick: () => { input.value = target; onPick(); input.focus(); },
      })));
  }

  /* ---------- View: results ---------- */

  function currentResultsEntry() {
    const id = state.route.param;
    if (id) {
      if (state.scan && state.scan.id === id) return state.scan;
      return state.history.find(e => e.id === id) || null;
    }
    return state.scan || state.history[0] || null;
  }

  const ui = {};

  function renderResultsView(view) {
    const entry = currentResultsEntry();
    if (!entry) {
      append(view, [
        pageHeader({ eyebrow: t('nav.analyze'), title: t('nav.results') }),
        h('div', { class: 'panel' }, emptyState('gauge', state.route.param ? t('results.goneTitle') : t('results.emptyTitle'),
          t('results.emptyDesc'), newScanLink())),
      ]);
      return;
    }
    const running = isRunning(entry);
    const actions = running
      ? [button(t('results.cancel'), { iconName: 'stop', variant: 'danger', onclick: cancelScan })]
      : [
        button(t('results.print'), { iconName: 'printer', onclick: () => window.print() }),
        button('CSV', { iconName: 'download', onclick: () => exportCsv(entry) }),
        button('JSON', { iconName: 'download', onclick: () => exportJson(entry) }),
        button(t('results.runAgain'), {
          iconName: 'retry', variant: 'primary', disabled: !!(state.scan && state.scan.running),
          onclick: () => startScan(entry.target, entry.rows.map(r => r.id)),
        }),
      ];
    ui.desc = h('span');
    ui.progress = h('div');
    ui.stats = h('div', { class: 'stats-grid' });
    ui.cats = h('div', { class: 'cat-bars' });
    ui.seg = h('div');
    ui.catSelect = categorySelect(e => { state.filter.category = e.target.value; refreshResults(); });
    ui.tbody = h('tbody');
    ui.entry = entry;

    append(view, [
      pageHeader({ eyebrow: running ? t('results.running') : t('nav.results'), title: entry.target, desc: ui.desc, actions }),
      entry.cancelled && !running ? h('div', { class: 'notice notice-info' }, icon('info', 18),
        h('p', { text: t('results.cancelledNotice') })) : null,
      ui.progress,
      ui.stats,
      h('div', { class: 'layout-2' },
        panel({
          title: t('results.checks'),
          toolbar: [ui.seg, ui.catSelect, searchBox(t('results.filter'))],
          flush: true,
          body: h('div', { class: 'table-wrap' }, h('table', { class: 'data-table' },
            h('thead', null, h('tr', null,
              h('th', { class: 'col-status', text: t('results.colStatus') }),
              h('th', { text: t('results.colCheck') }),
              h('th', { class: 'col-num', text: t('results.colTime') }),
              h('th', null, h('span', { class: 'sr-only', text: t('results.colActions') })))),
            ui.tbody)),
        }),
        panel({
          title: t('results.byCategory'), desc: t('results.byCategoryDesc'),
          body: [ui.cats, h('div', { class: 'legend' },
            [['seg-pass', 'pass'], ['seg-warn', 'warn'], ['seg-fail', 'fail'], ['seg-unknown', 'unknown']]
              .map(([cls, s]) => h('span', null, h('span', { class: `dot ${cls}`, 'aria-hidden': 'true' }), statusLabel(s))))],
        })),
    ]);
    refreshResults();
  }

  function refreshResultsMeta() {
    const entry = ui.entry;
    if (!entry || !ui.desc) return;
    const c = tally(entry.rows);
    const running = isRunning(entry);
    const parts = [countChecks(entry.rows.length), t('results.started', { when: fmtDateTime(entry.startedAt, true) })];
    const dur = entryDuration(entry);
    if (dur !== null) parts.push(running ? t('results.soFar', { duration: fmtDuration(dur) }) : t('results.took', { duration: fmtDuration(dur) }));
    ui.desc.textContent = parts.join(' · ');

    clear(ui.progress);
    if (running) {
      const w = n => `${(n / c.total) * 100}%`;
      ui.progress.appendChild(h('div', { class: 'panel' }, h('div', { class: 'run-strip' },
        h('div', { class: 'run-strip-meta' },
          h('span', null, h('strong', { text: t('results.progressDone', { done: c.done, total: c.total }) }), t('results.progressSuffix'),
            c.running ? t('results.progressRunning', { n: c.running }) : ''),
          h('span', { text: t('results.elapsed', { duration: fmtDuration(dur) }) })),
        h('div', {
          class: 'progress', role: 'progressbar', 'aria-label': t('results.progressAria'),
          'aria-valuemin': '0', 'aria-valuemax': String(c.total), 'aria-valuenow': String(c.done),
        },
        h('span', { class: 'seg-pass', style: `width:${w(c.pass)}` }),
        h('span', { class: 'seg-warn', style: `width:${w(c.warn)}` }),
        h('span', { class: 'seg-fail', style: `width:${w(c.fail)}` }),
        h('span', { class: 'seg-unknown', style: `width:${w(c.unknown)}` }),
        h('span', { class: 'seg-running', style: `width:${w(c.running)}` })))));
    }
  }

  function refreshResults() {
    const entry = ui.entry;
    if (!entry || !ui.tbody || !document.body.contains(ui.tbody)) return;
    const c = tally(entry.rows);
    const running = isRunning(entry);
    refreshResultsMeta();

    clear(ui.stats);
    const rateTone = c.passRate === null ? null : c.passRate >= 80 ? 'success' : c.passRate >= 50 ? 'warning' : 'danger';
    append(ui.stats, [
      statCard(t('results.passRate'), c.passRate === null ? '' : pct(c.passRate), {
        tone: rateTone, missing: c.passRate === null ? (running ? t('results.waiting') : t('results.noVerdicts')) : null,
        sub: c.verdicts ? t('results.passRateSub', { pass: c.pass, checks: countChecks(c.verdicts) }) : t('results.passRateSubEmpty'),
      }),
      statCard(t('results.failed'), nf.format(c.fail), { tone: c.fail ? 'danger' : null, sub: t('results.failedSub') }),
      statCard(t('results.warnings'), nf.format(c.warn), { tone: c.warn ? 'warning' : null, sub: t('results.warningsSub') }),
      statCard(t('results.noVerdict'), nf.format(c.unknown), { sub: t('results.noVerdictSub') }),
    ]);

    clear(ui.cats);
    for (const cat of CATEGORIES) {
      const rows = entry.rows.filter(r => CHECK[r.id] && CHECK[r.id].cat === cat.id);
      if (!rows.length) continue;
      const ct = tally(rows);
      const w = n => `${(n / ct.total) * 100}%`;
      ui.cats.appendChild(h('div', { class: 'cat-bar-row' },
        h('div', { class: 'cat-bar-head' },
          h('button', {
            type: 'button', class: 'btn-link cat-bar-name', text: categoryLabel(cat.id),
            title: t('results.showOnly', { category: categoryLabel(cat.id) }),
            onclick: () => { state.filter.category = cat.id; ui.catSelect.value = cat.id; refreshResults(); },
          }),
          h('span', { class: 'cat-bar-count', text: t('results.catCount', { pass: ct.pass, total: ct.total }) })),
        h('div', { class: 'progress', 'aria-hidden': 'true' },
          ct.pass ? h('span', { class: 'seg-pass', style: `width:${w(ct.pass)}` }) : null,
          ct.warn ? h('span', { class: 'seg-warn', style: `width:${w(ct.warn)}` }) : null,
          ct.fail ? h('span', { class: 'seg-fail', style: `width:${w(ct.fail)}` }) : null,
          ct.unknown ? h('span', { class: 'seg-unknown', style: `width:${w(ct.unknown)}` }) : null)));
    }

    clear(ui.seg);
    ui.seg.appendChild(segmented(t('filter.status'), [
      { value: 'all', label: t('filter.all'), count: c.total },
      { value: 'fail', label: t('filter.fail'), count: c.fail },
      { value: 'warn', label: t('filter.warn'), count: c.warn },
      { value: 'unknown', label: t('filter.unknown'), count: c.unknown },
      { value: 'pass', label: t('filter.pass'), count: c.pass },
    ], state.filter.status, v => { state.filter.status = v; refreshResults(); }));

    const rows = entry.rows
      .filter(r => state.filter.status === 'all' || r.status === state.filter.status)
      .filter(r => state.filter.category === 'all' || (CHECK[r.id] && CHECK[r.id].cat === state.filter.category))
      .filter(r => matches(state.query, checkName(r.id), r.id, r.text, r.error, checkHint(r.id)));
    if (!running) {
      rows.sort((a, b) => (STATUS[a.status] || STATUS.unknown).rank - (STATUS[b.status] || STATUS.unknown).rank
        || ((CHECK[a.id] || {}).order || 0) - ((CHECK[b.id] || {}).order || 0));
    }

    clear(ui.tbody);
    if (!rows.length) {
      ui.tbody.appendChild(h('tr', null, h('td', { colspan: '4', class: 'empty-row-cell', text: t('results.noMatch') })));
      return;
    }
    const busy = !!(state.scan && state.scan.running);
    for (const r of rows) {
      const name = checkName(r.id);
      const cat = CHECK[r.id] ? CHECK[r.id].cat : null;
      const result = r.error
        ? h('div', { class: 'cell-error', text: r.error })
        : r.text ? h('div', { class: 'cell-result', text: r.text }) : null;
      ui.tbody.appendChild(h('tr', { dataset: { check: r.id } },
        h('td', { class: 'col-status' }, statusBadge(r.status)),
        h('td', null,
          h('div', { class: 'cell-primary', text: name }),
          h('div', { class: 'cell-sub' }, cat ? categoryLabel(cat) : '', ' · ', h('code', { text: r.id })),
          result),
        h('td', { class: 'col-num', 'data-label': t('results.colTime'), text: fmtDuration(r.ms) }),
        h('td', { class: 'col-right' }, h('div', { class: 'action-group' },
          iconButton(r.status === 'running' ? 'loader' : 'retry', t('results.retry', { name }), () => retryCheck(entry, r.id),
            { disabled: busy, spin: r.status === 'running' }),
          iconButton('copy', t('results.copyCurl', { name }), () => copyCurl(curlFor(entry.target, r.id)))))));
    }
  }

  /* ---------- View: history ---------- */

  let clearArmed = null;
  function clearHistoryButton() {
    const btn = button(t('history.clear'), {
      iconName: 'trash', variant: 'danger', disabled: !state.history.length,
      onclick: () => {
        if (clearArmed) {
          clearTimeout(clearArmed); clearArmed = null;
          state.history = state.scan && state.scan.running ? state.history.filter(e => e.id === state.scan.id) : [];
          saveHistory();
          toast(t('toast.historyCleared'), 'trash');
          renderView();
          return;
        }
        btn.querySelector('span').textContent = t('history.clearConfirm');
        clearArmed = setTimeout(() => { clearArmed = null; btn.querySelector('span').textContent = t('history.clear'); }, 3000);
      },
    });
    return btn;
  }

  function renderHistoryView(view) {
    ui.historyBody = h('tbody');
    const cols = ['history.colTarget', 'history.colStarted', 'history.colPassRate', 'history.colFailed', 'history.colWarnings', 'history.colNoVerdict', 'history.colDuration'];
    append(view, [
      pageHeader({
        eyebrow: t('nav.analyze'), title: t('nav.history'),
        desc: t('history.desc', { n: HISTORY_CAP }),
        actions: [clearHistoryButton()],
      }),
      state.history.length
        ? panel({
          title: t('history.scans'), desc: t('count.scan', { n: state.history.length }), flush: true,
          toolbar: [searchBox(t('history.filter'))],
          body: h('div', { class: 'table-wrap' }, h('table', { class: 'data-table' },
            h('thead', null, h('tr', null,
              cols.map((key, i) => h('th', { class: i >= 2 ? 'col-num' : null, text: t(key) })),
              h('th', null, h('span', { class: 'sr-only', text: t('results.colActions') })))),
            ui.historyBody)),
        })
        : h('div', { class: 'panel' }, emptyState('history', t('history.emptyTitle'), t('history.emptyDesc'), newScanLink())),
    ]);
    renderTableOnly();
  }

  function renderHistoryRows() {
    const body = ui.historyBody;
    if (!body) return;
    clear(body);
    const list = state.history.filter(e => matches(state.query, e.target));
    if (!list.length) {
      body.appendChild(h('tr', null, h('td', { colspan: '8', class: 'empty-row-cell', text: t('history.noMatch') })));
      return;
    }
    const busy = !!(state.scan && state.scan.running);
    for (const e of list) {
      const c = tally(e.rows);
      const running = isRunning(e);
      body.appendChild(h('tr', null,
        h('td', null,
          h('a', { class: 'cell-primary', href: `#/results/${e.id}`, text: e.target }),
          h('div', { class: 'cell-sub', text: countChecks(e.rows.length) + (running ? t('history.runningSuffix') : e.cancelled ? t('history.cancelledSuffix') : '') })),
        h('td', { 'data-label': t('history.colStarted'), text: fmtDateTime(e.startedAt) }),
        h('td', { class: 'col-num', 'data-label': t('history.colPassRate'), text: c.passRate === null ? '' : pct(c.passRate) }),
        h('td', { class: 'col-num', 'data-label': t('history.colFailed') }, c.fail ? h('span', { class: 'badge badge-danger', text: nf.format(c.fail) }) : nf.format(0)),
        h('td', { class: 'col-num', 'data-label': t('history.colWarnings') }, c.warn ? h('span', { class: 'badge badge-warning', text: nf.format(c.warn) }) : nf.format(0)),
        h('td', { class: 'col-num', 'data-label': t('history.colNoVerdict'), text: nf.format(c.unknown) }),
        h('td', { class: 'col-num', 'data-label': t('history.colDuration'), text: running ? t('history.runningLabel') : fmtDuration(entryDuration(e)) }),
        h('td', { class: 'col-right' }, h('div', { class: 'action-group' },
          iconButton('retry', t('history.rescan', { target: e.target }), () => startScan(e.target, e.rows.map(r => r.id)), { disabled: busy }),
          iconButton('trash', t('history.delete', { target: e.target }), () => {
            state.history = state.history.filter(x => x.id !== e.id);
            saveHistory();
            renderView();
          }, { disabled: running })))));
    }
  }

  /* ---------- View: catalog ---------- */

  function renderCatalogView(view) {
    ui.catalogBody = h('tbody');
    const catSelect = categorySelect(e => { state.filter.category = e.target.value; renderTableOnly(); });
    append(view, [
      pageHeader({
        eyebrow: t('nav.reference'), title: t('nav.catalog'),
        desc: t('catalog.desc', { n: CHECKS.length }),
        actions: [h('a', { class: 'btn', href: '#/scan' }, icon('play', 16), h('span', { text: t('nav.newScan') }))],
      }),
      panel({
        title: t('catalog.checks'), flush: true,
        desc: (state.api.status === 'ok' ? t('catalog.descApi') : t('catalog.descNoApi')) || null,
        toolbar: [catSelect, searchBox(t('results.filter'))],
        body: h('div', { class: 'table-wrap' }, h('table', { class: 'data-table' },
          h('thead', null, h('tr', null,
            h('th', { text: t('catalog.colCheck') }), h('th', { text: t('catalog.colCategory') }), h('th', { text: t('catalog.colWhat') }),
            h('th', null, h('span', { class: 'sr-only', text: t('results.colActions') })))),
          ui.catalogBody)),
      }),
    ]);
    renderTableOnly();
  }

  // The API's descriptions are its Python docstrings, in English: other
  // languages show the translated short description instead.
  function checkDescription(id) {
    return (i18n.lang === 'en' && state.api.descriptions[id]) || checkHint(id);
  }

  function renderCatalogRows() {
    const body = ui.catalogBody;
    if (!body) return;
    clear(body);
    const list = CHECKS
      .filter(c => state.filter.category === 'all' || c.cat === state.filter.category)
      .filter(c => matches(state.query, checkName(c.id), c.id, checkHint(c.id), state.api.descriptions[c.id], categoryLabel(c.cat)));
    if (!list.length) {
      body.appendChild(h('tr', null, h('td', { colspan: '4', class: 'empty-row-cell', text: t('catalog.noMatch') })));
      return;
    }
    for (const c of list) {
      const name = checkName(c.id);
      body.appendChild(h('tr', null,
        h('td', null, h('div', { class: 'cell-primary', text: name }), h('div', { class: 'cell-sub' }, h('code', { text: c.id }))),
        h('td', { 'data-label': t('catalog.colCategory') }, h('span', { class: 'badge badge-neutral', text: categoryLabel(c.cat) })),
        h('td', { 'data-label': t('catalog.colWhat') }, h('div', { class: 'cell-result', text: checkDescription(c.id) })),
        h('td', { class: 'col-right' }, h('div', { class: 'action-group' },
          iconButton('play', t('catalog.scanOnly', { name }), () => {
            state.selection = new Set([c.id]);
            save('wm.selection', [c.id]);
            navigate('#/scan');
          }),
          iconButton('copy', t('results.copyCurl', { name }), () => copyCurl(curlFor(null, c.id)))))));
    }
  }

  function renderTableOnly() {
    if (state.route.name === 'catalog') renderCatalogRows();
    else if (state.route.name === 'history') renderHistoryRows();
  }

  /* ---------- View: settings ---------- */

  function clampInt(v, min, max, fallback) {
    const n = parseInt(v, 10);
    return Number.isFinite(n) ? Math.min(max, Math.max(min, n)) : fallback;
  }

  function radioCards(name, legend, options, current, onPick) {
    return h('fieldset', { class: 'radio-group' },
      h('legend', { class: 'sr-only', text: legend }),
      options.map(([value, title, help]) => h('label', { class: `radio-card${current === value ? ' selected' : ''}`, dataset: { choice: value } },
        h('input', { type: 'radio', name, value, checked: current === value, onchange: () => onPick(value) }),
        h('span', null, h('span', { class: 'radio-title', text: title }), h('span', { class: 'radio-help', text: help })))));
  }

  function renderSettingsView(view) {
    const a = state.api;
    const baseInput = h('input', {
      id: 'api-base', class: 'form-input mono', type: 'url', placeholder: location.origin,
      value: state.settings.apiBase, spellcheck: 'false', autocomplete: 'off', 'aria-describedby': 'api-base-help',
    });
    const saveApi = async e => {
      e.preventDefault();
      const v = baseInput.value.trim().replace(/\/+$/, '');
      if (v && !/^https?:\/\/[^/\s]+/i.test(v)) {
        baseInput.setAttribute('aria-invalid', 'true');
        toast(t('toast.badAddress'), 'alert');
        return;
      }
      baseInput.removeAttribute('aria-invalid');
      state.settings.apiBase = v;
      save('wm.settings', state.settings);
      state.api = { status: 'unknown', version: null, total: null, descriptions: {}, error: null };
      renderHealth();
      await checkHealth();
      toast(state.api.status === 'ok' ? t('toast.apiConnected') : t('toast.apiSavedDown'), state.api.status === 'ok' ? 'check' : 'alert');
    };

    const timeout = h('input', { id: 's-timeout', class: 'form-input', type: 'number', min: '5', max: '300', step: '1', value: state.settings.timeout });
    const conc = h('input', { id: 's-conc', class: 'form-input', type: 'number', min: '1', max: '8', step: '1', value: state.settings.concurrency });
    const psk = h('input', { id: 's-psk', class: 'form-input mono', type: 'password', autocomplete: 'off', value: state.pagespeedKey, placeholder: t('settings.pskPlaceholder') });
    const saveScan = e => {
      e.preventDefault();
      state.settings.timeout = clampInt(timeout.value, 5, 300, 30);
      state.settings.concurrency = clampInt(conc.value, 1, 8, 4);
      timeout.value = state.settings.timeout;
      conc.value = state.settings.concurrency;
      state.pagespeedKey = psk.value.trim();
      save('wm.settings', state.settings);
      toast(t('toast.scanSaved'), 'check');
    };

    const sections = [['api', 'settings.api'], ['scan', 'settings.scan'], ['appearance', 'settings.appearance'], ['data', 'settings.data'], ['about', 'settings.about']];
    const kv = (label, value) => h('div', { class: 'kv-box' }, h('span', { class: 'kv-label', text: label }), h('span', { class: 'kv-val' }, value));
    const statusText = a.status === 'ok' ? t('settings.statusOnline') : a.status === 'down' ? t('settings.statusDown') : t('settings.statusChecking');

    append(view, [
      pageHeader({ eyebrow: t('nav.system'), title: t('nav.settings'), desc: t('settings.desc') }),
      h('div', { class: 'settings-shell' },
        h('nav', { class: 'settings-nav', 'aria-label': t('settings.sections') },
          h('ul', { class: 'settings-nav-list' }, sections.map(([id, key], i) => h('li', null,
            h('button', {
              type: 'button', class: `settings-nav-btn${i === 0 ? ' active' : ''}`, text: t(key),
              onclick: ev => {
                view.querySelectorAll('.settings-nav-btn').forEach(b => b.classList.toggle('active', b === ev.currentTarget));
                document.getElementById(`set-${id}`).scrollIntoView({ behavior: 'smooth', block: 'start' });
              },
            }))))),
        h('div', { class: 'settings-content' },
          panel({
            id: 'set-api', title: t('settings.api'), desc: t('settings.apiDesc'),
            body: h('form', { class: 'stack', onsubmit: saveApi, novalidate: true },
              h('div', { class: 'field' },
                h('label', { class: 'field-label', for: 'api-base', text: t('settings.apiLabel') }),
                baseInput,
                h('p', { id: 'api-base-help', class: 'field-help', text: t('settings.apiHelp') })),
              h('div', { class: 'row' }, button(t('settings.saveTest'), { variant: 'primary', type: 'submit' })),
              h('div', { class: 'kv-grid' },
                kv(t('settings.status'), [h('span', { class: `dot ${a.status === 'ok' ? 'dot-success' : a.status === 'down' ? 'dot-danger' : 'dot-unknown'}` }), statusText]),
                kv(t('settings.version'), a.version || t('settings.notReported')),
                kv(t('settings.checksAvailable'), a.total === null ? t('settings.notReported') : nf.format(a.total)),
                kv(t('settings.endpoint'), h('code', { text: apiDisplay() }))),
              a.status === 'down' && a.error ? h('p', { class: 'field-help is-error', text: a.error }) : null),
          }),
          panel({
            id: 'set-scan', title: t('settings.scan'),
            body: h('form', { class: 'stack', onsubmit: saveScan, novalidate: true },
              h('div', { class: 'form-grid' },
                h('div', { class: 'field' }, h('label', { class: 'field-label', for: 's-timeout', text: t('settings.timeout') }), timeout,
                  h('p', { class: 'field-help', text: t('settings.timeoutHelp') })),
                h('div', { class: 'field' }, h('label', { class: 'field-label', for: 's-conc', text: t('settings.parallel') }), conc,
                  h('p', { class: 'field-help', text: t('settings.parallelHelp') })),
                h('div', { class: 'field' }, h('label', { class: 'field-label', for: 's-psk', text: t('settings.psk') }), psk,
                  h('p', { class: 'field-help', text: t('settings.pskHelp') }))),
              h('div', { class: 'row' }, button(t('settings.save'), { variant: 'primary', type: 'submit' }))),
          }),
          panel({
            id: 'set-appearance', title: t('settings.appearance'),
            body: h('div', { class: 'stack' },
              h('div', { class: 'field' },
                h('p', { class: 'field-label', text: t('settings.theme') }),
                radioCards('theme', t('settings.theme'), [
                  ['system', t('settings.themeSystem'), t('settings.themeSystemHelp')],
                  ['light', t('settings.themeLight'), t('settings.themeLightHelp')],
                  ['dark', t('settings.themeDark'), t('settings.themeDarkHelp')],
                ], readTheme(), applyTheme)),
              h('div', { class: 'field' },
                h('p', { class: 'field-label', text: t('settings.language') }),
                // Language names stay in their own language, so they can be
                // found whatever the current one.
                radioCards('language', t('settings.language'), [
                  ['auto', t('settings.languageAuto'), t('settings.languageAutoHelp')],
                  ['en', 'English', t('settings.languageEnHelp')],
                  ['it', 'Italiano', t('settings.languageItHelp')],
                ], readLangPref(), applyLanguage))),
          }),
          panel({
            id: 'set-data', title: t('settings.data'), desc: t('settings.dataDesc', { n: HISTORY_CAP }),
            body: h('div', { class: 'row' }, clearHistoryButton()),
          }),
          panel({
            id: 'set-about', title: t('settings.about'),
            body: h('ul', { class: 'link-list' }, [
              ['github', t('settings.source'), 'github.com/fabriziosalmi/websites-monitor', 'https://github.com/fabriziosalmi/websites-monitor'],
              ['box', t('settings.image'), 'ghcr.io/fabriziosalmi/websites-monitor', 'https://github.com/fabriziosalmi/websites-monitor/pkgs/container/websites-monitor'],
              ['book', t('settings.apiDocs'), a.status === 'ok' ? t('settings.apiDocsLive') : t('settings.apiDocsStatic'), a.status === 'ok' ? apiUrl('/api/docs') : 'swagger.html'],
              ['book', t('settings.redoc'), t('settings.redocDesc'), apiUrl('/api/redoc')],
            ].map(([ic, title, desc, href]) => h('li', null, h('a', { href, target: '_blank', rel: 'noopener' },
              icon(ic, 18), h('span', { style: 'flex:1;min-width:0' }, h('span', { class: 'link-title', text: title }), h('br'), h('span', { class: 'link-desc', text: desc })),
              icon('external', 14))))),
          }))),
    ]);
  }

  /* ---------- Theme and language ---------- */

  const darkQuery = window.matchMedia('(prefers-color-scheme: dark)');
  function readTheme() { try { return localStorage.getItem('wm.theme') || 'system'; } catch (e) { return 'system'; } }
  function applyTheme(pref) {
    try { localStorage.setItem('wm.theme', pref); } catch (e) { /* the choice lasts for this page only */ }
    const dark = pref === 'dark' || (pref === 'system' && darkQuery.matches);
    document.documentElement.classList.toggle('dark', dark);
    document.querySelectorAll('input[name="theme"]').forEach(i => i.closest('.radio-card').classList.toggle('selected', i.value === pref));
  }
  darkQuery.addEventListener('change', () => { if (readTheme() === 'system') applyTheme('system'); });

  async function applyLanguage(pref) {
    try {
      if (pref === 'auto') localStorage.removeItem('wm.lang'); else localStorage.setItem('wm.lang', pref);
    } catch (e) { /* the choice lasts for this page only */ }
    await loadLanguage(resolveLang(pref));
    applyStaticText();
    setCollapsed(sidebar.classList.contains('collapsed'));
    renderHealth();
    renderNavCounts();
    renderView();
  }
  window.addEventListener('languagechange', () => { if (readLangPref() === 'auto') applyLanguage('auto'); });

  /* ---------- Router ---------- */

  const ROUTES = {
    scan: { label: 'nav.newScan', render: renderScanView },
    results: { label: 'nav.results', render: renderResultsView },
    history: { label: 'nav.history', render: renderHistoryView },
    catalog: { label: 'nav.catalog', render: renderCatalogView },
    settings: { label: 'nav.settings', render: renderSettingsView },
  };

  function parseRoute() {
    const raw = location.hash.replace(/^#\/?/, '');
    const [path, qs] = raw.split('?');
    const [name, param] = path.split('/');
    return { name: ROUTES[name] ? name : 'scan', param: param ? decodeURIComponent(param) : null, query: new URLSearchParams(qs || '') };
  }
  function navigate(hash) {
    if (location.hash === hash) onRoute(); else location.hash = hash;
  }
  function onRoute() {
    const prev = state.route.name;
    state.route = parseRoute();
    if (prev !== state.route.name) {
      setQuery('');
      if (state.route.name !== 'results') state.filter = { status: 'all', category: 'all' };
      else state.filter.status = 'all';
    }
    closeDrawer();
    renderView();
    $('#view').focus({ preventScroll: true });
    $('#viewport').scrollTop = 0;
  }
  function renderView() {
    const view = $('#view');
    const active = document.activeElement;
    const keepFocusId = active && view.contains(active) && active.id ? active.id : null;
    clear(view);
    for (const k of Object.keys(ui)) delete ui[k];
    const route = ROUTES[state.route.name];
    route.render(view);
    document.querySelectorAll('.sb-item[data-route]').forEach(a => {
      const on = a.dataset.route === state.route.name;
      a.classList.toggle('active', on);
      if (on) a.setAttribute('aria-current', 'page'); else a.removeAttribute('aria-current');
    });
    const entry = state.route.name === 'results' ? currentResultsEntry() : null;
    $('#mobile-page-label').textContent = entry ? entry.target : t(route.label);
    document.title = `${entry ? entry.target + ' · ' : ''}${t(route.label)} · ${t('app.name')}`;
    if (keepFocusId && document.getElementById(keepFocusId)) document.getElementById(keepFocusId).focus({ preventScroll: true });
  }

  function renderNavCounts() {
    const rc = $('#nav-results-count');
    if (state.scan && state.scan.running) {
      const c = tally(state.scan.rows);
      rc.textContent = `${nf.format(c.done)}/${nf.format(c.total)}`;
      rc.hidden = false;
    } else rc.hidden = true;
    const hc = $('#nav-history-count');
    hc.textContent = nf.format(state.history.length);
    hc.hidden = !state.history.length;
  }
  setInterval(() => { if (state.scan && state.scan.running) renderNavCounts(); }, 500);

  /* ---------- Shell ---------- */

  const sidebar = $('#app-sidebar');
  const backdrop = $('#mobile-backdrop');
  function openDrawer() {
    sidebar.classList.add('drawer-open'); backdrop.classList.add('open');
    $('#btn-mobile-menu').setAttribute('aria-expanded', 'true');
  }
  function closeDrawer() {
    sidebar.classList.remove('drawer-open'); backdrop.classList.remove('open');
    $('#btn-mobile-menu').setAttribute('aria-expanded', 'false');
  }
  function setCollapsed(collapsed) {
    sidebar.classList.toggle('collapsed', collapsed);
    const btn = $('#btn-collapse');
    const label = collapsed ? t('sidebar.expand') : t('sidebar.collapse');
    btn.setAttribute('aria-expanded', String(!collapsed));
    btn.setAttribute('aria-label', label);
    btn.querySelector('.hide-collapsed').textContent = label;
    save('wm.sidebar', collapsed);
  }

  async function init() {
    await loadLanguage(resolveLang(readLangPref()));
    applyStaticText();
    document.querySelectorAll('[data-icon]').forEach(el => {
      el.prepend(icon(el.dataset.icon, parseInt(el.dataset.size || '18', 10)));
      if (el.tagName === 'SPAN') el.replaceWith(...el.childNodes);
    });
    const isMac = /Mac|iPhone|iPad/.test(navigator.platform || navigator.userAgent);
    $('#search-kbd').textContent = isMac ? '⌘K' : 'Ctrl K';

    $('#btn-mobile-menu').addEventListener('click', openDrawer);
    $('#btn-mobile-close').addEventListener('click', closeDrawer);
    backdrop.addEventListener('click', closeDrawer);
    $('#btn-collapse').addEventListener('click', () => setCollapsed(!sidebar.classList.contains('collapsed')));
    setCollapsed(!!load('wm.sidebar', false));

    const global = $('#global-search');
    global.addEventListener('input', e => setQuery(e.target.value, e.target));
    global.addEventListener('keydown', e => {
      if (e.key === 'Escape') { setQuery('', null); global.blur(); }
      if (e.key === 'Enter') {
        e.preventDefault();
        if (!['results', 'catalog', 'history'].includes(state.route.name)) {
          const q = state.query;
          navigate('#/catalog');
          setQuery(q);
        }
        closeDrawer();
      }
    });
    document.addEventListener('keydown', e => {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k') {
        e.preventDefault();
        const page = document.querySelector('[data-page-search]');
        if (window.innerWidth < 1024 && page) page.focus();
        else { if (sidebar.classList.contains('collapsed')) setCollapsed(false); global.focus(); global.select(); }
      }
      if ((e.metaKey || e.ctrlKey) && e.key === 'Enter' && state.route.name === 'scan') {
        const form = document.querySelector('#view form');
        if (form) { e.preventDefault(); form.requestSubmit(); }
      }
      if (e.key === 'Escape' && sidebar.classList.contains('drawer-open')) closeDrawer();
    });

    window.addEventListener('hashchange', onRoute);
    state.route = parseRoute();
    renderHealth();
    renderNavCounts();
    renderView();
    checkHealth();
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();

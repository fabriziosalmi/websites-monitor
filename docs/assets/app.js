/*
  Website Monitor web UI.

  Every check runs as its own POST /monitor/single request, a few at a time,
  so results arrive as each check finishes, a single check can be retried,
  and a scan can be cancelled. All text that comes from the API or from the
  scanned site goes into the page through textContent, never innerHTML.

  A check's verdict is the emoji it starts with, as the checks return it:
  green passed, yellow or orange warning, red failed, white no verdict
  (error, timeout or not applicable). Nothing else is guessed.
*/
(function () {
  'use strict';

  /* ---------- Catalog ---------- */

  const CATEGORIES = [
    { id: 'security', label: 'Security', icon: 'shield' },
    { id: 'performance', label: 'Performance', icon: 'gauge' },
    { id: 'seo', label: 'SEO and content', icon: 'search' },
    { id: 'domain', label: 'Domain and DNS', icon: 'server' },
    { id: 'privacy', label: 'Privacy and tracking', icon: 'eye-off' },
    { id: 'accessibility', label: 'Accessibility and mobile', icon: 'accessibility' },
    { id: 'technical', label: 'Technical', icon: 'cpu' },
  ];
  const CATEGORY = Object.fromEntries(CATEGORIES.map(c => [c.id, c]));

  const CHECKS = [
    ['ssl_cert', 'SSL certificate', 'Validity and days to expiry', 'security'],
    ['ssl_cipher_strength', 'TLS cipher strength', 'Negotiated cipher suite', 'security'],
    ['security_headers', 'Security headers', 'CSP, X-Frame-Options and others', 'security'],
    ['hsts', 'HSTS', 'Strict-Transport-Security header', 'security'],
    ['xss_protection', 'XSS protection', 'X-XSS-Protection header', 'security'],
    ['cors_headers', 'CORS policy', 'Cross-origin response headers', 'security'],
    ['mixed_content', 'Mixed content', 'HTTP resources on HTTPS pages', 'security'],
    ['subresource_integrity', 'Subresource integrity', 'SRI on external scripts and styles', 'security'],
    ['rate_limiting', 'Rate limiting', 'Response to a burst of requests', 'security'],
    ['data_leakage', 'Data leakage', 'Mentions in public GitHub code', 'security'],

    ['pagespeed_performances', 'PageSpeed score', 'Google PageSpeed Insights', 'performance'],
    ['website_load_time', 'Load time', 'Total time to load the page', 'performance'],
    ['server_response_time', 'Server response time', 'Time to first byte', 'performance'],
    ['brotli_compression', 'Brotli compression', 'Content-Encoding: br', 'performance'],
    ['asset_minification', 'Asset minification', 'CSS and JavaScript minified', 'performance'],
    ['cdn', 'CDN', 'Content delivery network in front', 'performance'],
    ['redirect_chains', 'Redirect chains', 'Number of hops to the final URL', 'performance'],
    ['redirects', 'HTTPS redirect', 'HTTP redirects to HTTPS', 'performance'],

    ['sitemap', 'Sitemap', 'sitemap.xml present and valid', 'seo'],
    ['robot_txt', 'robots.txt', 'Present and well formed', 'seo'],
    ['open_graph_protocol', 'Open Graph tags', 'Social sharing metadata', 'seo'],
    ['alt_tags', 'Image alt text', 'Every image has an alt attribute', 'seo'],
    ['semantic_markup', 'Semantic markup', 'Structured data in the page', 'seo'],
    ['url_canonicalization', 'Canonical URL', 'rel="canonical" link', 'seo'],
    ['favicon', 'Favicon', 'Site icon present', 'seo'],
    ['broken_links', 'Broken links', 'Internal links that fail', 'seo'],
    ['external_links', 'External links', 'Outbound links reachable', 'seo'],

    ['domain_expiration', 'Domain expiration', 'Registration expiry date', 'domain'],
    ['dnssec', 'DNSSEC', 'Signed DNS zone', 'domain'],
    ['dns_blacklist', 'DNS blocklists', 'Listed on DNS-based blocklists', 'domain'],
    ['domain_breach', 'Breach exposure', 'Domain in known data breaches', 'domain'],
    ['domainsblacklists_blacklist', 'Domain blocklists', 'Aggregated threat lists', 'domain'],
    ['subdomain_enumeration', 'Subdomains', 'Common subdomains that resolve', 'domain'],
    ['email_domain', 'Email records', 'SPF and mail records', 'domain'],

    ['cookie_policy', 'Cookie policy', 'Policy page linked', 'privacy'],
    ['cookie_flags', 'Cookie flags', 'Secure and HttpOnly set', 'privacy'],
    ['cookie_duration', 'Cookie duration', 'Session cookie lifetimes', 'privacy'],
    ['cookie_samesite_attribute', 'Cookie SameSite', 'SameSite attribute set', 'privacy'],
    ['ad_and_tracking', 'Ads and tracking', 'Analytics and ad scripts', 'privacy'],
    ['floc', 'FLoC opt-out', 'interest-cohort permission policy', 'privacy'],
    ['privacy_exposure', 'Privacy exposure', 'Sensitive data in the page', 'privacy'],
    ['privacy_protected_whois', 'WHOIS privacy', 'Registrant data redacted', 'privacy'],
    ['third_party_requests', 'Third-party requests', 'Requests to other domains', 'privacy'],
    ['third_party_resources', 'Third-party resources', 'Scripts and styles from other domains', 'privacy'],

    ['accessibility', 'Accessibility', 'Accessibility score', 'accessibility'],
    ['mobile_friendly', 'Mobile friendly', 'Viewport and responsive layout', 'accessibility'],
    ['amp_compatibility', 'AMP', 'AMP version available', 'accessibility'],
    ['internationalization', 'Internationalization', 'lang and hreflang attributes', 'accessibility'],
    ['browser_compatibility', 'Browser compatibility', 'Markup older browsers handle', 'accessibility'],

    ['content_type_headers', 'Content-Type header', 'MIME type and charset', 'technical'],
    ['cms_used', 'CMS detection', 'Platform behind the site', 'technical'],
    ['clientside_rendering', 'Client-side rendering', 'Content rendered by JavaScript', 'technical'],
    ['deprecated_libraries', 'Deprecated libraries', 'Outdated JavaScript libraries', 'technical'],
  ].map(([id, name, hint, cat], order) => ({ id, name, hint, cat, order }));
  const CHECK = Object.fromEntries(CHECKS.map(c => [c.id, c]));

  const STATUS = {
    fail: { label: 'Failed', badge: 'badge-danger', dot: 'dot-danger', rank: 0 },
    warn: { label: 'Warning', badge: 'badge-warning', dot: 'dot-warning', rank: 1 },
    unknown: { label: 'No verdict', badge: 'badge-neutral', dot: 'dot-unknown', rank: 2 },
    pass: { label: 'Passed', badge: 'badge-success', dot: 'dot-success', rank: 3 },
    running: { label: 'Running', badge: 'badge-accent', rank: 4 },
    queued: { label: 'Queued', badge: 'badge-neutral', rank: 5 },
    cancelled: { label: 'Cancelled', badge: 'badge-neutral', rank: 6 },
  };
  const VERDICT_EMOJI = [['🟢', 'pass'], ['🟡', 'warn'], ['🟠', 'warn'], ['🔴', 'fail'], ['⚪', 'unknown']];
  const DONE = new Set(['pass', 'warn', 'fail', 'unknown']);
  const HISTORY_CAP = 20;

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

  const nf = new Intl.NumberFormat('en-US');
  function fmtDuration(ms) {
    if (ms === null || ms === undefined || !Number.isFinite(ms)) return '';
    if (ms < 1000) return `${Math.round(ms)} ms`;
    const s = ms / 1000;
    if (s < 60) return `${s.toFixed(s < 10 ? 1 : 0)} s`;
    const m = Math.floor(s / 60);
    return `${m} min ${Math.round(s - m * 60)} s`;
  }
  function fmtTime(ts) {
    return new Date(ts).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
  }
  function fmtDateTime(ts) {
    const d = new Date(ts);
    const today = new Date();
    const sameDay = d.toDateString() === today.toDateString();
    const time = d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    return sameDay ? `Today ${time}` : `${d.toLocaleDateString([], { day: 'numeric', month: 'short', year: 'numeric' })} ${time}`;
  }
  function plural(n, one, many) { return `${nf.format(n)} ${n === 1 ? one : (many || one + 's')}`; }

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
    if (r && r.status === 'error') { status = 'unknown'; if (!error) error = 'The check raised an error'; }
    return { status, text, error };
  }

  function tally(rows) {
    const t = { pass: 0, warn: 0, fail: 0, unknown: 0, running: 0, queued: 0, cancelled: 0, total: rows.length };
    for (const r of rows) t[r.status] = (t[r.status] || 0) + 1;
    t.done = t.pass + t.warn + t.fail + t.unknown;
    t.verdicts = t.pass + t.warn + t.fail;
    t.passRate = t.verdicts ? Math.round((t.pass / t.verdicts) * 100) : null;
    return t;
  }
  function entryDuration(e) {
    return e.finishedAt ? e.finishedAt - e.startedAt : (isRunning(e) ? Date.now() - e.startedAt : null);
  }
  function isRunning(e) { return !!(state.scan && state.scan.id === e.id && state.scan.running); }

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
      if (body === null) throw new Error('The API did not answer with JSON');
      return body;
    } catch (e) {
      if (outerSignal && outerSignal.aborted) throw new DOMException('Cancelled', 'AbortError');
      if (e.name === 'AbortError') throw new Error(`No answer within ${Math.round(timeoutMs / 1000)} s`);
      if (e instanceof TypeError) throw new Error('The API could not be reached');
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
      if (body.status !== 'healthy') throw new Error(`The API reports "${body.status}"`);
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
      text.textContent = `API ${a.version ? 'v' + a.version : 'online'}${a.total ? ` · ${a.total} checks` : ''}`;
    } else if (a.status === 'down') {
      text.textContent = 'API unreachable';
    } else {
      text.textContent = 'Checking API';
    }
    $('#health-row').title = a.status === 'down' ? `${apiDisplay()}: ${a.error}` : apiDisplay();
    const docs = $('#nav-api-docs');
    docs.href = a.status === 'ok' ? apiUrl('/api/docs') : 'swagger.html';
    $('#sb-sub').textContent = apiBase() ? apiBase().replace(/^https?:\/\//, '') : 'Security, speed, SEO';
  }

  /* ---------- Scan engine ---------- */

  function newId() {
    return Date.now().toString(36) + Math.random().toString(36).slice(2, 7);
  }

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
      const t = tally(scan.rows);
      toast(scan.cancelled
        ? `Scan cancelled after ${plural(t.done, 'check')}`
        : `${scan.target}: ${t.pass} passed, ${t.warn} warnings, ${t.fail} failed`, scan.cancelled ? 'info' : 'check');
      renderNavCounts();
      if (state.route.name === 'results') renderView();
    });
    renderNavCounts();
  }
  let ticker = null;
  function warnBeforeUnload(e) { e.preventDefault(); e.returnValue = ''; }

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
      if (!r) throw new Error('The API returned no result for this check');
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
    if (state.scan && state.scan.running) { toast('Wait for the running scan to finish', 'info'); return; }
    const row = entry.rows.find(r => r.id === id);
    if (!row) return;
    const live = state.scan && state.scan.id === entry.id ? state.scan : entry;
    const liveRow = live.rows.find(r => r.id === id);
    live.timeout = live.timeout || clampInt(state.settings.timeout, 5, 300, 30);
    await runCheck(live, liveRow);
    upsertHistory(live);
    const status = STATUS[liveRow.status];
    toast(`${CHECK[id] ? CHECK[id].name : id}: ${status ? status.label.toLowerCase() : liveRow.status}`, 'retry');
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
    return entry.rows.map(r => {
      const c = CHECK[r.id] || { name: r.id, cat: 'other' };
      return {
        id: r.id, name: c.name, category: c.cat, status: r.status,
        result: r.text || '', error: r.error || '', duration_ms: r.ms === null ? null : Math.round(r.ms),
      };
    });
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
    const t = tally(entry.rows);
    const doc = {
      target: entry.target,
      started_at: new Date(entry.startedAt).toISOString(),
      finished_at: entry.finishedAt ? new Date(entry.finishedAt).toISOString() : null,
      duration_ms: entryDuration(entry),
      cancelled: !!entry.cancelled,
      api: apiDisplay(),
      timeout_s: entry.timeout,
      summary: { passed: t.pass, warnings: t.warn, failed: t.fail, no_verdict: t.unknown, pass_rate_percent: t.passRate },
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
    const base = apiDisplay();
    const body = JSON.stringify({ website: target || 'example.com', checks: [id] });
    return `curl -s -X POST '${base}/monitor/single' -H 'Content-Type: application/json' -d '${body}'`;
  }
  async function copyText(text, what) {
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
    toast(ok ? `${what} copied` : `Could not copy ${what.toLowerCase()}`, ok ? 'copy' : 'alert');
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
      s.label);
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
  function segmented(label, options, value, onChange) {
    return h('div', { class: 'segmented', role: 'group', 'aria-label': label },
      options.map(o => h('button', {
        type: 'button', 'aria-pressed': String(o.value === value), dataset: { value: o.value },
        onclick: () => onChange(o.value),
      }, o.label, o.count !== undefined ? h('span', { class: 'seg-count', text: nf.format(o.count) }) : null)));
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
    return h('div', { class: 'notice notice-warning', role: 'alert' },
      icon('alert', 18),
      h('div', null,
        h('p', { class: 'notice-title', text: onPages ? 'This page has no API behind it' : 'The API is not reachable' }),
        h('p', null,
          onPages
            ? ['This copy of the interface is static. Start the API (', h('code', { text: 'docker compose up -d website-monitor-api' }), ') and set its address in ', h('a', { href: '#/settings', text: 'Settings' }), '. An HTTPS page can only call an HTTPS API.']
            : [`${apiDisplay()}: ${state.api.error || 'no answer'}. Check that the API is running, or change its address in `, h('a', { href: '#/settings', text: 'Settings' }), '.'])));
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
    const needle = q.toLowerCase();
    return fields.some(f => f && String(f).toLowerCase().includes(needle));
  }

  /* ---------- View: new scan ---------- */

  function normalizeTarget(input) {
    let s = (input || '').trim();
    if (!s) return { empty: true };
    if (!/^[a-z][a-z0-9+.-]*:\/\//i.test(s)) s = 'https://' + s;
    let u;
    try { u = new URL(s); } catch (e) { return { error: 'This is not a valid domain or URL.' }; }
    if (u.protocol !== 'http:' && u.protocol !== 'https:') return { error: 'Only http and https addresses can be checked.' };
    const host = u.hostname.toLowerCase().replace(/\.$/, '');
    if (!host || (!host.includes('.') && host !== 'localhost')) return { error: 'Enter a full domain, such as example.com.' };
    const dropped = [];
    if (u.port) dropped.push('port');
    if ((u.pathname && u.pathname !== '/') || u.search) dropped.push('path');
    return { host, dropped };
  }

  function renderScanView(view) {
    const prefill = state.route.query.get('target') || state.lastTarget || '';
    const running = !!(state.scan && state.scan.running);
    const input = h('input', {
      id: 'target', class: 'form-input', type: 'text', inputmode: 'url', autocomplete: 'url', spellcheck: 'false',
      placeholder: 'example.com or https://example.com', 'aria-describedby': 'target-help', value: prefill,
    });
    const help = h('p', { id: 'target-help', class: 'field-help', 'aria-live': 'polite' });
    const runBtn = button('Run', { iconName: running ? 'loader' : 'play', variant: 'primary', type: 'submit', disabled: running });
    if (running) runBtn.querySelector('svg').classList.add('spin');

    const updateHelp = () => {
      const n = normalizeTarget(input.value);
      state.lastTarget = input.value;
      input.removeAttribute('aria-invalid');
      help.className = 'field-help';
      if (n.empty) help.textContent = 'A domain or a URL. Checks run against the domain.';
      else if (n.error) { help.textContent = n.error; help.className = 'field-help is-error'; }
      else {
        help.textContent = `Checks will run against ${n.host}` + (n.dropped.length ? ` (the ${n.dropped.join(' and ')} is ignored).` : '.');
      }
    };
    const updateRunLabel = () => {
      const n = state.selection.size;
      runBtn.querySelector('span').textContent = running ? 'Scan running' : n === CHECKS.length ? `Run all ${n} checks` : `Run ${plural(n, 'check')}`;
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
          help.textContent = n.error || 'Enter the domain to check.';
          input.focus();
          return;
        }
        if (!state.selection.size) { toast('Select at least one check', 'alert'); return; }
        startScan(n.host, Array.from(state.selection));
      },
    },
    h('div', { class: 'field' },
      h('label', { class: 'field-label', for: 'target', text: 'Website' }),
      h('div', { class: 'target-row' }, h('div', { class: 'input-icon' }, icon('globe', 16), input), runBtn),
      help),
    recentTargets(input, updateHelp),
    h('p', { class: 'text-muted' },
      `Each check gets ${state.settings.timeout} s on the server, ${plural(state.settings.concurrency, 'check')} at a time. `,
      h('a', { href: '#/settings', text: 'Change' })));

    const selCount = h('span');
    const picker = h('div', { class: 'picker-grid' });
    const refreshPicker = () => {
      selCount.textContent = `${state.selection.size} of ${CHECKS.length} selected`;
      picker.querySelectorAll('[data-cat]').forEach(card => {
        const cat = card.dataset.cat;
        const ids = CHECKS.filter(c => c.cat === cat).map(c => c.id);
        const on = ids.filter(id => state.selection.has(id)).length;
        const box = card.querySelector('.picker-cat-head input');
        box.checked = on === ids.length;
        box.indeterminate = on > 0 && on < ids.length;
        card.classList.toggle('is-off', on === 0);
        card.querySelector('.picker-cat-count').textContent = `${on}/${ids.length}`;
        card.querySelectorAll('.picker-item input').forEach(i => { i.checked = state.selection.has(i.value); });
      });
      save('wm.selection', Array.from(state.selection));
      updateRunLabel();
    };
    for (const cat of CATEGORIES) {
      const items = CHECKS.filter(c => c.cat === cat.id);
      const head = h('input', {
        type: 'checkbox', class: 'check', 'aria-label': `All ${cat.label} checks`,
        onchange: e => { items.forEach(c => e.target.checked ? state.selection.add(c.id) : state.selection.delete(c.id)); refreshPicker(); },
      });
      picker.appendChild(h('div', { class: 'picker-cat', dataset: { cat: cat.id } },
        h('label', { class: 'picker-cat-head' },
          head,
          h('span', { class: 'picker-cat-icon' }, icon(cat.icon, 16)),
          h('span', { class: 'picker-cat-name', text: cat.label }),
          h('span', { class: 'picker-cat-count' })),
        h('ul', { class: 'picker-list' }, items.map(c => h('li', null,
          h('label', { class: 'picker-item' },
            h('input', {
              type: 'checkbox', class: 'check', value: c.id,
              onchange: e => { e.target.checked ? state.selection.add(c.id) : state.selection.delete(c.id); refreshPicker(); },
            }),
            h('span', { class: 'picker-item-text' },
              h('span', { class: 'picker-item-name', text: c.name }),
              h('span', { class: 'picker-item-hint', text: c.hint }))))))));
    }

    append(view, [
      pageHeader({
        eyebrow: 'Analyze', title: 'New scan',
        desc: 'Run checks against one website. Results appear as each check finishes.',
      }),
      apiDownNotice(),
      panel({ title: 'Target', body: form }),
      panel({
        title: 'Checks', desc: selCount,
        actions: [
          button('Select all', { size: 'sm', onclick: () => { CHECKS.forEach(c => state.selection.add(c.id)); refreshPicker(); } }),
          button('Clear', { size: 'sm', onclick: () => { state.selection.clear(); refreshPicker(); } }),
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
      h('span', { class: 'text-muted', text: 'Recent:' }),
      seen.slice(0, 6).map(t => h('button', {
        type: 'button', class: 'chip', text: t,
        onclick: () => { input.value = t; onPick(); input.focus(); },
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
        pageHeader({ eyebrow: 'Analyze', title: 'Results' }),
        h('div', { class: 'panel' }, emptyState('gauge', state.route.param ? 'This scan is no longer in the history' : 'No scan yet',
          'Run a scan and its results show up here, check by check, as they arrive.',
          h('a', { class: 'btn btn-primary', href: '#/scan' }, icon('play', 16), h('span', { text: 'New scan' })))),
      ]);
      return;
    }
    const running = isRunning(entry);
    const actions = running
      ? [button('Cancel scan', { iconName: 'stop', variant: 'danger', onclick: cancelScan })]
      : [
        button('Print', { iconName: 'printer', onclick: () => window.print() }),
        button('CSV', { iconName: 'download', onclick: () => exportCsv(entry) }),
        button('JSON', { iconName: 'download', onclick: () => exportJson(entry) }),
        button('Run again', {
          iconName: 'retry', variant: 'primary', disabled: !!(state.scan && state.scan.running),
          onclick: () => startScan(entry.target, entry.rows.map(r => r.id)),
        }),
      ];
    ui.desc = h('span');
    ui.progress = h('div');
    ui.stats = h('div', { class: 'stats-grid' });
    ui.cats = h('div', { class: 'cat-bars' });
    ui.seg = h('div');
    ui.catSelect = h('select', {
      class: 'form-input filter-select', 'aria-label': 'Category',
      onchange: e => { state.filter.category = e.target.value; refreshResults(); },
    }, h('option', { value: 'all', text: 'All categories' }), CATEGORIES.map(c => h('option', { value: c.id, text: c.label })));
    ui.catSelect.value = state.filter.category;
    ui.tbody = h('tbody');
    ui.entry = entry;

    append(view, [
      pageHeader({ eyebrow: running ? 'Scan running' : 'Results', title: entry.target, desc: ui.desc, actions }),
      entry.cancelled && !running ? h('div', { class: 'notice notice-info' }, icon('info', 18),
        h('p', { text: 'This scan was cancelled: checks that had not finished are marked as cancelled.' })) : null,
      ui.progress,
      ui.stats,
      h('div', { class: 'layout-2' },
        panel({
          title: 'Checks',
          toolbar: [ui.seg, ui.catSelect, searchBox('Filter checks')],
          flush: true,
          body: h('div', { class: 'table-wrap' }, h('table', { class: 'data-table' },
            h('thead', null, h('tr', null,
              h('th', { class: 'col-status', text: 'Status' }),
              h('th', { text: 'Check' }),
              h('th', { class: 'col-num', text: 'Time' }),
              h('th', null, h('span', { class: 'sr-only', text: 'Actions' })))),
            ui.tbody)),
        }),
        panel({
          title: 'By category', desc: 'Passed, warnings, failed and no verdict, per category.',
          body: [ui.cats, h('div', { class: 'legend' },
            [['seg-pass', 'Passed'], ['seg-warn', 'Warning'], ['seg-fail', 'Failed'], ['seg-unknown', 'No verdict']]
              .map(([cls, label]) => h('span', null, h('span', { class: `dot ${cls}`, 'aria-hidden': 'true' }), label)))],
        })),
    ]);
    refreshResults();
  }

  function refreshResultsMeta() {
    const entry = ui.entry;
    if (!entry || !ui.desc) return;
    const t = tally(entry.rows);
    const running = isRunning(entry);
    const parts = [plural(entry.rows.length, 'check'), `started ${fmtDateTime(entry.startedAt)}`];
    const dur = entryDuration(entry);
    if (dur !== null) parts.push(running ? `${fmtDuration(dur)} so far` : `took ${fmtDuration(dur)}`);
    ui.desc.textContent = parts.join(' · ');

    clear(ui.progress);
    if (running) {
      const pct = n => `${(n / t.total) * 100}%`;
      ui.progress.appendChild(h('div', { class: 'panel' }, h('div', { class: 'run-strip' },
        h('div', { class: 'run-strip-meta' },
          h('span', null, h('strong', { text: `${t.done} of ${t.total}` }), ' checks done',
            t.running ? ` · ${t.running} running` : ''),
          h('span', { text: `${fmtDuration(dur)} elapsed` })),
        h('div', {
          class: 'progress', role: 'progressbar', 'aria-label': 'Scan progress',
          'aria-valuemin': '0', 'aria-valuemax': String(t.total), 'aria-valuenow': String(t.done),
        },
        h('span', { class: 'seg-pass', style: `width:${pct(t.pass)}` }),
        h('span', { class: 'seg-warn', style: `width:${pct(t.warn)}` }),
        h('span', { class: 'seg-fail', style: `width:${pct(t.fail)}` }),
        h('span', { class: 'seg-unknown', style: `width:${pct(t.unknown)}` }),
        h('span', { class: 'seg-running', style: `width:${pct(t.running)}` })))));
    }
  }

  function refreshResults() {
    const entry = ui.entry;
    if (!entry || !ui.tbody || !document.body.contains(ui.tbody)) return;
    const t = tally(entry.rows);
    const running = isRunning(entry);
    refreshResultsMeta();

    clear(ui.stats);
    const rateTone = t.passRate === null ? null : t.passRate >= 80 ? 'success' : t.passRate >= 50 ? 'warning' : 'danger';
    append(ui.stats, [
      statCard('Pass rate', t.passRate === null ? '' : `${t.passRate}%`, {
        tone: rateTone, missing: t.passRate === null ? (running ? 'Waiting for results' : 'No verdicts') : null,
        sub: t.verdicts ? `${t.pass} of ${plural(t.verdicts, 'check')} with a verdict` : 'Checks that passed, warned or failed',
      }),
      statCard('Failed', nf.format(t.fail), { tone: t.fail ? 'danger' : null, sub: 'Needs fixing' }),
      statCard('Warnings', nf.format(t.warn), { tone: t.warn ? 'warning' : null, sub: 'Worth a look' }),
      statCard('No verdict', nf.format(t.unknown), { sub: 'Error, timeout or not applicable' }),
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
            type: 'button', class: 'btn-link cat-bar-name', text: cat.label,
            title: `Show only ${cat.label}`,
            onclick: () => { state.filter.category = cat.id; ui.catSelect.value = cat.id; refreshResults(); },
          }),
          h('span', { class: 'cat-bar-count', text: `${ct.pass} of ${ct.total} passed` })),
        h('div', { class: 'progress', 'aria-hidden': 'true' },
          ct.pass ? h('span', { class: 'seg-pass', style: `width:${w(ct.pass)}` }) : null,
          ct.warn ? h('span', { class: 'seg-warn', style: `width:${w(ct.warn)}` }) : null,
          ct.fail ? h('span', { class: 'seg-fail', style: `width:${w(ct.fail)}` }) : null,
          ct.unknown ? h('span', { class: 'seg-unknown', style: `width:${w(ct.unknown)}` }) : null)));
    }

    clear(ui.seg);
    ui.seg.appendChild(segmented('Status', [
      { value: 'all', label: 'All', count: t.total },
      { value: 'fail', label: 'Failed', count: t.fail },
      { value: 'warn', label: 'Warnings', count: t.warn },
      { value: 'unknown', label: 'No verdict', count: t.unknown },
      { value: 'pass', label: 'Passed', count: t.pass },
    ], state.filter.status, v => { state.filter.status = v; refreshResults(); }));

    const rows = entry.rows
      .filter(r => state.filter.status === 'all' || r.status === state.filter.status)
      .filter(r => state.filter.category === 'all' || (CHECK[r.id] && CHECK[r.id].cat === state.filter.category))
      .filter(r => { const c = CHECK[r.id] || {}; return matches(state.query, c.name, r.id, r.text, r.error, c.hint); });
    if (!running) {
      rows.sort((a, b) => (STATUS[a.status] || STATUS.unknown).rank - (STATUS[b.status] || STATUS.unknown).rank
        || ((CHECK[a.id] || {}).order || 0) - ((CHECK[b.id] || {}).order || 0));
    }

    clear(ui.tbody);
    if (!rows.length) {
      ui.tbody.appendChild(h('tr', null, h('td', { colspan: '4', class: 'empty-row-cell', text: 'No check matches these filters.' })));
      return;
    }
    const busy = !!(state.scan && state.scan.running);
    for (const r of rows) {
      const c = CHECK[r.id] || { name: r.id, cat: 'technical' };
      const result = r.error
        ? h('div', { class: 'cell-error', text: r.error })
        : r.text ? h('div', { class: 'cell-result', text: r.text })
          : null;
      ui.tbody.appendChild(h('tr', { dataset: { check: r.id } },
        h('td', { class: 'col-status' }, statusBadge(r.status)),
        h('td', null,
          h('div', { class: 'cell-primary', text: c.name }),
          h('div', { class: 'cell-sub' }, (CATEGORY[c.cat] || { label: c.cat }).label, ' · ', h('code', { text: r.id })),
          result),
        h('td', { class: 'col-num', 'data-label': 'Time', text: fmtDuration(r.ms) }),
        h('td', { class: 'col-right' }, h('div', { class: 'action-group' },
          iconButton(r.status === 'running' ? 'loader' : 'retry', `Run ${c.name} again`, () => retryCheck(entry, r.id),
            { disabled: busy, spin: r.status === 'running' }),
          iconButton('copy', `Copy the curl command for ${c.name}`, () => copyText(curlFor(entry.target, r.id), 'curl command'))))));
    }
  }

  /* ---------- View: history ---------- */

  let clearArmed = null;
  function clearHistoryButton() {
    const btn = button('Clear history', {
      iconName: 'trash', variant: 'danger', disabled: !state.history.length,
      onclick: () => {
        if (clearArmed) {
          clearTimeout(clearArmed); clearArmed = null;
          const keep = state.scan && state.scan.running ? state.history.filter(e => e.id === state.scan.id) : [];
          state.history = keep;
          saveHistory();
          toast('History cleared', 'trash');
          renderView();
          return;
        }
        btn.querySelector('span').textContent = 'Click again to clear';
        clearArmed = setTimeout(() => { clearArmed = null; btn.querySelector('span').textContent = 'Clear history'; }, 3000);
      },
    });
    return btn;
  }

  function renderHistoryView(view) {
    ui.historyBody = h('tbody');
    append(view, [
      pageHeader({
        eyebrow: 'Analyze', title: 'History',
        desc: `The last ${HISTORY_CAP} scans, kept in this browser only.`,
        actions: [clearHistoryButton()],
      }),
      state.history.length
        ? panel({
          title: 'Scans', desc: plural(state.history.length, 'scan'), flush: true,
          toolbar: [searchBox('Filter by domain')],
          body: h('div', { class: 'table-wrap' }, h('table', { class: 'data-table' },
            h('thead', null, h('tr', null,
              ['Target', 'Started', 'Pass rate', 'Failed', 'Warnings', 'No verdict', 'Duration'].map((t, i) =>
                h('th', { class: i >= 2 ? 'col-num' : null, text: t })),
              h('th', null, h('span', { class: 'sr-only', text: 'Actions' })))),
            ui.historyBody)),
        })
        : h('div', { class: 'panel' }, emptyState('history', 'No scans yet', 'Scans you run from this browser are listed here.',
          h('a', { class: 'btn btn-primary', href: '#/scan' }, icon('play', 16), h('span', { text: 'New scan' })))),
    ]);
    renderTableOnly();
  }

  function renderHistoryRows() {
    const body = ui.historyBody;
    if (!body) return;
    clear(body);
    const list = state.history.filter(e => matches(state.query, e.target));
    if (!list.length) {
      body.appendChild(h('tr', null, h('td', { colspan: '8', class: 'empty-row-cell', text: 'No scan matches this filter.' })));
      return;
    }
    const busy = !!(state.scan && state.scan.running);
    for (const e of list) {
      const t = tally(e.rows);
      const running = isRunning(e);
      body.appendChild(h('tr', null,
        h('td', null,
          h('a', { class: 'cell-primary', href: `#/results/${e.id}`, text: e.target }),
          h('div', { class: 'cell-sub', text: `${plural(e.rows.length, 'check')}${running ? ' · running' : e.cancelled ? ' · cancelled' : ''}` })),
        h('td', { 'data-label': 'Started', text: fmtDateTime(e.startedAt) }),
        h('td', { class: 'col-num', 'data-label': 'Pass rate', text: t.passRate === null ? '' : `${t.passRate}%` }),
        h('td', { class: 'col-num', 'data-label': 'Failed' }, t.fail ? h('span', { class: 'badge badge-danger', text: nf.format(t.fail) }) : '0'),
        h('td', { class: 'col-num', 'data-label': 'Warnings' }, t.warn ? h('span', { class: 'badge badge-warning', text: nf.format(t.warn) }) : '0'),
        h('td', { class: 'col-num', 'data-label': 'No verdict', text: nf.format(t.unknown) }),
        h('td', { class: 'col-num', 'data-label': 'Duration', text: running ? 'Running' : fmtDuration(entryDuration(e)) }),
        h('td', { class: 'col-right' }, h('div', { class: 'action-group' },
          iconButton('retry', `Scan ${e.target} again`, () => startScan(e.target, e.rows.map(r => r.id)), { disabled: busy }),
          iconButton('trash', `Delete the scan of ${e.target}`, () => {
            state.history = state.history.filter(x => x.id !== e.id);
            saveHistory();
            renderView();
          }, { disabled: running })))));
    }
  }

  /* ---------- View: catalog ---------- */

  function renderCatalogView(view) {
    ui.catalogBody = h('tbody');
    const catSelect = h('select', {
      class: 'form-input filter-select', 'aria-label': 'Category',
      onchange: e => { state.filter.category = e.target.value; renderTableOnly(); },
    }, h('option', { value: 'all', text: 'All categories' }), CATEGORIES.map(c => h('option', { value: c.id, text: c.label })));
    catSelect.value = state.filter.category;
    append(view, [
      pageHeader({
        eyebrow: 'Reference', title: 'Check catalog',
        desc: `The ${CHECKS.length} checks the API runs. Each one can be called on its own through POST /monitor/single or GET /check/{id}.`,
        actions: [h('a', { class: 'btn', href: '#/scan' }, icon('play', 16), h('span', { text: 'New scan' }))],
      }),
      panel({
        title: 'Checks', flush: true,
        desc: state.api.status === 'ok' ? 'Descriptions come from the API.' : 'Connect the API to see the full description of each check.',
        toolbar: [catSelect, searchBox('Filter checks')],
        body: h('div', { class: 'table-wrap' }, h('table', { class: 'data-table' },
          h('thead', null, h('tr', null,
            h('th', { text: 'Check' }), h('th', { text: 'Category' }), h('th', { text: 'What it looks at' }),
            h('th', null, h('span', { class: 'sr-only', text: 'Actions' })))),
          ui.catalogBody)),
      }),
    ]);
    renderTableOnly();
  }

  function renderCatalogRows() {
    const body = ui.catalogBody;
    if (!body) return;
    clear(body);
    const list = CHECKS
      .filter(c => state.filter.category === 'all' || c.cat === state.filter.category)
      .filter(c => matches(state.query, c.name, c.id, c.hint, state.api.descriptions[c.id], CATEGORY[c.cat].label));
    if (!list.length) {
      body.appendChild(h('tr', null, h('td', { colspan: '4', class: 'empty-row-cell', text: 'No check matches this filter.' })));
      return;
    }
    for (const c of list) {
      body.appendChild(h('tr', null,
        h('td', null, h('div', { class: 'cell-primary', text: c.name }), h('div', { class: 'cell-sub' }, h('code', { text: c.id }))),
        h('td', { 'data-label': 'Category' }, h('span', { class: 'badge badge-neutral', text: CATEGORY[c.cat].label })),
        h('td', { 'data-label': 'What it looks at' }, h('div', { class: 'cell-result', text: state.api.descriptions[c.id] || c.hint })),
        h('td', { class: 'col-right' }, h('div', { class: 'action-group' },
          iconButton('play', `Scan with ${c.name} only`, () => {
            state.selection = new Set([c.id]);
            save('wm.selection', [c.id]);
            navigate('#/scan');
          }),
          iconButton('copy', `Copy the curl command for ${c.name}`, () => copyText(curlFor(null, c.id), 'curl command'))))));
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
        toast('The address must start with http:// or https://', 'alert');
        return;
      }
      baseInput.removeAttribute('aria-invalid');
      state.settings.apiBase = v;
      save('wm.settings', state.settings);
      state.api = { status: 'unknown', version: null, total: null, descriptions: {}, error: null };
      renderHealth();
      await checkHealth();
      toast(state.api.status === 'ok' ? 'Connected to the API' : 'Saved, but the API does not answer', state.api.status === 'ok' ? 'check' : 'alert');
    };

    const timeout = h('input', { id: 's-timeout', class: 'form-input', type: 'number', min: '5', max: '300', step: '1', value: state.settings.timeout });
    const conc = h('input', { id: 's-conc', class: 'form-input', type: 'number', min: '1', max: '8', step: '1', value: state.settings.concurrency });
    const psk = h('input', { id: 's-psk', class: 'form-input mono', type: 'password', autocomplete: 'off', value: state.pagespeedKey, placeholder: 'Optional' });
    const saveScan = e => {
      e.preventDefault();
      state.settings.timeout = clampInt(timeout.value, 5, 300, 30);
      state.settings.concurrency = clampInt(conc.value, 1, 8, 4);
      timeout.value = state.settings.timeout;
      conc.value = state.settings.concurrency;
      state.pagespeedKey = psk.value.trim();
      save('wm.settings', state.settings);
      toast('Scan defaults saved', 'check');
    };

    const pref = load('wm.theme', null) || readTheme();
    const themeCards = [['system', 'System', 'Follow the operating system'], ['light', 'Light', 'Always light'], ['dark', 'Dark', 'Always dark']]
      .map(([value, title, help]) => h('label', { class: `radio-card${pref === value ? ' selected' : ''}`, dataset: { themeCard: value } },
        h('input', { type: 'radio', name: 'theme', value, checked: pref === value, onchange: () => applyTheme(value) }),
        h('span', null, h('span', { class: 'radio-title', text: title }), h('span', { class: 'radio-help', text: help }))));

    const sections = [
      ['api', 'API connection'], ['scan', 'Scan defaults'], ['appearance', 'Appearance'], ['data', 'Data in this browser'], ['about', 'About'],
    ];
    const kv = (label, value) => h('div', { class: 'kv-box' }, h('span', { class: 'kv-label', text: label }), h('span', { class: 'kv-val' }, value));

    append(view, [
      pageHeader({ eyebrow: 'System', title: 'Settings', desc: 'Where the API lives, how scans run, and how this page looks.' }),
      h('div', { class: 'settings-shell' },
        h('nav', { class: 'settings-nav', 'aria-label': 'Settings sections' },
          h('ul', { class: 'settings-nav-list' }, sections.map(([id, label], i) => h('li', null,
            h('button', {
              type: 'button', class: `settings-nav-btn${i === 0 ? ' active' : ''}`, text: label,
              onclick: ev => {
                view.querySelectorAll('.settings-nav-btn').forEach(b => b.classList.toggle('active', b === ev.currentTarget));
                document.getElementById(`set-${id}`).scrollIntoView({ behavior: 'smooth', block: 'start' });
              },
            }))))),
        h('div', { class: 'settings-content' },
          panel({
            id: 'set-api', title: 'API connection',
            desc: 'Leave the address empty when this page is served by the API itself.',
            body: h('form', { class: 'stack', onsubmit: saveApi, novalidate: true },
              h('div', { class: 'field' },
                h('label', { class: 'field-label', for: 'api-base', text: 'API address' }),
                baseInput,
                h('p', { id: 'api-base-help', class: 'field-help', text: 'For example http://localhost:8000. An HTTPS page can only reach an HTTPS API, and the API must allow this origin (it allows all by default).' })),
              h('div', { class: 'row' }, button('Save and test', { variant: 'primary', type: 'submit' })),
              h('div', { class: 'kv-grid' },
                kv('Status', [h('span', { class: `dot ${a.status === 'ok' ? 'dot-success' : a.status === 'down' ? 'dot-danger' : 'dot-unknown'}` }),
                  a.status === 'ok' ? 'Online' : a.status === 'down' ? 'Unreachable' : 'Checking']),
                kv('Version', a.version || 'Not reported'),
                kv('Checks available', a.total === null ? 'Not reported' : nf.format(a.total)),
                kv('Endpoint', h('code', { text: apiDisplay() }))),
              a.status === 'down' && a.error ? h('p', { class: 'field-help is-error', text: a.error }) : null),
          }),
          panel({
            id: 'set-scan', title: 'Scan defaults',
            body: h('form', { class: 'stack', onsubmit: saveScan, novalidate: true },
              h('div', { class: 'form-grid' },
                h('div', { class: 'field' }, h('label', { class: 'field-label', for: 's-timeout', text: 'Timeout per check (s)' }), timeout,
                  h('p', { class: 'field-help', text: 'Enforced by the server, from 5 to 300.' })),
                h('div', { class: 'field' }, h('label', { class: 'field-label', for: 's-conc', text: 'Checks in parallel' }), conc,
                  h('p', { class: 'field-help', text: 'Each check is its own request. From 1 to 8.' })),
                h('div', { class: 'field' }, h('label', { class: 'field-label', for: 's-psk', text: 'PageSpeed Insights API key' }), psk,
                  h('p', { class: 'field-help', text: 'Sent with the PageSpeed check only. Kept in this tab, never stored.' }))),
              h('div', { class: 'row' }, button('Save', { variant: 'primary', type: 'submit' }))),
          }),
          panel({ id: 'set-appearance', title: 'Appearance', body: h('fieldset', { class: 'radio-group' }, h('legend', { class: 'sr-only', text: 'Theme' }), themeCards) }),
          panel({
            id: 'set-data', title: 'Data in this browser',
            desc: `Scan history (the last ${HISTORY_CAP} scans), check selection, these settings and the theme live in this browser's local storage. Nothing is sent anywhere but the API.`,
            body: h('div', { class: 'row' }, clearHistoryButton()),
          }),
          panel({
            id: 'set-about', title: 'About',
            body: h('ul', { class: 'link-list' }, [
              ['github', 'Source code', 'github.com/fabriziosalmi/websites-monitor', 'https://github.com/fabriziosalmi/websites-monitor'],
              ['box', 'Docker image', 'hub.docker.com/r/fabriziosalmi/websites-monitor', 'https://hub.docker.com/r/fabriziosalmi/websites-monitor'],
              ['book', 'Interactive API docs', a.status === 'ok' ? 'Swagger UI served by the API' : 'Static Swagger UI', a.status === 'ok' ? apiUrl('/api/docs') : 'swagger.html'],
              ['book', 'ReDoc', 'API reference served by the API', apiUrl('/api/redoc')],
            ].map(([ic, title, desc, href]) => h('li', null, h('a', { href, target: '_blank', rel: 'noopener' },
              icon(ic, 18), h('span', { style: 'flex:1;min-width:0' }, h('span', { class: 'link-title', text: title }), h('br'), h('span', { class: 'link-desc', text: desc })),
              icon('external', 14))))),
          }))),
    ]);
  }

  /* ---------- Theme ---------- */

  const darkQuery = window.matchMedia('(prefers-color-scheme: dark)');
  function readTheme() { try { return localStorage.getItem('wm.theme') || 'system'; } catch (e) { return 'system'; } }
  function applyTheme(pref) {
    try { localStorage.setItem('wm.theme', pref); } catch (e) { /* the choice lasts for this page only */ }
    const dark = pref === 'dark' || (pref === 'system' && darkQuery.matches);
    document.documentElement.classList.toggle('dark', dark);
    document.querySelectorAll('[data-theme-card]').forEach(c => c.classList.toggle('selected', c.dataset.themeCard === pref));
  }
  darkQuery.addEventListener('change', () => { if (readTheme() === 'system') applyTheme('system'); });

  /* ---------- Router ---------- */

  const ROUTES = {
    scan: { label: 'New scan', render: renderScanView },
    results: { label: 'Results', render: renderResultsView },
    history: { label: 'History', render: renderHistoryView },
    catalog: { label: 'Check catalog', render: renderCatalogView },
    settings: { label: 'Settings', render: renderSettingsView },
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
    $('#mobile-page-label').textContent = entry ? entry.target : route.label;
    document.title = `${entry ? entry.target + ' · ' : ''}${route.label} · Website Monitor`;
    if (keepFocusId && document.getElementById(keepFocusId)) document.getElementById(keepFocusId).focus({ preventScroll: true });
  }

  function renderNavCounts() {
    const rc = $('#nav-results-count');
    if (state.scan && state.scan.running) {
      const t = tally(state.scan.rows);
      rc.textContent = `${t.done}/${t.total}`;
      rc.hidden = false;
    } else rc.hidden = true;
    const hc = $('#nav-history-count');
    hc.textContent = String(state.history.length);
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
    btn.setAttribute('aria-expanded', String(!collapsed));
    btn.setAttribute('aria-label', collapsed ? 'Expand sidebar' : 'Collapse sidebar');
    btn.querySelector('.hide-collapsed').textContent = collapsed ? 'Expand sidebar' : 'Collapse sidebar';
    save('wm.sidebar', collapsed);
  }

  function init() {
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
    if (load('wm.sidebar', false)) setCollapsed(true);

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

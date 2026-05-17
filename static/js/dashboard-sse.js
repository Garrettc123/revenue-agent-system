/**
 * dashboard-sse.js
 * Replaces the 5-second setInterval polling with a persistent SSE connection.
 * Drop-in replacement: add <script src="/static/js/dashboard-sse.js"></script>
 * to the dashboard HTML and remove the setInterval(updateDashboard, 5000) call.
 */

(function () {
  'use strict';

  // ── Helpers ────────────────────────────────────────────────────────────────

  function fmt(n, decimals = 2) {
    return Number(n).toLocaleString('en-US', {
      minimumFractionDigits: decimals,
      maximumFractionDigits: decimals,
    });
  }

  function setEl(id, value) {
    const el = document.getElementById(id);
    if (el) el.textContent = value;
  }

  function flash(id) {
    const el = document.getElementById(id);
    if (!el) return;
    el.classList.remove('sse-flash');
    // Force reflow so the animation restarts
    void el.offsetWidth;
    el.classList.add('sse-flash');
  }

  // ── Fetch helpers (same endpoints the old polling used) ────────────────────

  async function fetchJSON(url) {
    const r = await fetch(url);
    if (!r.ok) throw new Error(`${url} → ${r.status}`);
    return r.json();
  }

  async function refreshRevenue() {
    try {
      const d = await fetchJSON('/api/revenue');
      setEl('mrr', '$' + fmt(d.mrr));
      setEl('arr', '$' + fmt(d.arr));
      setEl('customers', d.customers);
      setEl('total-revenue', '$' + fmt(d.total_revenue));
      flash('mrr');
      flash('arr');
    } catch (e) {
      console.warn('[SSE] refreshRevenue failed:', e);
    }
  }

  async function refreshWealth() {
    try {
      const d = await fetchJSON('/api/wealth-index');
      setEl('wealth-index', fmt(d.wealth_index, 1));
      setEl('ltv', '$' + fmt(d.ltv));
    } catch (e) {
      console.warn('[SSE] refreshWealth failed:', e);
    }
  }

  async function refreshMaster() {
    try {
      const d = await fetchJSON('/api/masterwealth');
      setEl('master-wealth', '$' + fmt(d.total_wealth));
      setEl('master-mrr', '$' + fmt(d.mrr));
      setEl('master-arr', '$' + fmt(d.arr));
    } catch (e) {
      console.warn('[SSE] refreshMaster failed:', e);
    }
  }

  function refreshAll() {
    refreshRevenue();
    refreshWealth();
    refreshMaster();
  }

  // ── SSE connection ─────────────────────────────────────────────────────────

  let _es = null;
  let _reconnectDelay = 1000; // ms, doubles on each failure up to 30s
  const MAX_DELAY = 30000;

  function connect() {
    if (_es) {
      _es.close();
    }

    console.info('[SSE] connecting to /api/events/stream …');
    _es = new EventSource('/api/events/stream');

    _es.addEventListener('heartbeat', function () {
      console.debug('[SSE] heartbeat received');
      _reconnectDelay = 1000; // reset backoff on successful connection
    });

    // revenue_update fires on payment_intent.succeeded / charge.succeeded / invoice.payment_succeeded
    _es.addEventListener('revenue_update', function (e) {
      console.info('[SSE] revenue_update', e.data);
      refreshRevenue();
      refreshMaster();
    });

    // subscription_change fires on customer.subscription.created/updated/deleted
    _es.addEventListener('subscription_change', function (e) {
      console.info('[SSE] subscription_change', e.data);
      refreshAll();
    });

    _es.onerror = function (err) {
      console.warn('[SSE] connection error, reconnecting in', _reconnectDelay, 'ms', err);
      _es.close();
      _es = null;
      setTimeout(connect, _reconnectDelay);
      _reconnectDelay = Math.min(_reconnectDelay * 2, MAX_DELAY);
    };

    _es.onopen = function () {
      console.info('[SSE] connection established');
      _reconnectDelay = 1000;
      // Refresh immediately on (re)connect so the UI is fresh
      refreshAll();
    };
  }

  // ── Fallback polling (if SSE is not supported or blocked) ──────────────────

  function startFallbackPolling(intervalMs) {
    console.warn('[SSE] EventSource not supported — falling back to polling every', intervalMs, 'ms');
    setInterval(refreshAll, intervalMs);
  }

  // ── Inject CSS for flash animation ─────────────────────────────────────────

  const style = document.createElement('style');
  style.textContent = [
    '@keyframes sse-flash-anim {',
    '  0%   { background-color: rgba(72,199,142,.35); }',
    '  100% { background-color: transparent; }',
    '}',
    '.sse-flash { animation: sse-flash-anim .8s ease-out; }',
  ].join('\n');
  document.head.appendChild(style);

  // ── Boot ───────────────────────────────────────────────────────────────────

  if (typeof EventSource !== 'undefined') {
    connect();
  } else {
    startFallbackPolling(5000);
  }

  // Cancel SSE cleanly when page unloads
  window.addEventListener('beforeunload', function () {
    if (_es) _es.close();
  });

})();

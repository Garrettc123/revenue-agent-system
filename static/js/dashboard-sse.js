/**
 * dashboard-sse.js
 * Replaces the 5-second setInterval polling with a persistent SSE connection.
 * Drop-in replacement: add <script src="/static/js/dashboard-sse.js"></script>
 * to the dashboard HTML and remove the setInterval(updateDashboard, 5000) call.
 */

(function () {
  'use strict';

  // ── Helpers ────────────────────────────────────────────────────────────────

  function flash(id) {
    const el = document.getElementById(id);
    if (!el) return;
    el.classList.remove('sse-flash');
    // Force reflow so the animation restarts
    void el.offsetWidth;
    el.classList.add('sse-flash');
  }

  // ── Refresh helpers ────────────────────────────────────────────────────────
  // The dashboard template defines a global updateDashboard() that fetches
  // /api/revenue, /api/wealth-index, /api/masterwealth and /api/emergency-funds
  // and populates every element. Delegate to it so the element IDs and the
  // formatting rules live in exactly one place.

  function refreshAll() {
    if (typeof window.updateDashboard !== 'function') {
      console.warn('[SSE] updateDashboard() is not defined — nothing to refresh');
      return;
    }
    try {
      window.updateDashboard();
    } catch (e) {
      console.warn('[SSE] updateDashboard() failed:', e);
    }
  }

  function refreshRevenue() {
    refreshAll();
    flash('mrr');
    flash('arr');
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

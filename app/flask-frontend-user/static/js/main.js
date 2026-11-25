

(function () {
  'use strict';

  window.AD = window.AD || {};

  const prefersReducedMotion = () =>
    window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  let _uid = 0;
  const uid = (prefix = 'ad') => `${prefix}-${Date.now()}-${++_uid}`;

  const ADSidebar = (() => {
    let sidebarEl = null;
    let overlayEl = null;
    let hamburgerEl = null;
    let isOpen = false;

    function open() {
      if (!sidebarEl) return;
      isOpen = true;
      sidebarEl.classList.add('ad-sidebar--open');
      sidebarEl.classList.remove('ad-sidebar--collapsed');
      if (overlayEl) overlayEl.classList.add('ad-overlay--visible');
      document.body.classList.add('ad-sidebar-open');
      hamburgerEl && hamburgerEl.setAttribute('aria-expanded', 'true');
    }

    function close() {
      if (!sidebarEl) return;
      isOpen = false;
      sidebarEl.classList.remove('ad-sidebar--open');
      if (overlayEl) overlayEl.classList.remove('ad-overlay--visible');
      document.body.classList.remove('ad-sidebar-open');
      hamburgerEl && hamburgerEl.setAttribute('aria-expanded', 'false');
    }

    function toggle() {
      isOpen ? close() : open();
    }

    function highlightActive() {
      if (!sidebarEl) return;
      const path = window.location.pathname;
      const links = sidebarEl.querySelectorAll('.ad-nav-link, .ad-sidebar__link');

      links.forEach((link) => {
        link.classList.remove('ad-nav-link--active', 'active');
        const href = link.getAttribute('href');
        if (!href) return;

        if (href === path || (href !== '/' && path.startsWith(href))) {
          link.classList.add('ad-nav-link--active', 'active');
        }
      });
    }

    function init() {
      sidebarEl = document.querySelector('.ad-sidebar');
      overlayEl = document.querySelector('.ad-overlay');
      hamburgerEl = document.querySelector('.ad-hamburger');

      if (hamburgerEl) {
        hamburgerEl.addEventListener('click', (e) => {
          e.stopPropagation();
          toggle();
        });
      }

      if (overlayEl) {
        overlayEl.addEventListener('click', close);
      }

      document.addEventListener('click', (e) => {
        if (
          isOpen &&
          sidebarEl &&
          !sidebarEl.contains(e.target) &&
          hamburgerEl &&
          !hamburgerEl.contains(e.target)
        ) {
          close();
        }
      });

      highlightActive();
    }

    return { init, open, close, toggle, highlightActive, get isOpen() { return isOpen; } };
  })();

  const ADToast = (() => {
    let containerEl = null;

    const ICONS = {
      success:
        '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>',
      warning:
        '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>',
      error:
        '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>',
      info:
        '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>',
    };

    function ensureContainer() {
      if (containerEl && document.body.contains(containerEl)) return;
      containerEl = document.createElement('div');
      containerEl.className = 'ad-toast-container';
      containerEl.setAttribute('aria-live', 'polite');
      containerEl.setAttribute('aria-atomic', 'false');
      document.body.appendChild(containerEl);
    }

    function dismiss(toastEl) {
      toastEl.classList.add('ad-toast--out');
      toastEl.addEventListener('animationend', function () {
        toastEl.remove();
      });

      setTimeout(function () {
        if (toastEl.parentNode) toastEl.remove();
      }, 600);
    }

    function show(message, type = 'info', duration = 5000) {
      ensureContainer();

      const toast = document.createElement('div');
      toast.className = `ad-toast ad-toast--${type}`;
      toast.id = uid('toast');

      const icon = ICONS[type] || ICONS.info;

      toast.innerHTML = '<span class="ad-toast__icon">' + icon + '</span><span class="ad-toast__message">' + message + '</span><button class="ad-toast__close" aria-label="Zamknij powiadomienie">&times;</button>';

      toast.querySelector('.ad-toast__close').addEventListener('click', () => dismiss(toast));

      containerEl.appendChild(toast);

      requestAnimationFrame(() => {
        toast.classList.add('ad-toast--in');
      });

      if (duration > 0) {
        setTimeout(() => {
          if (toast.parentNode) dismiss(toast);
        }, duration);
      }

      return toast;
    }

    function init() {
      ensureContainer();
    }

    return { init, show, dismiss };
  })();

  const ADAnimate = (() => {

    function staggerIn(selector, delay = 80) {
      if (prefersReducedMotion()) return;

      const elements = document.querySelectorAll(selector);
      elements.forEach((el, i) => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(16px)';
        el.style.transition = `opacity 0.45s ease ${i * delay}ms, transform 0.45s ease ${i * delay}ms`;

        requestAnimationFrame(() => {
          requestAnimationFrame(() => {
            el.style.opacity = '1';
            el.style.transform = 'translateY(0)';
          });
        });
      });
    }

    function observeScroll(selector, delay = 80) {
      if (prefersReducedMotion()) return;
      if (!('IntersectionObserver' in window)) {

        document.querySelectorAll(selector).forEach((el) => {
          el.classList.add('ad-animate--visible');
        });
        return;
      }

      const observer = new IntersectionObserver(
        (entries) => {

          let visibleIndex = 0;
          entries.forEach((entry) => {
            if (entry.isIntersecting) {
              const el = entry.target;
              const stagger = visibleIndex * delay;
              el.style.transitionDelay = `${stagger}ms`;
              el.classList.add('ad-animate--visible');
              observer.unobserve(el);
              visibleIndex++;
            }
          });
        },
        { threshold: 0.1, rootMargin: '0px 0px -40px 0px' }
      );

      document.querySelectorAll(selector).forEach((el) => {
        el.classList.add('ad-animate--observe');
        observer.observe(el);
      });
    }

    function countUp(element, target, duration = 1500, decimals = 0) {
      if (!element) return;

      if (prefersReducedMotion()) {
        element.textContent = target.toFixed(decimals);
        return;
      }

      const start = performance.now();
      const from = 0;

      function tick(now) {
        const elapsed = now - start;
        const progress = Math.min(elapsed / duration, 1);

        const eased = 1 - Math.pow(1 - progress, 3);
        const current = from + (target - from) * eased;

        element.textContent = current.toFixed(decimals);

        if (progress < 1) {
          requestAnimationFrame(tick);
        } else {
          element.textContent = target.toFixed(decimals);
        }
      }

      requestAnimationFrame(tick);
    }

    function initCounters() {
      const counters = document.querySelectorAll('[data-count-target]');
      if (!counters.length) return;

      if (prefersReducedMotion() || !('IntersectionObserver' in window)) {
        counters.forEach((el) => {
          const target = parseFloat(el.dataset.countTarget) || 0;
          const decimals = parseInt(el.dataset.countDecimals, 10) || 0;
          el.textContent = target.toFixed(decimals);
        });
        return;
      }

      const observer = new IntersectionObserver(
        (entries) => {
          entries.forEach((entry) => {
            if (entry.isIntersecting) {
              const el = entry.target;
              const target = parseFloat(el.dataset.countTarget) || 0;
              const duration = parseInt(el.dataset.countDuration, 10) || 1500;
              const decimals = parseInt(el.dataset.countDecimals, 10) || 0;
              countUp(el, target, duration, decimals);
              observer.unobserve(el);
            }
          });
        },
        { threshold: 0.3 }
      );

      counters.forEach((el) => observer.observe(el));
    }

    function init() {

      staggerIn('.ad-card, .ad-stat-card, .ad-metric-card');

      observeScroll('.ad-animate');

      initCounters();
    }

    return { init, staggerIn, observeScroll, countUp, initCounters };
  })();

  const ADTheme = (() => {
    const STORAGE_KEY = 'ad-theme';
    const DARK = 'dark';
    const LIGHT = 'light';

    function getPreferred() {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (stored === DARK || stored === LIGHT) return stored;

      if (window.matchMedia && window.matchMedia('(prefers-color-scheme: light)').matches) {
        return LIGHT;
      }
      return DARK;
    }

    function apply(theme) {
      const root = document.documentElement;
      root.classList.remove('theme-dark', 'theme-light');
      root.classList.add(`theme-${theme}`);
      localStorage.setItem(STORAGE_KEY, theme);

      document.querySelectorAll('[data-theme-toggle]').forEach((btn) => {
        btn.setAttribute('aria-pressed', theme === DARK ? 'true' : 'false');
      });
    }

    function toggle() {
      const current = localStorage.getItem(STORAGE_KEY) || getPreferred();
      const next = current === DARK ? LIGHT : DARK;
      apply(next);
      return next;
    }

    function init() {
      apply(getPreferred());

      document.querySelectorAll('[data-theme-toggle]').forEach((btn) => {
        btn.addEventListener('click', () => {
          toggle();
        });
      });

      if (window.matchMedia) {
        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {

          if (!localStorage.getItem(STORAGE_KEY)) {
            apply(e.matches ? DARK : LIGHT);
          }
        });
      }
    }

    return { init, apply, toggle, getPreferred };
  })();

  const ADConnection = (() => {
    const POLL_INTERVAL = 30000;
    let timerId = null;
    let lastStatus = null;

    function updateIndicators(status) {
      const dots = document.querySelectorAll('.ad-connection-dot, .ad-status-indicator');
      dots.forEach((dot) => {
        dot.classList.remove('ad-connection-dot--online', 'ad-connection-dot--offline');
        dot.classList.add(`ad-connection-dot--${status}`);

        if (status === 'online') {
          dot.classList.add('ad-connection-dot--pulse');
        } else {
          dot.classList.remove('ad-connection-dot--pulse');
        }
      });

      const labels = document.querySelectorAll('.ad-connection-label');
      labels.forEach((label) => {
        label.textContent = status === 'online' ? 'Połączono' : 'Brak połączenia';
      });
    }

    async function poll() {

      if (!document.getElementById('backend-status')) {
        return;
      }

      try {
        const res = await fetch('/api/system-status', {
          method: 'GET',
          headers: { Accept: 'application/json' },
          cache: 'no-store',
        });

        if (!res.ok) throw new Error(`HTTP ${res.status}`);

        const data = await res.json();
        const status = data.status === 'ok' || data.online ? 'online' : 'offline';

        if (lastStatus !== null && lastStatus !== status) {
          if (status === 'online') {
            ADToast.show('Połączenie z systemem przywrócone.', 'success', 4000);
          } else {
            ADToast.show('Utracono połączenie z systemem.', 'error', 7000);
          }
        }

        lastStatus = status;
        updateIndicators(status);
      } catch (_err) {

        if (lastStatus !== 'offline' && lastStatus !== null) {
          ADToast.show('Utracono połączenie z systemem.', 'error', 7000);
        }
        lastStatus = 'offline';
        updateIndicators('offline');
      }
    }

    function start() {
      poll();
      timerId = setInterval(poll, POLL_INTERVAL);
    }

    function stop() {
      if (timerId) {
        clearInterval(timerId);
        timerId = null;
      }
    }

    function init() {

      if (document.getElementById('backend-status')) {
        return;
      }
      const hasIndicators = document.querySelector(
        '.ad-connection-dot, .ad-status-indicator, .ad-connection-label'
      );
      if (hasIndicators) {
        start();
      }
    }

    return { init, poll, start, stop };
  })();

  const ADDashboardStatus = (() => {
    const POLL_INTERVAL = 30000;
    let timerId = null;

    async function updateDashboardStatus() {

      if (!document.getElementById('backend-status')) {
        return;
      }

      try {
        const res = await fetch('/api/system-status', {
          method: 'GET',
          headers: { Accept: 'application/json' },
          cache: 'no-store',
        });

        if (!res.ok) throw new Error(`HTTP ${res.status}`);

        const data = await res.json();

        const backendStatusEl = document.getElementById('backend-status');
        if (backendStatusEl) {
          updateStatusElement(backendStatusEl, data.backend);
        }

        const databaseStatusEl = document.getElementById('database-status');
        if (databaseStatusEl) {
          updateStatusElement(databaseStatusEl, data.database);
        }

        const websocketStatusEl = document.getElementById('websocket-status');
        if (websocketStatusEl) {
          updateStatusElement(websocketStatusEl, data.websocket);
        }

        const lastUpdateEl = document.getElementById('last-update');
        if (lastUpdateEl) {
          lastUpdateEl.textContent = new Date().toLocaleTimeString('pl-PL', {
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
          });
        }
      } catch (err) {

        const backendStatusEl = document.getElementById('backend-status');
        const databaseStatusEl = document.getElementById('database-status');
        const websocketStatusEl = document.getElementById('websocket-status');
        const lastUpdateEl = document.getElementById('last-update');

        if (backendStatusEl) updateStatusElement(backendStatusEl, 'error');
        if (databaseStatusEl) updateStatusElement(databaseStatusEl, 'error');
        if (websocketStatusEl) updateStatusElement(websocketStatusEl, 'error');
        if (lastUpdateEl) lastUpdateEl.textContent = 'Błąd';
      }
    }

    function updateStatusElement(element, status) {

      element.querySelector('.ad-status-dot')?.classList.remove(
        'ad-status-dot--success',
        'ad-status-dot--warning',
        'ad-status-dot--error',
        'ad-status-dot--checking'
      );
      element.querySelector('.ad-connection-label')?.classList.remove(
        'ad-connection-label--success',
        'ad-connection-label--warning',
        'ad-connection-label--error',
        'ad-connection-label--checking'
      );

      const dot = element.querySelector('.ad-status-dot');
      const label = element.querySelector('.ad-connection-label');

      if (dot) {

        dot.classList.remove('ad-status-dot--pulse');

        if (status === 'connected' || status === 'online') {
          dot.classList.add('ad-status-dot--success');
          dot.classList.add('ad-status-dot--pulse');
          if (label) {
            label.textContent = 'Połączono';
            label.classList.add('ad-connection-label--success');
          }
        } else if (status === 'checking') {
          dot.classList.add('ad-status-dot--checking');
          if (label) {
            label.textContent = 'Sprawdzanie...';
            label.classList.add('ad-connection-label--checking');
          }
        } else {

          dot.classList.add('ad-status-dot--error');
          if (label) {
            label.textContent = 'Brak połączenia';
            label.classList.add('ad-connection-label--error');
          }
        }
      }
    }

    function start() {
      updateDashboardStatus();
      timerId = setInterval(updateDashboardStatus, POLL_INTERVAL);
    }

    function stop() {
      if (timerId) {
        clearInterval(timerId);
        timerId = null;
      }
    }

    function init() {

      if (document.getElementById('backend-status')) {

        if (ADConnection && typeof ADConnection.stop === 'function') {
          ADConnection.stop();
        }
        start();
      }
    }

    return { init, updateDashboardStatus, start, stop };
  })();

  const ADForms = (() => {

    function initFloatingLabels() {
      const inputs = document.querySelectorAll('.ad-input');

      inputs.forEach((input) => {
        const wrapper = input.closest('.ad-input-group, .ad-form-group');
        if (!wrapper) return;

        const updateState = () => {
          if (input.value && input.value.trim().length > 0) {
            wrapper.classList.add('ad-input-group--filled');
          } else {
            wrapper.classList.remove('ad-input-group--filled');
          }
        };

        input.addEventListener('focus', () => {
          wrapper.classList.add('ad-input-group--focused');
        });

        input.addEventListener('blur', () => {
          wrapper.classList.remove('ad-input-group--focused');
          updateState();
        });

        input.addEventListener('input', updateState);

        updateState();
      });
    }

    function initValidation() {
      const forms = document.querySelectorAll('.ad-form');

      forms.forEach((form) => {

        form.setAttribute('novalidate', '');

        form.addEventListener('submit', (e) => {
          const invalidFields = form.querySelectorAll(':invalid');
          if (invalidFields.length > 0) {
            e.preventDefault();
            invalidFields.forEach((field) => {
              const group = field.closest('.ad-input-group, .ad-form-group');
              if (group) group.classList.add('ad-input-group--error');
            });

            invalidFields[0].focus();
            return;
          }

          form.querySelectorAll('.ad-input-group--error').forEach((g) => {
            g.classList.remove('ad-input-group--error');
          });
        });

        form.querySelectorAll('.ad-input').forEach((input) => {
          input.addEventListener('input', () => {
            const group = input.closest('.ad-input-group, .ad-form-group');
            if (group) group.classList.remove('ad-input-group--error');
          });
        });
      });
    }

    function initSubmitLoading() {
      document.querySelectorAll('.ad-form').forEach((form) => {
        form.addEventListener('submit', () => {
          const btn = form.querySelector('[type="submit"], .ad-btn--submit');
          if (!btn) return;

          const originalText = btn.textContent;
          const loadingText = btn.dataset.loadingText || 'Wysyłanie…';

          btn.disabled = true;
          btn.classList.add('ad-btn--loading');
          btn.dataset.originalText = originalText;
          btn.textContent = loadingText;

          setTimeout(() => {
            btn.disabled = false;
            btn.classList.remove('ad-btn--loading');
            btn.textContent = btn.dataset.originalText || originalText;
          }, 10000);
        });
      });
    }

    function init() {
      initFloatingLabels();
      initValidation();
      initSubmitLoading();
    }

    return { init, initFloatingLabels, initValidation, initSubmitLoading };
  })();

  const ADAlerts = (() => {
    function init() {
      document.addEventListener('click', (e) => {
        const closeBtn = e.target.closest('.ad-alert-close');
        if (!closeBtn) return;

        const alert = closeBtn.closest('.ad-alert');
        if (!alert) return;

        alert.style.transition = 'opacity 0.3s ease, transform 0.3s ease, max-height 0.35s ease';
        alert.style.opacity = '0';
        alert.style.transform = 'translateX(20px)';
        alert.style.maxHeight = alert.scrollHeight + 'px';

        alert.offsetHeight;

        requestAnimationFrame(() => {
          alert.style.maxHeight = '0';
          alert.style.paddingTop = '0';
          alert.style.paddingBottom = '0';
          alert.style.marginTop = '0';
          alert.style.marginBottom = '0';
        });

        setTimeout(() => {
          alert.remove();
        }, 400);
      });
    }

    return { init };
  })();

  const ADKeyboard = (() => {

    function getFocusable(container) {
      return container.querySelectorAll(
        'a[href], button:not([disabled]), input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])'
      );
    }

    function init() {
      document.addEventListener('keydown', (e) => {

        if (e.key === 'Escape') {
          if (ADSidebar.isOpen) {
            ADSidebar.close();

            const hamburger = document.querySelector('.ad-hamburger');
            if (hamburger) hamburger.focus();
          }
        }

        if (e.key === 'Tab' && ADSidebar.isOpen) {
          const sidebar = document.querySelector('.ad-sidebar');
          if (!sidebar) return;

          const focusable = getFocusable(sidebar);
          if (focusable.length === 0) return;

          const first = focusable[0];
          const last = focusable[focusable.length - 1];

          if (e.shiftKey) {

            if (document.activeElement === first) {
              e.preventDefault();
              last.focus();
            }
          } else {

            if (document.activeElement === last) {
              e.preventDefault();
              first.focus();
            }
          }
        }
      });
    }

    return { init };
  })();

  const ADPush = (() => {
    const SUPPORTED = 'PushManager' in window && 'serviceWorker' in navigator;
    let swRegistration = null;

    function urlBase64ToUint8Array(base64String) {
      const padding = '='.repeat((4 - (base64String.length % 4)) % 4);
      const base64 = (base64String + padding).replace(/-/g, '+').replace(/_/g, '/');
      const raw = atob(base64);
      const output = new Uint8Array(raw.length);
      for (let i = 0; i < raw.length; i++) output[i] = raw.charCodeAt(i);
      return output;
    }

    function keyToBase64(key) {
      if (!key) return '';
      return btoa(String.fromCharCode.apply(null, new Uint8Array(key)));
    }

    async function ensureServiceWorker() {
      if (!swRegistration) {
        swRegistration = await navigator.serviceWorker.register('/settings/push-sw.js', { scope: '/' });
      }
      return swRegistration;
    }

    async function isEnabled() {
      if (!SUPPORTED) return false;
      const res = await fetch('/settings/api/config', { headers: { Accept: 'application/json' } });
      const config = await res.json();
      return !!config.push_notifications;
    }

    async function enable() {
      if (!SUPPORTED) throw new Error('Push not supported');
      const registration = await ensureServiceWorker();
      const resp = await fetch('/settings/push/vapid-public-key');
      if (!resp.ok) throw new Error(`VAPID key request failed (${resp.status})`);
      const data = await resp.json();
      if (!data.public_key) throw new Error('VAPID public key is missing');
      const subscription = await registration.pushManager.subscribe({
        userVisibleOnly: true,
        applicationServerKey: urlBase64ToUint8Array(data.public_key),
      });
      const saved = await fetch('/settings/push/subscribe', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          endpoint: subscription.endpoint,
          p256dh_key: keyToBase64(subscription.getKey('p256dh')),
          auth_key: keyToBase64(subscription.getKey('auth')),
        }),
      });
      if (!saved.ok) throw new Error(`Saving push subscription failed (${saved.status})`);
      const config = await fetch('/settings/api/config', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ push_notifications: true }),
      });
      if (!config.ok) throw new Error(`Saving push settings failed (${config.status})`);
      return true;
    }

    return { isSupported: () => SUPPORTED, isEnabled, enable };
  })();
  AD.Push = ADPush;

  AD.Sidebar = ADSidebar;
  AD.Toast = ADToast;
  AD.Animate = ADAnimate;
  AD.Theme = ADTheme;
  AD.Connection = ADConnection;
  AD.Forms = ADForms;
  AD.Alerts = ADAlerts;
  AD.Keyboard = ADKeyboard;
  AD.Push = ADPush;

  document.addEventListener('DOMContentLoaded', () => {

    document.body.classList.add('loaded');

    ADSidebar.init();
    ADToast.init();
    ADAnimate.init();
    ADTheme.init();
    ADConnection.init();
    ADDashboardStatus.init();
    ADForms.init();
    ADAlerts.init();
    ADKeyboard.init();
  });
})();

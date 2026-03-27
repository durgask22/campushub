/**
 * CampusHub — Main JavaScript
 * Handles: Tabs, Flash toasts, Mobile nav, Confirm dialogs, Demo login, Form enhancements
 */

/* ─── DOM Ready ─────────────────────────────────────────────────────────── */
document.addEventListener('DOMContentLoaded', () => {
  initTabs();
  initToasts();
  initMobileNav();
  initConfirmForms();
  initDemoLogin();
  initProgressBars();
  initFilterSearch();
  highlightActiveNav();
});

/* ─── Tab System ────────────────────────────────────────────────────────── */
function initTabs() {
  document.querySelectorAll('.tabs').forEach(tabGroup => {
    tabGroup.querySelectorAll('.tab-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        const target = btn.dataset.tab;
        tabGroup.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        // Find sibling panels container
        const panelContainer = tabGroup.nextElementSibling;
        if (panelContainer) {
          panelContainer.querySelectorAll('.tab-panel').forEach(panel => {
            panel.classList.toggle('active', panel.id === target);
          });
        }
      });
    });
    // Activate first tab by default
    const firstBtn = tabGroup.querySelector('.tab-btn');
    if (firstBtn && !tabGroup.querySelector('.tab-btn.active')) {
      firstBtn.click();
    }
  });
}

/* ─── Flash Toasts ──────────────────────────────────────────────────────── */
function initToasts() {
  // Auto-dismiss existing flash messages after 4s
  document.querySelectorAll('.alert').forEach(alert => {
    setTimeout(() => {
      alert.style.transition = 'opacity .4s ease, transform .4s ease';
      alert.style.opacity = '0';
      alert.style.transform = 'translateY(-8px)';
      setTimeout(() => alert.remove(), 400);
    }, 4000);
  });

  // Close on click
  document.querySelectorAll('.alert-close').forEach(btn => {
    btn.addEventListener('click', () => btn.closest('.alert').remove());
  });
}

/* ─── Mobile Navigation ─────────────────────────────────────────────────── */
function initMobileNav() {
  const hamburger = document.getElementById('hamburger');
  const mobileMenu = document.getElementById('mobile-menu');
  if (!hamburger || !mobileMenu) return;

  hamburger.addEventListener('click', () => {
    const isOpen = mobileMenu.style.display === 'block';
    mobileMenu.style.display = isOpen ? 'none' : 'block';
    hamburger.classList.toggle('open', !isOpen);
  });

  // Close on outside click
  document.addEventListener('click', e => {
    if (!hamburger.contains(e.target) && !mobileMenu.contains(e.target)) {
      mobileMenu.style.display = 'none';
      hamburger.classList.remove('open');
    }
  });
}

/* ─── Confirm Dialogs ───────────────────────────────────────────────────── */
function initConfirmForms() {
  document.querySelectorAll('[data-confirm]').forEach(el => {
    el.addEventListener('click', e => {
      const msg = el.dataset.confirm || 'Are you sure?';
      if (!confirm(msg)) e.preventDefault();
    });
  });
}

/* ─── Demo Login Buttons ─────────────────────────────────────────────────── */
function initDemoLogin() {
  document.querySelectorAll('.demo-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const email    = btn.dataset.email;
      const password = btn.dataset.password;
      const emailField    = document.getElementById('email');
      const passwordField = document.getElementById('password');
      if (emailField)    { emailField.value = email; emailField.focus(); }
      if (passwordField) { passwordField.value = password; }
      // Flash the form
      const form = emailField?.closest('form');
      if (form) {
        form.style.transition = 'box-shadow .2s';
        form.style.boxShadow = '0 0 0 3px rgba(200,97,42,.2)';
        setTimeout(() => form.style.boxShadow = '', 600);
      }
    });
  });
}

/* ─── Progress Bars ─────────────────────────────────────────────────────── */
function initProgressBars() {
  document.querySelectorAll('[data-progress]').forEach(bar => {
    const fill = bar.querySelector('.progress-bar-fill');
    if (fill) {
      const pct = Math.min(100, Math.max(0, parseFloat(bar.dataset.progress)));
      setTimeout(() => { fill.style.width = pct + '%'; }, 100);
      // Color feedback
      if (pct >= 90) fill.style.background = 'var(--red)';
      else if (pct >= 70) fill.style.background = 'var(--amber)';
    }
  });
}

/* ─── Live Filter Search ─────────────────────────────────────────────────── */
function initFilterSearch() {
  const searchInput = document.getElementById('live-search');
  if (!searchInput) return;
  const target = searchInput.dataset.target || '.searchable-item';

  searchInput.addEventListener('input', () => {
    const q = searchInput.value.toLowerCase().trim();
    document.querySelectorAll(target).forEach(item => {
      const text = item.textContent.toLowerCase();
      item.style.display = (!q || text.includes(q)) ? '' : 'none';
    });
  });
}

/* ─── Active Nav Link ────────────────────────────────────────────────────── */
function highlightActiveNav() {
  const path = window.location.pathname;
  document.querySelectorAll('.navbar-link').forEach(link => {
    const href = link.getAttribute('href');
    if (href && href !== '/' && path.startsWith(href)) {
      link.classList.add('active');
    } else if (href === '/' && path === '/') {
      link.classList.add('active');
    }
  });
}

/* ─── Countdown Timer ────────────────────────────────────────────────────── */
function startCountdown(el, targetDateStr) {
  function update() {
    const now = new Date();
    const target = new Date(targetDateStr);
    const diff = target - now;
    if (diff <= 0) { el.textContent = 'Event started!'; return; }
    const d = Math.floor(diff / 86400000);
    const h = Math.floor((diff % 86400000) / 3600000);
    const m = Math.floor((diff % 3600000) / 60000);
    el.textContent = `${d}d ${h}h ${m}m`;
  }
  update();
  setInterval(update, 60000);
}
document.querySelectorAll('[data-countdown]').forEach(el => {
  startCountdown(el, el.dataset.countdown);
});

/* ─── Registration confirm ──────────────────────────────────────────────── */
document.querySelectorAll('.register-form').forEach(form => {
  form.addEventListener('submit', e => {
    const btn = form.querySelector('button[type=submit]');
    if (btn) {
      btn.disabled = true;
      btn.textContent = 'Registering…';
    }
  });
});
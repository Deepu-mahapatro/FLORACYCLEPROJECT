/* ================================================================
   FLORACYCLE — auth.js  (v3 — Superuser-only admin, no role selector)
   JWT Authentication: Signup · Login · Logout · Session Guard

   SECURITY RULES:
   - Public signup always creates a PARTNER account (no role field)
   - Admin = only users created via `python manage.py createsuperuser`
     (role='admin' OR is_staff=true OR is_superuser=true)
   ================================================================ */

const API = '/api/v1';

/* ── Token helpers ──────────────────────────────────────────── */
const Auth = {
  setTokens(access, refresh) {
    sessionStorage.setItem('fc_access',  access);
    sessionStorage.setItem('fc_refresh', refresh);
  },
  getAccess()  { return sessionStorage.getItem('fc_access'); },
  getRefresh() { return sessionStorage.getItem('fc_refresh'); },

  setUser(user) { sessionStorage.setItem('fc_user', JSON.stringify(user)); },
  getUser() {
    try { return JSON.parse(sessionStorage.getItem('fc_user') || 'null'); }
    catch { return null; }
  },
  clear() {
    sessionStorage.removeItem('fc_access');
    sessionStorage.removeItem('fc_refresh');
    sessionStorage.removeItem('fc_user');
  },
  isLoggedIn() { return !!this.getAccess(); },

  /* Admin = superuser created via Django createsuperuser
     OR user whose role was manually set to 'admin' in shell/admin */
  isAdmin() {
    const u = this.getUser();
    if (!u) return false;
    return u.role === 'admin' || u.is_staff === true || u.is_superuser === true;
  },
  isPartner() { return !this.isAdmin(); },

  tokenPayload() {
    const token = this.getAccess();
    if (!token) return null;
    try {
      const base64 = token.split('.')[1].replace(/-/g, '+').replace(/_/g, '/');
      return JSON.parse(atob(base64));
    } catch { return null; }
  },

  isTokenExpired() {
    const payload = this.tokenPayload();
    if (!payload) return true;
    return Date.now() / 1000 > payload.exp;
  }
};

/* ── Authenticated fetch wrapper ────────────────────────────── */
async function authFetch(url, options = {}) {
  if (Auth.isTokenExpired() && Auth.getRefresh()) {
    const ok = await refreshAccessToken();
    if (!ok) { Auth.clear(); window.location.href = '/'; return; }
  }
  const headers = {
    'Content-Type': 'application/json',
    ...(options.headers || {}),
  };
  if (Auth.getAccess()) {
    headers['Authorization'] = `Bearer ${Auth.getAccess()}`;
  }
  return fetch(url, { ...options, headers });
}

async function refreshAccessToken() {
  try {
    const res = await fetch(`${API}/auth/refresh/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh: Auth.getRefresh() }),
    });
    if (!res.ok) return false;
    const data = await res.json();
    sessionStorage.setItem('fc_access', data.access);
    if (data.refresh) sessionStorage.setItem('fc_refresh', data.refresh);
    return true;
  } catch { return false; }
}

/* ── Register (partner only — no role field sent) ────────────── */
async function registerUser({ email, full_name, phone, password, password2 }) {
  const res = await fetch(`${API}/auth/register/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, full_name, phone, password, password2 }),
  });
  const data = await res.json();
  if (res.ok) {
    Auth.setTokens(data.tokens.access, data.tokens.refresh);
    Auth.setUser(data.user);
  }
  return { ok: res.ok, data, status: res.status };
}

/* ── Login ───────────────────────────────────────────────────── */
async function loginUser({ email, password }) {
  const res = await fetch(`${API}/auth/login/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  });
  const data = await res.json();
  if (res.ok) {
    Auth.setTokens(data.access, data.refresh);
    Auth.setUser(data.user);
  }
  return { ok: res.ok, data, status: res.status };
}

/* ── Logout ──────────────────────────────────────────────────── */
async function logoutUser() {
  const refresh = Auth.getRefresh();
  if (refresh) {
    try {
      await authFetch(`${API}/auth/logout/`, {
        method: 'POST',
        body: JSON.stringify({ refresh }),
      });
    } catch { /* ignore */ }
  }
  Auth.clear();
  window.location.href = '/';
}

/* ── Auth Modal UI ───────────────────────────────────────────── */
function showAuthModal(tab = 'login') {
  const modal = document.getElementById('auth-modal');
  if (!modal) return;
  modal.classList.add('active');
  switchAuthTab(tab);
  document.body.style.overflow = 'hidden';
}

function closeAuthModal() {
  const modal = document.getElementById('auth-modal');
  if (modal) modal.classList.remove('active');
  document.body.style.overflow = '';
  clearAuthErrors();
}

function switchAuthTab(tab) {
  document.querySelectorAll('.auth-tab').forEach(t => t.classList.toggle('active', t.dataset.tab === tab));
  document.querySelectorAll('.auth-form-panel').forEach(p => p.classList.toggle('hidden', p.dataset.panel !== tab));
}

function clearAuthErrors() {
  document.querySelectorAll('.auth-error').forEach(e => { e.textContent = ''; e.classList.add('hidden'); });
}

function showAuthError(formId, message) {
  const el = document.querySelector(`#${formId} .auth-error`);
  if (el) { el.textContent = message; el.classList.remove('hidden'); }
}

/* ── Update Navbar based on auth state ─────────────────────── */
function updateNavbarAuth() {
  const user = Auth.getUser();
  const navAuthArea = document.getElementById('nav-auth-area');
  const loginNotice = document.getElementById('pickup-login-notice');
  if (!navAuthArea) return;

  if (user) {
    if (loginNotice) loginNotice.style.display = 'none';
    const isAdmin = Auth.isAdmin();
    navAuthArea.innerHTML = `
      <div class="nav-user-menu">
        <button class="nav-user-btn" id="nav-user-btn">
          <span class="nav-user-avatar">${user.full_name.charAt(0).toUpperCase()}</span>
          <span class="nav-user-name">${user.full_name.split(' ')[0]}</span>
          <span class="nav-user-arrow">▾</span>
        </button>
        <div class="nav-user-dropdown" id="nav-user-dropdown">
          <div class="dropdown-header">
            <strong>${user.full_name}</strong>
            <span class="user-role-badge ${isAdmin ? 'admin' : 'partner'}">${isAdmin ? '👑 Admin' : '🌸 Partner'}</span>
          </div>
          <hr/>
          ${isAdmin ? `<a href="/dashboard/" class="dropdown-item">📊 Dashboard</a>` : ''}
          <button class="dropdown-item logout-btn" id="nav-logout-btn">🚪 Logout</button>
        </div>
      </div>`;

    document.getElementById('nav-user-btn')?.addEventListener('click', (e) => {
      e.stopPropagation();
      document.getElementById('nav-user-dropdown')?.classList.toggle('open');
    });
    document.addEventListener('click', () => {
      document.getElementById('nav-user-dropdown')?.classList.remove('open');
    });
    document.getElementById('nav-logout-btn')?.addEventListener('click', logoutUser);
  } else {
    if (loginNotice) loginNotice.style.display = 'flex';
    navAuthArea.innerHTML = `
      <button class="btn-login" id="btn-open-login">Login</button>
      <button class="btn-signup nav-cta" id="btn-open-signup">Sign Up</button>`;

    document.getElementById('btn-open-login')?.addEventListener('click', () => showAuthModal('login'));
    document.getElementById('btn-open-signup')?.addEventListener('click', () => showAuthModal('signup'));
  }
}

/* ── Auth form submission handlers ────────────────────────────── */
function initAuthForms() {
  // Login form
  const loginForm = document.getElementById('login-form');
  loginForm?.addEventListener('submit', async (e) => {
    e.preventDefault();
    clearAuthErrors();
    const btn = loginForm.querySelector('button[type=submit]');
    btn.disabled = true; btn.textContent = 'Logging in…';

    const email    = loginForm.querySelector('#login-email').value.trim();
    const password = loginForm.querySelector('#login-password').value;

    if (!email || !password) {
      showAuthError('login-form', 'Please enter your email and password.');
      btn.disabled = false; btn.textContent = 'Login';
      return;
    }

    const { ok, data, status } = await loginUser({ email, password });

    if (ok) {
      closeAuthModal();
      updateNavbarAuth();
      showToast(`Welcome back, ${data.user.full_name.split(' ')[0]}! 🌸`);
      if (Auth.isAdmin()) {
        setTimeout(() => window.location.href = '/dashboard/', 800);
      }
    } else {
      let msg = 'Invalid email or password. Please try again.';
      if (status === 401) {
        const detail = data.detail || '';
        if (detail.toLowerCase().includes('inactive')) {
          msg = 'Your account is inactive. Please contact the administrator.';
        } else {
          msg = 'Incorrect email or password. Please check and try again.';
        }
      } else if (status === 400) {
        msg = data.detail || data.non_field_errors?.[0] || 'Login failed. Please check your details.';
      } else if (status >= 500) {
        msg = 'Server error. Please try again in a moment.';
      }
      showAuthError('login-form', msg);
    }
    btn.disabled = false; btn.textContent = 'Login';
  });

  // Signup form — NO role field, always creates partner
  const signupForm = document.getElementById('signup-form');
  signupForm?.addEventListener('submit', async (e) => {
    e.preventDefault();
    clearAuthErrors();
    const btn = signupForm.querySelector('button[type=submit]');
    btn.disabled = true; btn.textContent = 'Creating account…';

    const email     = signupForm.querySelector('#signup-email').value.trim();
    const full_name = signupForm.querySelector('#signup-name').value.trim();
    const phone     = signupForm.querySelector('#signup-phone')?.value.trim() || '';
    const password  = signupForm.querySelector('#signup-password').value;
    const password2 = signupForm.querySelector('#signup-password2').value;

    if (!email || !full_name || !password) {
      showAuthError('signup-form', 'Please fill in all required fields.');
      btn.disabled = false; btn.textContent = 'Create Account';
      return;
    }
    if (password !== password2) {
      showAuthError('signup-form', 'Passwords do not match.');
      btn.disabled = false; btn.textContent = 'Create Account';
      return;
    }
    if (password.length < 8) {
      showAuthError('signup-form', 'Password must be at least 8 characters.');
      btn.disabled = false; btn.textContent = 'Create Account';
      return;
    }

    // NOTE: no 'role' sent — backend always assigns 'partner'
    const { ok, data, status } = await registerUser({ email, full_name, phone, password, password2 });

    if (ok) {
      closeAuthModal();
      updateNavbarAuth();
      showToast(`Welcome, ${data.user.full_name.split(' ')[0]}! Account created 🌸`);
      // Partners never get redirected to dashboard
    } else {
      let msg = 'Registration failed. Please try again.';
      if (data.email) {
        msg = Array.isArray(data.email) ? data.email[0] : data.email;
        if (msg.toLowerCase().includes('already exists') || msg.toLowerCase().includes('already registered')) {
          msg = 'This email is already registered. Please log in instead.';
        }
      } else if (data.password) {
        msg = Array.isArray(data.password) ? data.password[0] : data.password;
      } else if (data.password2) {
        msg = Array.isArray(data.password2) ? data.password2[0] : data.password2;
      } else if (data.non_field_errors) {
        msg = data.non_field_errors[0];
      } else if (data.detail) {
        msg = data.detail;
      } else {
        const errs = Object.values(data).flat();
        if (errs.length) msg = errs[0];
      }
      showAuthError('signup-form', msg);
    }
    btn.disabled = false; btn.textContent = 'Create Account';
  });

  // Tab switching
  document.querySelectorAll('.auth-tab').forEach(tab => {
    tab.addEventListener('click', () => switchAuthTab(tab.dataset.tab));
  });

  // Close on overlay click
  document.getElementById('auth-modal')?.addEventListener('click', (e) => {
    if (e.target.id === 'auth-modal') closeAuthModal();
  });

  // Close button
  document.querySelector('.auth-modal-close')?.addEventListener('click', closeAuthModal);
}

/* ── Dashboard page: guard + load real data ────────────────────── */
function initDashboardAuth() {
  if (!document.querySelector('.dashboard-layout')) return;

  const user = Auth.getUser();
  if (!user) {
    window.location.href = '/?login=1';
    return;
  }
  if (!Auth.isAdmin()) {
    showToast('Dashboard is for admin users only. 👑', 'error');
    setTimeout(() => { window.location.href = '/'; }, 1500);
    return;
  }

  // Show user info in sidebar
  const sidebarUser = document.getElementById('sidebar-user-info');
  if (sidebarUser) {
    const roleLabel = Auth.isAdmin() ? '👑 Admin' : '🌸 Partner';
    sidebarUser.innerHTML = `
      <div class="sidebar-user-avatar">${user.full_name.charAt(0)}</div>
      <div>
        <div class="sidebar-user-name">${user.full_name}</div>
        <div class="sidebar-user-role">${roleLabel}</div>
      </div>`;
  }

  // Wire logout button in sidebar
  document.getElementById('sidebar-logout-btn')?.addEventListener('click', (e) => {
    e.preventDefault();
    logoutUser();
  });

  // Load real data from API
  loadDashboardDataFromAPI();
}

/* ── Load dashboard data from real API ─────────────────────────── */
async function loadDashboardDataFromAPI() {
  try {
    const res = await authFetch(`${API}/dashboard/summary/`);
    if (!res.ok) return;
    const data = await res.json();

    setEl('stat-pickups',   data.stats?.total_pickups ?? 0);
    setEl('stat-flowers',   (data.stats?.total_flowers_kg ?? 0).toFixed(0) + ' kg');
    setEl('stat-products',  data.stats?.total_products ?? 0);
    setEl('stat-enquiries', data.stats?.total_enquiries ?? 0);

    renderAPIPickupTable(data.recent_pickups);
    renderAPIEnquiryTable(data.recent_enquiries);
  } catch (err) {
    console.warn('Dashboard API unavailable.', err);
  }
}

function renderAPIPickupTable(pickups) {
  const tbody = document.getElementById('pickup-table-body');
  if (!tbody || !pickups) return;
  if (!pickups.length) {
    tbody.innerHTML = '<tr><td colspan="6" style="text-align:center;padding:30px;color:var(--text-light)">No pickup requests yet.</td></tr>';
    return;
  }
  tbody.innerHTML = pickups.map(p => `
    <tr>
      <td>${p.temple_name || p.full_name}</td>
      <td>${p.flower_type || '-'}</td>
      <td>${p.quantity_kg} kg</td>
      <td>${p.pickup_date || '-'}</td>
      <td><span class="status-badge status-${(p.status || 'Pending').toLowerCase()}">${p.status || 'Pending'}</span></td>
      <td><button class="btn-outline-sm" style="padding:4px 10px;font-size:.75rem;" onclick="window.dashSwitchSection('pickups')">Manage</button></td>
    </tr>
  `).join('');
}

function renderAPIEnquiryTable(enquiries) {
  const tbody = document.getElementById('recent-enquiry-table-body');
  if (!tbody || !enquiries) return;
  if (!enquiries.length) {
    tbody.innerHTML = '<tr><td colspan="6" style="text-align:center;padding:30px;color:var(--text-light)">No enquiries yet.</td></tr>';
    return;
  }
  tbody.innerHTML = enquiries.map(e => `
    <tr>
      <td>${e.customer_name}</td>
      <td>${e.product_name || 'General Enquiry'}</td>
      <td>${e.quantity || '-'}</td>
      <td>${e.email}</td>
      <td>${e.phone || '-'}</td>
      <td>${e.message || '-'}</td>
    </tr>
  `).join('');
}

/* ── Pickup form: submit to real API ────────────────────────── */
async function submitPickupToAPI(formData) {
  const headers = { 'Content-Type': 'application/json' };
  if (Auth.getAccess()) headers['Authorization'] = `Bearer ${Auth.getAccess()}`;
  const res = await fetch(`${API}/pickups/`, {
    method: 'POST',
    headers,
    body: JSON.stringify(formData),
  });
  return { ok: res.ok, status: res.status, data: await res.json() };
}

/* ── Enquiry form: submit to real API (public) ───────────────── */
async function submitEnquiryToAPI(formData) {
  const res = await fetch(`${API}/enquiries/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(formData),
  });
  return { ok: res.ok, status: res.status, data: await res.json() };
}

/* ── Toast helper ───────────────────────────────────────────────── */
function showToast(message, type = 'success') {
  let container = document.getElementById('toast-container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'toast-container';
    document.body.appendChild(container);
  }
  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  toast.textContent = message;
  container.appendChild(toast);
  requestAnimationFrame(() => toast.classList.add('show'));
  setTimeout(() => { toast.classList.remove('show'); setTimeout(() => toast.remove(), 400); }, 3500);
}

/* ── Auto-open login modal if ?login=1 ─────────────────────────── */
function checkAutoOpenLogin() {
  const params = new URLSearchParams(window.location.search);
  if (params.get('login') === '1') {
    setTimeout(() => showAuthModal('login'), 300);
  }
}

/* ── Helper ─────────────────────────────────────────────────────── */
function setEl(id, val) {
  const el = document.getElementById(id);
  if (el) el.textContent = val;
}

/* ── Init all auth ──────────────────────────────────────────────── */
document.addEventListener('DOMContentLoaded', () => {
  updateNavbarAuth();
  initAuthForms();
  initDashboardAuth();
  checkAutoOpenLogin();
});

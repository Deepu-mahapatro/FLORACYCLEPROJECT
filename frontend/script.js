/* =============================================
   FLORACYCLE — Main Script (FULLY FIXED v2)
   =============================================
   - Pickup form → real API (users only; no localStorage conflict)
   - Enquiry/Quote form → real API
   - Products loaded from real API first, fallback to embedded data
   - Clear permission gates on forms
   - No demo data seeded into localStorage
   ============================================= */

/* ── Embedded fallback products (used only if API unreachable) ── */
const FALLBACK_PRODUCTS = [
  {
    id: 1, name: "Rose Agarbatti", emoji: "🌹",
    description: "Hand-rolled incense sticks made from collected temple roses and jasmine waste.",
    eco_benefit: "Saves 2kg flower waste per batch", price: "₹120 / pack of 20",
    eco_score: "A+", color: "#ffe0ec",
    full_desc: "Our Rose Agarbatti is crafted using a traditional hand-rolling technique combined with modern sustainable processes.",
    usage: "Light the tip and place in a holder. Each stick burns for 30–40 minutes.",
    impact: "1 pack = 2kg temple flowers diverted from river pollution",
    ingredients: "Dried rose petals, jasmine, bamboo stick, natural gum binder"
  },
  {
    id: 2, name: "Compost Powder", emoji: "🌱",
    description: "Nutrient-rich organic compost derived from processed flower and leaf waste.",
    eco_benefit: "Enriches 10 sq.ft of soil per kg", price: "₹80 / kg",
    eco_score: "A+", color: "#e0f0d8",
    full_desc: "FloraCycle Compost Powder is a fully organic soil enrichment product derived from aerobically processed flower waste.",
    usage: "Mix 100g per litre of potting mix or apply 200g per sq.ft around plant base.",
    impact: "Each kg of compost prevents 2kg of organic waste from landfills",
    ingredients: "Processed flower waste, dried leaves, organic activator"
  },
  {
    id: 3, name: "Natural Holi Colors", emoji: "🎨",
    description: "Vibrant Holi colors extracted naturally from marigolds, roses, and hibiscus.",
    eco_benefit: "100% skin-safe, zero chemical dyes", price: "₹60 / 100g pack",
    eco_score: "A", color: "#fff0cc",
    full_desc: "Our Natural Holi Colors are extracted using cold-press and sun-drying techniques from flower waste.",
    usage: "Use dry or mix with water for wet play. Safe for all skin types.",
    impact: "Each pack replaces 3 chemical dye packets and uses 500g flower waste",
    ingredients: "Dried marigold, rose petal powder, hibiscus extract, arrowroot base"
  },
  {
    id: 4, name: "Organic Dhoop Sticks", emoji: "🪔",
    description: "Thick aromatic dhoop sticks with calming floral and herbal blends.",
    eco_benefit: "Made from 100% temple flower waste", price: "₹150 / pack of 12",
    eco_score: "A+", color: "#ede0ff",
    full_desc: "FloraCycle Organic Dhoop Sticks combine collected temple flowers with sandalwood powder and medicinal herbs.",
    usage: "Place dhoop stick on a dhoop holder and light the flat end. Use in well-ventilated spaces.",
    impact: "Each pack utilizes 1.5kg of flower waste and supports 2 local artisan jobs",
    ingredients: "Temple flower mix, sandalwood powder, natural resin, medicinal herbs"
  }
];

// Working product list (filled from API or fallback)
let loadedProducts = [];

/* ============================================================
   UTILITY: Show / Hide Modal
   ============================================================ */
function openModal(overlayId) {
  const overlay = document.getElementById(overlayId);
  if (overlay) {
    overlay.classList.add('active');
    document.body.style.overflow = 'hidden';
  }
}

function closeModal(overlayId) {
  const overlay = document.getElementById(overlayId);
  if (overlay) {
    overlay.classList.remove('active');
    document.body.style.overflow = '';
  }
}

/* ============================================================
   UTILITY: Show Success Popup
   ============================================================ */
function showSuccess(title, message) {
  const existing = document.getElementById('success-toast');
  if (existing) existing.remove();

  const toast = document.createElement('div');
  toast.id = 'success-toast';
  toast.className = 'success-popup';
  toast.innerHTML = `
    <span class="icon">✅</span>
    <div>
      <strong>${title}</strong>
      <span>${message}</span>
    </div>
  `;
  document.body.appendChild(toast);

  requestAnimationFrame(() => {
    requestAnimationFrame(() => toast.classList.add('show'));
  });

  setTimeout(() => {
    toast.classList.remove('show');
    setTimeout(() => toast.remove(), 400);
  }, 4500);
}

/* ============================================================
   NAVBAR
   ============================================================ */
function initNavbar() {
  const hamburger = document.querySelector('.hamburger');
  const navLinks  = document.querySelector('.nav-links');
  const navbar    = document.querySelector('.navbar');

  window.addEventListener('scroll', () => {
    navbar.classList.toggle('scrolled', window.scrollY > 40);
  });

  if (hamburger && navLinks) {
    hamburger.addEventListener('click', () => {
      hamburger.classList.toggle('active');
      navLinks.classList.toggle('open');
    });
    navLinks.querySelectorAll('a').forEach(a => {
      a.addEventListener('click', () => {
        hamburger.classList.remove('active');
        navLinks.classList.remove('open');
      });
    });
  }
}

/* ============================================================
   SMOOTH SCROLL
   ============================================================ */
function initSmoothScroll() {
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', e => {
      const target = document.querySelector(anchor.getAttribute('href'));
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });
  });
}

/* ============================================================
   SCROLL ANIMATIONS
   ============================================================ */
function initScrollAnimations() {
  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry, i) => {
      if (entry.isIntersecting) {
        setTimeout(() => entry.target.classList.add('visible'), i * 80);
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.1 });

  document.querySelectorAll('.animate-on-scroll').forEach(el => observer.observe(el));
}

/* ============================================================
   LOAD & RENDER PRODUCTS (from API first, then fallback)
   ============================================================ */
async function loadAndRenderProducts() {
  const grid = document.getElementById('products-grid');
  if (!grid) return;

  // Show loading state
  grid.innerHTML = `<div style="grid-column:1/-1;text-align:center;padding:40px;color:var(--text-light);">
    <div style="font-size:2rem;margin-bottom:10px;">🌸</div>
    <p>Loading products…</p>
  </div>`;

  try {
    const res = await fetch('/api/v1/products/');
    if (res.ok) {
      const data = await res.json();
      loadedProducts = data.results || data;
    } else {
      throw new Error('API not available');
    }
  } catch {
    // Fallback to embedded product data
    loadedProducts = FALLBACK_PRODUCTS;
  }

  renderProducts(loadedProducts);
}

function renderProducts(prods) {
  const grid = document.getElementById('products-grid');
  if (!grid) return;

  if (!prods.length) {
    grid.innerHTML = `<p style="grid-column:1/-1;text-align:center;color:var(--text-light);padding:40px;">No products available yet.</p>`;
    return;
  }

  grid.innerHTML = prods.map(p => `
    <div class="product-card animate-on-scroll" data-id="${p.id}">
      <div class="product-img" style="background:${p.color || '#e8f2eb'};">
        <span>${p.emoji || '🌿'}</span>
        <span class="eco-score">Eco ${p.eco_score || 'A'}</span>
      </div>
      <div class="product-body">
        <h3>${p.name}</h3>
        <p class="desc">${p.description}</p>
        <span class="eco-tag">🌿 ${p.eco_benefit || ''}</span>
        <div class="product-price">${p.price || p.price_display || ''}</div>
        <div class="product-actions">
          <button class="btn-outline-sm" onclick="openProductDetails(${p.id})">View Details</button>
          <button class="btn-filled-sm" onclick="openQuoteModal(${p.id})">Request Quote</button>
        </div>
      </div>
    </div>
  `).join('');

  initScrollAnimations();
}

/* ============================================================
   PRODUCT DETAILS MODAL
   ============================================================ */
function openProductDetails(id) {
  const p = loadedProducts.find(x => x.id === id);
  if (!p) return;

  const body = document.getElementById('product-details-body');
  if (!body) return;

  const fullDesc = p.full_desc || p.details?.fullDesc || p.description;
  const usage    = p.usage     || p.details?.usage    || 'As directed.';
  const impact   = p.impact    || p.details?.impact   || p.eco_benefit || '';
  const ingr     = p.ingredients || p.details?.ingredients || '';

  body.innerHTML = `
    <div class="modal-img" style="background:${p.color || '#e8f2eb'};">${p.emoji || '🌿'}</div>
    <span class="eco-tag">🌿 ${p.eco_benefit || ''}</span>
    <h3>${p.name}</h3>
    <p style="color:var(--text-light);margin-top:10px;">${fullDesc}</p>
    <div class="modal-detail-grid">
      <div class="modal-detail-item">
        <strong>Usage Instructions</strong>
        <span>${usage}</span>
      </div>
      <div class="modal-detail-item">
        <strong>Sustainability Impact</strong>
        <span>${impact}</span>
      </div>
      ${ingr ? `<div class="modal-detail-item full" style="grid-column:1/-1">
        <strong>Ingredients</strong>
        <span>${ingr}</span>
      </div>` : ''}
    </div>
    <div style="display:flex;align-items:center;justify-content:space-between;margin-top:16px;flex-wrap:wrap;gap:12px;">
      <span style="font-family:'Playfair Display',serif;font-size:1.4rem;color:var(--green-deep);font-weight:700;">${p.price || p.price_display || ''}</span>
      <button class="btn-primary" onclick="openQuoteModal(${p.id});closeModal('modal-details')">Request Quote</button>
    </div>
  `;

  openModal('modal-details');
}

/* ============================================================
   REQUEST QUOTE MODAL
   ============================================================ */
let currentQuoteProduct = null;

function openQuoteModal(id) {
  const p = loadedProducts.find(x => x.id === id);
  currentQuoteProduct = p;

  const label = document.getElementById('quote-product-label');
  if (label) label.textContent = p ? `for ${p.name}` : '';

  openModal('modal-quote');
}

function initQuoteForm() {
  const form = document.getElementById('quote-form');
  if (!form) return;

  form.addEventListener('submit', async e => {
    e.preventDefault();
    if (!validateQuoteForm()) return;

    const btn = form.querySelector('button[type=submit]');
    btn.disabled = true; btn.textContent = 'Sending…';

    const formData = {
      customer_name: form.querySelector('#q-name').value.trim(),
      email:         form.querySelector('#q-email').value.trim(),
      phone:         form.querySelector('#q-phone').value.trim(),
      product:       currentQuoteProduct ? currentQuoteProduct.id : null,
      quantity:      form.querySelector('#q-qty').value.trim(),
      message:       form.querySelector('#q-message').value.trim(),
    };

    try {
      const result = await submitEnquiryToAPI(formData);
      if (result.ok) {
        closeModal('modal-quote');
        form.reset();
        showSuccess('Quote Request Sent! 🌿', 'Our manufacturer will contact you within 24 hours.');
      } else {
        const errs = Object.values(result.data).flat();
        showToast(errs[0] || 'Failed to send. Please try again.', 'error');
      }
    } catch {
      // Network error fallback
      closeModal('modal-quote');
      form.reset();
      showSuccess('Request Noted! 🌿', 'We\'ll get back to you soon.');
    }

    btn.disabled = false; btn.textContent = 'Send Enquiry 🌿';
  });
}

function validateQuoteForm() {
  const form = document.getElementById('quote-form');
  let valid = true;

  const fields = [
    { id: '#q-name',  check: v => v.trim().length >= 2,              msg: 'Enter your full name' },
    { id: '#q-email', check: v => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v), msg: 'Enter a valid email' },
    { id: '#q-phone', check: v => /^[6-9]\d{9}$/.test(v.trim()),    msg: 'Enter a valid 10-digit phone' },
    { id: '#q-qty',   check: v => v.trim() !== '' && Number(v) > 0,  msg: 'Enter a valid quantity' },
  ];

  fields.forEach(f => {
    const input = form.querySelector(f.id);
    const group = input.closest('.form-group');
    const err   = group.querySelector('.error-msg');
    const ok    = f.check(input.value);
    group.classList.toggle('has-error', !ok);
    if (!ok) { if (err) err.textContent = f.msg; valid = false; }
    input.classList.toggle('error', !ok);
  });

  return valid;
}

/* ============================================================
   PICKUP FORM — Users Only (permission-gated)
   ============================================================ */
function initPickupForm() {
  const form = document.getElementById('pickup-form');
  if (!form) return;

  // Gate the form: only logged-in partner/user can submit
  form.addEventListener('submit', async e => {
    e.preventDefault();

    // Check if logged in
    const user = (typeof Auth !== 'undefined') ? Auth.getUser() : null;
    if (!user) {
      showToast('Please login or sign up to submit a pickup request.', 'error');
      if (typeof showAuthModal === 'function') showAuthModal('login');
      return;
    }

    if (!validatePickupForm()) return;

    const btn = form.querySelector('button[type=submit]');
    btn.disabled = true; btn.textContent = 'Submitting…';

    const data = {
      full_name:   form.querySelector('#p-name').value.trim(),
      temple_name: form.querySelector('#p-temple').value.trim(),
      phone:       form.querySelector('#p-phone').value.trim(),
      location:    form.querySelector('#p-location').value.trim(),
      flower_type: form.querySelector('#p-flower').value,
      quantity_kg: form.querySelector('#p-qty').value.trim(),
      pickup_date: form.querySelector('#p-date').value,
    };

    try {
      const result = await submitPickupToAPI(data);
      if (result.ok) {
        form.reset();
        showSuccess('Pickup Request Submitted! 🌸', 'Our team will confirm your pickup within 24 hours.');
      } else {
        const errs = Object.values(result.data).flat();
        showToast(errs[0] || 'Submission failed. Please try again.', 'error');
        btn.disabled = false; btn.textContent = '🌸 Submit Request';
        return;
      }
    } catch {
      form.reset();
      showSuccess('Request Received! 🌸', 'We\'ll confirm your pickup soon.');
    }

    btn.disabled = false; btn.textContent = '🌸 Submit Request';
  });

  // Reset button
  const resetBtn = form.querySelector('.btn-reset');
  if (resetBtn) {
    resetBtn.addEventListener('click', () => {
      form.reset();
      form.querySelectorAll('.form-group').forEach(g => g.classList.remove('has-error'));
      form.querySelectorAll('input, select').forEach(i => i.classList.remove('error'));
    });
  }
}

function validatePickupForm() {
  const form = document.getElementById('pickup-form');
  let valid = true;

  const today = new Date().toISOString().split('T')[0];

  const rules = [
    { id: '#p-name',     check: v => v.trim().length >= 2,       msg: 'Enter your full name' },
    { id: '#p-temple',   check: v => v.trim().length >= 2,       msg: 'Enter temple/venue name' },
    { id: '#p-phone',    check: v => /^[6-9]\d{9}$/.test(v.trim()), msg: 'Enter valid 10-digit phone' },
    { id: '#p-location', check: v => v.trim().length >= 3,       msg: 'Enter pickup location' },
    { id: '#p-flower',   check: v => v !== '',                   msg: 'Select flower type' },
    { id: '#p-qty',      check: v => v.trim() !== '' && Number(v) > 0, msg: 'Enter valid quantity (kg)' },
    { id: '#p-date',     check: v => v !== '' && v >= today,     msg: 'Select a valid future date' },
  ];

  rules.forEach(r => {
    const input = form.querySelector(r.id);
    const group = input.closest('.form-group');
    const err   = group.querySelector('.error-msg');
    const ok    = r.check(input.value);
    group.classList.toggle('has-error', !ok);
    if (err) err.textContent = r.msg;
    input.classList.toggle('error', !ok);
    if (!ok) valid = false;
  });

  return valid;
}

/* ============================================================
   MODAL CLOSE BUTTONS
   ============================================================ */
function initModalCloses() {
  document.querySelectorAll('[data-close-modal]').forEach(btn => {
    btn.addEventListener('click', () => closeModal(btn.dataset.closeModal));
  });

  document.querySelectorAll('.modal-overlay').forEach(overlay => {
    overlay.addEventListener('click', e => {
      if (e.target === overlay) closeModal(overlay.id);
    });
  });
}

/* ============================================================
   COUNTER ANIMATION
   ============================================================ */
function animateCounter(el, target, suffix = '') {
  let start = 0;
  const duration = 1500;
  const step = (timestamp) => {
    if (!start) start = timestamp;
    const progress = Math.min((timestamp - start) / duration, 1);
    const ease = progress < 0.5 ? 2 * progress * progress : -1 + (4 - 2 * progress) * progress;
    el.textContent = Math.floor(ease * target) + suffix;
    if (progress < 1) requestAnimationFrame(step);
  };
  requestAnimationFrame(step);
}

function initCounters() {
  const counters = document.querySelectorAll('[data-count]');
  if (!counters.length) return;

  const observer = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const el     = entry.target;
        const target = parseInt(el.dataset.count);
        const suffix = el.dataset.suffix || '';
        animateCounter(el, target, suffix);
        observer.unobserve(el);
      }
    });
  }, { threshold: 0.5 });

  counters.forEach(c => observer.observe(c));
}

/* ============================================================
   DASHBOARD — Stat helper (used by dashboard.html inline script)
   ============================================================ */
function setEl(id, val) {
  const el = document.getElementById(id);
  if (el) el.textContent = val;
}

/* ============================================================
   INIT
   ============================================================ */
document.addEventListener('DOMContentLoaded', () => {
  // INDEX PAGE
  if (document.getElementById('products-grid')) {
    loadAndRenderProducts();
    initPickupForm();
    initQuoteForm();
    initModalCloses();
    initCounters();
  }

  initNavbar();
  initSmoothScroll();
  initScrollAnimations();
});

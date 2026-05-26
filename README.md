# 🌸 FloraCycle — Eco Flower Waste Management Platform (v2 Fixed)

FloraCycle collects flower waste from temples and venues, converts it into eco-products (agarbatti, compost, Holi colors), and sells them back through a clean web platform.

---

## ⚡ Quick Start (One Command)

```bash
bash setup.sh
```

Then open **http://127.0.0.1:8000** in your browser.

---

## 🔑 Login Credentials

| Role    | Email                    | Password      | Access |
|---------|--------------------------|---------------|--------|
| Admin   | admin@floracycle.in      | Admin@1234    | Full dashboard, manage products, update pickup status, view enquiries |
| Partner | temple@floracycle.in     | Partner@1234  | Submit pickup requests, browse products, request quotes |

> **Register new accounts** via the Sign Up button → choose "Temple/Venue Partner" for user role.

---

## 👑 Permissions Summary

| Action                        | Public | Partner (logged in) | Admin |
|-------------------------------|--------|---------------------|-------|
| Browse products               | ✅     | ✅                  | ✅    |
| Request quote / enquiry       | ✅     | ✅                  | ✅    |
| Submit pickup request         | ❌     | ✅                  | ✅    |
| View dashboard                | ❌     | ❌                  | ✅    |
| Update pickup status          | ❌     | ❌                  | ✅    |
| Add / edit / delete products  | ❌     | ❌                  | ✅    |
| View all enquiries            | ❌     | ❌                  | ✅    |

---

## 🐛 Issues Fixed in v2

1. **Login system** — Clear error messages for wrong password, inactive account, already-registered email
2. **localStorage conflicts** — Tokens now use `sessionStorage`; demo data keys don't collide with auth keys
3. **Homepage products** — Loaded live from `/api/v1/products/` with embedded fallback if API is offline
4. **Pickup form permission** — Shows login prompt if user not authenticated; sends to real API
5. **Enquiry form** — Posts to `/api/v1/enquiries/` with confirmation toast
6. **Dashboard auth.js missing** — `auth.js` now loaded in `dashboard.html`
7. **Wrong API URLs** — `/pickups/list/` → `/pickups/all/`, `/enquiries/list/` → `/enquiries/all/`
8. **Product field mismatch** — `price_display` → `price` in add-product POST body
9. **Admin redirect** — Partners redirected away from dashboard with clear message
10. **Demo data seeded** — `setup.sh` auto-creates admin + partner accounts + 4 products

---

## 📁 Project Structure

```
FloraCycle_fixed/
├── setup.sh                  # One-command setup (run this first)
├── manage.py
├── requirements.txt
├── .env.example
├── config/
│   ├── settings.py           # JWT, CORS, SQLite/PostgreSQL
│   └── urls.py
├── apps/
│   ├── users/                # Custom User model + JWT auth
│   ├── products/             # Eco-product catalog
│   ├── pickups/              # Pickup request management
│   ├── enquiries/            # Quote/enquiry management
│   ├── dashboard/            # Admin summary API
│   └── permissions.py        # IsAdminRole permission class
└── frontend/
    ├── index.html            # Main landing page
    ├── dashboard.html        # Admin dashboard
    ├── auth.js               # JWT auth, login/signup forms, session guard
    ├── script.js             # Product render, pickup/enquiry forms
    └── style.css             # All styles
```

---

## 📡 API Reference

### Auth
| Method | Endpoint                    | Auth     | Description |
|--------|-----------------------------|----------|-------------|
| POST   | /api/v1/auth/register/      | None     | Register new user |
| POST   | /api/v1/auth/login/         | None     | Login → returns JWT |
| POST   | /api/v1/auth/logout/        | Bearer   | Logout (blacklists token) |
| POST   | /api/v1/auth/refresh/       | None     | Refresh access token |
| GET    | /api/v1/auth/profile/       | Bearer   | Get own profile |

### Products
| Method | Endpoint                    | Auth       | Description |
|--------|-----------------------------|------------|-------------|
| GET    | /api/v1/products/           | None       | List active products |
| GET    | /api/v1/products/<id>/      | None       | Product detail |
| POST   | /api/v1/products/create/    | Admin only | Create product |
| PATCH  | /api/v1/products/<id>/manage/ | Admin only | Update product |
| DELETE | /api/v1/products/<id>/manage/ | Admin only | Soft-delete product |

### Pickups
| Method | Endpoint                    | Auth       | Description |
|--------|-----------------------------|------------|-------------|
| POST   | /api/v1/pickups/            | Any logged-in | Submit pickup request |
| GET    | /api/v1/pickups/all/        | Admin only | List all pickups |
| PATCH  | /api/v1/pickups/<id>/       | Admin only | Update status |

### Enquiries
| Method | Endpoint                    | Auth       | Description |
|--------|-----------------------------|------------|-------------|
| POST   | /api/v1/enquiries/          | None       | Submit enquiry |
| GET    | /api/v1/enquiries/all/      | Admin only | List all enquiries |

### Dashboard
| Method | Endpoint                    | Auth       | Description |
|--------|-----------------------------|------------|-------------|
| GET    | /api/v1/dashboard/summary/  | Admin only | Stats + recent data |

---

## 🧪 Manual Testing

```bash
# Register
curl -X POST http://localhost:8000/api/v1/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","full_name":"Test User","password":"Test@1234","password2":"Test@1234","role":"partner"}'

# Login
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@floracycle.in","password":"Admin@1234"}'

# Submit pickup (replace TOKEN)
curl -X POST http://localhost:8000/api/v1/pickups/ \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"full_name":"Arjun Patel","temple_name":"Shree Ram Temple","phone":"9876543210","location":"Pune","flower_type":"Marigold","quantity_kg":15,"pickup_date":"2026-06-01"}'
```

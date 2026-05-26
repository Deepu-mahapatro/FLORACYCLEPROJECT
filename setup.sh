#!/usr/bin/env bash
# ================================================================
# FloraCycle — One-Command Setup Script  (v2 FIXED)
# Usage: bash setup.sh
# ================================================================

set -e
GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; CYAN='\033[0;36m'; NC='\033[0m'

echo ""
echo -e "${GREEN}🌸 FloraCycle Setup (v2)${NC}"
echo "======================================="

# ── 1. Python check ──────────────────────────────────────────
echo -e "\n${YELLOW}[1/7] Checking Python...${NC}"
python3 --version || { echo -e "${RED}Python 3 not found. Install it first.${NC}"; exit 1; }

# ── 2. Virtual environment ────────────────────────────────────
echo -e "\n${YELLOW}[2/7] Creating virtual environment...${NC}"
python3 -m venv venv
source venv/bin/activate
echo "Activated: $(which python)"

# ── 3. Install dependencies ───────────────────────────────────
echo -e "\n${YELLOW}[3/7] Installing Python packages...${NC}"
pip install --upgrade pip -q
pip install -r requirements.txt -q
echo "All packages installed."

# ── 4. Create .env file ───────────────────────────────────────
echo -e "\n${YELLOW}[4/7] Setting up .env...${NC}"
if [ ! -f .env ]; then
    cp .env.example .env
    SECRET=$(python3 -c "import secrets,string; print(''.join(secrets.choice(string.ascii_letters+string.digits+'!@#\$%^&*') for _ in range(52)))")
    sed -i "s|your-very-secret-key-change-this-in-production-use-50-chars|${SECRET}|" .env
    echo ".env created with a new secret key."
else
    echo ".env already exists — skipping."
fi

# ── 5. Database migrations ────────────────────────────────────
echo -e "\n${YELLOW}[5/7] Running migrations...${NC}"
python manage.py migrate --run-syncdb

# ── 6. Seed demo admin + partner accounts ─────────────────────
echo -e "\n${YELLOW}[6/7] Creating demo accounts...${NC}"
python manage.py shell << 'PYEOF'
from apps.users.models import User

# Admin account
if not User.objects.filter(email='admin@floracycle.in').exists():
    u = User.objects.create_user(
        email='admin@floracycle.in',
        password='Admin@1234',
        full_name='FloraCycle Admin',
        phone='9800000000',
        role='admin',
    )
    u.is_staff = True
    u.is_superuser = True
    u.save()
    print('  ✅ Admin account created:   admin@floracycle.in / Admin@1234')
else:
    print('  ✅ Admin account already exists.')

# Remove the old hardcoded demo partner if it still exists in the DB
from django.db import connection
tables = connection.introspection.table_names()
if 'fc_users' in tables:
    User.objects.filter(email='temple@floracycle.in').delete()
    print('  ✅ Removed hardcoded demo partner (temple@floracycle.in) if it existed.')
# Partners register via the public signup form — no demo data seeded.

# Seed demo products if none exist
from apps.products.models import Product
if not Product.objects.exists():
    products = [
        dict(name='Rose Agarbatti', emoji='🌹', description='Hand-rolled incense sticks made from collected temple roses and jasmine waste.', eco_benefit='Saves 2kg flower waste per batch', price='₹120 / pack of 20', eco_score='A+', color='#ffe0ec', full_desc='Crafted using traditional hand-rolling combined with sustainable processes.', usage='Light the tip and place in a holder. Burns 30–40 minutes.', impact='1 pack = 2kg temple flowers diverted from river pollution', ingredients='Dried rose petals, jasmine, bamboo stick, natural gum binder'),
        dict(name='Compost Powder', emoji='🌱', description='Nutrient-rich organic compost derived from processed flower and leaf waste.', eco_benefit='Enriches 10 sq.ft of soil per kg', price='₹80 / kg', eco_score='A+', color='#e0f0d8', full_desc='Fully organic soil enrichment product from aerobically processed flower waste.', usage='Mix 100g per litre of potting mix. Water after application.', impact='Each kg prevents 2kg of organic waste from landfills', ingredients='Processed flower waste, dried leaves, organic activator'),
        dict(name='Natural Holi Colors', emoji='🎨', description='Vibrant Holi colors extracted naturally from marigolds, roses, and hibiscus.', eco_benefit='100% skin-safe, zero chemical dyes', price='₹60 / 100g pack', eco_score='A', color='#fff0cc', full_desc='Extracted using cold-press and sun-drying techniques. Dermatologically tested.', usage='Use dry or mix with water. Safe for all skin types.', impact='Each pack replaces 3 chemical dye packets, uses 500g flower waste', ingredients='Dried marigold, rose petal powder, hibiscus extract, arrowroot base'),
        dict(name='Organic Dhoop Sticks', emoji='🪔', description='Thick aromatic dhoop sticks with calming floral and herbal blends.', eco_benefit='Made from 100% temple flower waste', price='₹150 / pack of 12', eco_score='A+', color='#ede0ff', full_desc='Combines temple flowers with sandalwood powder and medicinal herbs.', usage='Place on dhoop holder and light the flat end. Use in ventilated spaces.', impact='Each pack uses 1.5kg of flower waste, supports 2 artisan jobs', ingredients='Temple flower mix, sandalwood powder, natural resin, medicinal herbs'),
    ]
    for pd in products:
        Product.objects.create(**pd)
    print(f'  ✅ {len(products)} demo products seeded.')
else:
    print(f'  ✅ Products already exist ({Product.objects.count()} found).')
PYEOF

# ── 7. Done ───────────────────────────────────────────────────
echo ""
echo -e "${GREEN}✅ Setup complete!${NC}"
echo ""
echo -e "${CYAN}  Start the server:${NC}"
echo "    source venv/bin/activate && python manage.py runserver"
echo ""
echo -e "${CYAN}  Open in browser:${NC}    http://127.0.0.1:8000"
echo -e "${CYAN}  Django admin:${NC}       http://127.0.0.1:8000/admin/"
echo -e "${CYAN}  API base:${NC}           http://127.0.0.1:8000/api/v1/"
echo ""
echo -e "${GREEN}🔑 Login Credentials:${NC}"
echo -e "  ${YELLOW}Admin    →${NC}  admin@floracycle.in   /  Admin@1234"
echo -e "  ${YELLOW}Partner  →${NC}  Register via /  (public signup form)"
echo ""
echo -e "${GREEN}👑 Permissions:${NC}"
echo -e "  Partner  → Can submit pickup requests"
echo -e "  Admin    → Can update pickup status, add/edit products, view all enquiries"
echo ""
echo -e "${GREEN}📡 API Endpoints:${NC}"
echo "  POST /api/v1/auth/register/        — Create new account"
echo "  POST /api/v1/auth/login/           — Login (returns JWT)"
echo "  POST /api/v1/auth/logout/          — Logout (blacklists token)"
echo "  POST /api/v1/auth/refresh/         — Refresh access token"
echo "  GET  /api/v1/products/             — List all products (public)"
echo "  POST /api/v1/pickups/              — Submit pickup (any logged-in user)"
echo "  GET  /api/v1/pickups/all/          — List all pickups (admin only)"
echo "  PATCH /api/v1/pickups/<id>/        — Update pickup status (admin only)"
echo "  POST /api/v1/enquiries/            — Submit quote enquiry (public)"
echo "  GET  /api/v1/enquiries/all/        — List all enquiries (admin only)"
echo "  POST /api/v1/products/create/      — Add product (admin only)"
echo "  GET  /api/v1/dashboard/summary/    — Dashboard stats (admin only)"
echo ""

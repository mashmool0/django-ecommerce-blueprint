# Django E-Commerce Blueprint (Models-First)

A fast-start **Django** e-commerce foundation you can **clone and run in minutes**.
It’s opinionated around a clean domain model (catalog → cart/checkout → orders/payments → reviews/messaging → analytics → CMS/SEO) so you can focus on your business logic, marketing, and UI instead of reinventing tables.

* Clone → migrate → seed → explore in Admin → build.
* Production-leaning models with Persian content (fa-IR), English slugs, E.164 phone auth, and Iran-friendly defaults.
* Designed to **grow into advanced marketing & campaign automation** (Mixpanel/GA4, SMS, coupons, shortlinks, snapshots).

> This repo is **models-first**. Admin & seeders are included.
> APIs and Docker are optional and not enabled by default—you can add them when you’re ready.

---

## 🚀 Quick Start

```bash
# 1) get the code
git clone <YOUR_REPO_URL> django-ecommerce-blueprint
cd django-ecommerce-blueprint

# 2) env & deps (Python 3.11+ recommended)
python3 -m venv venv
source venv/bin/activate
pip install -U pip
pip install -r requirements.txt
cp .env.example .env

# 3) migrate + seed + run
python manage.py migrate
python manage.py createsuperuser
python manage.py seed_demo
python manage.py seed_promos_carts
python manage.py seed_order_from_checkout
python manage.py seed_reviews_messaging
python manage.py seed_analytics
python manage.py seed_cms
python manage.py runserver 127.0.0.1:8080
```

Open **Admin:** `http://127.0.0.1:8080/admin/`

---

## ✅ What’s Inside (high-level)

* **Auth:** custom User with **phone (OTP)** as username + optional password, Profile, and OTP audit table.
* **Catalog:** Brand, Category (tree), Product (SPU), Variant (SKU), Allowed weights (enum table), Grind types, Media assets, **price history**.
* **Promotions:** site-wide **GlobalDiscount**, **Coupons** (percent/fixed, scope & limits).
* **Inventory:** single warehouse (extensible), **StockItem** (on-hand/reserved), **StockReservation** (checkout TTL).
* **Cart & Checkout:** guest/user carts, line snapshots, coupon attach, **Checkout snapshot** of totals & address.
* **Orders:** immutable **OrderHeader/OrderLine** snapshots (money/fees/COGS), Shipments, Returns, Coupon redemptions.
* **Payments:** **Zarrinpal** service & example create/verify endpoints (commented out by default).
* **Reviews & Wishlist:** product reviews tied to **verified purchases**, optional images; wishlists per variant.
* **Messaging:** Campaigns, **SMS outbox** (provider-agnostic, Amoot-friendly), shortlinks & click tracking.
* **Analytics:** write-once **EventLog**, **DailyUserSnapshot**, **DailyInventorySnapshot** for fast dashboards.
* **CMS + SEO:** Articles (blog) with categories & tags + product linking, Pages, reusable **SeoMeta** blocks, site SEO defaults.

---

## 🧭 Project Layout

```
apps/
  accounts/   # custom phone user, profile, OTP
  analytics/  # EventLog + daily user/inventory snapshots
  carts/      # Cart, CartItem, Checkout
  catalog/    # Brand/Category, Product/Variant, Price history, Promotions, Media
  cms/        # Articles, Pages, SeoMeta blocks, Article↔Product links
  common/     # base models (UUID, timestamps), management commands (seeders)
  inventory/  # Warehouse, StockItem, StockReservation
  messaging/  # Campaign, MessageOutbox, ShortLink, ShortLinkClick
  orders/     # OrderHeader/Line, Shipment, Returns, CouponRedemption
  payments/   # Payment model + Zarrinpal service (example API, not wired by default)
django-ecommerce-blueprint/
  settings/   # base.py, local.py, prod.py (env-driven)
  urls.py     # admin (+ optional docs); business APIs disabled by default
manage.py
```

**Conventions**

* Content Persian (`*_fa` fields), **slugs English** (`slug_en`).
* Currency: **toman** (integers).
* Phone: **E.164** (+98…).
* Timezone: **Asia/Tehran**, language **fa-IR**.

---

## 🧩 Core Design & Why

* **SPU/SKU split:** `Product` (marketing) vs `ProductVariant` (weight/grind) so **stock, price, limits, analytics** are correct per variant.
* **Snapshot everything:** Orders store all money & fees (`subtotal`, `discounts`, `shipping`, `gateway_fee`, `refund_amount`) + per-line price/COGS. This keeps reports simple & stable.
* **Promotions order:** Apply **coupon** first, then **global discount**, then add shipping/tax (documented & consistent).
* **OTP as separate table:** secure, auditable, supports pre-signup flows and throttling.
* **Analytics snapshots:** nightly `Daily*Snapshot` tables make dashboards fast (no heavy joins).

---

## 🔧 Setup & Configuration

### Requirements

* Python **3.11+**
* SQLite (default) or Postgres (recommended for real projects)
* A working virtualenv

### Environment variables (`.env`)

```env
# Core
SECRET_KEY=change-me
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=sqlite:///db.sqlite3
CORS_ALLOWED_ORIGINS=http://localhost:3000

# (Optional) Payments – example only, APIs disabled by default
ZARRINPAL_MERCHANT_ID=test-merchant-id
ZARRINPAL_BASE_URL=https://sandbox.zarinpal.com/pg/rest/WebGate/
PAYMENTS_CALLBACK_BASE=http://127.0.0.1:8080
ZARRINPAL_CALLBACK_PATH=/api/payments/zarrinpal/verify/
```

> Switch to Postgres by setting `DATABASE_URL` like
> `postgres://user:pass@localhost:5432/shop`

---

## 🗃️ Seeders (Demo Data)

Run any time; they’re idempotent:

* `seed_demo` — brands/categories/products, variants, prices, media, **stock**.
* `seed_promos_carts` — 10% **GlobalDiscount**, `WELCOME10` coupon, **guest cart** + items + **Checkout** snapshot.
* `seed_order_from_checkout` — converts the demo **Checkout → Order**, adds Payment row (captured) & Shipment.
* `seed_reviews_messaging` — 2 **reviews** (verified purchase), wishlist entries, SMS **campaign/outbox**, **shortlink** + click.
* `seed_analytics` — event log rows (page/product/cart/order), **DailyUserSnapshot**, **DailyInventorySnapshot**.
* `seed_cms` — 2 blog **articles** (+ category/tags), **About** page, SEO blocks & **site SEO defaults**.

---

## 🛠️ How to Run (Dev)

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver 127.0.0.1:8080
```

* Admin: `http://127.0.0.1:8080/admin/`
* (Optional) API docs: `/api/docs/` if you kept drf-spectacular wired.

---

## 🔒 Authentication Model

* `accounts.User` (custom): **phone\_number** is the username; optional password.
* `accounts.OTPCode`: hashed codes (+ purpose, expiry, attempts) — separate table for **security/audit**.
* `accounts.UserProfile`: first/last name (fa), birthday, city, **SMS opt-in** fields.

**Why separate OTP?** Pre-signup flows, auditability, rate-limit & retries, and no racey single “otp” slot on User.

---

## 🛍️ Catalog & Promotions

* `catalog.Product` (SPU) → `ProductVariant` (SKU) with **AllowedWeight** and `GrindType`.
* `VariantPrice` captures **price history** (and compare-at).
* `GlobalDiscount` toggles site-wide % off.
* `Coupon` supports **percent/fixed**, time windows, **scope** (categories/products), and usage limits.

---

## 📦 Inventory

* `Warehouse` (single now; future-proofed)
* `StockItem` (per variant): `on_hand`, `reserved`, `reorder_level`
* `StockReservation` (variant, cart, qty, `expires_at`) to prevent oversell during checkout spikes.

---

## 🛒 Cart & Checkout

* `Cart` for **user or guest** (`anonymous_id`); optional `applied_coupon`.
* `CartItem` stores a **unit\_price\_snapshot\_toman** (so UI doesn’t flicker if price changes).
* `Checkout` freezes **totals**, address, delivery & payment method, so payment/verify is deterministic.

---

## 📑 Orders, Payments & Shipping

* `OrderHeader` & `OrderLine` store **immutable snapshots** (money, fees, COGS, weight) for eternal accuracy.
* `Shipment` (carrier/status/tracking, fee snapshot), `ReturnRequest/ReturnItem`.
* `CouponRedemption` records **actual discount** a coupon gave on the order.
* `Payment` (Zarrinpal-ready) is linked to **Checkout** first; after verify, it binds to the **Order**.

> Example Zarrinpal create/verify endpoints exist but **are not included in root URLs** by default (models-first focus). Enable them when ready (see below).

---

## ⭐ Reviews, Wishlist, Messaging

* `Review` ties to **Product + User + Order** → enforce **verified purchase**.
* `ReviewMedia` lets you attach images (via `MediaAsset`).
* `Wishlist` is per **variant**.
* `Campaign` & `MessageOutbox` (SMS), provider/status fields, and `ShortLink` + `ShortLinkClick` for CTR tracking.

---

## 📈 Analytics & SEO

* `EventLog` ledger for **page/product/cart/order** events with UTM & arbitrary properties; booleans to mark **sent to GA/Mixpanel**.
* `DailyUserSnapshot` & `DailyInventorySnapshot` to power dashboards (CLTV, churn, turnover) without heavy joins.
* `SeoMeta` blocks for **Product/Category/Article/Page** + `SiteSeoDefault` fallback.

---


## 🛣️ Roadmap (what you can add next)

* DRF APIs for catalog/cart/checkout/orders (JWT + OTP endpoints).
* Payment provider abstraction & tests (mock gateway).
* Celery + scheduled tasks (daily snapshots, cleanups).
* Docker Compose (Postgres/Redis) when you want infra.
* Basic test suite (pytest-django).
* ERD diagram in `/docs/`.

---

## 📄 License

**MIT** — free for commercial & personal use.

---

## 🙋 FAQ

* **Why English slugs with Persian content?**
  Cleaner URLs, better tooling compatibility, easy admin search; content stays Persian (`*_fa` fields).

* **Why separate OTP table?**
  Security, audit, pre-signup flows, and proper throttling/rate limiting.

* **Can I use multiple warehouses or currencies later?**
  Yes. The schema is extensible—add more warehouses & currency fields without breaking the core model.

---

If you spot anything rough or want a feature added, open an issue or a PR. Happy building! ☕

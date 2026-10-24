# Masarak

A mobile-first Flask prototype for smarter everyday choices in Saudi Arabia. The interface follows the supplied Masarak screens: teal/green cards, a shared header, Food and Market comparisons, and persistent bottom navigation. It adapts from 320px phones to centered desktop layouts without a phone frame.

## Run locally

Requires Python 3.10 or newer (tested on Python 3.12).

```bash
python -m venv venv
```

Activate the environment:

```bash
# macOS / Linux
source venv/bin/activate

# Windows PowerShell
venv\Scripts\Activate.ps1

# Windows Command Prompt
venv\Scripts\activate.bat
```

Install and start:

```bash
pip install -r requirements.txt
python app.py
```

Open `http://localhost:5000`. Set `PORT` to change the port. The server listens on all interfaces for cloud development; Flask debug mode is off. This is a development server, not a production deployment.

Cloud checkout: `/workspace/masarak`. The prepared virtual environment is `.venv`, so run `.venv/bin/python app.py` there. Each cloud task is already isolated; use this checkout without creating a Git worktree.

## What works

- Food and Market compare **only HungerStation and Ninja**, using illustrative local JSON.
- Best prices are calculated in Python; tied valid offers are both highlighted. No cheapest provider is hard-coded.
- Grocery filters run without reloading. Home search finds known Masarak features.
- Riyadh, Jeddah, and Dammam are prototype city choices stored in browser localStorage. No GPS is used and changing cities does not change the sample dataset.
- A deterministic demo assistant recommends catalog items and adds selected offers to a session cart. It is not connected to a language model or live external data.
- Cart add/remove/quantity changes use server-calculated prices and validated provider/item references. Each offer supports 1–20 units; the demo supports up to 12 distinct offers.
- Demo checkout clearly reports that **no payment was taken and no order was submitted**. Cart totals are illustrative item subtotals; delivery, tax and service fees are not quoted.
- Wallet, profile, notifications, and membership use demo information. Wallet buttons explain their prototype status without collecting financial details.
- Ride and Hotels have coming-soon/demo screens and appear under Future alongside flights and World Cup 2034. No fake booking results are generated.

## Project layout

```text
app.py                    Application factory, HTML routes, JSON API, safe errors
services/comparison.py    Price normalization, provider restriction, JSON loading
services/food_comparison.py     Replaceable food data source
services/grocery_comparison.py  Replaceable grocery data source
services/cart.py          Validated session cart, authoritative sample totals
services/assistant.py     Replaceable demo recommendation boundary
services/payments.py      Demo payment adapter; future provider integration point
data/                     Sample food and grocery catalogs
templates/                Jinja pages and reusable UI macros
static/css/               Brand styles and responsive overrides
static/js/                Search, city, filters, cart, and assistant interactions
static/images/            Local line icons and illustrated placeholders
scrapers/README.md        Future scraper handoff and expected schema
tests/                    Standard-library unittest suite
```

## Routes

| Route | Purpose |
| --- | --- |
| `/` | Home, category search, quick access, recommendations |
| `/food`, `/grocery` | Comparison screens |
| `/offers` | Best sample offers |
| `/future` | Upcoming services |
| `/coming-soon/ride`, `/coming-soon/hotels` | Honest demo/coming-soon pages |
| `/wallet`, `/profile` | Demo account screens |
| `/assistant` | Chat and catalog recommendations |
| `/cart`, `/checkout` | Working sample cart and demo checkout |
| `GET /api/food`, `GET /api/grocery` | `{source: "sample", currency: "SAR", items: [...]}` |
| `GET /api/cart` | Current cart with calculated totals |
| `POST /api/cart` | Add, update or remove validated cart entries |
| `POST /api/assistant` | `{message: "I want Al Baik"}` → reply and recommendations |
| `POST /api/checkout` | Explicit demo result; never charges/submits |

Unknown routes return branded 404 pages. Broken data sources return friendly 503 states. Unexpected server failures have a branded 500 page without exposed stack traces. Mutation endpoints require the session CSRF token from the page's `csrf-token` meta element in the `X-CSRF-Token` header. Browser helpers implement this automatically.

Cart add request:

```json
{"kind":"food","item_id":"albaik","provider":"Ninja","quantity":1}
```

For update/remove, send `{"action":"update","key":"food:albaik:Ninja","quantity":2}` or `{"action":"remove","key":"food:albaik:Ninja"}`. Submitted price fields are ignored. All responses use SAR.

## Connect scraper data later

No external platforms are scraped by this application. Replace the source in `get_food_data()` / `get_grocery_data()` with your Python pipeline output, retaining normalization through `load_items()` (or its record normalization equivalent). Templates and APIs consume the same normalized schema, so a data-source replacement does not require frontend changes. See [scrapers/README.md](scrapers/README.md).

Do not relabel data as live until the source is connected and validated; update the API `source` and visible sample notices together. Production comparisons should also define item equivalence, timestamps, location coverage, taxes, fees, and stock semantics.

## Future AI, payment and ordering integrations

`services/assistant.py:recommend()` is the assistant boundary. A future model must still return validated catalog references; model text or browser input must never set authoritative prices. Rendering uses text nodes for user messages.

`services/payments.py:DemoPaymentProvider` defines the initial checkout boundary. Select a payment provider before replacing it. Real payments require secure server credentials, verified webhooks, idempotent operations, authentication, persistent orders, delivery/tax calculation, and reconciliation. Real HungerStation/Ninja order submission additionally requires a supported ordering integration. Scraped prices alone do not enable ordering. The current adapter cannot accept payment details or submit an external order.

For development, the app generates a random session signing key at process startup if `MASARAK_SECRET_KEY` is absent. That fallback resets sessions/carts on restart and is suitable only for local demos. For persistent sessions, set a stable random `MASARAK_SECRET_KEY` through secure environment configuration; do not commit it. Configure secure cookies and a production WSGI server behind HTTPS for deployment. The cookie cart is a small prototype, not order persistence.

## Branding and assets

The official logo was visible in the conversation but was not supplied as an accessible file in the workspace. The app does not invent a replacement mark. Place the original PNG at:

```text
static/images/logo/masarak.png
```

The shared header automatically uses it when present. Until then a plain Masarak wordmark identifies the app. Local SVG food/product illustrations are intentional placeholders, not real provider product photos. Replace each file under `static/images/placeholders/` or change the JSON `image` filename to a matching local asset. Ensure those images exist and provide accessible alt text.

## WebView and accessibility

The app includes `viewport-fit=cover`, safe-area padding, touch targets, semantic controls, visible focus states, reduced-motion support, and sufficient content space above fixed navigation. It uses internal navigation, local assets, no popup windows, and no GPS request. The optional manifest supplies name, standalone mode, and theme colors; PWA install icons/offline support await the original brand assets and are not implemented.

## Validation

```bash
python -m unittest discover -s tests -v
node --check static/js/main.js
node --check static/js/comparison.js
node --check static/js/assistant.js
```

The suite covers normalization, malformed data, provider restrictions, rendered routes, APIs, safe errors, cart quantity/provider/price validation, CSRF, assistant catalog recommendations, and demo checkout. Node is only needed for the optional JavaScript syntax check, not to run the app.

Optional browser QA uses Playwright (not a runtime dependency):

```bash
pip install playwright
# Use an existing Chromium or install a browser with Playwright.
# Start Flask first in another terminal.
MASARAK_BROWSER=/usr/bin/chromium python tests/browser_qa.py
```

Browser QA covers 320px, 390px, 768px and 1440px, page overflow, local image loading, search, city persistence, filters, assistant/cart, demo checkout, navigation and browser errors. Screenshots are saved to ignored `artifacts/`.

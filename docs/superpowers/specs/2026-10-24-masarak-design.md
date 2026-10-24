# Masarak application design

## Intent and constraints
Build the actual mobile-first Saudi service comparison application described in the uploaded brief. Follow the supplied screenshots, teal-to-green palette, rounded cards, consistent header, and fixed bottom navigation. Support 320px through desktop widths with safe-area spacing and accessible controls. Use Python 3, Flask, Jinja, custom CSS, vanilla JavaScript, and JSON; no frontend framework or Bootstrap.

## Approaches and decision
The proposed Flask application with server-rendered templates and replaceable Python data services was accepted. A frontend framework conflicts with the requested stack. Connecting live scraping, payments, or external ordering now depends on integrations that have not been supplied. Prepare those boundaries while making the current sample-data workflow usable and clearly labeled.

## Screens and navigation
Implement Home, Food, Grocery/Market, Offers, Future, Wallet, Assistant, Profile, reusable Coming Soon, and branded error pages. Preserve the screenshot hierarchy, greeting, two-by-two quick access, recommendations, comparison cards, membership card, wallet presentation, and assistant chat. Home search routes to known internal features; grocery categories filter without reload. Store the selected prototype city in localStorage. Include every navigation path in the supplied QA checklist. Rides and hotels remain demo/coming-soon experiences, also listed under Future alongside flights and World Cup 2034.

## Comparison and data
Food and Market support only HungerStation and Ninja everywhere, including offers and assistant text. Until scraper code arrives, use explicitly labeled illustrative JSON prices. Central Python loading and normalization services feed both templates and /api/food and /api/grocery. Handle malformed records, missing or unavailable prices, numeric strings, duplicate providers, ties, and SAR formatting. Select best prices from valid available offers rather than hard-coding a provider. Missing data produces a useful empty/error state. Document the schema and scraper replacement points; do not scrape external services during this build.

## Assistant and cart
The accepted initial ordering scope is choosing sample items and preparing a cart. Build a working deterministic assistant flow that uses the comparison services and supports selecting an item, provider, and quantity, inspecting the cart, and proceeding to checkout. Clearly identify this as a demo assistant using sample data. Keep assistant responses behind a replaceable service boundary for a future model/API. Cart contents and totals are validated by the backend; client-provided prices are not authoritative. No external order is submitted without a supported provider ordering integration.

## Payments and wallet
Payment provider is undecided. Define a small provider-independent checkout boundary with a demo implementation that cannot charge money. Show an explicit demo checkout confirmation without claiming payment or delivery occurred. Do not collect real payment details. Wallet balances, transactions, top-up, send, and payment-method interactions are demo-only until a real integration is selected. Future payment work requires provider selection, secure credentials, server-side payment validation, webhook verification, and external order coordination.

## Architecture and implementation choices
Use app.py/application factory, modular services, templates, static/css, static/js, static/images, data JSON, tests, requirements, and README. These organization choices are the builder's defaults. Serve assets locally where practical. Use the supplied official logo if an accessible image file is available; never silently replace it with a redrawn mark. If inaccessible, document the missing asset and its expected path. Food/product placeholders may be local. Flask sessions hold the prototype cart; secrets come from environment configuration, with an explicitly development-only local fallback. No production readiness claim.

## Validation and delivery
Test price normalization and best-price behavior, provider restrictions, data failure states, routes/APIs, cart validation, and demo checkout. Start Flask and make functional HTTP requests. Where browser automation is available, verify mobile and desktop layout, search, city persistence, filters, assistant/cart, and navigation, including overflow and browser errors. Document any unverified behavior and missing assets/integrations. Provide install/run instructions, scraper integration guidance, WebView considerations, and reusable cloud startup configuration after implementation. Use the existing isolated checkout; do not create a worktree.

## Deferred integrations
Real scraped datasets and scraper Python code, real AI credentials/model integration, payment provider and credentials, and supported HungerStation/Ninja order submission are not available yet. Current functionality must remain honest about these boundaries.

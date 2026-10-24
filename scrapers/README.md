# Future scraper integration

No scraper is implemented or executed in this version. Connect your existing Python data pipeline here once supplied. Both Food and Market currently support only HungerStation and Ninja.

## Source boundary

`services/food_comparison.py:get_food_data()` and `services/grocery_comparison.py:get_grocery_data()` return the records used by both Jinja templates and JSON APIs. Currently they call `services/comparison.py:load_items()` with a sample file. Change the source path to your validated scraper output; keep the same return schema. Use atomic file replacement so readers never observe half-written JSON.

## Input contract

Top level: JSON list of item objects. Required fields: unique stable `id`, `name` (or food `restaurant`), and `providers` list. Item image filenames reference local `static/images/placeholders/` assets. Grocery category is one of Dairy, Produce, Pantry. Food also supplies `category`, `cuisine`, `distance_km`, and `rating`.

```json
[
  {
    "id": "milk",
    "name": "Fresh Milk (2L)",
    "category": "Dairy",
    "image": "milk.svg",
    "providers": [
      {"name": "HungerStation", "price": "12.00", "available": true, "delivery_minutes": 30},
      {"name": "Ninja", "price": 13, "available": true, "delivery_minutes": 20}
    ]
  }
]
```

Food delivery estimates can use `delivery_min` / `delivery_max` instead of `delivery_minutes`. Price is SAR numeric or a plain numeric string, not a formatted `SAR 12` string. Missing, negative, nonfinite, boolean and malformed prices cannot win comparisons. `available: false` removes the offer from best-price selection. Provider names are normalized case-insensitively and unsupported platforms are excluded. Duplicate providers retain the lowest valid available price; ties across different providers both receive `is_best`.

Output adds `title`, normalized string `id`, and providers containing canonical `name`, numeric-or-null `price`, `available`, human-readable `delivery`, and calculated `is_best`. Malformed individual records are skipped; broken/missing files raise `DataUnavailable` and yield safe 503 responses.

## Before real data goes live

Define equivalent basket/item sizes across providers, location coverage, availability timestamps and tax/fee treatment. Update the API `source`, visible sample notices, assistant disclaimers and checkout assumptions together. Keep a safe stale-data/error state. Scraper prices are not permission or capability to submit orders: actual ordering needs a supported platform integration. No credentials belong in these files or sample data.

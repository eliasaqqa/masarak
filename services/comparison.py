"""Normalize scraper-compatible records before exposing them to any client."""
import json
from decimal import Decimal, InvalidOperation
from pathlib import Path

SUPPORTED = {'hungerstation': 'HungerStation', 'ninja': 'Ninja'}
DATA_DIR = Path(__file__).resolve().parent.parent / 'data'

class DataUnavailable(Exception):
    """A data source could not be read safely."""


def money(value):
    if isinstance(value, bool) or not isinstance(value, (str, int, float, Decimal)):
        return None
    try:
        amount = Decimal(str(value))
        if not amount.is_finite() or amount < 0 or amount > Decimal('1000000'):
            return None
        return amount.quantize(Decimal('0.01'))
    except (InvalidOperation, ValueError):
        return None


def normalize_providers(providers):
    unique = {}
    for raw in providers if isinstance(providers, list) else []:
        if not isinstance(raw, dict):
            continue
        name = SUPPORTED.get(str(raw.get('name', '')).strip().lower())
        if not name:
            continue
        amount = money(raw.get('price'))
        available = raw.get('available', True) is True and amount is not None
        provider = {'name': name, 'price': float(amount) if amount is not None else None,
                    'available': available, 'delivery': 'Time not available', 'is_best': False}
        minimum = raw.get('delivery_min', raw.get('delivery_minutes'))
        maximum = raw.get('delivery_max')
        if isinstance(minimum, (int, float)) and not isinstance(minimum, bool) and 0 < minimum < 1440:
            provider['delivery'] = f'{int(minimum)}–{int(maximum)} min' if isinstance(maximum, (int, float)) and minimum <= maximum < 1440 else f'{int(minimum)} min'
        existing = unique.get(name)
        if existing is None or (available and (not existing['available'] or amount < Decimal(str(existing['price'])))):
            unique[name] = provider
    result = list(unique.values())
    best = find_best_price(result)
    for provider in result:
        provider['is_best'] = bool(best and provider['available'] and provider['price'] == best['price'])
    return result


def find_best_price(providers):
    valid = [p for p in providers if isinstance(p, dict) and p.get('available', True) is True and money(p.get('price')) is not None]
    return min(valid, key=lambda p: money(p['price'])) if valid else None


def load_items(path):
    try:
        records = json.loads(Path(path).read_text(encoding='utf-8'))
        if not isinstance(records, list):
            raise ValueError('Expected a list')
    except (OSError, ValueError) as error:
        raise DataUnavailable('We couldn’t load comparison data right now. Please try again.') from error
    result = []
    seen = set()
    for raw in records:
        if not isinstance(raw, dict):
            continue
        title = raw.get('name', raw.get('restaurant'))
        item_id = str(raw.get('id', '')).strip()
        if not item_id or item_id in seen or not isinstance(title, str) or not title.strip():
            continue
        seen.add(item_id)
        result.append({**raw, 'id': item_id, 'title': title.strip(), 'providers': normalize_providers(raw.get('providers'))})
    return result

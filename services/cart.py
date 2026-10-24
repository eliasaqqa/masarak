"""A small session cart storing references, never client prices."""
from decimal import Decimal

class CartError(ValueError):
    pass


def quantity(value):
    if type(value) is not int or not 1 <= value <= 20:
        raise CartError('Choose a quantity between 1 and 20.')
    return value


def resolve(catalogs, kind, item_id, provider):
    if kind not in ('food', 'grocery'):
        raise CartError('Choose Food or Market.')
    item = next((i for i in catalogs[kind] if i['id'] == item_id), None)
    offer = next((p for p in item['providers'] if p['name'] == provider and p['available']), None) if item else None
    if not offer:
        raise CartError('This item or provider is unavailable. Please choose another offer.')
    return item, offer


def update_cart(entries, payload, catalogs):
    entries = [dict(e) for e in entries]
    action = payload.get('action', 'add')
    if action in ('remove', 'update'):
        existing = next((e for e in entries if e['key'] == payload.get('key')), None)
        if not existing:
            raise CartError('This item is no longer in your cart.')
        if action == 'remove':
            entries.remove(existing)
        else:
            existing['quantity'] = quantity(payload.get('quantity'))
        return entries
    if action != 'add':
        raise CartError('Unknown cart action.')
    kind, item_id, provider = (payload.get(k) for k in ('kind', 'item_id', 'provider'))
    resolve(catalogs, kind, item_id, provider)
    count = quantity(payload.get('quantity', 1))
    key = f'{kind}:{item_id}:{provider}'
    existing = next((e for e in entries if e['key'] == key), None)
    if existing:
        existing['quantity'] = quantity(existing['quantity'] + count)
    else:
        if len(entries) >= 12:
            raise CartError('The demo cart supports up to 12 different offers.')
        entries.append(dict(key=key, kind=kind, item_id=item_id, provider=provider, quantity=count))
    return entries


def summarize(entries, catalogs):
    items, unavailable, total = [], [], Decimal('0')
    for entry in entries:
        try:
            item, offer = resolve(catalogs, entry['kind'], entry['item_id'], entry['provider'])
            count = quantity(entry['quantity'])
        except (CartError, KeyError):
            unavailable.append(entry.get('key', 'Unknown item'))
            continue
        amount = Decimal(str(offer['price'])) * count
        total += amount
        items.append({**entry, 'title': item['title'], 'image': item.get('image'),
                      'unit_price': offer['price'], 'line_total': float(amount)})
    return dict(items=items, total=float(total), count=sum(i['quantity'] for i in items),
                unavailable=unavailable, source='sample', currency='SAR')

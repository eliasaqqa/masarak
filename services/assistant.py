"""Deterministic demo assistant. Replace this boundary with a model later."""
from .comparison import find_best_price


def recommend(message, catalogs):
    query = message.lower()
    if any(word in query for word in ('ride', 'hotel', 'flight', 'world cup')):
        return {'reply': 'Rides, hotels, flights and World Cup bookings are coming soon. I can help prepare a Food or Market demo cart today.', 'recommendations': []}
    kind = 'grocery' if any(word in query for word in ('grocery', 'market', 'milk', 'rice', 'produce', 'dairy', 'pantry', 'avocado', 'yogurt', 'tomato', 'oil')) else 'food'
    items = catalogs[kind]
    matches = [i for i in items if i['title'].lower() in query or i['id'].lower() in query]
    if not matches:
        matches = items
    recommendations = []
    for item in matches[:3]:
        best = find_best_price(item['providers'])
        if best:
            recommendations.append({'kind':kind, 'item_id':item['id'], 'title':item['title'],
                                    'provider':best['name'], 'price':best['price'], 'delivery':best['delivery']})
    return {'reply': 'Here are the lowest sample prices I found. Choose an item below to prepare your demo cart. These are illustrative prices, not live offers.',
            'recommendations': recommendations}

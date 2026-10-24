import json
import tempfile
import unittest
from pathlib import Path
from services.comparison import normalize_providers, find_best_price, load_items, DataUnavailable
from services.food_comparison import get_food_data
from services.grocery_comparison import get_grocery_data

class ComparisonTests(unittest.TestCase):
    def test_normalizes_numeric_strings_and_selects_lowest(self):
        offers = normalize_providers([{'name':'HungerStation','price':'48.10'}, {'name':'Ninja','price':'46'}])
        self.assertEqual(find_best_price(offers)['name'], 'Ninja')
        self.assertEqual(offers[0]['price'],48.1)
        self.assertTrue(offers[1]['is_best'])

    def test_invalid_prices_never_win(self):
        for value in [None, '', 'x', 'NaN', float('inf'), '-1', True, {}, '1e999']:
            with self.subTest(value=value):
                offers = normalize_providers([{'name':'Ninja','price':value}])
                self.assertIsNone(find_best_price(offers))
                self.assertFalse(offers[0]['available'])

    def test_ties_and_unavailable(self):
        offers = normalize_providers([{'name':'Ninja','price':12}, {'name':'HungerStation','price':12}])
        self.assertTrue(all(p['is_best'] for p in offers))
        offers = normalize_providers([{'name':'Ninja','price':1,'available':False}, {'name':'HungerStation','price':12}])
        self.assertEqual(find_best_price(offers)['name'],'HungerStation')

    def test_deduplicates_and_restricts_providers(self):
        offers=normalize_providers([None, 'bad', {'name':'Jahez','price':1}, {'name':'ninja','price':20}, {'name':'Ninja','price':10}, {'name':'HungerStation','price':30}])
        self.assertEqual(len(offers),2)
        self.assertEqual(find_best_price(offers)['price'],10)
        self.assertEqual({p['name'] for p in offers}, {'Ninja','HungerStation'})
        self.assertEqual(normalize_providers(None),[])

    def test_data_failure_and_malformed_records(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'sample.json'
            with self.assertRaises(DataUnavailable): load_items(path)
            path.write_text('{broken')
            with self.assertRaises(DataUnavailable): load_items(path)
            path.write_text(json.dumps([None, {}, {'id':'a','name':'Milk','providers':None}]))
            self.assertEqual(len(load_items(path)),1)

    def test_sample_catalogs_have_supported_providers_and_categories(self):
        food=get_food_data(); grocery=get_grocery_data()
        self.assertGreaterEqual(len(food),3)
        self.assertEqual({i['category'] for i in grocery},{'Dairy','Produce','Pantry'})
        for item in food+grocery:
            self.assertEqual({p['name'] for p in item['providers']},{'HungerStation','Ninja'})
            self.assertIsNotNone(find_best_price(item['providers']))

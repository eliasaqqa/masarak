import unittest
from unittest.mock import patch
from app import create_app
from services.comparison import DataUnavailable

class AppTests(unittest.TestCase):
    def setUp(self):
        self.app=create_app({'TESTING':True,'SECRET_KEY':'test-only'})
        self.client=self.app.test_client()
        self.client.get('/api/cart')
        with self.client.session_transaction() as s: self.csrf=s['csrf_token']

    def post(self,url,data):
        return self.client.post(url,json=data,headers={'X-CSRF-Token':self.csrf})

    def test_all_pages(self):
        for url in ['/', '/food','/grocery','/offers','/future','/wallet','/profile','/assistant','/cart','/checkout','/coming-soon/ride','/coming-soon/hotels']:
            with self.subTest(url=url):
                r=self.client.get(url)
                self.assertEqual(r.status_code,200)
                self.assertIn(b'Masarak',r.data)
        for url in ['/no-such-page','/coming-soon/invalid']:
            self.assertEqual(self.client.get(url).status_code,404)

    def test_header_declares_favicon_without_missing_asset(self):
        response=self.client.get('/')
        self.assertIn(b'rel="icon"',response.data)

    def test_comparison_api(self):
        for kind in ['food','grocery']:
            r=self.client.get('/api/'+kind)
            self.assertEqual(r.status_code,200)
            self.assertEqual(r.json['source'],'sample')
            for item in r.json['items']:
                self.assertEqual({p['name'] for p in item['providers']},{'Ninja','HungerStation'})

    def test_cart_authoritative_price_update_remove_and_demo_checkout(self):
        r=self.post('/api/cart',{'kind':'food','item_id':'albaik','provider':'Ninja','quantity':2,'price':0})
        self.assertEqual(r.status_code,200)
        self.assertEqual(r.json['total'],92)
        key=r.json['items'][0]['key']
        r=self.post('/api/cart',{'action':'update','key':key,'quantity':3})
        self.assertEqual(r.json['total'],138)
        r=self.post('/api/checkout',{})
        self.assertEqual(r.status_code,200)
        self.assertEqual(r.json['mode'],'demo')
        self.assertFalse(r.json['charged'])
        self.assertFalse(r.json['order_submitted'])
        r=self.post('/api/cart',{'action':'remove','key':key})
        self.assertEqual(r.json['total'],0)
        self.assertEqual(self.post('/api/checkout',{}).status_code,400)

    def test_cart_validation_and_csrf(self):
        self.assertEqual(self.client.post('/api/cart',json={}).status_code,403)
        for data in [None, [], {'kind':'ride'}, {'kind':'food','item_id':'missing','provider':'Ninja','quantity':1}, {'kind':'food','item_id':'albaik','provider':'Other','quantity':1}]:
            self.assertEqual(self.post('/api/cart',data).status_code,400)
        for q in [0,-1,100,True,1.5,'bad']:
            self.assertEqual(self.post('/api/cart',{'kind':'food','item_id':'albaik','provider':'Ninja','quantity':q}).status_code,400)

    def test_assistant_uses_catalog_and_prepares_cart_actions(self):
        r=self.post('/api/assistant',{'message':'I want Al Baik'})
        self.assertEqual(r.status_code,200)
        self.assertTrue(r.json['recommendations'])
        offer=r.json['recommendations'][0]
        self.assertEqual(offer['item_id'],'albaik')
        self.assertIn(offer['provider'],['HungerStation','Ninja'])
        self.assertIn('sample',r.json['reply'].lower())
        self.assertEqual(self.post('/api/assistant',{'message':'x'*1001}).status_code,400)

    def test_missing_data_has_safe_error(self):
        with patch('app.get_food_data',side_effect=DataUnavailable('source failed')):
            r=self.client.get('/api/food')
            self.assertEqual(r.status_code,503)
            self.assertIn('error',r.json)
            r=self.client.get('/food')
            self.assertEqual(r.status_code,503)
            self.assertIn(b'Please try again',r.data)

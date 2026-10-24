"""Masarak: Flask prototype with replaceable comparison and ordering services."""
import hmac
import os
import secrets
from pathlib import Path
from flask import Flask, jsonify, render_template, request, session
from services.comparison import DataUnavailable
from services.food_comparison import get_food_data
from services.grocery_comparison import get_grocery_data
from services.cart import CartError, update_cart, summarize
from services.assistant import recommend
from services.payments import DemoPaymentProvider

FEATURES = {
    'ride': {'title': 'Ride Comparison', 'icon':'car', 'description': "We're working on bringing you a smarter way to compare ride prices and transportation options across platforms."},
    'hotels': {'title': 'Hotel Comparison', 'icon':'hotel', 'description': "We're working on bringing you an easier way to compare hotel prices and find the best stay for your trip."},
}


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.update(SECRET_KEY=os.environ.get('MASARAK_SECRET_KEY') or secrets.token_hex(32),
                      SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE='Lax',
                      MAX_CONTENT_LENGTH=16384)
    if test_config:
        app.config.update(test_config)

    @app.before_request
    def protect_mutations():
        session.setdefault('csrf_token', secrets.token_hex(24))
        if request.method in ('POST', 'PUT', 'PATCH', 'DELETE'):
            token = request.headers.get('X-CSRF-Token', '')
            if not token.isascii() or not hmac.compare_digest(token, session['csrf_token']):
                return jsonify(error='Your session changed. Refresh the page and try again.'), 403

    @app.after_request
    def headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['Referrer-Policy'] = 'same-origin'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['Content-Security-Policy'] = "default-src 'self'; img-src 'self' data:; style-src 'self'; script-src 'self'; base-uri 'self'; form-action 'self'; frame-ancestors 'self'"
        if request.path.startswith('/api/'):
            response.headers['Cache-Control'] = 'no-store'
        return response

    @app.template_filter('sar')
    def sar(value):
        return f'{value:,.2f}' if value is not None else '—'

    @app.context_processor
    def globals_for_templates():
        logo = next((f'images/logo/masarak.{ext}' for ext in ('png', 'jpg')
                     if (Path(app.static_folder) / f'images/logo/masarak.{ext}').is_file()), None)
        return {'cart_count': sum(e.get('quantity', 0) for e in session.get('cart', [])),
                'logo_available': bool(logo), 'logo_filename': logo}

    def catalogs():
        return {'food':get_food_data(), 'grocery':get_grocery_data()}

    def payload():
        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            raise CartError('Please send a valid request.')
        return data

    def render_page(template, title, active='home', **context):
        return render_template(template, title=title, active=active, **context)

    @app.get('/')
    def home():
        return render_page('home.html', 'Your everyday, made easier')

    @app.get('/food')
    def food():
        return render_page('comparison.html','Food Delivery',kind='food',items=get_food_data(),subtitle='Compare prices. Find your favourite.',tip='Save more by comparing prices before ordering!')

    @app.get('/grocery')
    def grocery():
        return render_page('comparison.html','Grocery Delivery',kind='grocery',items=get_grocery_data(),subtitle='A smarter way to fill your basket.',tip='Get the best deals on groceries by comparing prices!')

    @app.get('/offers')
    def offers():
        return render_page('offers.html','A little more for less',active='offers',catalogs=catalogs())

    @app.get('/future')
    def future():
        return render_page('future.html','Future Features',active='future')

    @app.get('/coming-soon/<feature>')
    def coming_soon(feature):
        from flask import abort
        if feature not in FEATURES:
            abort(404)
        return render_page('coming-soon.html',FEATURES[feature]['title'],active='future',feature=FEATURES[feature])

    @app.get('/wallet')
    def wallet():
        return render_page('wallet.html','Masarak Wallet',active='wallet')

    @app.get('/profile')
    def profile():
        return render_page('profile.html','Profile')

    @app.get('/assistant')
    def assistant():
        return render_page('assistant.html','AI Assistant')

    @app.get('/cart')
    def cart():
        return render_page('cart.html','Your cart',cart=summarize(session.get('cart',[]),catalogs()))

    @app.get('/checkout')
    def checkout():
        return render_page('checkout.html','Checkout',cart=summarize(session.get('cart',[]),catalogs()))

    @app.get('/api/food')
    def food_api():
        return jsonify(source='sample',currency='SAR',items=get_food_data())

    @app.get('/api/grocery')
    def grocery_api():
        return jsonify(source='sample',currency='SAR',items=get_grocery_data())

    @app.route('/api/cart', methods=['GET','POST'])
    def cart_api():
        data=catalogs()
        if request.method == 'POST':
            session['cart'] = update_cart(session.get('cart',[]),payload(),data)
        return jsonify(summarize(session.get('cart',[]),data))

    @app.post('/api/assistant')
    def assistant_api():
        message=payload().get('message')
        if not isinstance(message,str) or not message.strip() or len(message)>1000:
            raise CartError('Please enter a message of 1–1,000 characters.')
        return jsonify(recommend(message.strip(),catalogs()))

    @app.post('/api/checkout')
    def checkout_api():
        cart=summarize(session.get('cart',[]),catalogs())
        if not cart['items'] or cart['unavailable']:
            raise CartError('Please review your cart before checkout.')
        return jsonify(DemoPaymentProvider().checkout(cart))

    @app.errorhandler(CartError)
    def cart_error(error):
        return jsonify(error=str(error)),400

    @app.errorhandler(DataUnavailable)
    def data_error(error):
        message='We couldn’t load comparison data right now. Please try again.'
        if request.path.startswith('/api/'):
            return jsonify(error=message),503
        return render_page('error.html','A little pause',code=503,message=message),503

    @app.errorhandler(404)
    def not_found(error):
        if request.path.startswith('/api/'):
            return jsonify(error='This endpoint was not found.'),404
        return render_page('error.html','A turn we haven’t mapped yet',code=404,message='This page could not be found. Let’s get you back on your path.'),404

    @app.errorhandler(500)
    def server_error(error):
        if request.path.startswith('/api/'):
            return jsonify(error='Something went wrong. Please try again.'),500
        return render_page('error.html','Something went wrong',code=500,message='Please try again in a moment.'),500

    return app


if __name__ == '__main__':
    create_app().run(host='0.0.0.0',port=int(os.environ.get('PORT',5000)),debug=False)

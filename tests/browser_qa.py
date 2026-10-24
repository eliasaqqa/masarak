from playwright.sync_api import sync_playwright, expect
import json
import os
from pathlib import Path
base=os.environ.get('MASARAK_BASE_URL','http://127.0.0.1:5000').rstrip('/')
art=Path(__file__).resolve().parent.parent/'artifacts'
art.mkdir(exist_ok=True)
with sync_playwright() as p:
    browser=p.chromium.launch(executable_path=os.environ.get('MASARAK_BROWSER','/usr/bin/chromium'),headless=True,args=['--no-sandbox'])
    page=browser.new_page(viewport={'width':390,'height':844},device_scale_factor=1)
    errors=[]
    page.on('pageerror',lambda e:errors.append(str(e)))
    page.on('console',lambda m:errors.append(m.text) if m.type=='error' else None)
    routes=['/','/food','/grocery','/offers','/future','/wallet','/profile','/assistant','/cart','/checkout','/coming-soon/ride','/coming-soon/hotels']
    for width in [320,390,768,1440]:
        page.set_viewport_size({'width':width,'height':900 if width>500 else 844})
        for route in routes:
            response=page.goto(base+route)
            assert response.status==200,(route,response.status)
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'),(width,route,'overflow')
            broken=page.locator('img').evaluate_all('async images => { images.forEach(i => i.loading = "eager"); return (await Promise.all(images.map(async i => { try { await i.decode(); return null; } catch { return i.src; } }))).filter(Boolean); }')
            assert not broken,(route,broken)
            if width in [390,1440] and route in ['/','/food','/grocery','/wallet','/assistant']:
                page.screenshot(path=str(art/f'{route.strip("/") or "home"}-{width}.png'),full_page=True)
    page.set_viewport_size({'width':390,'height':844})
    page.goto(base+'/')
    page.select_option('#city','Jeddah')
    page.locator('#home-search').fill('market')
    page.locator('#home-search').press('ArrowDown')
    page.keyboard.press('Enter')
    page.wait_for_url('**/grocery')
    assert page.locator('#city').input_value()=='Jeddah'
    page.get_by_role('button',name='Dairy',exact=True).click()
    assert page.locator('.product-card:visible').count()==2
    page.get_by_role('button',name='Produce',exact=True).click()
    assert page.locator('.product-card:visible').count()==2
    page.get_by_role('button',name='Pantry',exact=True).click()
    assert page.locator('.product-card:visible').count()==2
    page.get_by_role('button',name='All Items',exact=True).click()
    assert page.locator('.product-card:visible').count()==6
    page.goto(base+'/food')
    page.get_by_role('button',name='Add Al Baik from Ninja to cart').click()
    expect(page.locator('#toast')).to_contain_text('Added')
    page.goto(base+'/cart')
    assert '46.00' in page.locator('.cart-summary').inner_text()
    page.get_by_role('button',name='Increase quantity').click()
    page.wait_for_load_state('networkidle')
    assert '92.00' in page.locator('.cart-summary').inner_text()
    page.get_by_role('link',name='Continue to demo checkout').click()
    page.get_by_role('button',name='Complete demo checkout').click()
    page.locator('#checkout-result').wait_for(state='visible')
    assert 'No payment was taken' in page.locator('#checkout-result').inner_text()
    page.goto(base+'/assistant')
    page.locator('#chat-input').fill('I want Al Baik')
    page.get_by_role('button',name='Send message').click()
    page.locator('.chat-recommendation').wait_for()
    assert page.locator('.chat-recommendation').count()==1
    page.get_by_role('button',name='+ Add to demo cart').click()
    expect(page.locator('#toast')).to_contain_text('Added')
    page.locator('#chat-input').fill('<img src=x onerror=alert(1)>')
    page.get_by_role('button',name='Send message').click()
    expect(page.locator('#chat-messages')).to_have_attribute('aria-busy','false')
    assert '<img src=x' in page.locator('.chat-bubble.user').last.inner_text()
    assert page.locator('#chat-messages img').count()==0
    page.goto(base+'/wallet')
    page.get_by_role('button',name='Top Up').click()
    assert page.locator('#demo-dialog').is_visible()
    page.get_by_role('button',name='Got it').click()
    for label,route in [('Home','/'),('Offers','/offers'),('Future','/future'),('Wallet','/wallet')]:
        page.locator('.bottom-nav').get_by_role('link',name=label,exact=True).click()
        page.wait_for_url(base+route)
    page.goto(base+'/')
    page.get_by_role('link',name='Ride',exact=False).filter(has=page.locator('.quick-label')).first.click()
    page.wait_for_url('**/coming-soon/ride')
    assert page.get_by_role('heading',name='Ride Comparison').is_visible()
    for label, target in [('Food','/food'),('Market','/grocery'),('Hotels','/coming-soon/hotels')]:
        page.goto(base+'/')
        page.locator('.quick-card').filter(has_text=label).click()
        page.wait_for_url(base+target)
    page.goto(base+'/')
    page.get_by_role('link',name='Profile',exact=True).click()
    page.wait_for_url('**/profile')
    page.get_by_role('link',name='Open AI assistant').click()
    page.wait_for_url('**/assistant')
    page.goto(base+'/future')
    page.get_by_role('link',name='Ride',exact=False).click()
    page.wait_for_url('**/coming-soon/ride')
    page.goto(base+'/future')
    page.get_by_role('link',name='Hotels').click()
    page.wait_for_url('**/coming-soon/hotels')
    assert page.get_by_role('heading',name='Hotel Comparison').is_visible()
    assert not errors,errors
    print(json.dumps({'pages_checked':len(routes)*4,'widths':[320,390,768,1440],'functional_flows':'search, city, filters, cart, quantities, demo checkout, assistant, XSS rendering, wallet dialog, navigation','browser_errors':errors,'screenshots':str(art)},indent=2))
    browser.close()

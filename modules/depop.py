from bs4 import BeautifulSoup
import re
from typing import Optional
from datetime import datetime

from modules.scraper import Scraper

class Depop:
    def __init__(self, headless=False, profile:Optional[str]='') -> None:
        print('Depop:')
        
        # Setup Chrome driver
        self.se = Scraper()
        self.driver = self.se.setup_driver(headless=headless, profile=profile)       
        if not self.driver:
            print('Unable to open chrome driver')
            exit()
            
        # Setup cookies
        self.cookie_file = 'cookies/depop_cookies.pkl'
        
    
    def login(self, depop_username, depop_password):
    
        is_logged_in_selector='button[data-testid="userNavItem-wrapper"]'
    
        # Login
        self.se.get_page('https://www.depop.com/login/')
        
        is_success = self.se.login_with_cookies(is_logged_in_selector, self.cookie_file)
        if is_success:
            return True
        
        # accept all cookies
        self.se.find_element('button[data-testid="cookieBanner__acceptAllButton"]', click=True, print_error=False)

        return self.se.fill_login_form(
            username=depop_username,
            password=depop_password,
            username_selector='#username',
            password_selector='#password',
            submit_selector= 'button[data-testid="login__cta"]',
            is_logged_in_selector=is_logged_in_selector,
            cookie_file=self.cookie_file
        )
        
    def get_sold_items(self):
        sold_items = []
        self.se.get_page('https://www.depop.com/sellinghub/sold-items/')
        self.se.wait_random_time(2, 3)
        
        div = self.se.find_element('div[role="list"]')
        
        # Iterate through orders
        self.se.wait_random_time(3, 4)
        for i in range(15):
            orders = self.se.find_elements('div[role="listitem"]', parent=div)
           
            # Scroll once
            if i == 0:
                self.se.scroll_into_view(element=orders[-1])
                self.se.wait_random_time(4, 5)
           
            if i < len(orders):
                # print(i, len(orders))
                items = self.get_order_items(orders[i])    
                sold_items.extend(items)
            else:
                break    
        return sold_items    
   
    def get_order_items(self, item):
        sold_items = []
        try:
            # Shipping State
            shipping_status = self.se.find_element('div[data-testid="receipt__shipping_status"]')
            assert shipping_status is not None
            if shipping_status.text != 'Awaiting shipping':
                return []
            
            receipts_div = self.se.find_element('div[class^="ReceiptsList"]', timeout=1, parent=item, click=True)
            assert receipts_div is not None
            self.se.wait_random_time(4, 5)
            
            # Side Drawer
            soup = BeautifulSoup(self.driver.page_source, 'html.parser') # type: ignore
            aside = soup.select_one('aside[data-testid="simpleDrawer"]')
            assert aside is not None
            
            # Order Date
            date_p = aside.select_one('section div p[type="caption1"]')
            assert date_p is not None
            date = date_p.text.replace('Sold on', '').strip()
            date = datetime.strptime(date, '%m/%d/%Y').strftime('%Y-%m-%d')
            
            # Payment State
            payment_state = aside.select_one('div[class*="PaymentState"] p')
            state = payment_state.text if payment_state else ''
            if state == 'Payment refunded on':
                return []
            
            # Order Earning
            total_earning = float(aside.select('table tr')[-1].text.split('$')[1])
            
            
            # Items
            products = aside.select('a[href^="/products/"]')
            ln = len(products)
            
            # Platform
            platform = 'Depop Bundle {}'.format(ln) if ln > 1 else 'Depop'
            
            for product in products:
                name = product.text.split('\n')[0].replace('Name:', '').strip()
                item_codes = re.findall(r'\d{6}', name)
                assert len(item_codes) > 0
                
                sold_items.append({
                    'item_code': item_codes[0],
                    'name': name,
                    'date': date,
                    'earning': round(total_earning/ln, 2),
                    'platform': platform
                })
            
            return sold_items
        except (AssertionError, IndexError):
            # traceback.print_exc()
            # print('Unable to parse {} item'.format(item.text))
            return []
        
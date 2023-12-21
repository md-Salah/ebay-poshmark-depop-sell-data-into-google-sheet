from bs4 import BeautifulSoup
import re
from typing import Optional
from datetime import datetime

from modules.scraper import Scraper

class Poshmark:
    def __init__(self, headless:bool=False, proxy:Optional[str]=None, profile:Optional[str]='') -> None:
        print('Poshmark:')
        
        # Setup Chrome driver
        self.se = Scraper()
        self.driver = self.se.setup_driver(headless=headless, proxy=proxy, profile=profile)       
        if not self.driver:
            print('Unable to open chrome driver')
            exit()
            
        # Setup cookies
        self.cookie_file = 'cookies/poshmark_cookies.pkl'
        
    
    def login(self, poshmark_username, poshmark_password):    
        is_logged_in_selector = 'a[href="/sell"]'
    
        # Login
        self.se.get_page('https://poshmark.com/login')
        
        is_success = self.se.login_with_cookies(is_logged_in_selector, self.cookie_file)
        if is_success:
            return True

        is_success = self.se.fill_login_form(
            username=poshmark_username,
            password=poshmark_password,
            username_selector='#login_form_username_email',
            password_selector='#login_form_password',
            submit_selector= 'button[data-pa-name="login"]',
            is_logged_in_selector=is_logged_in_selector,
            cookie_file=self.cookie_file,
        )
        if is_success:
            return True
        
        input('Login poshmark manually and press ENTER: ')
        is_success = self.se.is_logged_in(is_logged_in_selector, timeout=5)
        if is_success:
            print('Login success')
            self.se.save_cookies(self.cookie_file)
            return True
        
        return False    
        
        
    def get_sold_items(self):
        sold_items = []
        self.se.get_page('https://poshmark.com/order/sales')
        self.se.wait_random_time(2, 3)
        
        # Iterate through orders
        for i in range(15):
            orders = self.se.find_elements('a[data-et-name="order"]')
            if i < len(orders):
                items = self.get_order_items(orders[i])   
                sold_items.extend(items)
            else:
                break    
        return sold_items    
            
    def get_order_items(self, item):
        sold_items = []
        new_tab = False
        try:
            # Order Status
            order_status = self.se.find_element('div[class^="order-item__content__order-status"]', parent=item)
            assert order_status is not None
            assert order_status.text.strip() == 'Sold'
            
            new_tab = self.se.open_new_tab(item.get_attribute('href'))
            self.se.wait_random_time(4, 5)
            
            soup = BeautifulSoup(self.driver.page_source, 'html.parser') # type: ignore
            
            # Order Date
            date_p = soup.select_one('.listing-info__detail')
            date = date_p.text.strip() if date_p else ''
            date = datetime.strptime(date, '%b-%d-%Y').strftime('%Y-%m-%d')  # Dec-21-2023

            
            # status_p = soup.select_one('span[class^="order-status__display"]')
            # assert status_p is not None
            # assert status_p.text.strip() == 'Sold'
            
            # Order Earning
            earning_div = self.se.find_element_by_visible_text('div', 'Your Earnings:')
            assert earning_div is not None
            earning_span = self.se.find_element('span', parent=earning_div)
            total_earning = float(earning_span.text.replace('$', '').strip()) if earning_span else 0
            
            # Items
            products = soup.select('div[class^="order-items__item-title"]')
            ln = len(products)
            
            platform = 'Poshmark'
            
            for product in products:
                name = product.text.strip()
                item_codes = re.findall(r'\d{6}', name)
                assert len(item_codes) > 0
                
                sold_items.append({
                    'item_code': item_codes[0],
                    'name': name,
                    'date': date,
                    'earning': round(total_earning/ln, 2),
                    'platform': platform
                })
            
            
        except (AssertionError, IndexError, ValueError):
            # traceback.print_exc()
            # print('Unable to parse {} item'.format(item.text))
            pass

        if new_tab:
            self.se.switch_to_tab(0, close_current_tab=True)
        return sold_items
    
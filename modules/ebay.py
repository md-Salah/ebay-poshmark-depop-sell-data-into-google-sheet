from bs4 import BeautifulSoup
import re

from modules.scraper import Scraper

class Ebay:
    def __init__(self, headless=False, proxy=None) -> None:
        print('Ebay:')
        
        # Setup Chrome driver
        self.se = Scraper()
        self.driver = self.se.setup_driver(headless=headless, proxy=proxy)       
        if not self.driver:
            print('Unable to open chrome driver')
            exit()
            
        # Setup cookies
        self.se.cookie_file = 'cookies/ebay_cookies.pkl'
        
    
    def login(self, ebay_username, ebay_password):
        is_logged_in_selector = 'button[aria-controls="gh-eb-u-o"]'
    
        # Login Page
        self.se.get_page('https://www.ebay.com/')
        
        is_success = self.se.login_with_cookies(is_logged_in_selector)
        if is_success:
            return True

        self.se.find_element('a[href^="https://signin.ebay.com"]', click=True)
        if 'https://signin.ebay.com/ws/' in self.se.driver.current_url:
            self.se.element_send_keys(ebay_username, '#userid')
            self.se.find_element('#signin-continue-btn', click=True)
            self.se.wait_random_time(2, 3)
            self.se.element_send_keys(ebay_password, '#pass')
            self.se.find_element('#sgnBt', click=True)
            
        input('Please login to Ebay and press ENTER:')
        if self.se.is_logged_in(is_logged_in_selector, timeout=5):
            print('Login success')
            self.se.save_cookies()
            return True
        
        return False    
        
        
    def get_sold_items(self):
        sold_items = []
        # self.se.get_page('https://www.ebay.com/sh/ord/?filter=status:ALL_ORDERS')
        self.se.get_page('https://www.ebay.com/sh/ord/?filter=status:AWAITING_SHIPMENT')
        self.se.wait_random_time(2, 3)
        
        # Iterate through orders
        for i in range(15):
            orders = self.se.find_elements('tr[class^="order-info"]')
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
            order_details = self.se.find_element('.order-details a', parent=item)
            url = order_details.get_attribute('href') if order_details else None
            if url is None:
                return []
            
            new_tab = self.se.open_new_tab(url)
            self.se.wait_random_time(4, 5)
            
            soup = BeautifulSoup(self.driver.page_source, 'html.parser') # type: ignore
            
            # Order Date
            date = ''
            date_divs = soup.select('.order-info .info-item')
            for div in date_divs:
                if 'Date sold' in div.text:
                    date = div.text.replace('Date sold', '').strip()
                    break
            
            # Order Earning
            earning_div = soup.select_one('.earnings .total .amount .value')
            total_earning = float(earning_div.text.replace('$', '').strip()) if earning_div else 0
            
            products = soup.select('#itemInfo .lineItemCardInfo__text a')
            ln = len(products)
            
            platform = 'Ebay'
            
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
            
            
        except (AssertionError, IndexError):
            pass

        if new_tab:
            self.se.switch_to_tab(0, close_current_tab=True)
        return sold_items
    
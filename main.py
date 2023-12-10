import traceback
from dotenv import load_dotenv
import time
import os


from modules.scraper import Scraper
from modules import files as fs

load_dotenv()


def main():
    start_time = time.time()
    
    d = Scraper()
    try:
        if d.setup_driver(headless=False, profile = os.getenv('chrome_profile')):
            d.get_page('https://www.google.com/')
            d.element_send_keys('Who is lionel messi?', selector='textarea[name="q"]')
            
            print('Chrome is ready')
        
        
            input('Exit? Press ENTER: ')
    except Exception:
        traceback.print_exc()
    finally:
        print('\nExecution time: {} min'.format(
            round((time.time() - start_time)/60, 2)))
        del d

        

if __name__ == '__main__':
    main()
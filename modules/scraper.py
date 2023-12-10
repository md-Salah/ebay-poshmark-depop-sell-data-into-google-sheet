import os
import pickle
import time
import random
import requests
from requests.exceptions import ConnectTimeout, ReadTimeout, SSLError
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, InvalidArgumentException
from selenium.webdriver.chrome.service import Service

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select
from selenium.webdriver.remote.webelement import WebElement
from typing import Optional, Union


import zipfile
import traceback	


class Scraper:
	cookie_file:Optional[str]='cookies/cookies.pkl'
	error_file:str='error.txt'

	def __init__(self):
		pass

	def __del__(self):
		try:
			self.driver.close()
			self.driver.quit()
		except AttributeError:
			pass
		except Exception:
			pass

		
	# Setup driver with best practice options
	def setup_driver(self, headless:bool=True, profile:Optional[str]=None, proxy: Optional[str]=None) -> Optional[webdriver.Chrome]:
		options = Options()
		service = Service()
  
		if headless:
			options.add_argument('--headless=new')
		if profile:
			options.add_argument(f'--user-data-dir={profile}')
		if proxy:
			plugin = self.proxy_extension(proxy)
			if plugin:
				options.add_extension(plugin)

		[options.add_argument(argument) for argument in [
			'--start-maximized',
			'--disable-blink-features=AutomationControlled',
			'--disable-dev-shm-usage',
			'--no-sandbox',
			'--disable-site-isolation-trials',
			'--autoplay-policy=no-user-gesture-required',
			'--hide-crash-restore-bubble'
		]]

		experimental_options = {
			'excludeSwitches': ['enable-automation', 'enable-logging'],
			'prefs': {
				'profile.default_content_setting_values.notifications': 2,
				
				# Disable Save password popup
				'credentials_enable_service': False,
				'profile.password_manager_enabled': False
			}
		}
		[options.add_experimental_option(key, value) for key, value in experimental_options.items()]
			

		try:
			self.driver =  webdriver.Chrome(options=options, service=service)
			return self.driver
		except Exception:
			print(f'Failed to setup browser. Check if another chrome is open with same profile. See "{self.error_file}" for more info.')
			with open(self.error_file, 'a') as file:
				traceback.print_exc(file=file)
			return None
            
	def wait_random_time(self, a:float=0.20, b:float=1.20) -> None:
		time.sleep(round(random.uniform(a, b), 2))

	def get_page(self, url: str, print_error:bool=True) -> Optional[BeautifulSoup]:
		try:
			self.driver.get(url)
			self.wait_random_time(1, 1.5)
   
			return BeautifulSoup(self.driver.page_source, 'html.parser')
		except InvalidArgumentException:
			if print_error:
				print('InvalidArgumentException, bad url: "{}"'.format(url))
		except Exception:
			traceback.print_exc()

		return None

	def get_page_by_requests(self, url: str, print_error:bool=True, add_cookies:bool=False) -> Optional[BeautifulSoup]:
		try:
			session = requests.Session()
			
			if add_cookies:
				[session.cookies.set(cookie['name'], cookie['value']) for cookie in self.driver.get_cookies()]
				
			response = session.get(url)
			if response.status_code == 200:
				return BeautifulSoup(response.text, 'html.parser')
		except (ReadTimeout, ConnectTimeout, SSLError) as err:
			if print_error:
				print('{}: url: "{}"'.format(err.__class__, url))
		except Exception:
			traceback.print_exc()

		return None
   
	def try_auto_login(self, is_logged_in_selector:str) -> bool:

		# Check if already logged in
		if self.is_logged_in(is_logged_in_selector, timeout=3):
			print('Auto logged in')
			return True
  
		# Load cookies if available
		if self.cookie_file and self.load_cookies(self.cookie_file, False) and self.is_logged_in(is_logged_in_selector, timeout=5):
			print('Logged In using cookies')
			return True

		return False

   
	def fill_login_form(self, username:str, password:str, username_selector:str, password_selector:str, submit_selector:str, is_logged_in_selector:str) -> bool:
	
		print('User {} is logging in...'.format(username))
 		# Fill username and password
		if not self.element_send_keys(username, username_selector):
			print('Login failed, error with Username.')
			return False
		if not self.element_send_keys(password, password_selector):
			print('Login failed, error with Password.')
			return False
		
		# Submit button
		self.wait_random_time()
		if self.find_element(submit_selector, click=True) is None:
			print('Login failed, error with Submit button.')
			return False

		# Chcek if logged in
		self.wait_random_time(2, 3)
		if self.is_logged_in(is_logged_in_selector, timeout=30):
			if self.cookie_file:
				self.save_cookies(self.cookie_file)
				print('Login success and Cookies are saved.')
			else:
				print('Login success.')
			return True
		else:
			print('Login failed.')
	
		return False


	def load_cookies(self, filename:str='cookies/cookies.pkl', print_error:bool=True) -> bool:
		if os.path.exists(filename):
			with open(filename, 'rb') as file:
				cookies = pickle.load(file)
				
				for cookie in cookies:
					self.driver.add_cookie(cookie)

			self.driver.refresh()
			self.wait_random_time(2, 3)
			return True
		else:
			if print_error:
				print('Cookies file not found, filename: "{}"'.format(filename))
			return False


	def save_cookies(self, filename:str='cookies/cookies.pkl') -> None:
		try:
			if not os.path.exists(filename.split('/')[0]):
				os.mkdir(filename.split('/')[0])

			with open(filename, 'wb') as file:
				pickle.dump(self.driver.get_cookies(), file)
		except Exception:
			traceback.print_exc()


	def is_logged_in(self, selector:str, timeout:float=15) -> bool:
		element = self.find_element(selector, timeout=timeout, print_error=False)
		
		return True if element else False


	def find_element(self, selector:str, timeout:float = 15, parent:Optional[WebElement]=None, print_error:bool=True, click:bool=False) -> Optional[WebElement]:
		element = None

		driver = parent or self.driver
		try:
			wait_until = EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
			element = WebDriverWait(driver, timeout).until(wait_until) # type: ignore
		except TimeoutException:
			if print_error:
				print('TimeoutException, selector: "{}", timeout: {} sec'.format(selector, timeout))
		except Exception:
			if print_error:
				traceback.print_exc()			

		# If click is True
		if click and element:
			element.click()

		return element
	

	def find_elements(self, selector: str, parent:Optional[WebElement]=None, print_error:bool=True) -> list[WebElement]:
		elements = []
		driver = parent or self.driver
		
		try:
			elements = driver.find_elements(By.CSS_SELECTOR, selector)
		except Exception:
			if print_error:
				traceback.print_exc()
		
		return elements

	def find_element_by_visible_text(self, tag:str, text:str, print_error:bool=True, click:bool=False) -> Optional[WebElement]:
		element = None
		try:
			element = self.driver.find_element(By.XPATH, "//{}[contains(text(),'{}')]".format(tag, text))
		except NoSuchElementException:
			if print_error:
				print('NoSuchElementException, text: {} + {}'.format(tag, text))
		except Exception:
			if print_error:
				traceback.print_exc()
 	
		if click and element:
			element.click()
   
		return element

 
	def element_send_keys(self, text:str, selector:str='', element:Optional[WebElement]=None, gap:Optional[float]=0.01, timeout:float=15) -> bool:
		
		if len(text) == 0:
			raise ValueError('Please provide a text to send keys')
		if element:
			pass
		elif selector:
			element = self.find_element(selector, timeout=timeout, print_error=True)
		else:
			print('Please provide a selector or WebElement to send keys "{}"'.format(text))

		if element:
			try:
				element.click()
				element.clear()

				if gap:
					for char in text:
						element.send_keys(char)
						time.sleep(gap)
				else:
					element.send_keys(text)
     
				return True			
			except Exception:
				traceback.print_exc()
		
		return False
  
	
	def select_dropdown(self, selector:str, value:str='', text:str='', timeout:float=15) -> bool:
		element= self.find_element(selector, timeout=timeout, print_error=True)
		if element:
			select = Select(element)
			if text:
				select.select_by_visible_text(text)
			elif value:
				select.select_by_value(value)
			else:
				raise ValueError('Please provide a value or text to select from dropdown')
			return True

		return False

	def add_emoji(self, selector:str, text:str, timeout:float=5) -> bool:
		JS_ADD_TEXT_TO_INPUT = """
		var elm = arguments[0], txt = arguments[1];
		elm.value += txt;
		elm.dispatchEvent(new Event('change'));
		"""
		element = self.find_element(selector, timeout=timeout, print_error=True)
		if element:
			self.driver.execute_script(JS_ADD_TEXT_TO_INPUT, element, text) 
			element.send_keys('.')
			element.send_keys(Keys.BACKSPACE)
			element.send_keys(Keys.TAB)
			return True
		return False

	def scroll_into_view(self, selector:str='', element=None, timeout:int=15) -> None:
		if element:
			pass
		elif selector:
			element = self.find_element(selector, timeout=timeout, print_error=True)
		else:
			print('Please provide a selector or WebElement to scroll into view')
   
   
		if element:
			self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'auto',block: 'center',inline: 'center'});", element)
	

	def upload_files(self, selector:str, files:Union[str, list[str]], timeout:float=15) -> bool:
		element = self.find_element(selector, timeout=timeout, print_error=True)
		if element:
			try:
				element.send_keys(files)
				return True
			except InvalidArgumentException:
				print('InvalidArgumentException, Check files path are correct. selector: "{}", files: "{}"'.format(selector, files))
			except Exception:
				traceback.print_exc()

		return False

	def element_wait_to_be_invisible(self, selector:str, timeout:float=15, print_error:bool=True) -> bool:
		try:
			wait_until = EC.invisibility_of_element_located((By.CSS_SELECTOR, selector))
			WebDriverWait(self.driver, timeout).until(wait_until)
			return True
		except TimeoutException:
			if print_error:
				print('TimeoutException, selector: "{}", timeout: {} sec'.format(selector, timeout))
		except Exception:
			if print_error:
				traceback.print_exc()
		return False

	def open_new_tab(self, url:str, tab_index:int=1) -> bool:
		try:
			self.driver.execute_script("window.open(arguments[0])", url)	#Causing javascript error: missing ) after argument list.
			self.driver.switch_to.window(self.driver.window_handles[tab_index])
			return True
		except Exception:
			traceback.print_exc()
			return False
  
	def switch_to_tab(self, tab_index:int, close_current_tab:bool=False) -> None:
		if close_current_tab:
			self.driver.close()
		self.driver.switch_to.window(self.driver.window_handles[tab_index])
  
  
	def proxy_extension(self, proxy):
		proxy= proxy.split(':')
		PROXY_HOST = proxy[0]
		PROXY_PORT = proxy[1]
		PROXY_USER = proxy[2]
		PROXY_PASS = proxy[3]

		manifest_json = """
		{
			"version": "1.0.0",
			"manifest_version": 2,
			"name": "Chrome Proxy",
			"permissions": [
				"proxy",
				"tabs",
				"unlimitedStorage",
				"storage",
				"<all_urls>",
				"webRequest",
				"webRequestBlocking"
			],
			"background": {
				"scripts": ["background.js"]
			},
			"minimum_chrome_version":"22.0.0"
		}
		"""

		background_js = """
		var config = {
				mode: "fixed_servers",
				rules: {
				singleProxy: {
					scheme: "http",
					host: "%s",
					port: parseInt(%s)
				},
				bypassList: ["localhost"]
				}
			};

		chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});

		function callbackFn(details) {
			return {
				authCredentials: {
					username: "%s",
					password: "%s"
				}
			};
		}

		chrome.webRequest.onAuthRequired.addListener(
					callbackFn,
					{urls: ["<all_urls>"]},
					['blocking']
		);
		""" % (PROXY_HOST, PROXY_PORT, PROXY_USER, PROXY_PASS)

		if os.path.exists('tmp'):
			os.mkdir('tmp')
		pluginfile = 'tmp/proxy_auth_plugin.zip'

		with zipfile.ZipFile(pluginfile, 'w') as zp:
			zp.writestr("manifest.json", manifest_json)
			zp.writestr("background.js", background_js)
		
		return pluginfile
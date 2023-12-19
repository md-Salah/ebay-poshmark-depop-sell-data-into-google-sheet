import os
from dotenv import load_dotenv

load_dotenv()
    
class Settings:
    depop_username = os.getenv('depop_username')
    depop_password = os.getenv('depop_password')
    poshmark_username = os.getenv('poshmark_username')
    poshmark_password = os.getenv('poshmark_password')
    ebay_username = os.getenv('ebay_username')
    ebay_password = os.getenv('ebay_password')
    
    def __init__(self) -> None:
        if self.depop_username is None or self.depop_password is None:
            raise Exception('Please set your depop username and password in the .env file')
        if self.poshmark_username is None or self.poshmark_password is None:
            raise Exception('Please set your poshmark username and password in the .env file')
        if self.ebay_username is None or self.ebay_password is None:
            raise Exception('Please set your ebay username and password in the .env file')

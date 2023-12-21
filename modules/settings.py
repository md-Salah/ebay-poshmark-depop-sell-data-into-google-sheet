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
    profile = os.path.join(os.getcwd(), './profile/Default')
    service_account = os.getenv('service_account')
    
    def __init__(self) -> None:
        if self.depop_username is None or self.depop_password is None:
            raise Exception('Please set your depop username and password in the .env file')
        if self.poshmark_username is None or self.poshmark_password is None:
            raise Exception('Please set your poshmark username and password in the .env file')
        if self.ebay_username is None or self.ebay_password is None:
            raise Exception('Please set your ebay username and password in the .env file')
        if self.profile is None:
            raise Exception('Please set your chrome profile in the .env file')
        if self.service_account is None:
            raise Exception('Please set your service account in the .env file')
        
        assert os.path.exists(self.service_account), 'Service account file does not exist'
        
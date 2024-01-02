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
    filename = os.getenv('filename')
    sheetname = os.getenv('sheetname')

    def __init__(self) -> None:
        try:
            assert self.depop_username is not None, 'Depop username is not set in .env file'
            assert self.depop_password is not None, 'Depop password is not set in .env file'

            assert self.poshmark_username is not None, 'Poshmark username is not set in .env file'
            assert self.poshmark_password is not None, 'Poshmark password is not set in .env file'

            assert self.ebay_username is not None, 'Ebay username is not set in .env file'
            assert self.ebay_password is not None, 'Ebay password is not set in .env file'

            assert self.service_account is not None, 'Service account is not set in .env file'

            assert self.filename is not None, 'Filename is not set'
            assert self.sheetname is not None, 'Sheetname is not set'

            assert os.path.exists(
                self.service_account), 'Service account file does not exist'
        except AssertionError as e:
            print(e)
            exit()

import traceback
import time
from collections import Counter

from modules.settings import Settings
from modules.depop import Depop
from modules.poshmark import Poshmark
from modules.ebay import Ebay
from modules.gsheet import GoogleSheet


def main():
    start_time = time.time()
    settings = Settings()

    try:
        sold_items = []

        # # Ebay
        # ebay = Ebay(profile=settings.profile)
        # if ebay.login(settings.ebay_username, settings.ebay_password):
        #     sold_items += ebay.get_sold_items()
        # del ebay
        # time.sleep(3)

        # # Poshmark
        # poshmark = Poshmark(profile=settings.profile)
        # if poshmark.login(settings.poshmark_username, settings.poshmark_password):
        #     sold_items += poshmark.get_sold_items()
        # del poshmark
        # time.sleep(3)

        # Depop
        depop = Depop()
        if depop.login(settings.depop_username, settings.depop_password):
            sold_items += depop.get_sold_items()
        del depop

        print('\nTotal sold items: {}'.format(len(sold_items)))
        [print('{}: {}'.format(key, value)) for key, value in Counter(
            [item.get('platform') for item in sold_items]).items()]

        # Google Sheet
        print('\nUpdating Google Sheet...')
        gsheet = GoogleSheet(
            service_account=settings.service_account)  # type: ignore
        gsheet.update_sold_items(
            filename=settings.filename, sheetname=settings.sheetname, sold_items=sold_items)  # type: ignore
        del gsheet

        print('')
        [print(item) for item in sold_items]

        # input('\nPress any key to exit...')
    except Exception:
        print('Unexpected error occurred. Please see "error.log" for more details.')
        with open('error.log', 'w') as f:
            f.write(traceback.format_exc())
    finally:
        print('\nExecution time: {} min'.format(
            round((time.time() - start_time)/60, 2)))


if __name__ == '__main__':
    main()

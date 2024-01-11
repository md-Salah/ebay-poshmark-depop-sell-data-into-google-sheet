import gspread
import pandas as pd
from gspread.exceptions import SpreadsheetNotFound
from requests.exceptions import ConnectionError
import os
import traceback
import time

class GoogleSheet:
    
    def __init__(self, service_account:str) -> None:
        try:
            self.sa = gspread.service_account(filename=service_account)  # type: ignore
        except Exception:
            traceback.print_exc()
        
    def update_sold_items(self, filename:str, sheetname:str, sold_items:list[dict]):
        added, updated = [], []

        # Strip header
        sheets = self.sa.open(filename)
        wsh = sheets.worksheet(sheetname)
        row_number = 1
        header = [value.strip() for value in wsh.row_values(row_number)]
        wsh.update('A{}'.format(row_number), [header])
        
        products = wsh.get_all_records(numericise_ignore=['all'])
        
        col_map = {
            'Sold Price': 'earning',
            'Sold Date': 'date',
            'Sold Platform': 'platform'
        }
        
        for i, item in enumerate(sold_items):
            index = self.item_in_products(item['item_code'], products)
            if index == -1:
                # Add new item
                col_map['Name'] = 'name'
                row = len(products) + 2
                for key in col_map:
                    value = item.get(col_map[key], '')
                    wsh.update_cell(row, header.index(key)+1, value)
                
                added.append(item['item_code'])
            else:
                # Update existing item
                row = index + 2
                for key in col_map:
                    value = item.get(col_map[key], '')
                    wsh.update_cell(row, header.index(key)+1, value)
                updated.append(item['item_code'])
                
            if i % 14 == 0:
                time.sleep(60)

        print('Added: {}'.format(added))
        print('Updated: {}'.format(updated))
            
            
    def item_in_products(self, item_code:str, products:list[dict]) -> int:
        item_code = str(item_code).strip()
        
        for index, product in enumerate(products):
            if item_code in str(product['Name']):
                return index
        return -1
    
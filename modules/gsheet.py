import gspread
import pandas as pd
from gspread.exceptions import SpreadsheetNotFound
from requests.exceptions import ConnectionError
import os
import traceback

class GoogleSheet:
    
    def __init__(self, service_account:str) -> None:
        try:
            self.sa = gspread.service_account(filename=service_account)  # type: ignore
        except Exception:
            traceback.print_exc()
    
    def read_sheet(self, filename:str, sheetname:str) -> list[dict]:
        try:
            sheets = self.sa.open(filename)
            wsh = sheets.worksheet(sheetname)
            
            return wsh.get_all_records()  
        except (SpreadsheetNotFound, ConnectionError):
            print('SpreadsheetNotFound: {} + {}'.format(filename, sheetname))
        
        return []   
        
        
    def update_sheet(self, filename:str, sheetname:str, data:list[dict], columns=[]):
        try:
            sheets = self.sa.open(filename)
            wsh = sheets.worksheet(sheetname)
            
            df = pd.DataFrame(data)
            df = df[columns] if columns else df
            df = df.fillna('')
            
            wsh.clear()
            wsh.update([df.columns.values.tolist()] + df.values.tolist())
        except SpreadsheetNotFound:
            print('Spreadsheet not found: {} + {}'.format(filename, sheetname))
            os.system('pause')
        
        
    def update_sold_items(self, filename:str, sheetname:str, sold_items:list[dict]):
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
        added, updated = [], []
        
        for item in sold_items:
            index = self.item_in_products(item['item_code'], products)
            if index == -1:
                # Add new item
                new_product = {key:item.get(col_map.get(key, ''), '') for key in header}
                new_product['Name'] = item['name']
                products.append(new_product)
                added.append(item['item_code'])
            else:
                # Update existing item
                for key in col_map:
                    products[index][key] = item[col_map[key]]
                updated.append(item['item_code'])

        # Save the changes
        self.update_sheet(filename, sheetname, products, header)
        print('Added: {}'.format(added))
        print('Updated: {}'.format(updated))
            
    def item_in_products(self, item_code:str, products:list[dict]) -> int:
        item_code = str(item_code).strip()
        
        for index, product in enumerate(products):
            if item_code in str(product['Name']):
                return index
        
        return -1
    
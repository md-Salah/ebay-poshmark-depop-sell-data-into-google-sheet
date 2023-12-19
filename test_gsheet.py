from modules.gsheet import GoogleSheet


gsheet = GoogleSheet('sa-test.json')

filename = 'INVENTORY/SALES (2023)'
sheetname = 'LISTINGS'

# listings = gsheet.read_sheet(filename, sheetname)
# print(len(listings))
# print(listings[:2])


# data, cell = gsheet.find_a_row(filename, sheetname, '003212')
# if data:
#     print(data)
#     data['SKU'] = '003212'
#     gsheet.update_a_row(filename, sheetname, data, cell.row)
    
# data, cell = gsheet.find_a_row(filename, sheetname, '003212')
# print(data)

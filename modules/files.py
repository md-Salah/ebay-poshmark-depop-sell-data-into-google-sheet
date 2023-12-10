import pandas as pd
import traceback
from typing import Optional

def read_txt(filename:str) -> Optional[str]:
    try:
        with open(filename, "r") as file:
            return file.read()
    except FileNotFoundError:
        print(f'File "{filename}" not found')
    except Exception:
        traceback.print_exc()
    
    return None


def write_to_txt(data:str, filename:str='output.txt') -> None:
    try:
        with open(filename, 'w', encoding='utf-8') as file:
            file.write(data)
    except Exception:
        traceback.print_exc()


def read_sheet(filename:str, dtype: Optional[dict]=None) -> pd.DataFrame:
    df = pd.DataFrame()
    
    try:
        if filename.endswith('.csv'):
            df = pd.read_csv(filename, dtype=dtype)
        elif filename.endswith('.xlsx'):
            df = pd.read_excel(filename, dtype=dtype)
        else:
            print('File type not supported "{}"'.format(filename))
    except FileNotFoundError:
        print(f'File "{filename}" not found')
    except Exception:
        traceback.print_exc()
    
    return df


def write_to_sheet(df: pd.DataFrame, filename:str='output.csv') -> None:
    try:
        if filename.endswith('.csv'):
            df.to_csv(filename, index=False)
        elif filename.endswith('.xlsx'):
            df.to_excel(filename, index=False)
        else:
            print('File type not supported "{}"'.format(filename))
    except PermissionError:
        print(f'File: "{filename}" is open with another software')
        input('Close the file and press ENTER to save data: ')
        write_to_sheet(df, filename)
    except Exception:
        traceback.print_exc()
        

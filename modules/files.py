import os
import json
from typing import List

def load_json(filename: str) -> List[dict]:
    if not os.path.exists(filename):
        return []

    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except Exception:
        return []


def dump_json(filename: str, data: dict) -> None:
    if not os.path.exists(filename.split('/')[0]):
        os.makedirs(filename.split('/')[0])
    
    with open(filename, 'w') as f:
        json.dump(data, f)

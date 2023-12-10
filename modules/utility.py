def price_float(price:str) -> float:
    if not price.strip():
        return 0
    return round(float(price.replace('€', '').replace('.', '').replace(',', '.').strip()), 2)

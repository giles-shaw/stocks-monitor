import requests
from sys import argv


iex_batch_url = 'https://api.iextrading.com/1.0/stock/market/batch'

symbols = argv
symbols = ','.join(symbols)
payload = {'symbols': symbols, 'types': 'price'}

r = requests.get(
   iex_batch_url,
   params=payload
   )
r = r.json()

for ticker, details in r.items():
    print(f'{ticker}: {details["price"]}')

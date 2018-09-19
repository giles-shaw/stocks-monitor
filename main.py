import requests
import urwid
from sys import argv


iex_batch_url = 'https://api.iextrading.com/1.0/stock/market/batch'

symbols = argv
symbols = ','.join(symbols)
payload = {'symbols': symbols, 'types': 'price'}

msg = urwid.Text('Press any key to refresh:')


def refresh(c):

    r = requests.get(
       iex_batch_url,
       params=payload
       )
    r = r.json()

    txt = ''
    for ticker, details in r.items():
        txt = txt + f'{ticker}: {details["price"]}\n'
    msg.set_text(txt)


# refresh(0)
fill = urwid.Filler(msg, 'top')
loop = urwid.MainLoop(fill, unhandled_input=refresh)
loop.run()

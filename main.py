import asyncio
import threading
from datetime import datetime
from sys import argv
from time import sleep

import requests
import urwid

iex_batch_url = "https://api.iextrading.com/1.0/stock/market/batch"

symbols = argv
symbols = ",".join(symbols)
payload = {"symbols": symbols, "types": "price"}

msg = urwid.Text("Fetching data...")


def exit_on_any_key(_):
    raise urwid.ExitMainLoop()


def refresh():

    while True:
        r = requests.get(iex_batch_url, params=payload)
        r = r.json()

        txt = ""
        for ticker, details in r.items():
            txt = txt + f'{ticker}: {details["price"]}\n'

        txt += f'Time is: {datetime.now().strftime("%X")}\n'
        txt += "Press any key to exit."
        msg.set_text(txt)
        sleep(1)


watcher = threading.Thread(target=refresh)
# refresh(0)
fill = urwid.Filler(msg, "top")
loop = urwid.MainLoop(fill, unhandled_input=exit_on_any_key)

watcher.start()
loop.run()

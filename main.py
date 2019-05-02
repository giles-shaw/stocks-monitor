import asyncio
import random
from datetime import datetime
from sys import argv
from threading import Thread
from time import sleep
from typing import Any, Dict, List, Union

import requests
import urwid
from numpy import random

IEX_BATCH_URL = "https://api.iextrading.com/1.0/stock/market/batch"


def exit_on_any_key(_):
    raise urwid.ExitMainLoop()


class Prices:
    def __init__(self, symbols):
        self.symbols = symbols
        self.prices = self.get_prices()

    def get_prices(self):
        r = requests.get(
            IEX_BATCH_URL, params={"symbols": ",".join(
                self.symbols), "types": "price"}
        )
        return r.json()

    def get_fake_prices(self):
        for details in self.prices.values():
            details["price"] += random.normal(0, 1)
        return self.prices

    def update_loop(self, delay=10):
        while True:
            self.prices = self.get_fake_prices()
            sleep(delay)


def refresh(loop: urwid.MainLoop, args):

    prices, fill, msg = args
    txt = ""
    for ticker, details in prices.prices.items():
        txt = txt + f'{ticker}: {details["price"]}\n'
    msg.set_text(txt)
    loop.draw_screen()
    loop.set_alarm_in(1, refresh, (prices, fill, msg))


def gui(prices: Prices):

    msg = urwid.Text("")
    fill = urwid.Filler(msg, "top")
    loop = urwid.MainLoop(fill, unhandled_input=exit_on_any_key)
    loop.set_alarm_in(0, refresh, (prices, fill, msg))
    loop.run()


def stocks_monitor(symbols: List[str]):

    prices = Prices(symbols)
    updater = Thread(target=prices.update_loop, daemon=True)
    updater.start()

    gui(prices)


def cli():

    symbols = argv[1:]
    stocks_monitor(symbols)


if __name__ == "__main__":
    cli()

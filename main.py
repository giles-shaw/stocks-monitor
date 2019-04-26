import asyncio
import random
import threading
from datetime import datetime
from sys import argv
from time import sleep
from typing import Any, Dict, List, Union

import requests
import urwid

iex_batch_url = "https://api.iextrading.com/1.0/stock/market/batch"


def exit_on_any_key(_):
    raise urwid.ExitMainLoop()


# def update_stock_info(info) -> Dict[str, Union[str, float]]:
#
#     while True:
#         for symbol in info.keys():
#             info[symbol] = {"price": random.randint(1, 101)}
#         sleep(1)


class Prices:
    def __init__(self, symbols):
        self.symbols = symbols
        self.prices = self.get_prices()
        if self.prices is None:
            raise ValueError("prices is None")

    def get_prices(self):
        r = requests.get(
            iex_batch_url, params={"symbols": ",".join(
                self.symbols), "types": "price"}
        )
        if r.status_code // 100 == 2:
            return r.json()
        else:
            raise Error()

    def get_fake_prices(self):
        for details in self.prices.values():
            details["price"] += 1
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
    txt += "Press any key to exit."
    msg.set_text(txt)
    loop.draw_screen()
    loop.set_alarm_in(1, refresh, (prices, fill, msg))


def gui(prices: Prices):

    msg = urwid.Text("Press any key to exit.")
    fill = urwid.Filler(msg, "top")
    loop = urwid.MainLoop(fill, unhandled_input=exit_on_any_key)
    loop.set_alarm_in(0, refresh, (prices, fill, msg))
    loop.run()


def stocks_monitor(symbols: List[str]):

    prices = Prices(symbols)
    updater = threading.Thread(target=prices.update_loop)
    updater.daemon = True
    updater.start()

    gui(prices)


def cli():

    symbols = argv[1:]
    stocks_monitor(symbols)


if __name__ == "__main__":
    cli()

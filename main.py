from sys import argv
from threading import Thread
from time import sleep
from typing import List

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
        return list(v["price"] for v in r.json().values())

    def get_fake_prices(self):

        return [p + round(random.normal(0, 1), 2) for p in self.prices]

    def update_loop(self, delay=5):
        while True:
            self.prices = self.get_fake_prices()
            sleep(delay)


def get_prices_column(prices):

    return ["Price"] + ["\n{0:.2f}".format(p) for p in prices]


def get_symbols_column(symbols):

    return ["Stock"] + ["\n" + sym for sym in symbols]


def refresh(loop: urwid.MainLoop, args):

    prices, stock_column, prices_column = args

    # txt = ""
    # for ticker, details in prices.prices.items():
    #     txt = txt + f'{ticker}: {details["price"]}\n'

    # msg.set_text(txt)
    stock_column.set_text(get_symbols_column(prices.symbols))
    prices_column.set_text(get_prices_column(prices.prices_string))
    loop.draw_screen()
    loop.set_alarm_in(1, refresh, (prices, stock_column, prices_column))


def gui(prices: Prices):

    stock_column = urwid.Text(get_symbols_column(prices.symbols))
    prices_column = urwid.Text(get_prices_column(prices.prices))

    columns = urwid.Columns(
        [("pack", stock_column), ("pack", prices_column)], dividechars=1
    )
    fill = urwid.Filler(columns, "top")
    loop = urwid.MainLoop(fill, unhandled_input=exit_on_any_key)
    loop.set_alarm_in(0, refresh, (prices, stock_column, prices_column))
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

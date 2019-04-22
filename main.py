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
#         payload = requests.get(
#             iex_batch_url, params={
#                 "symbols": ",".join(symbols), "types": "price"}
#         ).json()
#         for symbol in info.keys():
#             info[symbol] = payload[symbol]
#         sleep(10)


def update_stock_info(info) -> Dict[str, Union[str, float]]:

    while True:
        for symbol in info.keys():
            info[symbol] = {"price": random.randint(1, 101)}
        sleep(1)


def refresh(loop: urwid.MainLoop, args):

    info, fill, msg = args
    txt = ""
    for ticker, details in info.items():
        txt = txt + f'{ticker}: {details["price"]}\n'
    txt += "Press any key to exit."
    msg.set_text(txt)
    loop.draw_screen()
    loop.set_alarm_in(1, refresh, (info, fill, msg))


def gui(info: Dict[str, Union[str, float]]):

    msg = urwid.Text("Fetching data...")
    fill = urwid.Filler(msg, "top")
    loop = urwid.MainLoop(fill, unhandled_input=exit_on_any_key)
    loop.set_alarm_in(0, refresh, (info, fill, msg))
    loop.run()


def stocks_monitor(symbols: List[str]):

    info = dict((s, {"price": None}) for s in symbols)
    updater = threading.Thread(target=update_stock_info, args=(info,))
    updater.daemon = True
    updater.start()

    gui(info)


def cli():

    symbols = argv[1:]
    print(symbols)
    stocks_monitor(symbols)


if __name__ == "__main__":
    cli()

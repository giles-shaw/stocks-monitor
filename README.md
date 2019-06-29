# stocks-monitor
A command line utility for viewing real time stock ticker information provided by the [IEX Cloud Stocks API](https://iexcloud.io/).

## Authentication
`stocks-monitor` requires a free account with IEX Cloud and an associated [publishable API key](https://iexcloud.io/docs/api/#authentication). Create a folder named `stocks-monitor` in the directory defined by the environment variable `$XDG_CONFIG_HOME` if it exists and in `$HOME/.config` otherwise. Put a file `credentials.toml` there containing a line of the form `iex_publishable_token = "your_api_token_here"`. An example `credentials.toml` file can be found in the `templates` folder.

## Usage
Once your `credentials.toml` file is in place, simply run, for instance, 
```
stocks-monitor -s AAPL MSFT
```
to display up to date stock information.

If the markets are closed, use 
```
stocks-monitor -t -s AAPL MSFT
```
to run `stocks-monitor` in testing mode with simulated data based on the last trading day.

`stocks-monitor` can sort the information it presents to you according to any of the columns displayed. Simply press the index key of the corresponding column (i.e., press `1` to sort by the first column, `2` to sort by the second column). `stocks-monitor` will sort numeric columns in descending order and text based columns in ascending order. Attempting to sort an already sorted column will reverse the sort order.


## IEX Cloud API Limits
IEX Cloud limit the number of monthly requests that users can make to their API for free. Users are allocated a fixed number of [IEX Cloud Messages](https://iexcloud.io/docs/api/#data-weighting) at the start of each month and different requests to the IEX Cloud API consume different numbers of IEX Cloud Messages. Note that `stocks-monitor` will consume some of these on your behalf continuously at a certain rate when run without the `-t` testing option, and that a fixed number of messages are consumed when fetching information from the previous trading day whenever `stocks-monitor` is run with the `-t` option.


## Configuration
Some aspects of `stocks-monitor`'s behaviour can be configured by placing a `config.toml` file following the schema provided in `templates` in your `stocks-monitor` folder:

* You can define a default list of stock ticker symbols for `stocks-monitor` to use in the absence of other arguments. Once such a list is defined, running `stocks-monitor` or `stocks-monitor -t` without additional arguments will now display information for your default list of ticker symbols from here on after.

* `stocks-monitor` can be configured to display any stock attributes which are accessible via the [IEX Cloud quote call](https://iexcloud.io/docs/api/#quote). IEX Cloud attribute names can be verbose, so you can set aliases for them as well.

* You can configure how long `stocks-monitor` waits between sending requests to the IEX Cloud API. Beware that setting a lower request wait time will result in `stocks-monitor` consuming IEX Cloud `messages` on your behalf at a faster rate. 

## Requirements
`stocks-monitor` requires `Python 3.6` or higher, and the libraries `urwid`, `numpy`, `pandas`, `toml`, and `requests`. `stocks-monitor` has been tested using `zsh` and `bash` on `macOS Mojave`.

## Installation
```
mkdir stocks-monitor && cd stocks-monitor 
git pull "https://github.com/giles-shaw/stocks-monitor" && python setup.py install
``` 
As usual, it is recommended that you do this inside of a virtual environment.

## Contact
Comments and suggestions are much appreciated. Email giles.shaw@gmail.com


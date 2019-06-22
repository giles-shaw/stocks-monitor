# stocks-monitor
A command line utility for viewing real time stock ticker information provided by the [IEX Cloud Stocks API](https://iexcloud.io/).

## Authentication
`stocks-monitor` requires a free account with IEX Cloud and its associated [publishable API key](https://iexcloud.io/docs/api/#authentication). Create a folder named `.stocks-monitor` in your home folder and put a file `credentials.toml` there containing a line of the form `iex_publishable_token = "your_api_token_here"`. An example `credentials.toml` file can be found in the `templates` folder.

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

`stocks-monitor` can sort the information it presents to you according to any of the columns displayed. Simply press the index key of the corresponding column (i.e., press `1` to sort by the first column, `2` to sort by the first column). `stocks-monitor` will sort numeric columns in descending order and text based columns in ascending order. Attempting to sort an already sorted column will reverse the sort order.

## Configuration

`stocks-monitor` can be configured to run with a default set of stock ticker symbols. To do this, create a `config.toml` file following the schema provided in `templates` and place this in your `.stocks-monitor` folder. Running `stocks-monitor` or `stocks-monitor -t` without additional arguments will now refer to your default list of ticker symbols from here on after.

Additionally, `config.toml` allows for `stocks-monitor` to be configured to display any stock attributes which are accessible via the [IEX Cloud quote call](https://iexcloud.io/docs/api/#quote). IEX Cloud attribute names can be verbose, so you can set aliases for them as well.

## Requirements
`stocks-monitor` requires `Python 3.7` or higher, and the libraries `urwid`, `numpy`, `pandas`, `toml`, and `requests`. `stocks-monitor` has been tested using `zsh` and `bash` on `macOS Mojave`.

## Installation

```
mkdir stocks-monitor && cd stocks-monitor 
git pull "https://github.com/giles-shaw/stocks-monitor" && python setup.py install
``` 
As usual, it is recommended that you do this inside of a virtual environment.

## Contact
Comments and suggestions are much appreciated. Email giles.shaw@gmail.com


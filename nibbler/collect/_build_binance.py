import ccxt
import pathlib as pt


binance = ccxt.binance()
markets = binance.fetch_markets()
firstMarket = markets[0]
cwd = pt.Path(__file__).parent

lines = \
"\
from . import Collector\n\n\n\
\
class _Meta(Collector):\n\
    _exchange = \"binance\"\n\
    limit = 1000\n\n\n\
"

for market in markets:
    lines += \
f"\
class %s(_Meta):\n\
    symbol = \"%s\"\n\n\n\
"%(market["id"], market["symbol"])

with open(cwd/"binance.py", "w") as f:
    f.write(lines)


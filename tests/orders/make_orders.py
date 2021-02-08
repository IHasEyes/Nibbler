import nibbler as nb
import pathlib as pt
import bokeh.plotting as bkp
from bokeh.plotting import output_file
from bokeh.io import show, export_png

cwd = pt.Path(__file__).parent
resource_directory = (cwd/"../../resources/data").absolute()
assert resource_directory.exists()

btc_15m = resource_directory/"BTC_USDT_15m.csv"
btc_1h = resource_directory/"BTC_USDT_1h.csv"
btc_4h = resource_directory/"BTC_USDT_4h.csv"

if __name__ == "__main__":

    binance_exchange = nb.exchanges.Exchange("binance")

    # register a new market to the exchange
    btc_market = binance_exchange.new_spot_market("BTC", "USDT")
    btc_market.add_ohlcv_feed_from_csv(btc_15m, btc_1h, btc_4h)

    # create a new user account
    new_account = binance_exchange.new_account()
    # fund their accounts
    new_account.spot_wallets["USDT"].fund(1000)
    new_account.futures_wallet.fund(1000)
    # create an order
    order_generated = False
    output_file("./run.html")

    binance_exchange.initialize()
    for i in range(1000): binance_exchange.step()

    btc_market.plot_multi_timeframe_ohlcv()
    fig = btc_market.plot_multi_timeframe_ohlcv()
    buy_order = nb.exchanges.SpotBuyOrder(btc_market, new_account, 4200, 0.1)
    buy_order.plot(fig.children[0].children[0])
    order_generated = True
    show(fig)
    print(new_account.spot_wallets)
    print(new_account.spot_portfolio_value())

    for i in range(200): binance_exchange.step()
    print(new_account.spot_wallets)
    print(new_account.spot_portfolio_value())

    btc_market.plot_multi_timeframe_ohlcv()
    fig = btc_market.plot_multi_timeframe_ohlcv()
    sell_order = nb.exchanges.SpotSellOrder(btc_market, new_account, 4500, 0.1)
    sell_order.plot(fig.children[0].children[0])
    show(fig)
    print(new_account.spot_wallets)
    print(new_account.spot_portfolio_value())

    for i in range(1000): binance_exchange.step()
    print(new_account.spot_wallets)
    print(new_account.spot_portfolio_value())
    btc_market.plot_multi_timeframe_ohlcv()
    fig = btc_market.plot_multi_timeframe_ohlcv()
    show(fig)

    for i in range(1): binance_exchange.step()
    print(new_account.spot_wallets)

    print(new_account.futures_wallet)
    print(new_account.spot_portfolio_value())

    pass

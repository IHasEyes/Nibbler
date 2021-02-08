import nibbler as nb
import pathlib as pt

cwd = pt.Path(__file__).parent
resource_directory = cwd/"../../resources/data"
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

    print(new_account.spot_wallets["USDT"])
    print(new_account.futures_wallet)

    pass
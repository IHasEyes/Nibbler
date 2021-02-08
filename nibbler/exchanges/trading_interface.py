from .exchange import Exchange, Account
from ..markets import Market, Spot, Futures
import abc


class TradingInterface(abc.ABC):

    def __init__(self, market: Market, exchange: Exchange, account: Account):
        self.exchange = exchange
        self.account  = account
        self.market   = market
        assert account.id in exchange.accounts.keys(), \
            "trading account not registered to exchange"

    @abc.abstractmethod
    def limit_buy(self, price, amount, *args, **kwargs):
        NotImplemented

    @abc.abstractmethod
    def limit_sell(self, price, amount, *args, **kwargs):
        NotImplemented

    @abc.abstractmethod
    def market_buy(self, amount, *args, **kwargs):
        NotImplemented

    @abc.abstractmethod
    def market_self(self, amount, *args, **kwargs):
        NotImplemented

    @abc.abstractmethod
    def stop_limit_buy(self, amount, *args, **kwargs):
        NotImplemented

    @abc.abstractmethod
    def stop_limit_sell(self, amount, *args, **kwargs):
        NotImplemented

class SpotTrading(TradingInterface):

    def __init__(self, market: Spot, exchange: Exchange, account: Account):
        assert isinstance(market, Spot), "input market is not a spot market"
        super().__init__(market, exchange, account)
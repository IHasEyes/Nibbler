import abc
from . exchange import Exchange, Account
from ..markets import Market


class Order(abc.ABC):

    side = None
    kind = None

    @classmethod
    def from_total_spent(
        cls,
        market : Market,
        account: Account,
        price  : float,
        total  : float
    ):
        amount = total/price
        return cls(market, account, price, amount)

    @abc.abstractmethod
    def check_already_triggered(self, market, price):
        NotImplemented

    def __init__(
        self,
        market         : Market,
        account        : Account,
        price          : float,
        amount         : float,
        timestop       : int = None,
        is_market_price: bool = False,
        logger = None
    ):
        if self.check_already_triggered(market, price):
            is_market_price = True
        assert market.kind == self.kind
        self.market          = market

        self.account         = account

        if is_market_price:
            self.price = self.market.current_close
        else:
            self.price = price

        self.amount          = amount
        self.is_market_price = is_market_price
        self.id              = None
        self.vault           = 0
        self.set_timestop(timestop)

        self.initialize()
        self.add_self_to_market_and_account()

        # function which logs transaction on open and close
        self.logger = logger
        if self.logger is not None:
            self.logger.on_open()

    @property
    def fees(self):
        if self.is_market_price:
            return self.market.taker_fee
        return self.market.maker_fee

    def withdraw(self, amount):
        # assert amount <= self.vault, "withdrawn amount is greater than vault
        # balance"
        if amount > self.vault: amount = self.vault
        self.vault -= amount
        return amount

    def add_self_to_market_and_account(self):
        order_dict = self.market.orders[self.account]
        order_id = len(order_dict)
        while order_id in order_dict.keys():
            order_id += 1
        self.id = order_id
        order_dict[order_id] = self
        self.account.orders[self.market][order_id] = self

    def set_timestop(self, timestop):
        if timestop is not None:
            if timestop > self.market.currentdatetime:
                self.timestop = timestop
            else:
                raise Exception("Assigned timestop is in the past")
        else:
            self.timestop = None

    def is_timestopped(self):
        if self.timestop is not None:
            if self.market.current_datetime >= self.timestop:
                return True
        return False

    def process(self):

        if self.is_market_price:
            self.price = self.market.current_open

        if self.check_triggered():
            self.on_fill()
            # as the order has been fill log the data with the logging function
            if self.logger is not None:
                self.logger.on_fill()
            if self.vault == 0:
                self.close()
            return 0

        if self.is_timestopped():
            self.close()
            return 0

    def close(self):
        self.return_vault()
        self.close_datetime = self.market.master_feed.current_datetime
        if self.logger is not None:
            self.logger.on_close()
        del self.market.orders[self.account][self.id]
        del self.account.orders[self.market][self.id]

    @abc.abstractmethod
    def check_triggered(self):
        NotImplemented

    @abc.abstractmethod
    def initialize(self):
        NotImplemented

    @abc.abstractmethod
    def on_fill(self):
        NotImplemented

    @abc.abstractmethod
    def return_vault(self):
        NotImplemented
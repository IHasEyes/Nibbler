from .orders import Order
from ..markets import Market
from . import SpotWallet, Account, Wallet
import abc
import bokeh.plotting as bp
from bokeh.models import Span


class SpotOrder(Order):
    '''
    abstract class for spot sell and buy orders
    '''

    kind = "spot"

    @property
    def wallet_1(self) -> Wallet:
        # sellers wallet i.e. if market is btcusdt, it will be the btc wallet
        return self.account.spot_wallets[self.market.pair1]

    @property
    def wallet_2(self)-> Wallet:
        # buyers wallet i.e. if market is btcusdt, it will be the usdt wallet
        return self.account.spot_wallets[self.market.pair2]

# ---------------------------------------------------------------------------- #
class SpotBuyOrder(SpotOrder):

    side = "long"

    def check_already_triggered(self, market: Market, price: float):
        # when entering a buy order the buy order price must be less than or equal to
        # the current price, if it is greater than the current price then the order
        # is converted into a market order
        return price >= market.current_close

    def check_triggered(self):
        return self.market.current_low <= self.price

    def initialize(self):
        self.vault += self.wallet_2.withdraw(self.amount*self.price)

    def on_fill(self):
        # get the slippage from the market
        intended_quantity  = self.vault/self.price
        quantity_filled    = self.market.fill_amount(intended_quantity)
        # now to burn the fees
        self.withdraw(quantity_filled*self.price)
        self.wallet_1.fund(quantity_filled*(1-self.fees))

    def return_vault(self):
        self.wallet_2.fund(self.vault)
        self.vault = 0

    def plot(self, fig: bp.Figure=None, line_width=2, **kwargs):
        if fig is None:
            fig = bp.figure(**kwargs)
        hline = Span(
            location=self.price, dimension="width", line_color="green",
            line_width=line_width
        )
        fig.renderers.extend([hline])
        return fig

# ---------------------------------------------------------------------------- #
class SpotSellOrder(SpotOrder):

    side = "short"

    def check_already_triggered(self, market: Market, price: float):
        # if price is less than or equal to the current candle close the
        # order will automatically be triggered
        return price <= market.current_close

    def check_triggered(self):
        return self.market.current_high >= self.price

    def initialize(self):
        self.vault += self.wallet_1.withdraw(self.amount)

    def on_fill(self):
        quantity_filled = self.market.fill_amount(self.vault)
        self.wallet_2.fund(
            self.withdraw(quantity_filled)*self.price*(1-self.fees)
        )

    def return_vault(self):
        self.wallet_1.fund(self.vault)
        self.vault = 0

    def plot(self, fig: bp.Figure=None, line_width=2, **kwargs):
        if fig is None:
            fig = bp.figure(**kwargs)
        hline = Span(
            location=self.price, dimension="width", line_color="red",
            line_width=line_width
        )
        fig.renderers.extend([hline])
        return fig
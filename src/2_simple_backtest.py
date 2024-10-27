from datetime import date, datetime, timedelta
from typing import Union
from demeter import TokenInfo, Actuator, Strategy, RowData, MarketInfo, MarketTypeEnum, ChainType, AtTimeTrigger
from demeter.aave import AaveBalance, AaveV3Market, AaveTokenStatus
import pandas as pd

global market

class ExampleStrategy(Strategy):
    def initialize(self):
        # Define a base date in June
        base_date = datetime(2024, 6, 5, 0, 0, 0) 

        # Create triggers with offsets from the base date
        supply_trigger = AtTimeTrigger(time=base_date + timedelta(days=1), do=self.supply)
        borrow_trigger = AtTimeTrigger(time=base_date + timedelta(days=2), do=self.borrow)
        repay_trigger = AtTimeTrigger(time=base_date + timedelta(days=3), do=self.repay)
        withdraw_trigger = AtTimeTrigger(time=base_date + timedelta(days=4), do=self.withdraw)
        self.triggers.extend([supply_trigger, withdraw_trigger, borrow_trigger, repay_trigger])
        self.counter = 0

    def supply(self, row_data: RowData):
        self.supply_key = market.supply(weth, 20, True)

    def borrow(self, row_data: RowData):
        self.borrow_key = market.borrow(weth, 1)

    def repay(self, row_data: RowData):
        market.repay(self.borrow_key)

    def withdraw(self, row_data: RowData):
        market.withdraw(self.supply_key)

    def on_bar(self, row_data: RowData):
        balance: AaveBalance = market.get_market_balance()
        market_status: Union[pd.Series, AaveTokenStatus] = row_data.market_status[market_key]
        self.counter += 1
        if self.counter%1440 == 0:
            print("\n\n{} June 2024".format(self.counter//1440))
            print(balance)
            print(market_status)
    
if __name__ == "__main__":
    usdc = TokenInfo(name="usdc", decimal=18, address="0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174")
    weth = TokenInfo(name="weth", decimal=18, address="0x7ceB23fD6bC0adD59E62ac25578270cFf1b9f619")
    token_list = [ usdc, weth ]

    market_key = MarketInfo("aave", MarketTypeEnum.aave_v3)
    market = AaveV3Market(market_key, "../data/riskparameters.csv", token_list)
    
    #Dataset downloaded from BigQuery
    market.data_path = "../data/sample"

    market.load_data(
        chain=ChainType.polygon,
        token_info_list=market.tokens,
        start_date=date(2024, 6, 1),
        end_date=date(2024, 6, 30),
    )

    actuator = Actuator()
    broker = actuator.broker
    broker.add_market(market)
    broker.set_balance(usdc, 20)
    broker.set_balance(weth, 100)
    actuator.strategy = ExampleStrategy()
    prices_df = pd.read_csv("../data/WETH_USDC_Prices.csv", index_col=0, parse_dates=True)

    actuator.set_price(prices_df)

    actuator.run()
    